from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from .models import CustomUser, Address


class UserManagerTest(TestCase):

    def test_create_user_success(self):
        user = CustomUser.objects.create_user(
            email="test@example.com",
            password="securepassword123",
            full_name="Test User",
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("securepassword123"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                email="",
                password="password123",
            )

    def test_create_user_without_password_raises_error(self):
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                email="test@example.com",
                password=None,
            )

    def test_duplicate_email_raises_validation_error(self):
        CustomUser.objects.create_user(
            email="duplicate@example.com",
            password="password123",
        )

        with self.assertRaises(ValidationError):
            CustomUser.objects.create_user(
                email="duplicate@example.com",
                password="password123",
            )

    def test_create_superuser(self):
        admin = CustomUser.objects.create_superuser(
            email="admin@example.com",
            password="adminpass",
            full_name="Admin User",
        )

        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_active)


class CustomUserModelTest(TestCase):

    def test_user_str_returns_email(self):
        user = CustomUser.objects.create_user(
            email="string@example.com",
            password="password123",
        )

        self.assertEqual(str(user), "string@example.com")

    def test_email_is_normalized_on_clean(self):
        user = CustomUser(
            email="TEST@EXAMPLE.COM",
            full_name="Normalize Test",
        )

        user.clean()
        self.assertEqual(user.email, "TEST@example.com")

    def test_clean_without_email_raises_validation_error(self):
        user = CustomUser(email="")

        with self.assertRaises(ValidationError):
            user.clean()


class AddressModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="address@example.com",
            password="password123",
            full_name="Address User",
        )

    def test_create_address_success(self):
        address = Address.objects.create(
            user=self.user,
            full_name="John Doe",
            phone_number="+123456789",
            line1="123 Main Street",
            city="Nairobi",
            postal_code="00100",
            country="Kenya",
        )

        self.assertEqual(address.user, self.user)
        self.assertEqual(address.city, "Nairobi")
        self.assertFalse(address.is_default)

    def test_address_str(self):
        address = Address.objects.create(
            user=self.user,
            full_name="Jane Doe",
            phone_number="+123456789",
            line1="456 Market Road",
            city="Mombasa",
            postal_code="80100",
            country="Kenya",
        )

        self.assertEqual(
            str(address),
            "Jane Doe - 456 Market Road, Mombasa"
        )

    def test_unique_address_per_user_constraint(self):
        Address.objects.create(
            user=self.user,
            full_name="John Doe",
            phone_number="+123456789",
            line1="789 Sunset Blvd",
            city="Kisumu",
            postal_code="40100",
            country="Kenya",
        )

        with self.assertRaises(IntegrityError):
            Address.objects.create(
                user=self.user,
                full_name="John Doe",
                phone_number="+123456789",
                line1="789 Sunset Blvd",
                city="Kisumu",
                postal_code="40100",
                country="Kenya",
            )

    def test_single_default_address_enforced(self):
        Address.objects.create(
            user=self.user,
            full_name="Default One",
            phone_number="+123456789",
            line1="1 Default Lane",
            city="Nakuru",
            postal_code="20100",
            country="Kenya",
            is_default=True,
        )

        address2 = Address(
            user=self.user,
            full_name="Default Two",
            phone_number="+123456789",
            line1="2 Default Lane",
            city="Nakuru",
            postal_code="20101",
            country="Kenya",
            is_default=True,
        )

        with self.assertRaises(ValidationError):
            address2.clean()

    def test_multiple_non_default_addresses_allowed(self):
        Address.objects.create(
            user=self.user,
            full_name="Address One",
            phone_number="+123456789",
            line1="Street 1",
            city="Eldoret",
            postal_code="30100",
            country="Kenya",
        )

        Address.objects.create(
            user=self.user,
            full_name="Address Two",
            phone_number="+123456789",
            line1="Street 2",
            city="Eldoret",
            postal_code="30101",
            country="Kenya",
        )

        self.assertEqual(self.user.addresses.count(), 2)
