import os
import posixpath
import uuid
import mimetypes
import logging

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.utils.text import get_valid_filename

logger = logging.getLogger(__name__)

try:
    from supabase import create_client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    logger.error("Supabase Python package is NOT installed.")


@deconstructible
class SupabaseMediaStorage(Storage):

    def __init__(
        self,
        bucket_name=None,
        supabase_url=None,
        supabase_key=None
    ):

        self.bucket_name = (
            bucket_name
            or getattr(
                settings,
                "SUPABASE_BUCKET_NAME",
                "website-images"
            )
        )

        self.supabase_url = (
            supabase_url
            or getattr(settings, "SUPABASE_URL", "")
            or os.environ.get("SUPABASE_URL", "")
        ).rstrip("/")

        self.supabase_key = (
            supabase_key
            or getattr(settings, "SUPABASE_KEY", "")
            or os.environ.get("SUPABASE_KEY", "")
        )

        self._client = None

        logger.info(
            "SUPABASE STORAGE INITIALIZED | "
            "URL_PRESENT=%s | KEY_PRESENT=%s | BUCKET=%s | PACKAGE=%s",
            bool(self.supabase_url),
            bool(self.supabase_key),
            self.bucket_name,
            HAS_SUPABASE
        )

    # ---------------------------------------------------------
    # Supabase client
    # ---------------------------------------------------------

    def get_client(self):

        if not HAS_SUPABASE:
            raise RuntimeError(
                "Supabase Python package is not installed."
            )

        if not self.supabase_url:
            raise RuntimeError(
                "SUPABASE_URL is missing."
            )

        if not self.supabase_key:
            raise RuntimeError(
                "SUPABASE_KEY is missing."
            )

        if self._client is None:

            logger.info(
                "Creating Supabase client..."
            )

            try:

                self._client = create_client(
                    self.supabase_url,
                    self.supabase_key
                )

                logger.info(
                    "Supabase client created successfully."
                )

            except Exception as e:

                logger.exception(
                    "FAILED TO CREATE SUPABASE CLIENT: %s",
                    e
                )

                raise

        return self._client

    # ---------------------------------------------------------
    # Clean path
    # ---------------------------------------------------------

    def _clean_path(self, name):

        name = str(name).replace("\\", "/").strip("/")

        parts = [
            part
            for part in name.split("/")
            if part and part not in (".", "..")
        ]

        return "/".join(parts)

    # ---------------------------------------------------------
    # Generate unique filename
    # ---------------------------------------------------------

    def get_available_name(self, name, max_length=None):

        name = self._clean_path(name)

        directory, filename = posixpath.split(name)

        filename = get_valid_filename(filename)

        base, extension = posixpath.splitext(filename)

        unique_prefix = uuid.uuid4().hex[:8]

        filename = (
            f"{unique_prefix}_{base}{extension}"
        )

        if directory:

            final_name = (
                f"{directory}/{filename}"
            )

        else:

            final_name = filename

        if max_length and len(final_name) > max_length:

            excess = len(final_name) - max_length

            base_length = max(
                1,
                len(base) - excess
            )

            filename = (
                f"{unique_prefix}_"
                f"{base[:base_length]}"
                f"{extension}"
            )

            final_name = (
                f"{directory}/{filename}"
                if directory
                else filename
            )

        return final_name

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    def _save(self, name, content):

        name = self.get_available_name(name)

        logger.info(
            "================================================"
        )

        logger.info(
            "SUPABASE UPLOAD STARTED"
        )

        logger.info(
            "Bucket: %s",
            self.bucket_name
        )

        logger.info(
            "Path: %s",
            name
        )

        logger.info(
            "URL configured: %s",
            bool(self.supabase_url)
        )

        logger.info(
            "Key configured: %s",
            bool(self.supabase_key)
        )

        logger.info(
            "Supabase package available: %s",
            HAS_SUPABASE
        )

        # Get client
        client = self.get_client()

        # Read file
        content.seek(0)

        file_bytes = content.read()

        logger.info(
            "File size: %s bytes",
            len(file_bytes)
        )

        # MIME type
        content_type, _ = mimetypes.guess_type(name)

        if not content_type:

            content_type = (
                "application/octet-stream"
            )

        logger.info(
            "Content type: %s",
            content_type
        )

        try:

            response = (
                client
                .storage
                .from_(self.bucket_name)
                .upload(
                    path=name,
                    file=file_bytes,
                    file_options={
                        "content-type": content_type,
                        "upsert": "true"
                    }
                )
            )

            logger.info(
                "SUPABASE UPLOAD SUCCESSFUL"
            )

            logger.info(
                "Bucket: %s",
                self.bucket_name
            )

            logger.info(
                "Path: %s",
                name
            )

            logger.info(
                "Response: %s",
                response
            )

            logger.info(
                "================================================"
            )

            return name

        except Exception as e:

            logger.exception(
                "SUPABASE UPLOAD FAILED"
            )

            logger.exception(
                "Bucket: %s",
                self.bucket_name
            )

            logger.exception(
                "Path: %s",
                name
            )

            logger.exception(
                "Error: %s",
                e
            )

            logger.info(
                "================================================"
            )

            # IMPORTANT:
            # Do NOT fall back to Render filesystem.
            raise

    # ---------------------------------------------------------
    # OPEN
    # ---------------------------------------------------------

    def _open(self, name, mode="rb"):

        name = self._clean_path(name)

        client = self.get_client()

        try:

            data = (
                client
                .storage
                .from_(self.bucket_name)
                .download(name)
            )

            return ContentFile(
                data,
                name=name
            )

        except Exception as e:

            logger.exception(
                "FAILED TO DOWNLOAD FROM SUPABASE: %s",
                e
            )

            raise FileNotFoundError(
                f"File '{name}' was not found "
                f"in Supabase bucket "
                f"'{self.bucket_name}'."
            )

    # ---------------------------------------------------------
    # URL
    # ---------------------------------------------------------

    def url(self, name):

        if not name:
            return ""

        name = str(name).strip()

        # Already a URL
        if name.startswith(
            ("http://", "https://")
        ):
            return name

        name = self._clean_path(name)

        if not self.supabase_url:

            raise RuntimeError(
                "SUPABASE_URL is missing."
            )

        url = (
            f"{self.supabase_url}"
            f"/storage/v1/object/public/"
            f"{self.bucket_name}/"
            f"{name}"
        )

        logger.debug(
            "Generated Supabase URL: %s",
            url
        )

        return url

    # ---------------------------------------------------------
    # EXISTS
    # ---------------------------------------------------------

    def exists(self, name):

        # We generate unique names anyway,
        # so Django does not need to find collisions.

        return False

    # ---------------------------------------------------------
    # DELETE
    # ---------------------------------------------------------

    def delete(self, name):

        name = self._clean_path(name)

        client = self.get_client()

        try:

            client.storage \
                .from_(self.bucket_name) \
                .remove([name])

            logger.info(
                "Deleted from Supabase: %s",
                name
            )

        except Exception as e:

            logger.exception(
                "Failed to delete from Supabase: %s",
                e
            )

    # ---------------------------------------------------------
    # SIZE
    # ---------------------------------------------------------

    def size(self, name):

        # Not required for displaying images.
        return 0