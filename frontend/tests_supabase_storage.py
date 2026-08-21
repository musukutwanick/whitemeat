import io
from PIL import Image
from unittest.mock import MagicMock, patch
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from whitemeat_backend.supabase_storage import SupabaseMediaStorage
from frontend.models import Accessory, MenuItem, RestaurantBranch, MenuCategory


class SupabaseStorageTests(TestCase):

    def _create_image_file(self, filename="test.jpg", color="blue", size=(100, 100)):
        file_obj = io.BytesIO()
        img = Image.new("RGB", size=size, color=color)
        img.save(file_obj, format="JPEG")
        file_obj.seek(0)
        return SimpleUploadedFile(filename, file_obj.read(), content_type="image/jpeg")

    def test_unique_filename_generation(self):
        storage = SupabaseMediaStorage(supabase_url="https://example.supabase.co", supabase_key="secretkey")
        name1 = storage.get_available_name("menu/burger.jpg")
        name2 = storage.get_available_name("menu/burger.jpg")
        
        self.assertTrue(name1.startswith("menu/"))
        self.assertTrue(name1.endswith("_burger.jpg"))
        self.assertTrue(name2.startswith("menu/"))
        self.assertTrue(name2.endswith("_burger.jpg"))
        # Names must be unique
        self.assertNotEqual(name1, name2)

    def test_url_generation_supabase_configured(self):
        storage = SupabaseMediaStorage(
            bucket_name="website-images",
            supabase_url="https://xyzproject.supabase.co",
            supabase_key="dummy_key"
        )
        url = storage.url("menu/8a1b2c3d_dish.jpg")
        expected = "https://xyzproject.supabase.co/storage/v1/object/public/website-images/menu/8a1b2c3d_dish.jpg"
        self.assertEqual(url, expected)

    def test_url_generation_already_full_url(self):
        storage = SupabaseMediaStorage(
            bucket_name="website-images",
            supabase_url="https://xyzproject.supabase.co",
            supabase_key="dummy_key"
        )
        url = storage.url("https://external.cdn.com/image.png")
        self.assertEqual(url, "https://external.cdn.com/image.png")

    def test_url_generation_fallback_unconfigured(self):
        storage = SupabaseMediaStorage(
            bucket_name="website-images",
            supabase_url="",
            supabase_key=""
        )
        url = storage.url("equipment/cage.jpg")
        self.assertEqual(url, "/media/equipment/cage.jpg")

    def test_image_validation(self):
        storage = SupabaseMediaStorage()
        valid_img = self._create_image_file()
        self.assertTrue(storage._validate_image(valid_img))

        corrupted = io.BytesIO(b"not an image at all")
        self.assertFalse(storage._validate_image(corrupted))

    @patch("whitemeat_backend.supabase_storage.create_client")
    def test_save_upload_to_supabase(self, mock_create_client):
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        mock_bucket = MagicMock()
        mock_client.storage.from_.return_value = mock_bucket
        mock_bucket.upload.return_value = {"Key": "website-images/menu/12345678_test.jpg"}

        storage = SupabaseMediaStorage(
            bucket_name="website-images",
            supabase_url="https://test.supabase.co",
            supabase_key="secret"
        )

        img_file = self._create_image_file()
        saved_name = storage._save("menu/test.jpg", img_file)

        self.assertTrue(saved_name.startswith("menu/"))
        self.assertTrue(saved_name.endswith("_test.jpg"))
        mock_bucket.upload.assert_called_once()

    def test_accessory_model_image_url(self):
        acc = Accessory.objects.create(
            name="Feeding Trough",
            price=25.00,
            is_available=True
        )
        # Without image, returns default
        self.assertEqual(acc.image_url, "/static/images/default-accessory.jpg")

    def test_menu_item_model_image_url(self):
        branch = RestaurantBranch.objects.create(
            name="Test Branch",
            slug="test-branch",
            address="123 Street",
            phone="123456",
            email="test@branch.com"
        )
        category = MenuCategory.objects.create(name="Mains", slug="mains", order=1)
        menu_item = MenuItem.objects.create(
            branch=branch,
            category=category,
            name="Grilled Rabbit",
            price=12.50,
            image_filename="dish1.jpg"
        )
        # Fallback to image_filename
        self.assertEqual(menu_item.image_url, "/static/images/dish1.jpg")
