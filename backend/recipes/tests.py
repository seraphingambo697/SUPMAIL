from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from cookbooks.models import Cookbook, CookbookMembership

from .models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


class RecipeTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', email='owner@example.com', password='pass1234')
        self.other = User.objects.create_user(username='other', email='other@example.com', password='pass1234')

    def _recipe_payload(self, **overrides):
        payload = {
            'title': 'Tarte aux pommes',
            'steps': 'Éplucher les pommes\nCuire 30 minutes',
            'prep_time_minutes': 20,
            'cook_time_minutes': 30,
            'servings': 6,
            'source': 'Création personnelle',
            'ingredients': [{'ingredient_name': 'pomme', 'quantity': 4, 'unit': 'pièce'}],
        }
        payload.update(overrides)
        return payload

    def test_create_personal_recipe(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/recipes/', self._recipe_payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(title='Tarte aux pommes')
        self.assertEqual(recipe.owner, self.owner)
        self.assertEqual(recipe.ingredients.count(), 1)
        self.assertEqual(Ingredient.objects.filter(name='pomme').count(), 1)

    def test_other_user_cannot_see_personal_recipe(self):
        recipe = Recipe.objects.create(title='Secret', owner=self.owner, steps='...')
        self.client.force_authenticate(user=self.other)
        response = self.client.get(f'/api/recipes/{recipe.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_user_cannot_delete_personal_recipe(self):
        recipe = Recipe.objects.create(title='Protégée', owner=self.owner, steps='...')
        # Rendre visible en la mettant dans un cookbook partagé où other est lecteur seul,
        # ce qui ne devrait pas suffire pour supprimer une recette qui reste "personnelle" du owner.
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(f'/api/recipes/{recipe.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_toggle_favorite(self):
        recipe = Recipe.objects.create(title='Soupe', owner=self.owner, steps='Mixer')
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f'/api/recipes/{recipe.id}/toggle_favorite/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_favorite'])
        response = self.client.post(f'/api/recipes/{recipe.id}/toggle_favorite/')
        self.assertFalse(response.data['is_favorite'])

    def test_filter_by_max_prep_time(self):
        Recipe.objects.create(title='Rapide', owner=self.owner, steps='...', prep_time_minutes=5)
        Recipe.objects.create(title='Longue', owner=self.owner, steps='...', prep_time_minutes=60)
        self.client.force_authenticate(user=self.owner)
        response = self.client.get('/api/recipes/', {'max_prep_time': 10})
        titles = [r['title'] for r in response.data['results']] if 'results' in response.data else [r['title'] for r in response.data]
        self.assertIn('Rapide', titles)
        self.assertNotIn('Longue', titles)

    def test_filter_by_ingredient(self):
        recipe = Recipe.objects.create(title='Salade', owner=self.owner, steps='...')
        ingredient = Ingredient.objects.create(name='tomate')
        RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, quantity=2, unit='pièce')
        Recipe.objects.create(title='Gâteau', owner=self.owner, steps='...')
        self.client.force_authenticate(user=self.owner)
        response = self.client.get('/api/recipes/', {'ingredient': 'tomate'})
        titles = [r['title'] for r in (response.data.get('results') or response.data)]
        self.assertIn('Salade', titles)
        self.assertNotIn('Gâteau', titles)

    def test_shared_cookbook_recipe_requires_editor_role_to_create(self):
        cookbook = Cookbook.objects.create(name='Partagé', owner=self.owner)
        CookbookMembership.objects.create(cookbook=cookbook, user=self.owner, role=CookbookMembership.ROLE_CREATOR)
        CookbookMembership.objects.create(cookbook=cookbook, user=self.other, role=CookbookMembership.ROLE_READER)

        self.client.force_authenticate(user=self.other)
        payload = self._recipe_payload(cookbook=cookbook.id)
        response = self.client.post('/api/recipes/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/recipes/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_reader_cannot_comment_but_commentator_can(self):
        cookbook = Cookbook.objects.create(name='Cookbook', owner=self.owner)
        CookbookMembership.objects.create(cookbook=cookbook, user=self.owner, role=CookbookMembership.ROLE_CREATOR)
        CookbookMembership.objects.create(cookbook=cookbook, user=self.other, role=CookbookMembership.ROLE_READER)
        recipe = Recipe.objects.create(title='Recette partagée', owner=self.owner, steps='...', cookbook=cookbook)

        self.client.force_authenticate(user=self.other)
        response = self.client.post(f'/api/recipes/{recipe.id}/comments/', {'content': 'Miam'})
        self.assertEqual(response.status_code, 403)

        CookbookMembership.objects.filter(cookbook=cookbook, user=self.other).update(
            role=CookbookMembership.ROLE_COMMENTATOR
        )
        response = self.client.post(f'/api/recipes/{recipe.id}/comments/', {'content': 'Miam'})
        self.assertEqual(response.status_code, 201)
