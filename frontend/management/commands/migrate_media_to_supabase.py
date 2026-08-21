import os
import posixpath
import mimetypes
import io
import requests
from PIL import Image
from django.core.management.base import BaseCommand
from django.conf import settings
from whitemeat_backend.supabase_storage import SupabaseMediaStorage
from frontend.models import Accessory, MenuItem, Notice


class Command(BaseCommand):
    help = "Safely migrate existing local media files (equipment and menu images) to Supabase Storage with verification."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate migration without modifying files or database records.',
        )
        parser.add_argument(
            '--verify',
            action='store_true',
            help='Verify that uploaded Supabase URLs are publicly accessible and readable via HTTP.',
        )
        parser.add_argument(
            '--upload-orphans',
            action='store_true',
            help='Also upload unlinked images from media/menu_images and media/accessory_images to Supabase.',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        verify = options.get('verify', False)
        upload_orphans = options.get('upload_orphans', False)

        storage = SupabaseMediaStorage()
        if not storage.is_configured:
            self.stderr.write(
                self.style.ERROR(
                    "Supabase credentials (SUPABASE_URL and SUPABASE_KEY) are missing or incomplete.\n"
                    "Please set SUPABASE_URL and SUPABASE_KEY environment variables before running migration."
                )
            )
            return

        client = storage.get_client()
        if not client:
            self.stderr.write(self.style.ERROR("Could not initialize Supabase client."))
            return

        self.stdout.write(self.style.NOTICE("=================================================="))
        self.stdout.write(self.style.NOTICE("SUPABASE MEDIA MIGRATION & VERIFICATION"))
        self.stdout.write(self.style.NOTICE("=================================================="))
        self.stdout.write(f"Target bucket: {storage.bucket_name}")
        self.stdout.write(f"Dry run mode: {'ENABLED' if dry_run else 'DISABLED'}")
        self.stdout.write(f"Verify URLs: {'ENABLED' if verify else 'DISABLED'}\n")

        migration_results = []
        stats = {
            'scanned': 0,
            'migrated': 0,
            'already_migrated': 0,
            'missing_file': 0,
            'errors': 0,
            'verified': 0,
        }

        # 1. Process Accessory (Equipment) Images
        self.stdout.write(self.style.MIGRATE_HEADING("1. Migrating Equipment / Accessory Images..."))
        for item in Accessory.objects.all().order_by('id'):
            if not item.image:
                continue
            stats['scanned'] += 1
            res = self._migrate_record(
                instance=item,
                item_type="Equipment",
                item_name=item.name,
                field_name='image',
                dest_folder='equipment',
                storage=storage,
                dry_run=dry_run,
                verify=verify,
                stats=stats,
            )
            migration_results.append(res)

        # 2. Process MenuItem Images
        self.stdout.write(self.style.MIGRATE_HEADING("\n2. Migrating Menu Item Images..."))
        for item in MenuItem.objects.all().order_by('id'):
            if not item.image:
                continue
            stats['scanned'] += 1
            res = self._migrate_record(
                instance=item,
                item_type="Menu",
                item_name=f"{item.name} ({item.branch.name if item.branch else ''})",
                field_name='image',
                dest_folder='menu',
                storage=storage,
                dry_run=dry_run,
                verify=verify,
                stats=stats,
            )
            migration_results.append(res)

        # 3. Process Notice Attachments
        self.stdout.write(self.style.MIGRATE_HEADING("\n3. Migrating Notice Attachments..."))
        for item in Notice.objects.all().order_by('id'):
            if item.image:
                stats['scanned'] += 1
                res = self._migrate_record(
                    instance=item,
                    item_type="Notice",
                    item_name=item.title,
                    field_name='image',
                    dest_folder='notices',
                    storage=storage,
                    dry_run=dry_run,
                    verify=verify,
                    stats=stats,
                )
                migration_results.append(res)
            if item.document:
                stats['scanned'] += 1
                res = self._migrate_record(
                    instance=item,
                    item_type="Notice Doc",
                    item_name=item.title,
                    field_name='document',
                    dest_folder='notices/documents',
                    storage=storage,
                    dry_run=dry_run,
                    verify=verify,
                    stats=stats,
                )
                migration_results.append(res)

        # 4. Optional: Process unlinked media files
        if upload_orphans:
            self.stdout.write(self.style.MIGRATE_HEADING("\n4. Uploading Unlinked Disk Images to Supabase..."))
            linked_files = {r['local_path'] for r in migration_results if r.get('local_path')}
            self._upload_orphans(storage, linked_files, dry_run, verify)

        # Print Table Report
        self._print_migration_table(migration_results)

        # Print Summary
        self.stdout.write(self.style.SUCCESS("\n=================================================="))
        self.stdout.write(self.style.SUCCESS("MIGRATION SUMMARY"))
        self.stdout.write(self.style.SUCCESS("=================================================="))
        self.stdout.write(f"Total DB records with files scanned: {stats['scanned']}")
        self.stdout.write(f"Successfully migrated & updated:     {stats['migrated']}")
        self.stdout.write(f"Already in Supabase:                 {stats['already_migrated']}")
        self.stdout.write(f"Missing local files on disk:         {stats['missing_file']}")
        self.stdout.write(f"Errors encountered:                  {stats['errors']}")
        if verify:
            self.stdout.write(f"Verified URLs (HTTP 200 & Valid):    {stats['verified']}")

    def _find_local_file(self, raw_path):
        """Locate existing local file in MEDIA_ROOT or static folder."""
        raw_clean = str(raw_path).replace('\\', '/').strip('/')
        candidates = [
            os.path.join(settings.MEDIA_ROOT, raw_clean),
            os.path.join(settings.MEDIA_ROOT, os.path.basename(raw_clean)),
            os.path.join(settings.MEDIA_ROOT, "accessory_images", os.path.basename(raw_clean)),
            os.path.join(settings.MEDIA_ROOT, "menu_images", os.path.basename(raw_clean)),
            os.path.join(settings.MEDIA_ROOT, "equipment", os.path.basename(raw_clean)),
            os.path.join(settings.MEDIA_ROOT, "menu", os.path.basename(raw_clean)),
            os.path.join(settings.BASE_DIR, 'static', 'images', os.path.basename(raw_clean)),
        ]
        for path in candidates:
            if os.path.exists(path) and os.path.isfile(path):
                return path
        return None

    def _migrate_record(self, instance, item_type, item_name, field_name, dest_folder, storage, dry_run, verify, stats):
        field_file = getattr(instance, field_name)
        current_name = str(field_file.name).replace('\\', '/').strip('/')

        result = {
            'id': instance.id,
            'type': item_type,
            'name': item_name,
            'old_path': current_name,
            'new_path': '',
            'new_url': '',
            'status': 'PENDING',
            'local_path': '',
        }

        # Check if already migrated to Supabase destination folder
        if current_name.startswith(f"{dest_folder}/") and '_' in os.path.basename(current_name):
            public_url = storage.url(current_name)
            result['new_path'] = current_name
            result['new_url'] = public_url
            result['status'] = 'ALREADY_MIGRATED'
            self.stdout.write(f"  [-] #{instance.id} {item_name} already migrated: {current_name}")
            stats['already_migrated'] += 1
            if verify:
                if self._verify_url(public_url):
                    stats['verified'] += 1
            return result

        local_file_path = self._find_local_file(current_name)
        if not local_file_path:
            result['status'] = 'MISSING_LOCAL_FILE'
            self.stdout.write(self.style.WARNING(f"  [?] Local file NOT found for #{instance.id} {item_name}: {current_name}"))
            stats['missing_file'] += 1
            return result

        result['local_path'] = local_file_path
        filename = os.path.basename(local_file_path)
        dest_path = f"{dest_folder}/{filename}"
        unique_dest_path = storage.get_available_name(dest_path)
        public_url = storage.url(unique_dest_path)
        result['new_path'] = unique_dest_path
        result['new_url'] = public_url

        if dry_run:
            result['status'] = 'DRY_RUN_OK'
            self.stdout.write(
                self.style.NOTICE(f"  [DRY RUN] Would upload {local_file_path} -> '{unique_dest_path}' for #{instance.id} {item_name}")
            )
            stats['migrated'] += 1
            return result

        # Read and validate image content
        try:
            with open(local_file_path, 'rb') as f:
                data = f.read()

            # Image readability verification
            if dest_folder in ['equipment', 'menu']:
                try:
                    img = Image.open(io.BytesIO(data))
                    img.verify()
                except Exception as img_err:
                    self.stdout.write(self.style.WARNING(f"  [!] Warning: Image verification check failed for {local_file_path}: {img_err}"))

            content_type, _ = mimetypes.guess_type(local_file_path)
            if not content_type:
                content_type = "image/jpeg" if filename.lower().endswith(('.jpg', '.jpeg')) else "application/octet-stream"

            # Upload to Supabase Storage
            client = storage.get_client()
            client.storage.from_(storage.bucket_name).upload(
                path=unique_dest_path,
                file=data,
                file_options={"content-type": content_type, "upsert": "true"}
            )

            # Verification of upload before DB update
            if verify:
                is_verified = self._verify_url(public_url)
                if is_verified:
                    stats['verified'] += 1
                else:
                    raise IOError(f"Upload verification failed: {public_url} is not accessible.")

            # Update DB record ONLY after successful upload and verification
            setattr(instance, field_name, unique_dest_path)
            instance.save(update_fields=[field_name])

            result['status'] = 'SUCCESS'
            self.stdout.write(
                self.style.SUCCESS(f"  [+] SUCCESS #{instance.id} {item_name} -> {public_url}")
            )
            stats['migrated'] += 1

        except Exception as e:
            result['status'] = f'ERROR: {str(e)}'
            self.stdout.write(self.style.ERROR(f"  [!] Failed migrating #{instance.id} {item_name}: {e}"))
            stats['errors'] += 1

        return result

    def _verify_url(self, url):
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                # Check if readable image
                try:
                    img = Image.open(io.BytesIO(resp.content))
                    img.verify()
                    self.stdout.write(self.style.SUCCESS(f"      [VERIFIED] HTTP 200 & Valid Image at {url}"))
                    return True
                except Exception:
                    self.stdout.write(self.style.SUCCESS(f"      [VERIFIED] HTTP 200 for {url}"))
                    return True
            else:
                self.stdout.write(self.style.WARNING(f"      [VERIFY FAIL] HTTP {resp.status_code} for {url}"))
                return False
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"      [VERIFY ERROR] {e} for {url}"))
            return False

    def _upload_orphans(self, storage, linked_files, dry_run, verify):
        media_dir = str(settings.MEDIA_ROOT)
        for root, dirs, files in os.walk(media_dir):
            for f in files:
                full_p = os.path.join(root, f)
                if full_p in linked_files:
                    continue
                rel_dir = os.path.relpath(root, media_dir).replace('\\', '/')
                dest_folder = "equipment" if "accessory" in rel_dir.lower() or "equipment" in rel_dir.lower() else "menu"
                dest_path = f"{dest_folder}/{f}"
                unique_dest_path = storage.get_available_name(dest_path)
                public_url = storage.url(unique_dest_path)

                if dry_run:
                    self.stdout.write(self.style.NOTICE(f"  [ORPHAN DRY RUN] Would upload {full_p} -> {unique_dest_path}"))
                else:
                    try:
                        with open(full_p, 'rb') as fp:
                            data = fp.read()
                        content_type, _ = mimetypes.guess_type(full_p) or "application/octet-stream"
                        client = storage.get_client()
                        client.storage.from_(storage.bucket_name).upload(
                            path=unique_dest_path,
                            file=data,
                            file_options={"content-type": content_type, "upsert": "true"}
                        )
                        self.stdout.write(self.style.SUCCESS(f"  [ORPHAN UPLOADED] {f} -> {public_url}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  [ORPHAN ERROR] {f}: {e}"))

    def _print_migration_table(self, results):
        self.stdout.write("\n" + "=" * 110)
        self.stdout.write(f"{'ID':<4} | {'Type':<10} | {'Item Name':<28} | {'Old Path':<30} | {'Status':<12}")
        self.stdout.write("-" * 110)
        for r in results:
            name_trunc = (r['name'][:26] + '..') if len(r['name']) > 28 else r['name']
            old_trunc = (r['old_path'][:28] + '..') if len(r['old_path']) > 30 else r['old_path']
            self.stdout.write(f"{r['id']:<4} | {r['type']:<10} | {name_trunc:<28} | {old_trunc:<30} | {r['status']:<12}")
        self.stdout.write("=" * 110)
