import django_filters

from .models import Recipe


class RecipeFilter(django_filters.FilterSet):
    """Filtrage avancé (2.2.4) : cookbook, tags, ingrédients, temps, favoris."""

    cookbook = django_filters.NumberFilter(field_name='cookbook_id')
    mine = django_filters.BooleanFilter(method='filter_mine')
    tag = django_filters.CharFilter(field_name='tags__name', lookup_expr='iexact')
    category = django_filters.CharFilter(field_name='tags__category', lookup_expr='iexact')
    ingredient = django_filters.CharFilter(field_name='ingredients__ingredient__name', lookup_expr='icontains')
    max_prep_time = django_filters.NumberFilter(field_name='prep_time_minutes', lookup_expr='lte')
    max_cook_time = django_filters.NumberFilter(field_name='cook_time_minutes', lookup_expr='lte')
    favorite = django_filters.BooleanFilter(method='filter_favorite')

    class Meta:
        model = Recipe
        fields = ['cookbook', 'tag', 'category', 'ingredient', 'max_prep_time', 'max_cook_time', 'favorite']

    def filter_mine(self, queryset, name, value):
        request = self.request
        if value:
            return queryset.filter(owner=request.user, cookbook__isnull=True)
        return queryset

    def filter_favorite(self, queryset, name, value):
        request = self.request
        if value:
            return queryset.filter(favorited_by=request.user)
        return queryset
