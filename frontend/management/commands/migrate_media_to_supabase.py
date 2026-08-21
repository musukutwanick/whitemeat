"""
Django management command: migrate_media_to_supabase

Run on Render Shell after setting SUPABASE_URL and SUPABASE_KEY:

  python manage.py migrate_media_to_supabase              # migrate + verify
  python manage.py migrate_media_to_supabase --dry-run    # preview only
  python manage.py migrate_media_to_supabase --upload-orphans  # also upload unlinked disk files
  python manage.py migrate_media_to_supabase --no-verify  # skip HTTP verification step

SAFETY: Does NOT delete any files. DB updated ONLY after upload+verify succeeds.
"""
import os
import io
import uuid
import json
import mimetypes
import requests
from datetime import datetime, timezone

from django.core.management.base import BaseCommand
from django.conf import settings
from frontend.models import Accessory, MenuItem, Notice

try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

try:
    from supabase import create_client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False


def _make_unique_path(dest_folder, filename):
    uid = uuid.uuid4().hex[:8]
    base, ext = os.path.splitext(filename)
    return f"{dest_folder}/{uid}_{base}{ext}"


def _public_url(supabase_url, bucket, path):
    return f"{supabase_url.rstrip('/')}/storage/v1/object/public/{bucket}/{path}"


def _find_local_file(media_root, raw_path):
    raw = str(raw_path).replace("\\", "/").strip("/")
    basename = os.path.basename(raw)
    candidates = [
        os.path.join(media_root, raw),
        os.path.join(media_root, basename),
        os.path.join(media_root, "accessory_images", basename),
        os.path.join(media_root, "menu_images", basename),
        os.path.join(media_root, "equipment", basename),
        os.path.join(media_root, "menu", basename),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


def _verify_url(url):
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            if HAS_PILLOW:
                try:
                    img = Image.open(io.BytesIO(resp.content))
                    img.verify()
                except Exception:
                    pass  # non-image files (docs) are fine if HTTP 200
            return True, "HTTP 200 OK"
        return False, f"HTTP {resp.status_code}"
    except Exception as e:
        return False, str(e)


def _upload(client, bucket, local_path, dest_path):
    with open(local_path, "rb") as fh:
        data = fh.read()
    content_type, _ = mimetypes.guess_type(local_path)
    content_type = content_type or "image/jpeg"
    client.storage.from_(bucket).upload(
        path=dest_path,
        file=data,
        file_options={"content-type": content_type, "upsert": "true"},
    )


class Command(BaseCommand):
    help = "Safely migrate existing local media (equipment & menu images) to Supabase Storage."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true",
                            help="Preview without uploading or changing DB.")
        parser.add_argument("--no-verify", action="store_true",
                            help="Skip HTTP URL verification after upload.")
        parser.add_argument("--upload-orphans", action="store_true",
                            help="Also upload unlinked disk files to Supabase (no DB update).")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        verify = not options["no_verify"]
        upload_orphans = options["upload_orphans"]

        supabase_url = (getattr(settings, "SUPABASE_URL", None) or os.environ.get("SUPABASE_URL", "")).rstrip("/")
        supabase_key = getattr(settings, "SUPABASE_KEY", None) or os.environ.get("SUPABASE_KEY", "")
        bucket = getattr(settings, "SUPABASE_BUCKET_NAME", None) or os.environ.get("SUPABASE_BUCKET_NAME", "website-images")
        media_root = str(settings.MEDIA_ROOT)

        # ── Preflight ──────────────────────────────────────────
        if not HAS_SUPABASE:
            self.stderr.write(self.style.ERROR(
                "supabase package not installed. Run: pip install supabase"
            ))
            return
        if not supabase_url or not supabase_key:
            self.stderr.write(self.style.ERROR(
                "SUPABASE_URL and SUPABASE_KEY must be set as environment variables."
            ))
            return

        client = create_client(supabase_url, supabase_key)

        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE("SUPABASE MEDIA MIGRATION"))
        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(f"Bucket      : {bucket}")
        self.stdout.write(f"MEDIA_ROOT  : {media_root}")
        self.stdout.write(f"Dry run     : {dry_run}")
        self.stdout.write(f"Verify URLs : {verify}\n")

        results = []

        # ── Equipment ──────────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("1. Equipment / Accessory Images"))
        for acc in Accessory.objects.all().order_by("id"):
            r = {"id": acc.id, "type": "Equipment", "name": acc.name,
                 "old_path": "", "new_path": "", "new_url": "", "status": "PENDING"}

            if not acc.image:
                r["status"] = "EMPTY (no image in DB)"
                self.stdout.write(f"  SKIP  #{acc.id} {acc.name}: no image field")
                results.append(r)
                continue

            cur = str(acc.image.name).replace("\\", "/").strip("/")
            r["old_path"] = cur

            if cur.startswith("equipment/") and len(os.path.basename(cur)) > 9:
                r["status"] = "ALREADY_MIGRATED"
                r["new_path"] = cur
                r["new_url"] = _public_url(supabase_url, bucket, cur)
                self.stdout.write(f"  SKIP  #{acc.id} {acc.name}: already in equipment/")
                results.append(r)
                continue

            local = _find_local_file(media_root, cur)
            if not local:
                r["status"] = "MISSING"
                self.stdout.write(self.style.WARNING(f"  MISS  #{acc.id} {acc.name}: no file on disk for '{cur}'"))
                results.append(r)
                continue

            dest = _make_unique_path("equipment", os.path.basename(local))
            url = _public_url(supabase_url, bucket, dest)
            r["new_path"] = dest
            r["new_url"] = url

            if dry_run:
                r["status"] = "DRY_RUN"
                self.stdout.write(self.style.NOTICE(
                    f"  DRY   #{acc.id} {acc.name}: {os.path.basename(local)} -> {dest}"
                ))
                results.append(r)
                continue

            try:
                self.stdout.write(f"  UP    #{acc.id} {acc.name}: {os.path.basename(local)} -> {dest}")
                _upload(client, bucket, local, dest)

                if verify:
                    ok, msg = _verify_url(url)
                    if not ok:
                        r["status"] = f"ERROR_VERIFY: {msg}"
                        self.stdout.write(self.style.ERROR(f"        VERIFY FAIL: {msg}"))
                        results.append(r)
                        continue
                    self.stdout.write(self.style.SUCCESS(f"        VERIFIED: {url}"))

                # DB update ONLY after successful upload + verify
                acc.image.name = dest
                acc.save(update_fields=["image"])
                r["status"] = "SUCCESS"
                self.stdout.write(self.style.SUCCESS(f"        DB UPDATED"))

            except Exception as e:
                r["status"] = f"ERROR: {e}"
                self.stdout.write(self.style.ERROR(f"        ERROR: {e}"))

            results.append(r)

        # ── Menu Items ─────────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("\n2. Menu Item Images"))
        for m in MenuItem.objects.all().select_related("branch").order_by("id"):
            label = f"{m.name} ({m.branch.name if m.branch else '?'})"
            r = {"id": m.id, "type": "Menu", "name": label,
                 "old_path": "", "new_path": "", "new_url": "", "status": "PENDING"}

            if not m.image:
                r["status"] = "EMPTY (no image in DB)"
                results.append(r)
                continue

            cur = str(m.image.name).replace("\\", "/").strip("/")
            r["old_path"] = cur

            if cur.startswith("menu/") and len(os.path.basename(cur)) > 9:
                r["status"] = "ALREADY_MIGRATED"
                r["new_path"] = cur
                r["new_url"] = _public_url(supabase_url, bucket, cur)
                self.stdout.write(f"  SKIP  #{m.id} {m.name}: already in menu/")
                results.append(r)
                continue

            local = _find_local_file(media_root, cur)
            if not local:
                r["status"] = "MISSING"
                self.stdout.write(self.style.WARNING(f"  MISS  #{m.id} {m.name}: no file on disk for '{cur}'"))
                results.append(r)
                continue

            dest = _make_unique_path("menu", os.path.basename(local))
            url = _public_url(supabase_url, bucket, dest)
            r["new_path"] = dest
            r["new_url"] = url

            if dry_run:
                r["status"] = "DRY_RUN"
                self.stdout.write(self.style.NOTICE(
                    f"  DRY   #{m.id} {m.name}: {os.path.basename(local)} -> {dest}"
                ))
                results.append(r)
                continue

            try:
                self.stdout.write(f"  UP    #{m.id} {m.name}: {os.path.basename(local)} -> {dest}")
                _upload(client, bucket, local, dest)

                if verify:
                    ok, msg = _verify_url(url)
                    if not ok:
                        r["status"] = f"ERROR_VERIFY: {msg}"
                        self.stdout.write(self.style.ERROR(f"        VERIFY FAIL: {msg}"))
                        results.append(r)
                        continue
                    self.stdout.write(self.style.SUCCESS(f"        VERIFIED: {url}"))

                m.image.name = dest
                m.save(update_fields=["image"])
                r["status"] = "SUCCESS"
                self.stdout.write(self.style.SUCCESS(f"        DB UPDATED"))

            except Exception as e:
                r["status"] = f"ERROR: {e}"
                self.stdout.write(self.style.ERROR(f"        ERROR: {e}"))

            results.append(r)

        # ── Notice Attachments ─────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("\n3. Notice Images & Documents"))
        for n in Notice.objects.all().order_by("id"):
            for field_name, folder in [("image", "notices"), ("document", "notices/documents")]:
                field_file = getattr(n, field_name)
                if not field_file:
                    continue
                cur = str(field_file.name).replace("\\", "/").strip("/")
                local = _find_local_file(media_root, cur)
                r = {"id": n.id, "type": f"Notice/{field_name}", "name": n.title,
                     "old_path": cur, "new_path": "", "new_url": "", "status": "PENDING"}

                if not local:
                    r["status"] = "MISSING"
                    self.stdout.write(self.style.WARNING(f"  MISS  #{n.id} {n.title} ({field_name}): file not found"))
                    results.append(r)
                    continue

                dest = _make_unique_path(folder, os.path.basename(local))
                url = _public_url(supabase_url, bucket, dest)
                r["new_path"] = dest
                r["new_url"] = url

                if dry_run:
                    r["status"] = "DRY_RUN"
                    self.stdout.write(self.style.NOTICE(f"  DRY   #{n.id} {n.title}/{field_name} -> {dest}"))
                    results.append(r)
                    continue

                try:
                    _upload(client, bucket, local, dest)
                    if verify:
                        ok, msg = _verify_url(url)
                        if not ok:
                            r["status"] = f"ERROR_VERIFY: {msg}"
                            results.append(r)
                            continue
                    setattr(n, field_name + "_path_", dest)  # save new path
                    field_file.name = dest
                    n.save(update_fields=[field_name])
                    r["status"] = "SUCCESS"
                    self.stdout.write(self.style.SUCCESS(f"  OK    #{n.id} {n.title}/{field_name} -> {url}"))
                except Exception as e:
                    r["status"] = f"ERROR: {e}"
                    self.stdout.write(self.style.ERROR(f"  ERR   #{n.id} {n.title}/{field_name}: {e}"))
                results.append(r)

        # ── Orphaned Files ─────────────────────────────────────
        if upload_orphans:
            self.stdout.write(self.style.MIGRATE_HEADING("\n4. Unlinked Orphan Files on Disk"))
            linked = set()
            for acc in Accessory.objects.all():
                if acc.image:
                    p = _find_local_file(media_root, str(acc.image.name))
                    if p:
                        linked.add(os.path.abspath(p))
            for m in MenuItem.objects.all():
                if m.image:
                    p = _find_local_file(media_root, str(m.image.name))
                    if p:
                        linked.add(os.path.abspath(p))

            if os.path.exists(media_root):
                for root, dirs, files in os.walk(media_root):
                    rel_dir = os.path.relpath(root, media_root).replace("\\", "/")
                    for fname in files:
                        full_p = os.path.join(root, fname)
                        if os.path.abspath(full_p) in linked:
                            continue
                        folder = "equipment" if ("accessory" in rel_dir.lower() or "equipment" in rel_dir.lower()) else "menu"
                        dest = _make_unique_path(folder, fname)
                        url = _public_url(supabase_url, bucket, dest)
                        r = {"id": "orphan", "type": f"Orphan/{folder}", "name": fname,
                             "old_path": f"{rel_dir}/{fname}", "new_path": dest, "new_url": url,
                             "status": "PENDING"}
                        if dry_run:
                            r["status"] = "DRY_RUN"
                            self.stdout.write(self.style.NOTICE(f"  DRY   [orphan] {fname} -> {dest}"))
                        else:
                            try:
                                _upload(client, bucket, full_p, dest)
                                if verify:
                                    ok, msg = _verify_url(url)
                                    r["status"] = "SUCCESS" if ok else f"UPLOADED (verify: {msg})"
                                else:
                                    r["status"] = "SUCCESS"
                                self.stdout.write(self.style.SUCCESS(f"  OK    [orphan] {fname} -> {url}"))
                            except Exception as e:
                                r["status"] = f"ERROR: {e}"
                                self.stdout.write(self.style.ERROR(f"  ERR   [orphan] {fname}: {e}"))
                        results.append(r)

        # ── Final Report ───────────────────────────────────────
        self._print_report(results)

        # Save JSON report
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(str(settings.BASE_DIR), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        report_path = os.path.join(backup_dir, f"migration_report_{ts}.json")
        with open(report_path, "w", encoding="utf-8") as fh:
            json.dump({"run_time": ts, "dry_run": dry_run, "results": results}, fh, indent=2)
        self.stdout.write(f"\nReport saved: {report_path}")

    def _print_report(self, results):
        self.stdout.write("\n" + "=" * 100)
        self.stdout.write("MIGRATION REPORT")
        self.stdout.write("=" * 100)
        self.stdout.write(f"{'ID':<6} | {'Type':<14} | {'Item Name':<35} | {'Old Path':<35} | {'Status'}")
        self.stdout.write("-" * 100)
        for r in results:
            nm = r["name"][:33] + ".." if len(r["name"]) > 35 else r["name"]
            op = r["old_path"][:33] + ".." if len(r["old_path"]) > 35 else r["old_path"]
            self.stdout.write(f"{str(r['id']):<6} | {r['type']:<14} | {nm:<35} | {op:<35} | {r['status']}")
        self.stdout.write("=" * 100)

        success = [r for r in results if r["status"] == "SUCCESS"]
        missing = [r for r in results if r["status"] == "MISSING"]
        empty   = [r for r in results if "EMPTY" in r["status"]]
        already = [r for r in results if r["status"] == "ALREADY_MIGRATED"]
        errors  = [r for r in results if r["status"].startswith("ERROR")]

        self.stdout.write(self.style.SUCCESS(f"\n  Successfully migrated & DB updated : {len(success)}"))
        self.stdout.write(f"  Already migrated (skipped)         : {len(already)}")
        self.stdout.write(f"  No image in DB (menu items etc.)   : {len(empty)}")
        self.stdout.write(self.style.WARNING(f"  Missing file on disk               : {len(missing)}"))
        self.stdout.write(self.style.ERROR(  f"  Errors                             : {len(errors)}"))

        if success:
            self.stdout.write(self.style.SUCCESS("\n--- SUCCESSFULLY MIGRATED ---"))
            for r in success:
                self.stdout.write(f"  ID {r['id']:>4} | {r['name']}")
                self.stdout.write(f"          OLD: {r['old_path']}")
                self.stdout.write(f"          NEW: {r['new_url']}")

        if missing:
            self.stdout.write(self.style.WARNING("\n--- MISSING FILES (no action taken) ---"))
            for r in missing:
                self.stdout.write(f"  ID {r['id']:>4} | {r['name']} | OLD: {r['old_path']} | Status: MISSING")
