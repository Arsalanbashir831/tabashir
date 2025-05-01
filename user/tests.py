from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from user.models import User

class UserTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('user-register')
        self.login_url = reverse('token_obtain_pair')
        self.profile_url = reverse('user-profile')
        self.change_password_url = reverse('change-password')

        self.user_data = {
            "email": "testuser@example.com",
            "password": "TestPass123!",
            "username": "Test User",
            "gender": "male",
            "phone": "+123456789",
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.user_data["email"]).exists())

    def test_user_login(self):
        User.objects.create_user(email=self.user_data["email"], password=self.user_data["password"])
        response = self.client.post(self.login_url, {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.token = response.data["access"]

    def authenticate(self):
        self.test_user_login()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_profile_view(self):
        self.authenticate()
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user_data["email"])

    def test_profile_update(self):
        self.authenticate()
        response = self.client.put(self.profile_url, {
            "username": "Updated User",
            "gender": "female",
            "title": "Data Scientist",
            "experience_years": 3,
            "education": "B.S. Computer Science",
            "skills": ["Python", "NLP", "Machine Learning"]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "Updated User")
        self.assertEqual(response.data["title"], "Data Scientist")

    def test_password_change(self):
        self.authenticate()
        response = self.client.post(self.change_password_url, {
            "old_password": self.user_data["password"],
            "new_password": "NewSecurePass456!"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure login with new password works
        response = self.client.post(self.login_url, {
            "email": self.user_data["email"],
            "password": "NewSecurePass456!"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
