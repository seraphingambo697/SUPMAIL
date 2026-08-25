from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from recipes.models import Ingredient, Recipe, RecipeIngredient

from .models import MealPlan

User = get_user_model()


class PlanningTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='chef', email='chef@example.com', password='pass1234')
        self.recipe = Recipe.objects.create(title='Pâtes', owner=self.user, steps='Cuire', servings=2)
        ingredient = Ingredient.objects.create(name='pâtes')
        RecipeIngredient.objects.create(recipe=self.recipe, ingredient=ingredient, quantity=200, unit='g')
        self.client.force_authenticate(user=self.user)

    def test_shopping_list_scales_with_servings(self):
        MealPlan.objects.create(user=self.user, recipe=self.recipe, date='2026-01-01', meal_type='dinner', servings=4)
        response = self.client.get('/api/meal-plans/shopping_list/', {'start': '2026-01-01', 'end': '2026-01-01'})
        self.assertEqual(response.status_code, 200)
        item = next(i for i in response.data if i['ingredient'] == 'pâtes')
        # 200g pour 2 portions -> 400g pour 4 portions
        self.assertEqual(item['quantity'], 400.0)

    def test_cannot_delete_others_meal_plan(self):
        other = User.objects.create_user(username='other2', email='other2@example.com', password='pass1234')
        plan = MealPlan.objects.create(user=other, recipe=self.recipe, date='2026-01-01', meal_type='dinner')
        response = self.client.delete(f'/api/meal-plans/{plan.id}/')
        self.assertEqual(response.status_code, 404)  # invisible car hors queryset
