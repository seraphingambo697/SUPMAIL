from django.db import transaction
from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import Comment, Favorite, Ingredient, Recipe, RecipeIngredient, Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'category']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(write_only=True)
    ingredient = IngredientSerializer(read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'ingredient', 'ingredient_name', 'quantity', 'unit']

    def create(self, validated_data):
        name = validated_data.pop('ingredient_name').strip().lower()
        ingredient, _ = Ingredient.objects.get_or_create(name=name)
        return RecipeIngredient.objects.create(ingredient=ingredient, **validated_data)


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'recipe', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


class RecipeListSerializer(serializers.ModelSerializer):
    """Version allégée pour les listes/filtres (2.2.4)."""
    tags = TagSerializer(many=True, read_only=True)
    is_favorite = serializers.SerializerMethodField()
    total_time_minutes = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'image', 'prep_time_minutes', 'cook_time_minutes',
            'total_time_minutes', 'servings', 'tags', 'is_favorite', 'cookbook', 'owner',
        ]

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()


class RecipeDetailSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True, required=False, source='tags'
    )
    ingredients = RecipeIngredientSerializer(many=True)
    comments = CommentSerializer(many=True, read_only=True)
    is_favorite = serializers.SerializerMethodField()
    total_time_minutes = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'steps', 'prep_time_minutes', 'cook_time_minutes',
            'total_time_minutes', 'servings', 'image', 'source', 'owner', 'cookbook',
            'tags', 'tag_ids', 'ingredients', 'comments', 'is_favorite',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        request = self.context['request']
        recipe = Recipe.objects.create(owner=request.user, **validated_data)
        recipe.tags.set(tags)
        for ing in ingredients_data:
            name = ing['ingredient_name'].strip().lower()
            ingredient, _ = Ingredient.objects.get_or_create(name=name)
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient,
                quantity=ing.get('quantity', 0), unit=ing.get('unit', ''),
            )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        if ingredients_data is not None:
            instance.ingredients.all().delete()
            for ing in ingredients_data:
                name = ing['ingredient_name'].strip().lower()
                ingredient, _ = Ingredient.objects.get_or_create(name=name)
                RecipeIngredient.objects.create(
                    recipe=instance, ingredient=ingredient,
                    quantity=ing.get('quantity', 0), unit=ing.get('unit', ''),
                )
        return instance
