from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone

from restaurant.models import Menu
from employee.models import Vote

User = get_user_model()


class EmployeeSignUpTest(APITestCase):
    def test_employee_signup(self):
        url = reverse("employee-signup")
        data = {
            "email": "employee@example.com",
            "password": "testpassword123",
            "confirm_password": "testpassword123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access_token", response.data["data"])
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, "employee@example.com")


class VoteMenuTest(APITestCase):
    def setUp(self):
        self.employee = User.objects.create_user(
            email="employee@example.com",
            password="testpassword123",
            user_type="employee",
        )
        self.restaurant1 = User.objects.create_user(
            email="restaurant1@example.com",
            password="testpassword123",
            user_type="restaurant",
        )
        self.restaurant2 = User.objects.create_user(
            email="restaurant2@example.com",
            password="testpassword123",
            user_type="restaurant",
        )
        self.restaurant3 = User.objects.create_user(
            email="restaurant3@example.com",
            password="testpassword123",
            user_type="restaurant",
        )
        today = timezone.now().date()
        self.menu1 = Menu.objects.create(
            restaurant=self.restaurant1,
            date=today,
        )
        self.menu2 = Menu.objects.create(
            restaurant=self.restaurant2,
            date=today,
        )
        self.menu3 = Menu.objects.create(
            restaurant=self.restaurant3,
            date=today,
        )

    def test_submit_vote_v1(self):
        self.client.force_authenticate(user=self.employee)
        url = reverse("submit-vote")
        headers = {"X-App-Version": "2.0"}

        # Submit first vote
        data = {"menu": str(self.menu1.id)}
        response = self.client.post(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vote.objects.count(), 1)

        # Attempt to submit second vote on the same day
        data = {"menu": str(self.menu2.id)}
        response = self.client.post(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Vote.objects.count(), 1)  # Vote count should remain 1

        # Verify the vote details
        vote = Vote.objects.first()
        self.assertEqual(vote.rank, 1)
        self.assertEqual(vote.menu, self.menu1)


class GetCurrentDayVoteTest(APITestCase):
    def setUp(self):
        self.employee = User.objects.create_user(
            email="employee@example.com",
            password="testpassword123",
            user_type="employee",
        )
        self.restaurant = User.objects.create_user(
            email="restaurant@example.com",
            password="testpassword123",
            user_type="restaurant",
        )
        self.restaurant2 = User.objects.create_user(
            email="restaurant2@example.com",
            password="testpassword123",
            user_type="restaurant",
        )
        self.menu1 = Menu.objects.create(
            restaurant=self.restaurant, date=timezone.now().date(),
            is_published=True
        )
        self.menu2 = Menu.objects.create(
            restaurant=self.restaurant2, date=timezone.now().date(),
            is_published=True
        )
        current_time = timezone.now()
        Vote.objects.create(
            user=self.employee,
            menu=self.menu1,
            rank=1,
            created_at=timezone.make_aware(current_time.replace(tzinfo=None)),
        )
        Vote.objects.create(
            user=self.employee,
            menu=self.menu2,
            rank=2,
            created_at=timezone.make_aware(current_time.replace(tzinfo=None)),
        )

    def test_get_vote_results(self):
        self.client.force_authenticate(user=self.employee)
        url = reverse("vote-results")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 2)
        self.assertGreater(
            response.data["data"][0]["total_points"],
            response.data["data"][1]["total_points"],
        )
