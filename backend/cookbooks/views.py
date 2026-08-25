from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Cookbook, CookbookInvitation, CookbookMembership
from .permissions import IsCookbookCreator, IsCookbookEditor, get_membership
from .serializers import CookbookInvitationSerializer, CookbookSerializer

User = get_user_model()


class CookbookViewSet(viewsets.ModelViewSet):
    """CRUD cookbooks + invitations/membres (2.2.2)."""
    serializer_class = CookbookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cookbook.objects.filter(memberships__user=self.request.user).distinct()

    def get_permissions(self):
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsCookbookCreator()]
        if self.action in ('update', 'partial_update'):
            return [permissions.IsAuthenticated(), IsCookbookEditor()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['get'])
    def search(self, request, pk=None):
        """Recherche propre au cookbook, par titre/ingrédients/tags/contenu (2.2.2)."""
        cookbook = self.get_object()
        q = request.query_params.get('q', '')
        from recipes.models import Recipe
        from recipes.serializers import RecipeListSerializer

        recipes = Recipe.objects.filter(cookbook=cookbook).filter(
            Q(title__icontains=q)
            | Q(ingredients__ingredient__name__icontains=q)
            | Q(tags__name__icontains=q)
            | Q(steps__icontains=q)
        ).distinct()
        return Response(RecipeListSerializer(recipes, many=True, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """Inviter un membre par e-mail avec un rôle (2.2.2)."""
        cookbook = self.get_object()
        membership = get_membership(request.user, cookbook)
        if not membership or not membership.can_edit():
            return Response({'detail': "Permission refusée."}, status=403)

        email = request.data.get('email')
        role = request.data.get('role', CookbookMembership.ROLE_READER)
        if not email:
            return Response({'detail': 'email requis.'}, status=400)
        valid_roles = dict(CookbookMembership.ROLE_CHOICES)
        if role not in valid_roles or role == CookbookMembership.ROLE_CREATOR:
            return Response({'detail': 'Rôle invalide.'}, status=400)

        invitation = CookbookInvitation.objects.create(
            cookbook=cookbook, invited_email=email, role=role, invited_by=request.user
        )

        # Si l'utilisateur existe déjà, on l'ajoute directement au cookbook.
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            CookbookMembership.objects.get_or_create(
                cookbook=cookbook, user=existing_user, defaults={'role': role}
            )
            invitation.accepted = True
            invitation.save()

        return Response(CookbookInvitationSerializer(invitation).data, status=201)

    @action(detail=True, methods=['post'], url_path='members/(?P<user_id>[^/.]+)/remove')
    def remove_member(self, request, pk=None, user_id=None):
        cookbook = self.get_object()
        membership = get_membership(request.user, cookbook)
        if not membership or not membership.can_edit():
            return Response({'detail': 'Permission refusée.'}, status=403)
        CookbookMembership.objects.filter(cookbook=cookbook, user_id=user_id).exclude(
            role=CookbookMembership.ROLE_CREATOR
        ).delete()
        return Response(status=204)

    @action(detail=True, methods=['post'], url_path='members/(?P<user_id>[^/.]+)/role')
    def update_member_role(self, request, pk=None, user_id=None):
        cookbook = self.get_object()
        membership = get_membership(request.user, cookbook)
        if not membership or membership.role != CookbookMembership.ROLE_CREATOR:
            return Response({'detail': 'Seul le créateur peut modifier les rôles.'}, status=403)
        role = request.data.get('role')
        valid_roles = dict(CookbookMembership.ROLE_CHOICES)
        if role not in valid_roles or role == CookbookMembership.ROLE_CREATOR:
            return Response({'detail': 'Rôle invalide.'}, status=400)
        CookbookMembership.objects.filter(cookbook=cookbook, user_id=user_id).update(role=role)
        return Response(status=200)


class MyInvitationsView(viewsets.ReadOnlyModelViewSet):
    """Liste des invitations en attente pour l'utilisateur courant."""
    serializer_class = CookbookInvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CookbookInvitation.objects.filter(
            invited_email=self.request.user.email, accepted=False
        )

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        invitation = self.get_object()
        CookbookMembership.objects.get_or_create(
            cookbook=invitation.cookbook, user=request.user, defaults={'role': invitation.role}
        )
        invitation.accepted = True
        invitation.save()
        return Response(status=200)
