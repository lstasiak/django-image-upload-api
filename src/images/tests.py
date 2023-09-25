import os
import shutil
from io import BytesIO
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from src.images.models import ExpiringLink, Image
from src.profiles.models import Subscription


def create_temporary_image(filename="test_image.jpg"):
    from PIL import Image

    test_image_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_data", "test_image.jpg"
    )
    with open(test_image_path, "rb") as f:
        image_data = BytesIO(f.read())

    image = Image.open(image_data)
    image_file = BytesIO()
    image.save(image_file, format="JPEG")
    image_file.seek(0)

    return InMemoryUploadedFile(
        image_file, None, filename, "image/jpeg", image_file.tell, charset=None
    )


@override_settings(CELERY_ALWAYS_EAGER=True)
class ImageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.profile = get_user_model().objects.create_user(
            username="testuser",
            email="test@email.com",
            password="secret",
            is_staff=True,
            is_active=True,
        )
        cls.image_file = create_temporary_image()
        with mock.patch(
            "src.images.signals.generate_thumbnails_task.delay", return_value=None
        ) as mock_obj:
            cls.image = Image.objects.create(
                owner=cls.profile, file=cls.image_file, title="Testing"
            )

        cls.exptected_image_name = "test_image"
        cls.exptected_ext = ".jpg"
        cls.exptected_image_path = cls.image.file.url

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT + "/uploaded_images")

    def test_image_owner(self):
        self.assertEqual(self.image.owner.username, "testuser")
        self.assertNotEqual(self.image.owner.email, "invalid@email.com")

    def test_get_original_url_method(self):
        self.assertEqual(self.image.file.url, self.exptected_image_path)

    @mock.patch.object(Image, "get_thumbnails", autospec=True)
    def test_get_thumbnails_method(self, mock_get_thumbnails):
        subscription = self.profile.subscription
        heights = subscription.get_thumbnail_heights
        exp_str = f"/media/uploaded_images/profiles/{self.profile.identifier}/{self.exptected_image_name}_%s{self.exptected_ext}"
        expected_thumbs = [(exp_str % (h,)) for h in heights]
        mock_get_thumbnails.return_value = expected_thumbs
        self.assertEqual(self.image.get_thumbnails(), expected_thumbs)
        mock_get_thumbnails.assert_called_once()


@override_settings(CELERY_ALWAYS_EAGER=True)
class ImageAPITests(APITestCase):
    def setUp(self):
        enterprise_subscription = Subscription.objects.get(id=3)
        self.profile = get_user_model().objects.create_user(
            username="Albert-Einstein",
            password="password",
            subscription=enterprise_subscription,
        )
        self.client.login(username="Albert-Einstein", password="password")
        self.image_file = create_temporary_image()
        with mock.patch(
            "src.images.signals.generate_thumbnails_task.delay", return_value=None
        ) as mock_obj:
            self.init_image = Image.objects.create(
                owner=self.profile, file=self.image_file, title="Testing"
            )

    # def test_create_image(self, mock_get_thumbnails):
    #     mock_get_thumbnails.return_value = []
    #
    #     url = "images"
    #
    #     data = {"file": self.image_file, "title": "Test 2"}
    #     response = self.client.post(url, data, format="multipart")
    #     print(response)
    #     mock_get_thumbnails.assert_called_once()
    #
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(Image.objects.count(), 2)
    #     self.assertEqual(Image.objects.first().owner, self.profile)
    #     self.assertEqual(Image.objects.last().title, "Test 2")
    #
    # @mock.patch("src.images.views.")
    # def test_list_images(self, mock_get_thumbnails):
    #     url = "images/"
    #     mock_get_thumbnails.return_value = None
    #     #     {
    #     #     "data": {"image_urls": ["test"]},
    #     #     "is_valid": True,
    #     # }
    #     # mock_get_thumbnails.return_value = []
    #     mock_get_thumbnails.assert_called_once()
    #
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data), 2)

    @mock.patch("src.images.signals.generate_thumbnails_task.delay", return_value=None)
    def test_create_expiring_link(self, mock_generate_thumbnails):
        image = Image.objects.create(
            owner=self.profile, file=self.image_file, title="Testing"
        )
        url = reverse("expiring-link-create-list")
        data = {"image": image.id, "expires_in": "350"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExpiringLink.objects.count(), 1)
        self.assertEqual(Image.objects.first().owner, self.profile)

    @mock.patch("src.images.signals.generate_thumbnails_task.delay", return_value=None)
    def test_list_expiring_links(self, mock_generate_thumbnails):
        image = Image.objects.create(
            owner=self.profile, file=self.image_file, title="Testing"
        )
        ExpiringLink.objects.create(image=image, expires_in="350")
        url = reverse("expiring-link-create-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    @mock.patch("src.images.signals.generate_thumbnails_task.delay", return_value=None)
    def test_get_expiring_link_detail(self, mock_generate_thumbnails):
        image = Image.objects.create(
            owner=self.profile, file=self.image_file, title="Testing"
        )
        url = reverse("expiring-link-create-list")
        data = {"image": image.id, "expires_in": "350"}
        response = self.client.post(url, data, format="json")
        link = response.data.get("link").split("/")[-2]
        url = reverse("expiring-link-retrieve", kwargs={"signed_link": link})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch("src.images.signals.generate_thumbnails_task.delay", return_value=None)
    def test_get_expiring_link_detail_with_expired_link(self, mock_generate_thumbnails):
        image = Image.objects.create(
            owner=self.profile, file=self.image_file, title="Testing"
        )
        expiring_link = ExpiringLink.objects.create(
            image=image, link="test", expires_in=-350
        )
        url = reverse(
            "expiring-link-retrieve", kwargs={"signed_link": expiring_link.link}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
