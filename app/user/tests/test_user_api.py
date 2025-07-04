# user/tests/test_user_api.py
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


class UserApiTests(APITestCase):

    def test_register_user_success(self):
        """Test that a user can be created with valid data"""
        payload = {
            'username': 'testuser',
            'password': 'strongpass123',
            'email': 'test@example.com',
            'role': 'researcher',
        }
        res = self.client.post(reverse('user:register'), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(
                username=payload['username']).exists())

    def test_register_user_password_too_short(self):
        """Test password must be more than 5 characters"""
        payload = {
            'username': 'testuser2',
            'password': 'pw',
            'email': 'test2@example.com'
        }
        res = self.client.post(reverse('user:register'), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(
                username=payload['username']).exists())

    def test_register_user_without_role_fails(self):
        """Test registration fails if role is not provided"""
        payload = {
            'username': 'noroleuser',
            'password': 'strongpass123',
            'email': 'norole@example.com'
            # no 'role'
        }
        res = self.client.post(reverse('user:register'), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='noroleuser').exists())

    def test_login_user_success(self):
        """Test that user can log in with correct credentials"""
        user = User.objects.create_user(username='loginuser',
            email='login@example.com', password='testpass123')
        payload = {
            'username': 'loginuser',
            'password': 'testpass123'
        }
        res = self.client.post('/api/token/', payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_login_user_invalid_credentials(self):
        """Test login fails with incorrect credentials"""
        User.objects.create_user(username='loginuser2',
            email='login2@example.com', password='correctpass')
        payload = {
            'username': 'loginuser2',
            'password': 'wrongpass'
        }
        res = self.client.post('/api/token/', payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', res.data)
        self.assertNotIn('refresh', res.data)
