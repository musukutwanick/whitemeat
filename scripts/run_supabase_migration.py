"""
Full Supabase Storage Migration Script
Runs Steps 3-8: Backup → Upload → Verify → Update DB → Report

Usage (from project root):
  python scripts/run_supabase_migration.py

Requires:
  SUPABASE_URL and SUPABASE_KEY environment variables to be set.

Does NOT delete any old files. Safe to re-run.
"""
import os
import sys
import json
import io
import mimetypes
import uuid
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whitemeat_backend.settings')
django.setup()

from django.conf import settings
from frontend.models import Accessory, MenuItem

try:
    from supabase import create_client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False

try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

import requests

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
MENU_BUCKET = os.environ.get("SUPABASE_MENU_BUCKET_NAME", "Menu images")
EQUIPMENT_BUCKET = os.environ.get("SUPABASE_EQUIPMENT_BUCKET_NAME", "equipment")
BUCKET_FOR = {"equipment": EQUIPMENT_BUCKET, "menu": MENU_BUCKET}
MEDIA_ROOT = str(settings.MEDIA_ROOT)
BACKUP_DIR = os.path.join(str(BASE_DIR), "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# SAFETY CHECKS
# ─────────────────────────────────────────────
def check_prerequisites():
    errors = []
    if not HAS_SUPABASE:
        errors.append("supabase Python package is not installed. Run: pip install supabase")
    if not SUPABASE_URL:
        errors.append("SUPABASE_URL environment variable is not set.")
    if not SUPABASE_KEY:
        errors.append("SUPABASE_KEY environment variable is not set.")
    return errors

# ─────────────────────────────────────────────
# BACKUP (Step 3)
# ─────────────────────────────────────────────
def create_backup():
    ts = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_DIR, f"migration_backup_{ts}.json")
    latest_path = os.path.join(BACKUP_DIR, "pre_supabase_migration_backup.json")

    equipment_data = []
    for acc in Accessory.objects.all().order_by('id'):
        equipment_data.append({
            "id": acc.id, "name": acc.name,
            "image_field": str(acc.image.name) if acc.image else "",
            "price": str(acc.price), "is_available": acc.is_available,
        })

    menu_data = []
    for m in MenuItem.objects.all().select_related('branch', 'category').order_by('id'):
        menu_data.append({
            "id": m.id, "name": m.name,
            "branch": m.branch.name if m.branch else "",
            "image_field": str(m.image.name) if m.image else "",
            "image_filename": m.image_filename or "",
        })

    disk_files = []
    if os.path.exists(MEDIA_ROOT):
        for root, dirs, files in os.walk(MEDIA_ROOT):
            for f in files:
                fp = os.path.join(root, f)
                rel = os.path.relpath(fp, MEDIA_ROOT).replace("\\", "/")
                disk_files.append({"path": rel, "size": os.path.getsize(fp)})

    payload = {
        "backup_time_utc": ts,
        "equipment": equipment_data,
        "menu_items": menu_data,
        "disk_files": disk_files,
    }
    for p in [backup_path, latest_path]:
        with open(p, 'w', encoding='utf-8') as fh:
            json.dump(payload, fh, indent=2)

    print(f"  [BACKUP] Saved to {backup_path}")
    return payload

# ─────────────────────────────────────────────
# FILE FINDER
# ─────────────────────────────────────────────
def find_local_file(raw_path):
    raw = str(raw_path).replace("\\", "/").strip("/")
    basename = os.path.basename(raw)
    candidates = [
        os.path.join(MEDIA_ROOT, raw),
        os.path.join(MEDIA_ROOT, basename),
        os.path.join(MEDIA_ROOT, "accessory_images", basename),
        os.path.join(MEDIA_ROOT, "menu_images", basename),
        os.path.join(MEDIA_ROOT, "equipment", basename),
        os.path.join(MEDIA_ROOT, "menu", basename),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None

# ─────────────────────────────────────────────
# UPLOAD TO SUPABASE
# ─────────────────────────────────────────────
def make_unique_name(dest_folder, original_filename):
    base, ext = os.path.splitext(original_filename)
    uid = uuid.uuid4().hex[:8]
    return f"{dest_folder}/{uid}_{base}{ext}"

def public_url(path, dest_folder):
    bucket = BUCKET_FOR.get(dest_folder, EQUIPMENT_BUCKET)
    return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}"

def upload_to_supabase(client, local_path, dest_folder, original_filename=None):
    if original_filename is None:
        original_filename = os.path.basename(local_path)
    dest_path = make_unique_name(dest_folder, original_filename)
    bucket = BUCKET_FOR.get(dest_folder, EQUIPMENT_BUCKET)

    with open(local_path, 'rb') as fh:
        data = fh.read()

    content_type, _ = mimetypes.guess_type(local_path)
    content_type = content_type or "image/jpeg"

    client.storage.from_(bucket).upload(
        path=dest_path,
        file=data,
        file_options={"content-type": content_type, "upsert": "true"}
    )
    return dest_path

# ─────────────────────────────────────────────
# VERIFY UPLOADED URL
# ─────────────────────────────────────────────
def verify_url(url):
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            return False, f"HTTP {resp.status_code}"
        # Try to verify it's a readable image
        if HAS_PILLOW:
            try:
                img = Image.open(io.BytesIO(resp.content))
                img.verify()
            except Exception:
                pass  # Not all files are images (docs); pass anyway if HTTP 200
        return True, "OK"
    except Exception as e:
        return False, str(e)

# ─────────────────────────────────────────────
# REPORT
# ─────────────────────────────────────────────
def print_report(results):
    print("\n" + "=" * 120)
    print(f"{'ID':<5} | {'Type':<10} | {'Item Name':<35} | {'Old Path':<40} | {'New Supabase Path':<45} | {'Status'}")
    print("-" * 120)
    for r in results:
        name = (r['name'][:33] + '..') if len(r['name']) > 35 else r['name']
        old  = (r['old_path'][:38] + '..') if len(r['old_path']) > 40 else r['old_path']
        new  = (r['new_path'][:43] + '..') if len(r['new_path']) > 45 else r['new_path']
        print(f"{r['id']:<5} | {r['type']:<10} | {name:<35} | {old:<40} | {new:<45} | {r['status']}")
    print("=" * 120)

    # Detailed URL list for successes
    successes = [r for r in results if r['status'] == 'SUCCESS']
    if successes:
        print("\n--- SUPABASE PUBLIC URLS ---")
        for r in successes:
            print(f"  ID {r['id']} | {r['name']}")
            print(f"    OLD:  {r['old_path']}")
            print(f"    NEW:  {r['new_url']}")

    # Missing
    missing = [r for r in results if r['status'] == 'MISSING']
    if missing:
        print("\n--- MISSING / UNRECOVERABLE ---")
        for r in missing:
            print(f"  ID {r['id']} | {r['name']} | OLD PATH: {r['old_path']} | Status: MISSING")

    # Errors
    errors = [r for r in results if r['status'].startswith('ERROR')]
    if errors:
        print("\n--- ERRORS ---")
        for r in errors:
            print(f"  ID {r['id']} | {r['name']} | {r['status']}")

    print("\n--- SUMMARY ---")
    print(f"  Total processed:           {len(results)}")
    print(f"  Successfully migrated:     {len(successes)}")
    print(f"  Already migrated (skip):   {len([r for r in results if r['status'] == 'ALREADY_MIGRATED'])}")
    print(f"  Missing/no image in DB:    {len([r for r in results if r['status'] == 'EMPTY'])}")
    print(f"  Missing file on disk:      {len(missing)}")
    print(f"  Errors:                    {len(errors)}")

# ─────────────────────────────────────────────
# MAIN MIGRATION
# ─────────────────────────────────────────────
def migrate(dry_run=False, verify=True):
    results = []
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    print("\n========================================")
    print("EQUIPMENT / ACCESSORY IMAGE MIGRATION")
    print("========================================")
    for acc in Accessory.objects.all().order_by('id'):
        r = {
            "id": acc.id, "type": "Equipment", "name": acc.name,
            "old_path": "", "new_path": "", "new_url": "", "status": "PENDING",
        }

        if not acc.image:
            r["status"] = "EMPTY"
            print(f"  [SKIP] ID {acc.id} {acc.name}: no image in DB")
            results.append(r)
            continue

        current_name = str(acc.image.name).replace("\\", "/").strip("/")
        r["old_path"] = current_name

        # Already migrated?
        if current_name.startswith("equipment/") and len(os.path.basename(current_name)) > 9:
            r["new_path"] = current_name
            r["new_url"] = public_url(current_name, "equipment")
            r["status"] = "ALREADY_MIGRATED"
            print(f"  [SKIP] ID {acc.id} {acc.name}: already in equipment/")
            results.append(r)
            continue

        local_path = find_local_file(current_name)
        if not local_path:
            r["status"] = "MISSING"
            print(f"  [MISSING] ID {acc.id} {acc.name}: file not found for '{current_name}'")
            results.append(r)
            continue

        original_filename = os.path.basename(local_path)
        dest_path = make_unique_name("equipment", original_filename)
        url = public_url(dest_path, "equipment")
        r["new_path"] = dest_path
        r["new_url"] = url

        if dry_run:
            r["status"] = "DRY_RUN"
            print(f"  [DRY RUN] ID {acc.id} {acc.name}: {local_path} -> {dest_path}")
            results.append(r)
            continue

        try:
            print(f"  [UPLOADING] ID {acc.id} {acc.name}: {os.path.basename(local_path)} -> {dest_path}")
            upload_to_supabase(client, local_path, "equipment", original_filename)

            if verify:
                ok, msg = verify_url(url)
                if not ok:
                    r["status"] = f"ERROR: verify failed: {msg}"
                    print(f"    [VERIFY FAIL] {url} — {msg}")
                    results.append(r)
                    continue
                print(f"    [VERIFIED] {url}")

            # DB update ONLY after verified upload
            acc.image.name = dest_path
            acc.save(update_fields=['image'])
            r["status"] = "SUCCESS"
            print(f"    [DB UPDATED] ID {acc.id} -> {dest_path}")

        except Exception as e:
            r["status"] = f"ERROR: {e}"
            print(f"    [ERROR] ID {acc.id}: {e}")

        results.append(r)

    print("\n========================================")
    print("MENU ITEM IMAGE MIGRATION")
    print("========================================")
    for m in MenuItem.objects.all().select_related('branch').order_by('id'):
        r = {
            "id": m.id, "type": "Menu",
            "name": f"{m.name} ({m.branch.name if m.branch else ''})",
            "old_path": "", "new_path": "", "new_url": "", "status": "PENDING",
        }

        if not m.image:
            r["status"] = "EMPTY"
            results.append(r)
            continue

        current_name = str(m.image.name).replace("\\", "/").strip("/")
        r["old_path"] = current_name

        # Already migrated?
        if current_name.startswith("menu/") and len(os.path.basename(current_name)) > 9:
            r["new_path"] = current_name
            r["new_url"] = public_url(current_name, "menu")
            r["status"] = "ALREADY_MIGRATED"
            print(f"  [SKIP] ID {m.id} {m.name}: already in menu/")
            results.append(r)
            continue

        local_path = find_local_file(current_name)
        if not local_path:
            r["status"] = "MISSING"
            print(f"  [MISSING] ID {m.id} {m.name}: file not found for '{current_name}'")
            results.append(r)
            continue

        original_filename = os.path.basename(local_path)
        dest_path = make_unique_name("menu", original_filename)
        url = public_url(dest_path, "menu")
        r["new_path"] = dest_path
        r["new_url"] = url

        if dry_run:
            r["status"] = "DRY_RUN"
            print(f"  [DRY RUN] ID {m.id} {m.name}: {local_path} -> {dest_path}")
            results.append(r)
            continue

        try:
            print(f"  [UPLOADING] ID {m.id} {m.name}: {os.path.basename(local_path)} -> {dest_path}")
            upload_to_supabase(client, local_path, "menu", original_filename)

            if verify:
                ok, msg = verify_url(url)
                if not ok:
                    r["status"] = f"ERROR: verify failed: {msg}"
                    print(f"    [VERIFY FAIL] {url} — {msg}")
                    results.append(r)
                    continue
                print(f"    [VERIFIED] {url}")

            m.image.name = dest_path
            m.save(update_fields=['image'])
            r["status"] = "SUCCESS"
            print(f"    [DB UPDATED] ID {m.id} -> {dest_path}")

        except Exception as e:
            r["status"] = f"ERROR: {e}"
            print(f"    [ERROR] ID {m.id}: {e}")

        results.append(r)

    # Also upload orphaned disk files to Supabase (no DB update, just preservation)
    print("\n========================================")
    print("ORPHANED DISK FILES — UPLOADING TO SUPABASE (no DB update)")
    print("========================================")
    linked_local = set()
    for acc in Accessory.objects.all():
        if acc.image:
            p = find_local_file(str(acc.image.name))
            if p:
                linked_local.add(os.path.abspath(p))
    for m in MenuItem.objects.all():
        if m.image:
            p = find_local_file(str(m.image.name))
            if p:
                linked_local.add(os.path.abspath(p))

    orphan_results = []
    if os.path.exists(MEDIA_ROOT):
        for root, dirs, files in os.walk(MEDIA_ROOT):
            rel_dir = os.path.relpath(root, MEDIA_ROOT).replace("\\", "/")
            for fname in files:
                full_p = os.path.join(root, fname)
                if os.path.abspath(full_p) in linked_local:
                    continue  # already migrated via DB
                folder = "equipment" if "accessory" in rel_dir.lower() or "equipment" in rel_dir.lower() else "menu"
                r_orphan = {
                    "id": "orphan", "type": f"Orphan({folder})",
                    "name": fname, "old_path": f"{rel_dir}/{fname}",
                    "new_path": "", "new_url": "", "status": "PENDING",
                }
                if dry_run:
                    dest_path = make_unique_name(folder, fname)
                    r_orphan["new_path"] = dest_path
                    r_orphan["new_url"] = public_url(dest_path, folder)
                    r_orphan["status"] = "DRY_RUN"
                    print(f"  [ORPHAN DRY RUN] {fname} -> {dest_path}")
                else:
                    try:
                        dest_path = upload_to_supabase(client, full_p, folder, fname)
                        url = public_url(dest_path, folder)
                        r_orphan["new_path"] = dest_path
                        r_orphan["new_url"] = url
                        if verify:
                            ok, msg = verify_url(url)
                            if ok:
                                r_orphan["status"] = "SUCCESS"
                                print(f"  [ORPHAN UPLOADED+VERIFIED] {fname} -> {url}")
                            else:
                                r_orphan["status"] = f"UPLOADED (verify fail: {msg})"
                                print(f"  [ORPHAN UPLOADED, VERIFY FAIL] {fname}: {msg}")
                        else:
                            r_orphan["status"] = "SUCCESS (no verify)"
                            print(f"  [ORPHAN UPLOADED] {fname} -> {url}")
                    except Exception as e:
                        r_orphan["status"] = f"ERROR: {e}"
                        print(f"  [ORPHAN ERROR] {fname}: {e}")
                orphan_results.append(r_orphan)

    return results, orphan_results


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Simulate without uploading or DB changes")
    parser.add_argument("--no-verify", action="store_true", help="Skip URL verification after upload")
    args = parser.parse_args()

    print("=" * 60)
    print("SUPABASE MEDIA MIGRATION SCRIPT")
    print("=" * 60)
    print(f"SUPABASE_URL  : {SUPABASE_URL[:40]}..." if len(SUPABASE_URL) > 40 else f"SUPABASE_URL  : {SUPABASE_URL}")
    print(f"SUPABASE_KEY  : {'****' + SUPABASE_KEY[-4:] if len(SUPABASE_KEY) > 4 else '(not set)'}")
    print(f"MENU BUCKET       : {MENU_BUCKET}")
    print(f"EQUIPMENT BUCKET  : {EQUIPMENT_BUCKET}")
    print(f"MEDIA_ROOT    : {MEDIA_ROOT}")
    print(f"DRY RUN       : {args.dry_run}")
    print(f"VERIFY URLs   : {not args.no_verify}")

    errors = check_prerequisites()
    if errors:
        print("\nPREREQUISITE ERRORS:")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)

    print("\n--- STEP 3: CREATING BACKUP ---")
    backup = create_backup()
    print(f"  Backed up {backup['equipment'].__len__()} equipment, {backup['menu_items'].__len__()} menu items, {backup['disk_files'].__len__()} disk files.")

    print("\n--- STEPS 4–6: MIGRATE, VERIFY, UPDATE DB ---")
    results, orphan_results = migrate(dry_run=args.dry_run, verify=not args.no_verify)

    print("\n--- MIGRATION REPORT (DB-linked records) ---")
    print_report(results)

    if orphan_results:
        print("\n--- ORPHANED FILES REPORT ---")
        print_report(orphan_results)

    # Save results to JSON report
    ts = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(BACKUP_DIR, f"migration_report_{ts}.json")
    with open(report_path, 'w', encoding='utf-8') as fh:
        json.dump({
            "run_time": ts, "dry_run": args.dry_run,
            "db_results": results, "orphan_results": orphan_results
        }, fh, indent=2)
    print(f"\n[REPORT SAVED] {report_path}")
