from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from cookbooks.models import Cookbook
from cookbooks.permissions import get_membership

from .models import Message
from .serializers import MessageSerializer


class MessageViewSet(viewsets.ModelViewSet):
    """Messagerie instantanée interne à un cookbook (2.2.8).

    Le frontend "poll" périodiquement GET /api/messages/?cookbook=<id>&after=<id>
    pour simuler le temps réel sans dépendance supplémentaire (websocket/redis).
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['cookbook']
    ordering_fields = ['created_at']

    def get_queryset(self):
        qs = Message.objects.filter(cookbook__memberships__user=self.request.user).distinct()
        after = self.request.query_params.get('after')
        if after:
            qs = qs.filter(id__gt=after)
        return qs

    def perform_create(self, serializer):
        cookbook = serializer.validated_data['cookbook']
        membership = get_membership(self.request.user, cookbook)
        if not membership:
            raise PermissionDenied("Vous n'êtes pas membre de ce cookbook.")
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied("Vous ne pouvez modifier que vos propres messages.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("Vous ne pouvez supprimer que vos propres messages.")
        instance.delete()
