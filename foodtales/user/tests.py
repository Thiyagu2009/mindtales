from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


class CustomUserModelTest(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_create_user(self):
        user = self.User.objects.create_user(
            email="test@example.com", password="testpass123", user_type="employee"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.employee_id.startswith("E-"))

    def test_create_superuser(self):
        admin_user = self.User.objects.create_superuser(
            email="admin@example.com", password="adminpass123", user_type="employee"
        )
        self.assertEqual(admin_user.email, "admin@example.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_create_restaurant_user(self):
        restaurant = self.User.objects.create_user(
            email="restaurant@example.com",
            password="restpass123",
            user_type="restaurant",
            restaurant_name="Test Restaurant",
        )
        self.assertEqual(restaurant.email, "restaurant@example.com")
        self.assertEqual(restaurant.user_type, "restaurant")
        self.assertEqual(restaurant.restaurant_name, "Test Restaurant")
        self.assertTrue(restaurant.restaurant_id.startswith("R-"))

    def test_unique_email(self):
        self.User.objects.create_user(
            email="unique@example.com", password="pass123", user_type="employee"
        )
        with self.assertRaises(IntegrityError):
            self.User.objects.create_user(
                email="unique@example.com", password="pass456", user_type="employee"
            )

    def test_unique_employee_id(self):
        user1 = self.User.objects.create_user(
            email="emp1@example.com", password="pass123", user_type="employee"
        )
        user2 = self.User.objects.create_user(
            email="emp2@example.com", password="pass456", user_type="employee"
        )
        self.assertNotEqual(user1.employee_id, user2.employee_id)

    def test_unique_restaurant_id(self):
        rest1 = self.User.objects.create_user(
            email="rest1@example.com", password="pass123", user_type="restaurant"
        )
        rest2 = self.User.objects.create_user(
            email="rest2@example.com", password="pass456", user_type="restaurant"
        )
        self.assertNotEqual(rest1.restaurant_id, rest2.restaurant_id)
