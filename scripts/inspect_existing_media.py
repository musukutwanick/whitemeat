import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whitemeat_backend.settings')
django.setup()

from django.conf import settings
from frontend.models import MenuItem, Accessory, RestaurantBranch, MenuCategory

def main():
    print("==================================================")
    print("STEP 1 & 2: DETAILED MEDIA & DATABASE INSPECTION")
    print("==================================================")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print(f"STORAGES: {getattr(settings, 'STORAGES', 'Not set')}")
    print(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set')}")
    print(f"SUPABASE_URL configured: {bool(os.environ.get('SUPABASE_URL'))}")
    print(f"SUPABASE_KEY configured: {bool(os.environ.get('SUPABASE_KEY'))}")
    print(f"SUPABASE_BUCKET_NAME: {os.environ.get('SUPABASE_BUCKET_NAME', 'website-images')}")

    print("\n--------------------------------------------------")
    print("PHYSICAL FILES PRESENT ON DISK IN MEDIA_ROOT")
    print("--------------------------------------------------")
    media_dir = str(settings.MEDIA_ROOT)
    disk_files = []
    if os.path.exists(media_dir):
        for root, dirs, files in os.walk(media_dir):
            for f in files:
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, media_dir).replace('\\', '/')
                sz = os.path.getsize(full_p)
                disk_files.append((rel_p, full_p, sz))
                print(f"  [FILE ON DISK] {rel_p} ({sz} bytes)")
    else:
        print("  MEDIA_ROOT directory does not exist on disk.")

    print(f"Total files on disk: {len(disk_files)}")

    print("\n--------------------------------------------------")
    print("EQUIPMENT (ACCESSORY) DATABASE AUDIT")
    print("--------------------------------------------------")
    accessories = list(Accessory.objects.all().order_by('id'))
    print(f"Total Equipment / Accessory items in DB: {len(accessories)}")
    equipment_audit = []
    for acc in accessories:
        img_name = str(acc.image.name) if acc.image else ""
        phys_path = None
        if img_name:
            c1 = os.path.join(settings.MEDIA_ROOT, img_name)
            c2 = os.path.join(settings.MEDIA_ROOT, os.path.basename(img_name))
            c3 = os.path.join(settings.MEDIA_ROOT, "accessory_images", os.path.basename(img_name))
            c4 = os.path.join(settings.MEDIA_ROOT, "equipment", os.path.basename(img_name))
            for cand in [c1, c2, c3, c4]:
                if os.path.exists(cand) and os.path.isfile(cand):
                    phys_path = cand
                    break
        
        status = "FOUND" if phys_path else ("EMPTY" if not img_name else "MISSING")
        equipment_audit.append({
            "id": acc.id,
            "name": acc.name,
            "price": str(acc.price),
            "image_field": img_name,
            "phys_path": phys_path,
            "status": status,
        })
        print(f"  ID {acc.id:2d} | {acc.name:<30} | ImageField: '{img_name}' | Status: {status}")

    print("\n--------------------------------------------------")
    print("MENU ITEMS DATABASE AUDIT")
    print("--------------------------------------------------")
    menu_items = list(MenuItem.objects.all().select_related('branch', 'category').order_by('id'))
    print(f"Total Menu Items in DB: {len(menu_items)}")
    menu_audit = []
    for m in menu_items:
        img_name = str(m.image.name) if m.image else ""
        img_fn = m.image_filename or ""
        phys_path = None
        
        # Check image field
        if img_name:
            c1 = os.path.join(settings.MEDIA_ROOT, img_name)
            c2 = os.path.join(settings.MEDIA_ROOT, os.path.basename(img_name))
            c3 = os.path.join(settings.MEDIA_ROOT, "menu_images", os.path.basename(img_name))
            c4 = os.path.join(settings.MEDIA_ROOT, "menu", os.path.basename(img_name))
            for cand in [c1, c2, c3, c4]:
                if os.path.exists(cand) and os.path.isfile(cand):
                    phys_path = cand
                    break
        
        # Check static fallback if image_filename exists
        static_path = None
        if img_fn:
            s1 = os.path.join(settings.BASE_DIR, "static", "images", img_fn)
            if os.path.exists(s1):
                static_path = s1

        status = "FOUND (MEDIA)" if phys_path else ("FOUND (STATIC)" if static_path else ("EMPTY" if not img_name and not img_fn else "MISSING"))
        menu_audit.append({
            "id": m.id,
            "name": m.name,
            "branch": m.branch.name if m.branch else "",
            "category": m.category.name if m.category else "",
            "image_field": img_name,
            "image_filename": img_fn,
            "phys_path": phys_path or static_path,
            "status": status,
        })
        print(f"  ID {m.id:2d} | {m.name:<30} | Branch: {m.branch.name:<25} | ImageField: '{img_name}' | ImageFilename: '{img_fn}' | Status: {status}")

    print("\n--------------------------------------------------")
    print("ORPHANED FILES ON DISK (NOT LINKED TO ANY DB RECORD)")
    print("--------------------------------------------------")
    linked_paths = set()
    for item in equipment_audit + menu_audit:
        if item["phys_path"]:
            linked_paths.add(os.path.abspath(item["phys_path"]))

    orphaned = []
    for rel_p, full_p, sz in disk_files:
        if os.path.abspath(full_p) not in linked_paths:
            orphaned.append((rel_p, full_p, sz))
            print(f"  [ORPHAN FILE ON DISK] {rel_p} ({sz} bytes)")

    if not orphaned:
        print("  None. All disk files are referenced in DB.")

    print("\n==================================================")
    print("INSPECTION COMPLETE")
    print("==================================================")

if __name__ == "__main__":
    main()
