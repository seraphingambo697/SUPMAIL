from django.conf import settings
from django.db import models

from cookbooks.models import Cookbook
from recipes.models import Recipe


class MealPlan(models.Model):
    """Planification d'un repas (2.2.3 / 2.2.5), personnelle ou de cookbook."""

    MEAL_TYPES = [
        ('breakfast', 'Petit-déjeuner'),
        ('lunch', 'Déjeuner'),
        ('dinner', 'Dîner'),
        ('snack', 'Collation'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meal_plans')
    cookbook = models.ForeignKey(Cookbook, on_delete=models.CASCADE, related_name='meal_plans', blank=True, null=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='meal_plan_entries')
    date = models.DateField()
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES, default='dinner')
    servings = models.PositiveIntegerField(default=4)

    class Meta:
        indexes = [models.Index(fields=['date'])]
        ordering = ['date', 'meal_type']

    def __str__(self):
        return f"{self.date} {self.meal_type}: {self.recipe}"
