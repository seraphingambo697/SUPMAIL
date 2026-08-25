from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cookbook, CookbookMembership

User = get_user_model()


class CookbookTests(APITestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username='creator', email='creator@example.com', password='pass1234')
        self.reader = User.objects.create_user(username='reader', email='reader@example.com', password='pass1234')
        self.outsider = User.objects.create_user(username='outsider', email='outsider@example.com', password='pass1234')

    def test_create_cookbook_sets_creator_role(self):
        self.client.force_authenticate(user=self.creator)
        response = self.client.post('/api/cookbooks/', {'name': 'Cuisine familiale', 'description': 'Recettes de famille'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cookbook = Cookbook.objects.get(name='Cuisine familiale')
        membership = CookbookMembership.objects.get(cookbook=cookbook, user=self.creator)
        self.assertEqual(membership.role, CookbookMembership.ROLE_CREATOR)

    def test_outsider_cannot_see_private_cookbook(self):
        cookbook = Cookbook.objects.create(name='Privé', owner=self.creator)
        CookbookMembership.objects.create(cookbook=cookbook, user=self.creator, role=CookbookMembership.ROLE_CREATOR)
        self.client.force_authenticate(user=self.outsider)
        response = self.client.get(f'/api/cookbooks/{cookbook.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invite_adds_existing_user_as_member(self):
        cookbook = Cookbook.objects.create(name='Partagé', owner=self.creator)
        CookbookMembership.objects.create(cookbook=cookbook, user=self.creator, role=CookbookMembership.ROLE_CREATOR)
        self.client.force_authenticate(user=self.creator)
        response = self.client.post(f'/api/cookbooks/{cookbook.id}/invite/', {
            'email': 'reader@example.com', 'role': 'reader',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            CookbookMembership.objects.filter(cookbook=cookbook, user=self.reader, role='reader').exists()
        )

    def test_reader_cannot_invite(self):
        cookbook = Cookbook.objects.create(name='Partagé', owner=self.creator)
        CookbookMembership.objects.create(cookbook=cookbook, user=self.creator, role=CookbookMembership.ROLE_CREATOR)
        CookbookMembership.objects.create(cookbook=cookbook, user=self.reader, role=CookbookMembership.ROLE_READER)
        self.client.force_authenticate(user=self.reader)
        response = self.client.post(f'/api/cookbooks/{cookbook.id}/invite/', {
            'email': 'outsider@example.com', 'role': 'reader',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_creator_can_delete_cookbook(self):
        cookbook = Cookbook.objects.create(name='À supprimer', owner=self.creator)
        CookbookMembership.objects.create(cookbook=cookbook, user=self.creator, role=CookbookMembership.ROLE_CREATOR)
        CookbookMembership.objects.create(cookbook=cookbook, user=self.reader, role=CookbookMembership.ROLE_EDITOR)

        self.client.force_authenticate(user=self.reader)
        response = self.client.delete(f'/api/cookbooks/{cookbook.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.creator)
        response = self.client.delete(f'/api/cookbooks/{cookbook.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_role_rejected(self):
        cookbook = Cookbook.objects.create(name='Test rôle', owner=self.creator)
        CookbookMembership.objects.create(cookbook=cookbook, user=self.creator, role=CookbookMembership.ROLE_CREATOR)
        self.client.force_authenticate(user=self.creator)
        response = self.client.post(f'/api/cookbooks/{cookbook.id}/invite/', {
            'email': 'outsider@example.com', 'role': 'creator',
        })
        self.assertEqual(response.status_code, 400)
