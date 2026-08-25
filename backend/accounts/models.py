from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Utilisateur SUPMEAL. Étend AbstractUser pour garder le hashing de mot
    de passe et les mécanismes d'auth standards de Django (jamais de mot de
    passe en clair)."""

    DIET_CHOICES = [
        ('none', 'Aucun'),
        ('vegetarian', 'Végétarien'),
        ('vegan', 'Végétalien'),
        ('pescatarian', 'Pescétarien'),
        ('gluten_free', 'Sans gluten'),
        ('halal', 'Halal'),
        ('kosher', 'Casher'),
    ]

    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # Préférences culinaires (2.2.5)
    diet = models.CharField(max_length=20, choices=DIET_CHOICES, default='none')
    allergies = models.CharField(max_length=255, blank=True, help_text="Séparées par des virgules")
    favorite_cuisine = models.CharField(max_length=100, blank=True)
    default_servings = models.PositiveIntegerField(default=4)

    # OAuth2
    oauth_provider = models.CharField(max_length=20, blank=True)
    oauth_id = models.CharField(max_length=255, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        indexes = [models.Index(fields=['email'])]

    def __str__(self):
        return self.username
