from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from restaurant.models import Menu, MenuItem

User = get_user_model()


class RestaurantSignUpViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("restaurant-signup")

    def test_restaurant_signup_success(self):
        data = {
            "email": "newrestaurant@example.com",
            "password": "testpass123",
            "confirm_password": "testpass123",
            "restaurant_name": "New Restaurant",
            "user_type": "restaurant",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access_token", response.data["data"])
        self.assertIn("refresh_token", response.data["data"])
        user = User.objects.get(email="newrestaurant@example.com")
        self.assertEqual(user.user_type, "restaurant")
        self.assertEqual(user.restaurant_name, "New Restaurant")
        self.assertTrue(user.restaurant_id.startswith("R-"))

    def test_restaurant_signup_invalid_data(self):
        data = {
            "email": "invalid_email",
            "password": "short",
            "restaurant_name": "New Restaurant",
            "user_type": "restaurant",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="invalid_email").exists())


class MenuCreateViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testrestaurant@example.com",
            password="testpass123",
            user_type="restaurant",
            restaurant_name="Test Restaurant",
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("menu-create")

    def test_create_menu_success(self):
        data = {
            "date": "2023-05-01",
            "is_published": True,
            "items": [
                {
                    "name": "Test Item",
                    "description": "A test item",
                    "price": "9.99",
                    "category": "main_course",
                }
            ],
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Menu.objects.count(), 1)
        self.assertEqual(MenuItem.objects.count(), 1)
        menu = Menu.objects.first()
        self.assertEqual(menu.restaurant, self.user)
        self.assertEqual(str(menu.date), "2023-05-01")

    def test_create_menu_invalid_data(self):
        data = {"date": "invalid_date", "is_published": True, "items": []}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Menu.objects.count(), 0)


class AllRestaurantsCurrentDayMenuViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("all-restaurants-current-day-menu")
        self.restaurant1 = User.objects.create_user(
            email="restaurant1@example.com",
            password="testpass123",
            user_type="restaurant",
            restaurant_name="Restaurant 1",
        )
        self.restaurant2 = User.objects.create_user(
            email="restaurant2@example.com",
            password="testpass123",
            user_type="restaurant",
            restaurant_name="Restaurant 2",
        )
        self.employee = User.objects.create_user(
            email="employee@example.com", password="testpass123", user_type="employee"
        )
        self.today = timezone.now().date()

    def test_list_todays_menus_success(self):
        Menu.objects.create(
            restaurant=self.restaurant1, date=self.today, is_published=True
        )
        Menu.objects.create(
            restaurant=self.restaurant2, date=self.today, is_published=True
        )

        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["results"]), 2)

    def test_list_todays_menus_empty(self):
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "No menus available for today.")
        self.assertIsNone(response.data["data"])

    def test_list_todays_menus_unauthorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
