from django.conf import settings
from django.db import models


class Cookbook(models.Model):
    """Livre de recettes partagé."""
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_cookbooks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['name'])]
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class CookbookMembership(models.Model):
    """Appartenance d'un utilisateur à un cookbook, avec permission """

    ROLE_CREATOR = 'creator'
    ROLE_EDITOR = 'editor'
    ROLE_COMMENTATOR = 'commentator'
    ROLE_READER = 'reader'
    ROLE_CHOICES = [
        (ROLE_CREATOR, 'Créateur'),
        (ROLE_EDITOR, 'Éditeur'),
        (ROLE_COMMENTATOR, 'Commentateur'),
        (ROLE_READER, 'Lecteur'),
    ]

    cookbook = models.ForeignKey(Cookbook, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cookbook_memberships'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_READER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cookbook', 'user')

    def __str__(self):
        return f"{self.user} @ {self.cookbook} ({self.role})"

    def can_edit(self):
        return self.role in (self.ROLE_CREATOR, self.ROLE_EDITOR)

    def can_comment(self):
        return self.role in (self.ROLE_CREATOR, self.ROLE_EDITOR, self.ROLE_COMMENTATOR)


class CookbookInvitation(models.Model):
    """Invitation d'un utilisateur à rejoindre un cookbook."""
    cookbook = models.ForeignKey(Cookbook, on_delete=models.CASCADE, related_name='invitations')
    invited_email = models.EmailField()
    role = models.CharField(max_length=20, choices=CookbookMembership.ROLE_CHOICES,
                             default=CookbookMembership.ROLE_READER)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Invitation {self.invited_email} -> {self.cookbook}"
