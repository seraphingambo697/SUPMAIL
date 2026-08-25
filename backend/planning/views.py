from collections import defaultdict

from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import MealPlan
from .serializers import MealPlanSerializer


class MealPlanViewSet(viewsets.ModelViewSet):
    """Planning de repas hebdomadaire/mensuel (2.2.3)."""
    serializer_class = MealPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = {
        'cookbook': ['exact'],
        'date': ['exact', 'gte', 'lte'],
        'meal_type': ['exact'],
    }

    def get_queryset(self):
        user = self.request.user
        return MealPlan.objects.filter(
            Q(user=user) | Q(cookbook__memberships__user=user)
        ).distinct()

    def perform_create(self, serializer):
        cookbook = serializer.validated_data.get('cookbook')
        if cookbook:
            from cookbooks.permissions import get_membership
            membership = get_membership(self.request.user, cookbook)
            if not membership or not membership.can_edit():
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Permission refusée sur ce cookbook.")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        self._check_owner_or_editor(serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        self._check_owner_or_editor(instance)
        instance.delete()

    def _check_owner_or_editor(self, plan):
        from rest_framework.exceptions import PermissionDenied
        if plan.user == self.request.user:
            return
        if plan.cookbook:
            from cookbooks.permissions import get_membership
            membership = get_membership(self.request.user, plan.cookbook)
            if membership and membership.can_edit():
                return
        raise PermissionDenied("Permission refusée.")

    @action(detail=False, methods=['get'])
    def shopping_list(self, request):
        """Génère automatiquement une liste de courses agrégée à partir du
        planning sur une période (?start=YYYY-MM-DD&end=YYYY-MM-DD) - fonctionnalité
        avancée mentionnée en bonus (2.3.2)."""
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        qs = self.get_queryset()
        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)

        aggregated = defaultdict(lambda: {'quantity': 0, 'unit': ''})
        for plan in qs.select_related('recipe').prefetch_related('recipe__ingredients__ingredient'):
            ratio = plan.servings / (plan.recipe.servings or 1)
            for line in plan.recipe.ingredients.all():
                key = (line.ingredient.name, line.unit)
                aggregated[key]['quantity'] += float(line.quantity) * ratio
                aggregated[key]['unit'] = line.unit

        result = [
            {'ingredient': name, 'quantity': round(data['quantity'], 2), 'unit': unit}
            for (name, unit), data in aggregated.items()
        ]
        result.sort(key=lambda x: x['ingredient'])
        return Response(result)
