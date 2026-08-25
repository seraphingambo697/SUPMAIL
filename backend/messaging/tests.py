from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from cookbooks.models import Cookbook, CookbookMembership

from .models import Message

User = get_user_model()


class MessagingTests(APITestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username='alice_m', email='alice_m@example.com', password='pass1234')
        self.bob = User.objects.create_user(username='bob_m', email='bob_m@example.com', password='pass1234')
        self.outsider = User.objects.create_user(username='out_m', email='out_m@example.com', password='pass1234')
        self.cookbook = Cookbook.objects.create(name='Chat CB', owner=self.alice)
        CookbookMembership.objects.create(cookbook=self.cookbook, user=self.alice, role='creator')
        CookbookMembership.objects.create(cookbook=self.cookbook, user=self.bob, role='reader')

    def test_member_can_send_and_list_messages(self):
        self.client.force_authenticate(user=self.bob)
        response = self.client.post('/api/messages/', {'cookbook': self.cookbook.id, 'content': 'Salut !'})
        self.assertEqual(response.status_code, 201)
        response = self.client.get('/api/messages/', {'cookbook': self.cookbook.id})
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)

    def test_non_member_cannot_send_message(self):
        self.client.force_authenticate(user=self.outsider)
        response = self.client.post('/api/messages/', {'cookbook': self.cookbook.id, 'content': 'Intrus'})
        self.assertEqual(response.status_code, 403)

    def test_cannot_delete_others_message(self):
        msg = Message.objects.create(cookbook=self.cookbook, author=self.alice, content='Message d\'Alice')
        self.client.force_authenticate(user=self.bob)
        response = self.client.delete(f'/api/messages/{msg.id}/')
        self.assertEqual(response.status_code, 403)

    def test_after_filter_returns_only_newer_messages(self):
        m1 = Message.objects.create(cookbook=self.cookbook, author=self.alice, content='Premier')
        Message.objects.create(cookbook=self.cookbook, author=self.alice, content='Second')
        self.client.force_authenticate(user=self.bob)
        response = self.client.get('/api/messages/', {'cookbook': self.cookbook.id, 'after': m1.id})
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['content'], 'Second')
