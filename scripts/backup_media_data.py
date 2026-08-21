import os
import sys
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whitemeat_backend.settings')
django.setup()

from django.conf import settings
from frontend.models import MenuItem, Accessory, Notice

def create_backup():
    backup_dir = os.path.join(str(BASE_DIR), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'pre_migration_media_backup_{timestamp}.json')
    latest_backup_path = os.path.join(backup_dir, 'pre_migration_media_backup.json')

    # Collect Equipment
    equipment_data = []
    for acc in Accessory.objects.all().order_by('id'):
        equipment_data.append({
            'id': acc.id,
            'name': acc.name,
            'description': acc.description,
            'price': str(acc.price),
            'image_field': str(acc.image.name) if acc.image else '',
            'is_available': acc.is_available,
            'created_at': acc.created_at.isoformat() if acc.created_at else None,
            'updated_at': acc.updated_at.isoformat() if acc.updated_at else None,
        })

    # Collect Menu Items
    menu_data = []
    for m in MenuItem.objects.all().select_related('branch', 'category').order_by('id'):
        menu_data.append({
            'id': m.id,
            'name': m.name,
            'branch_id': m.branch.id if m.branch else None,
            'branch_name': m.branch.name if m.branch else None,
            'category_id': m.category.id if m.category else None,
            'category_name': m.category.name if m.category else None,
            'price': str(m.price),
            'image_field': str(m.image.name) if m.image else '',
            'image_filename': m.image_filename or '',
            'is_available': m.is_available,
            'is_featured': m.is_featured,
        })

    # Collect Notices
    notice_data = []
    for n in Notice.objects.all().order_by('id'):
        notice_data.append({
            'id': n.id,
            'title': n.title,
            'image_field': str(n.image.name) if n.image else '',
            'document_field': str(n.document.name) if n.document else '',
        })

    # Collect disk files
    disk_files = []
    media_dir = str(settings.MEDIA_ROOT)
    if os.path.exists(media_dir):
        for root, dirs, files in os.walk(media_dir):
            for f in files:
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, media_dir).replace('\\', '/')
                disk_files.append({
                    'relative_path': rel_p,
                    'full_path': full_p,
                    'size_bytes': os.path.getsize(full_p),
                })

    backup_payload = {
        'backup_timestamp_utc': timestamp,
        'equipment_count': len(equipment_data),
        'equipment': equipment_data,
        'menu_items_count': len(menu_data),
        'menu_items': menu_data,
        'notices_count': len(notice_data),
        'notices': notice_data,
        'disk_files_count': len(disk_files),
        'disk_files': disk_files,
    }

    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(backup_payload, f, indent=2)

    with open(latest_backup_path, 'w', encoding='utf-8') as f:
        json.dump(backup_payload, f, indent=2)

    print(f"Backup created successfully at:")
    print(f" - {backup_path}")
    print(f" - {latest_backup_path}")
    print(f"Saved {len(equipment_data)} equipment records, {len(menu_data)} menu records, {len(disk_files)} disk file entries.")

if __name__ == '__main__':
    create_backup()
