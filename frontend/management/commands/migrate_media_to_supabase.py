import os
import posixpath
import mimetypes
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from whitemeat_backend.supabase_storage import SupabaseMediaStorage
from frontend.models import Accessory, MenuItem, Notice


class Command(BaseCommand):
    help = "Safely migrate existing local media files (equipment and menu images) to Supabase Storage."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate migration without modifying files or database records.',
        )
        parser.add_argument(
            '--verify',
            action='store_true',
            help='Verify that uploaded Supabase URLs are publicly accessible via HTTP GET.',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        verify = options.get('verify', False)

        storage = SupabaseMediaStorage()
        if not storage.is_configured:
            self.stderr.write(
                self.style.ERROR(
                    "Supabase credentials (SUPABASE_URL and SUPABASE_KEY) are missing or incomplete. "
                    "Please set SUPABASE_URL and SUPABASE_KEY environment variables before running this command."
                )
            )
            return

        client = storage.get_client()
        if not client:
            self.stderr.write(self.style.ERROR("Could not initialize Supabase client."))
            return

        self.stdout.write(self.style.NOTICE(f"=== Supabase Media Migration ==="))
        self.stdout.write(f"Target bucket: {storage.bucket_name}")
        self.stdout.write(f"Dry run mode: {'ENABLED' if dry_run else 'DISABLED'}\n")

        stats = {
            'scanned': 0,
            'migrated': 0,
            'already_migrated': 0,
            'missing_file': 0,
            'errors': 0,
            'verified': 0,
        }

        # 1. Process Accessory (Equipment) Images
        self.stdout.write(self.style.MIGRATE_HEADING("Processing Accessory / Equipment Images..."))
        for item in Accessory.objects.all():
            if not item.image:
                continue
            stats['scanned'] += 1
            self._migrate_record(
                instance=item,
                field_name='image',
                dest_folder='equipment',
                storage=storage,
                dry_run=dry_run,
                verify=verify,
                stats=stats,
            )

        # 2. Process MenuItem Images
        self.stdout.write(self.style.MIGRATE_HEADING("\nProcessing Menu Item Images..."))
        for item in MenuItem.objects.all():
            if not item.image:
                continue
            stats['scanned'] += 1
            self._migrate_record(
                instance=item,
                field_name='image',
                dest_folder='menu',
                storage=storage,
                dry_run=dry_run,
                verify=verify,
                stats=stats,
            )

        # 3. Process Notice Images & Documents (if any)
        self.stdout.write(self.style.MIGRATE_HEADING("\nProcessing Notice Attachments..."))
        for item in Notice.objects.all():
            if item.image:
                stats['scanned'] += 1
                self._migrate_record(
                    instance=item,
                    field_name='image',
                    dest_folder='notices',
                    storage=storage,
                    dry_run=dry_run,
                    verify=verify,
                    stats=stats,
                )
            if item.document:
                stats['scanned'] += 1
                self._migrate_record(
                    instance=item,
                    field_name='document',
                    dest_folder='notices/documents',
                    storage=storage,
                    dry_run=dry_run,
                    verify=verify,
                    stats=stats,
                )

        # Print Summary
        self.stdout.write(self.style.SUCCESS("\n=== Migration Summary ==="))
        self.stdout.write(f"Total records scanned with files: {stats['scanned']}")
        self.stdout.write(f"Successfully migrated: {stats['migrated']}")
        self.stdout.write(f"Already migrated: {stats['already_migrated']}")
        self.stdout.write(f"Local files not found: {stats['missing_file']}")
        self.stdout.write(f"Errors encountered: {stats['errors']}")
        if verify:
            self.stdout.write(f"Verified URLs (HTTP 200): {stats['verified']}")

    def _find_local_file(self, raw_path):
        """Locate existing local file in MEDIA_ROOT or static folder."""
        raw_clean = str(raw_path).replace('\\', '/').strip('/')
        candidates = [
            os.path.join(settings.MEDIA_ROOT, raw_clean),
            os.path.join(settings.MEDIA_ROOT, os.path.basename(raw_clean)),
            os.path.join(settings.BASE_DIR, 'static', 'images', os.path.basename(raw_clean)),
        ]
        for path in candidates:
            if os.path.exists(path) and os.path.isfile(path):
                return path
        return None

    def _migrate_record(self, instance, field_name, dest_folder, storage, dry_run, verify, stats):
        field_file = getattr(instance, field_name)
        current_name = str(field_file.name).replace('\\', '/').strip('/')

        # Check if already migrated to target folder
        if current_name.startswith(f"{dest_folder}/") and '_' in os.path.basename(current_name):
            self.stdout.write(f"  [-] #{instance.id} {instance} already in '{dest_folder}/': {current_name}")
            stats['already_migrated'] += 1
            if verify:
                self._verify_url(storage.url(current_name), stats)
            return

        local_file_path = self._find_local_file(current_name)
        if not local_file_path:
            self.stdout.write(self.style.WARNING(f"  [?] Local file not found for #{instance.id} {instance}: {current_name}"))
            stats['missing_file'] += 1
            return

        filename = os.path.basename(local_file_path)
        dest_path = f"{dest_folder}/{filename}"
        unique_dest_path = storage.get_available_name(dest_path)

        if dry_run:
            self.stdout.write(
                self.style.NOTICE(f"  [DRY RUN] Would upload {local_file_path} -> Supabase '{unique_dest_path}' for #{instance.id} {instance}")
            )
            stats['migrated'] += 1
            return

        # Perform actual upload
        try:
            with open(local_file_path, 'rb') as f:
                data = f.read()

            content_type, _ = mimetypes.guess_type(local_file_path)
            if not content_type:
                content_type = "application/octet-stream"

            client = storage.get_client()
            client.storage.from_(storage.bucket_name).upload(
                path=unique_dest_path,
                file=data,
                file_options={"content-type": content_type, "upsert": "true"}
            )

            # Update DB record
            setattr(instance, field_name, unique_dest_path)
            instance.save(update_fields=[field_name])

            public_url = storage.url(unique_dest_path)
            self.stdout.write(
                self.style.SUCCESS(f"  [+] Migrated #{instance.id} {instance} -> {public_url}")
            )
            stats['migrated'] += 1

            if verify:
                self._verify_url(public_url, stats)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  [!] Failed migrating #{instance.id} {instance}: {e}"))
            stats['errors'] += 1

    def _verify_url(self, url, stats):
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                self.stdout.write(self.style.SUCCESS(f"      [VERIFIED] HTTP 200 for {url}"))
                stats['verified'] += 1
            else:
                self.stdout.write(self.style.WARNING(f"      [VERIFY FAIL] HTTP {resp.status_code} for {url}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"      [VERIFY ERROR] {e} for {url}"))
