from rest_framework import serializers

from recipes.serializers import RecipeListSerializer

from .models import MealPlan


class MealPlanSerializer(serializers.ModelSerializer):
    recipe_detail = RecipeListSerializer(source='recipe', read_only=True)

    class Meta:
        model = MealPlan
        fields = ['id', 'user', 'cookbook', 'recipe', 'recipe_detail', 'date', 'meal_type', 'servings']
        read_only_fields = ['id', 'user']
