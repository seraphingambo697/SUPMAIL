from django.conf import settings
from django.db import models

from cookbooks.models import Cookbook


class Ingredient(models.Model):
    """Table maître des ingrédients """
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        indexes = [models.Index(fields=['name'])]
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    CATEGORY_CHOICES = [
        ('cuisine', 'Type de cuisine'),
        ('diet', 'Régime'),
        ('difficulty', 'Difficulté'),
        ('other', 'Autre'),
    ]
    name = models.CharField(max_length=80)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')

    class Meta:
        unique_together = ('name', 'category')
        indexes = [models.Index(fields=['name'])]

    def __str__(self):
        return f"{self.name} ({self.category})"


class Recipe(models.Model):
    """Une recette (2.2.3). Peut appartenir à un utilisateur seul (owner,
    cookbook=None) ou à un cookbook partagé."""

    title = models.CharField(max_length=200)
    steps = models.TextField(help_text="Instructions détaillées, une étape par ligne")
    prep_time_minutes = models.PositiveIntegerField(default=0)
    cook_time_minutes = models.PositiveIntegerField(default=0)
    servings = models.PositiveIntegerField(default=4)
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)
    source = models.CharField(max_length=500, blank=True, help_text="URL ou 'Création utilisateur'")

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipes'
    )
    cookbook = models.ForeignKey(
        Cookbook, on_delete=models.CASCADE, related_name='recipes', blank=True, null=True
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='recipes')
    favorited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='favorite_recipes', through='Favorite'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['prep_time_minutes']),
            models.Index(fields=['cook_time_minutes']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def total_time_minutes(self):
        return self.prep_time_minutes + self.cook_time_minutes


class RecipeIngredient(models.Model):
    """Ligne d'ingrédient structurée avec quantité (2.2.3)."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, related_name='recipe_lines')
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    unit = models.CharField(max_length=30, blank=True)

    class Meta:
        indexes = [models.Index(fields=['ingredient'])]

    def __str__(self):
        return f"{self.quantity} {self.unit} {self.ingredient}"


class Favorite(models.Model):
    """Table intermédiaire favoris, avec date pour tri éventuel."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')


class Comment(models.Model):
    """Commentaire d'une recette au sein d'un cookbook partagé (2.2.8)."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.recipe}"
