from django.conf import settings
from django.db import models

from cookbooks.models import Cookbook


class Message(models.Model):
    """Message de la messagerie instantanée interne à un cookbook (2.2.8)."""
    cookbook = models.ForeignKey(Cookbook, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [models.Index(fields=['cookbook', 'created_at'])]

    def __str__(self):
        return f"{self.author}: {self.content[:30]}"
