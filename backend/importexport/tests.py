import json

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from recipes.models import Ingredient, Recipe, RecipeIngredient

User = get_user_model()


class ImportExportTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='exporter', email='exporter@example.com', password='pass1234')
        self.client.force_authenticate(user=self.user)

    def test_export_json_contains_recipe(self):
        recipe = Recipe.objects.create(title='Riz cantonais', owner=self.user, steps='Faire revenir\nMélanger')
        ingredient = Ingredient.objects.create(name='riz')
        RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, quantity=300, unit='g')
        response = self.client.get('/api/export/', {'export_format': 'json'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        titles = [r['name'] for r in data['recipes']]
        self.assertIn('Riz cantonais', titles)

    def test_export_csv_returns_csv_content_type(self):
        Recipe.objects.create(title='Salade César', owner=self.user, steps='Mélanger')
        response = self.client.get('/api/export/', {'export_format': 'csv'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response['Content-Type'])
        self.assertIn(b'Salade C', response.content)

    def test_import_json_creates_recipe_owned_by_importer(self):
        payload = {
            'cookbooks': [],
            'recipes': [{
                'name': 'Ratatouille',
                'recipeYield': 4,
                'prepTime': 15,
                'performTime': 40,
                'recipeIngredient': [{'food': {'name': 'courgette'}, 'quantity': 2, 'unit': 'pièce'}],
                'recipeInstructions': [{'text': 'Couper les légumes'}, {'text': 'Faire mijoter'}],
                'tags': [],
                'orgURL': '',
            }],
        }
        upload = SimpleUploadedFile('import.json', json.dumps(payload).encode('utf-8'), content_type='application/json')
        response = self.client.post('/api/import/', {'file': upload}, format='multipart')
        self.assertEqual(response.status_code, 201)
        recipe = Recipe.objects.get(title='Ratatouille')
        self.assertEqual(recipe.owner, self.user)
        self.assertEqual(recipe.ingredients.count(), 1)

    def test_import_csv_creates_recipe(self):
        csv_content = "title,servings,prep_time,cook_time,ingredients,steps,tags,source,cookbook\n"
        csv_content += "Soupe miso,2,5,10,150 g tofu; 1 l bouillon,Chauffer | Servir,,,\n"
        upload = SimpleUploadedFile('import.csv', csv_content.encode('utf-8'), content_type='text/csv')
        response = self.client.post('/api/import/', {'file': upload}, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Recipe.objects.filter(title='Soupe miso', owner=self.user).exists())
