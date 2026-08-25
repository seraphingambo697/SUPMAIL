from django.db.models import Q
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from cookbooks.permissions import get_membership

from .filters import RecipeFilter
from .models import Comment, Favorite, Ingredient, Recipe, Tag
from .serializers import (
    CommentSerializer,
    IngredientSerializer,
    RecipeDetailSerializer,
    RecipeListSerializer,
    TagSerializer,
)


class RecipeViewSet(viewsets.ModelViewSet):
    """Gestion complète des recettes (2.2.3) + filtrage/recherche (2.2.4)."""

    filterset_class = RecipeFilter
    search_fields = ['title', 'steps', 'ingredients__ingredient__name', 'tags__name']
    ordering_fields = ['created_at', 'prep_time_minutes', 'cook_time_minutes', 'title']
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeListSerializer
        return RecipeDetailSerializer

    def get_queryset(self):
        user = self.request.user
        # Recettes personnelles de l'utilisateur + recettes des cookbooks dont il est membre.
        return Recipe.objects.filter(
            Q(owner=user, cookbook__isnull=True) | Q(cookbook__memberships__user=user)
        ).distinct().prefetch_related('tags', 'ingredients__ingredient')

    def perform_create(self, serializer):
        cookbook = serializer.validated_data.get('cookbook')
        if cookbook:
            membership = get_membership(self.request.user, cookbook)
            if not membership or not membership.can_edit():
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Vous n'avez pas la permission d'ajouter des recettes ici.")
        serializer.save()

    def perform_update(self, serializer):
        recipe = self.get_object()
        if recipe.cookbook:
            membership = get_membership(self.request.user, recipe.cookbook)
            if not membership or not membership.can_edit():
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Permission refusée.")
        elif recipe.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Permission refusée.")
        serializer.save()

    def perform_destroy(self, instance):
        """Seuls le propriétaire (recette perso) ou un créateur/éditeur du
        cookbook (recette partagée) peuvent supprimer une recette."""
        from rest_framework.exceptions import PermissionDenied
        if instance.cookbook:
            membership = get_membership(self.request.user, instance.cookbook)
            if not membership or not membership.can_edit():
                raise PermissionDenied("Permission refusée.")
        elif instance.owner != self.request.user:
            raise PermissionDenied("Permission refusée.")
        instance.delete()

    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Marquer/démarquer une recette comme favorite (2.2.3)."""
        recipe = self.get_object()
        fav, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
        if not created:
            fav.delete()
            return Response({'is_favorite': False})
        return Response({'is_favorite': True})

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """Commenter une recette au sein d'un cookbook (2.2.8)."""
        recipe = self.get_object()
        if request.method == 'GET':
            return Response(CommentSerializer(recipe.comments.all(), many=True).data)

        if recipe.cookbook:
            membership = get_membership(request.user, recipe.cookbook)
            if not membership or not membership.can_comment():
                return Response({'detail': 'Permission refusée.'}, status=403)
        serializer = CommentSerializer(data={'content': request.data.get('content'), 'recipe': recipe.id})
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, recipe=recipe)
        return Response(serializer.data, status=201)


class TagViewSet(viewsets.ModelViewSet):
    """Les tags sont un référentiel partagé : tout utilisateur authentifié peut
    en créer/lister, mais seul un administrateur peut les modifier/supprimer
    pour éviter qu'un tag utilisé par d'autres recettes ne casse ailleurs."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filterset_fields = ['category']

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class CommentViewSet(viewsets.GenericViewSet, mixins.DestroyModelMixin):
    """Permet à l'auteur d'un commentaire de le supprimer."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        from rest_framework.exceptions import PermissionDenied
        if instance.author != self.request.user:
            raise PermissionDenied("Vous ne pouvez supprimer que vos propres commentaires.")
        instance.delete()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Liste/recherche des ingrédients (autocomplete pour le formulaire recette)."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name']
