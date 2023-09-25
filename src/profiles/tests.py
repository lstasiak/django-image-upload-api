from django.contrib.auth import get_user_model
from django.test import TestCase

from src.profiles.models import Subscription


class ProfileTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.enterprise_profile = get_user_model().objects.create(
            username="Tester-1",
            password="password",
        )
        subscription = Subscription.objects.get(name="Enterprise")
        cls.enterprise_profile.subscription = subscription

        # create premium acc user
        cls.premium_profile = get_user_model().objects.create(
            username="Tester-2",
            password="password",
        )
        subscription = Subscription.objects.get(name="Premium")
        cls.premium_profile.subscription = subscription

        # create basic acc user
        cls.basic_profile = get_user_model().objects.create(
            username="Tester-3",
            password="password",
        )
        subscription = Subscription.objects.get(name="Basic")
        cls.basic_profile.subscription = subscription

    def test_create_profile(self):
        test_profile = get_user_model().objects.create_user(
            username="test", email="test@test.com", password="password"
        )
        self.assertEqual(test_profile.username, "test")
        self.assertEqual(test_profile.email, "test@test.com")
        self.assertTrue(test_profile.is_active)
        self.assertFalse(test_profile.is_staff)
        self.assertFalse(test_profile.is_superuser)

    def test_subscriptions(self):
        self.assertEqual(self.basic_profile.subscription.name, "Basic")
        self.assertEqual(self.premium_profile.subscription.name, "Premium")
        self.assertEqual(self.enterprise_profile.subscription.name, "Enterprise")

    def test_available_thumbnails(self):
        default_aspect_ratio = 16 / 9
        default_thumbnails = [(round(default_aspect_ratio * h), h) for h in (200, 400)]
        basic_sub = default_thumbnails[0]
        premium_sub = [basic_sub, default_thumbnails[1]]
        enterprise_sub = premium_sub

        current_user_basic = [
            (e.width, e.height)
            for e in self.basic_profile.subscription.get_thumbnail_sizes
        ]
        current_user_premium = [
            (e.width, e.height)
            for e in self.premium_profile.subscription.get_thumbnail_sizes
        ]
        current_user_enterprise = [
            (e.width, e.height)
            for e in self.enterprise_profile.subscription.get_thumbnail_sizes
        ]

        self.assertEqual(current_user_basic, [basic_sub])
        self.assertEqual(current_user_premium, premium_sub)
        self.assertEqual(current_user_enterprise, enterprise_sub)

    def test_can_get_original_file(self):
        self.assertFalse(self.basic_profile.subscription.original_file_access)
        self.assertTrue(self.premium_profile.subscription.original_file_access)
        self.assertTrue(self.enterprise_profile.subscription.original_file_access)

    def test_can_generate_expiring_links(self):
        self.assertFalse(self.basic_profile.subscription.expiring_link_option)
        self.assertFalse(self.premium_profile.subscription.expiring_link_option)
        self.assertTrue(self.enterprise_profile.subscription.expiring_link_option)
