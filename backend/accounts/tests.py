from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AccountsTests(APITestCase):
    def test_register_creates_user_with_hashed_password(self):
        response = self.client.post('/api/auth/register/', {
            'username': 'alice', 'email': 'alice@example.com', 'password': 'S3cure-Pass!',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        user = User.objects.get(username='alice')
        self.assertNotEqual(user.password, 'S3cure-Pass!')
        self.assertTrue(user.check_password('S3cure-Pass!'))

    def test_login_returns_jwt_tokens(self):
        User.objects.create_user(username='bob', email='bob@example.com', password='S3cure-Pass!')
        response = self.client.post('/api/auth/login/', {'username': 'bob', 'password': 'S3cure-Pass!'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password_rejected(self):
        User.objects.create_user(username='carl', email='carl@example.com', password='S3cure-Pass!')
        response = self.client.post('/api/auth/login/', {'username': 'carl', 'password': 'wrong'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_requires_authentication(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_preferences(self):
        user = User.objects.create_user(username='dana', email='dana@example.com', password='S3cure-Pass!')
        self.client.force_authenticate(user=user)
        response = self.client.patch('/api/auth/me/', {'diet': 'vegan', 'allergies': 'arachides'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.diet, 'vegan')

    def test_change_password_requires_correct_old_password(self):
        user = User.objects.create_user(username='eve', email='eve@example.com', password='OldPass1!')
        self.client.force_authenticate(user=user)
        response = self.client.post('/api/auth/me/change-password/', {
            'old_password': 'wrong', 'new_password': 'NewPass1!',
        })
        self.assertEqual(response.status_code, 400)
