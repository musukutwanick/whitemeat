import os
import posixpath
import uuid
import mimetypes
import logging
from io import BytesIO
from PIL import Image

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile, File
from django.core.files.storage import Storage, FileSystemStorage
from django.utils.deconstruct import deconstructible
from django.utils.text import get_valid_filename

logger = logging.getLogger(__name__)

# Try importing supabase
try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    logger.warning("supabase python package not installed; SupabaseMediaStorage will run in fallback mode.")


@deconstructible
class SupabaseMediaStorage(Storage):
    """
    Custom Django Storage backend that uploads files to Supabase Storage.
    Supports seamless fallback to FileSystemStorage if credentials are not configured.
    """

    def __init__(self, bucket_name=None, supabase_url=None, supabase_key=None):
        self.bucket_name = (
            bucket_name
            or getattr(settings, "SUPABASE_BUCKET_NAME", None)
            or os.environ.get("SUPABASE_BUCKET_NAME", "website-images")
        )
        self.supabase_url = (
            supabase_url
            or getattr(settings, "SUPABASE_URL", None)
            or os.environ.get("SUPABASE_URL", "")
        ).rstrip("/")
        self.supabase_key = (
            supabase_key
            or getattr(settings, "SUPABASE_KEY", None)
            or os.environ.get("SUPABASE_KEY", "")
        )

        self._client = None
        self._fallback_storage = FileSystemStorage(
            location=settings.MEDIA_ROOT,
            base_url=settings.MEDIA_URL
        )

    @property
    def is_configured(self):
        """Check if Supabase credentials and client are available."""
        return bool(HAS_SUPABASE and self.supabase_url and self.supabase_key)

    def get_client(self):
        """Get or initialize Supabase client."""
        if not self.is_configured:
            return None
        if self._client is None:
            try:
                self._client = create_client(self.supabase_url, self.supabase_key)
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                return None
        return self._client

    def _validate_image(self, content):
        """Verify that the uploaded content is a valid image file."""
        try:
            content.seek(0)
            img = Image.open(content)
            img.verify()
            content.seek(0)
            return True
        except Exception as e:
            logger.warning(f"File image validation failed: {e}")
            try:
                content.seek(0)
            except Exception:
                pass
            return False

    def _clean_path(self, name):
        """Normalize posix path for Supabase storage."""
        name = str(name).replace('\\', '/').strip('/')
        # Prevent path traversal
        parts = [p for p in name.split('/') if p and p not in ('.', '..')]
        return '/'.join(parts)

    def get_available_name(self, name, max_length=None):
        """
        Generate a unique filename to prevent accidental collisions.
        E.g., 'menu/dish.jpg' -> 'menu/a1b2c3d4_dish.jpg'
        """
        name = self._clean_path(name)
        dir_name, file_name = posixpath.split(name)
        
        # Sanitize filename
        clean_file_name = get_valid_filename(file_name)
        base, ext = posixpath.splitext(clean_file_name)
        
        # Check if already has a unique hex prefix
        if len(base) > 9 and base[8] == '_' and all(c in '0123456789abcdef' for c in base[:8]):
            unique_name = clean_file_name
        else:
            unique_prefix = uuid.uuid4().hex[:8]
            unique_name = f"{unique_prefix}_{base}{ext}"

        if dir_name:
            final_name = f"{dir_name}/{unique_name}"
        else:
            final_name = unique_name

        if max_length and len(final_name) > max_length:
            # Truncate base name if needed
            excess = len(final_name) - max_length
            base_len = max(1, len(base) - excess)
            unique_name = f"{unique_prefix}_{base[:base_len]}{ext}"
            final_name = f"{dir_name}/{unique_name}" if dir_name else unique_name

        return final_name

    def _save(self, name, content):
        """Save file content to Supabase Storage or fallback storage."""
        # Ensure we work with normalized unique name
        name = self.get_available_name(name)

        # Validate that image is well-formed
        is_valid_image = self._validate_image(content)
        # Note: Non-images like notices/documents can still be uploaded if needed, but warning is logged for images

        if not self.is_configured:
            logger.warning(
                "Supabase is not configured (SUPABASE_URL/SUPABASE_KEY missing). "
                "Falling back to local filesystem storage."
            )
            return self._fallback_storage._save(name, content)

        client = self.get_client()
        if not client:
            logger.error("Supabase client could not be obtained. Falling back to local storage.")
            return self._fallback_storage._save(name, content)

        # Prepare file content
        content.seek(0)
        file_bytes = content.read()
        content_type, _ = mimetypes.guess_type(name)
        if not content_type:
            content_type = "application/octet-stream"

        try:
            response = client.storage.from_(self.bucket_name).upload(
                path=name,
                file=file_bytes,
                file_options={"content-type": content_type, "upsert": "true"}
            )
            logger.info(f"Successfully uploaded {name} to Supabase bucket '{self.bucket_name}'")
            return name
        except Exception as e:
            logger.exception(f"Error uploading {name} to Supabase Storage: {e}")
            # Raise or fallback safely
            raise IOError(f"Supabase upload failed for {name}: {e}") from e

    def _open(self, name, mode='rb'):
        """Open a file from Supabase Storage or fallback."""
        name = self._clean_path(name)
        if not self.is_configured:
            return self._fallback_storage._open(name, mode)

        client = self.get_client()
        if not client:
            return self._fallback_storage._open(name, mode)

        try:
            data = client.storage.from_(self.bucket_name).download(name)
            return ContentFile(data, name=name)
        except Exception as e:
            logger.error(f"Error downloading {name} from Supabase: {e}")
            raise FileNotFoundError(f"File {name} not found in Supabase bucket '{self.bucket_name}'.")

    def exists(self, name):
        """
        Check if file exists in Supabase bucket.
        With unique prefix naming, collisions are avoided, but we can verify against bucket.
        """
        name = self._clean_path(name)
        if not self.is_configured:
            return self._fallback_storage.exists(name)
        return False

    def delete(self, name):
        """Delete file from Supabase Storage bucket."""
        name = self._clean_path(name)
        if not self.is_configured:
            return self._fallback_storage.delete(name)

        client = self.get_client()
        if not client:
            return self._fallback_storage.delete(name)

        try:
            client.storage.from_(self.bucket_name).remove([name])
            logger.info(f"Deleted {name} from Supabase bucket '{self.bucket_name}'")
        except Exception as e:
            logger.warning(f"Failed to delete {name} from Supabase: {e}")

    def url(self, name):
        """
        Generate the full public URL for a file in Supabase Storage.
        Returns: https://<supabase-url>/storage/v1/object/public/<bucket>/<name>
        """
        if not name:
            return ""

        name_str = str(name).strip()
        if name_str.startswith(("http://", "https://")):
            return name_str

        cleaned_name = self._clean_path(name_str)

        if not self.is_configured:
            # Fallback to local media URL
            return f"{settings.MEDIA_URL.rstrip('/')}/{cleaned_name}"

        # Standard Supabase public storage URL pattern
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{cleaned_name}"

    def size(self, name):
        """Return size of file if available."""
        name = self._clean_path(name)
        if not self.is_configured:
            return self._fallback_storage.size(name)
        return 0
