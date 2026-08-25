import csv
import io
import json

from django.db import transaction
from django.http import HttpResponse
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from cookbooks.models import Cookbook, CookbookMembership
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag


def recipe_to_dict(recipe):
    """Sérialise une recette dans un format proche du schéma Mealie (2.2.6)."""
    return {
        'name': recipe.title,
        'description': '',
        'recipeYield': recipe.servings,
        'prepTime': recipe.prep_time_minutes,
        'performTime': recipe.cook_time_minutes,
        'recipeIngredient': [
            {
                'note': f"{i.quantity} {i.unit} {i.ingredient.name}".strip(),
                'food': {'name': i.ingredient.name},
                'quantity': float(i.quantity),
                'unit': i.unit,
            }
            for i in recipe.ingredients.all()
        ],
        'recipeInstructions': [{'text': step} for step in recipe.steps.splitlines() if step.strip()],
        'tags': [{'name': t.name, 'category': t.category} for t in recipe.tags.all()],
        'orgURL': recipe.source,
        'cookbook': recipe.cookbook.name if recipe.cookbook else None,
    }


class ExportView(APIView):
    """Export de l'ensemble des recettes/cookbooks de l'utilisateur (2.2.6).

    GET /api/export/?export_format=json|csv
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        fmt = request.query_params.get('export_format', 'json')
        user = request.user
        recipes = Recipe.objects.filter(owner=user).distinct().prefetch_related(
            'ingredients__ingredient', 'tags'
        )
        cookbooks = Cookbook.objects.filter(memberships__user=user).distinct()

        if fmt == 'csv':
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow(['title', 'servings', 'prep_time', 'cook_time', 'ingredients', 'steps', 'tags', 'source', 'cookbook'])
            for r in recipes:
                ingredients_str = '; '.join(f"{i.quantity} {i.unit} {i.ingredient.name}" for i in r.ingredients.all())
                tags_str = ', '.join(t.name for t in r.tags.all())
                writer.writerow([
                    r.title, r.servings, r.prep_time_minutes, r.cook_time_minutes,
                    ingredients_str, r.steps.replace('\n', ' | '), tags_str, r.source,
                    r.cookbook.name if r.cookbook else '',
                ])
            response = HttpResponse(buffer.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="supmeal_export.csv"'
            return response

        data = {
            'cookbooks': [{'name': c.name, 'description': c.description} for c in cookbooks],
            'recipes': [recipe_to_dict(r) for r in recipes],
        }
        response = HttpResponse(json.dumps(data, indent=2, ensure_ascii=False), content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="supmeal_export.json"'
        return response


class ImportView(APIView):
    """Import de recettes/cookbooks depuis un fichier JSON compatible SUPMEAL/Mealie,
    ou CSV (2.2.7). L'utilisateur qui importe devient créateur des éléments importés."""
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        uploaded = request.FILES.get('file')
        if not uploaded:
            return Response({'detail': 'Fichier requis (champ "file").'}, status=400)

        user = request.user
        filename = uploaded.name.lower()
        created_recipes = 0
        created_cookbooks = 0

        if filename.endswith('.csv'):
            text = uploaded.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(text))
            for row in reader:
                recipe = Recipe.objects.create(
                    title=row.get('title', 'Sans titre'),
                    owner=user,
                    servings=int(row.get('servings') or 4),
                    prep_time_minutes=int(row.get('prep_time') or 0),
                    cook_time_minutes=int(row.get('cook_time') or 0),
                    steps=row.get('steps', '').replace(' | ', '\n'),
                    source=row.get('source', ''),
                )
                for part in (row.get('ingredients') or '').split(';'):
                    part = part.strip()
                    if not part:
                        continue
                    tokens = part.split(' ', 2)
                    qty = tokens[0] if tokens else '0'
                    unit = tokens[1] if len(tokens) > 1 else ''
                    name = tokens[2] if len(tokens) > 2 else part
                    ingredient, _ = Ingredient.objects.get_or_create(name=name.strip().lower())
                    try:
                        qty_val = float(qty)
                    except ValueError:
                        qty_val, unit, name = 0, '', part
                        ingredient, _ = Ingredient.objects.get_or_create(name=name.strip().lower())
                    RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, quantity=qty_val, unit=unit)
                created_recipes += 1
        else:
            data = json.load(uploaded)
            for cb in data.get('cookbooks', []):
                cookbook, created = Cookbook.objects.get_or_create(
                    name=cb['name'], owner=user, defaults={'description': cb.get('description', '')}
                )
                if created:
                    CookbookMembership.objects.get_or_create(
                        cookbook=cookbook, user=user, defaults={'role': CookbookMembership.ROLE_CREATOR}
                    )
                    created_cookbooks += 1

            for r in data.get('recipes', []):
                cookbook = None
                if r.get('cookbook'):
                    cookbook = Cookbook.objects.filter(name=r['cookbook'], owner=user).first()
                steps_text = '\n'.join(
                    step.get('text', step) if isinstance(step, dict) else str(step)
                    for step in r.get('recipeInstructions', [])
                )
                recipe = Recipe.objects.create(
                    title=r.get('name', 'Sans titre'),
                    owner=user,
                    cookbook=cookbook,
                    servings=int(r.get('recipeYield') or 4),
                    prep_time_minutes=int(r.get('prepTime') or 0),
                    cook_time_minutes=int(r.get('performTime') or 0),
                    steps=steps_text,
                    source=r.get('orgURL', ''),
                )
                for ing in r.get('recipeIngredient', []):
                    name = (ing.get('food', {}) or {}).get('name') or ing.get('note', 'ingrédient')
                    ingredient, _ = Ingredient.objects.get_or_create(name=name.strip().lower())
                    RecipeIngredient.objects.create(
                        recipe=recipe, ingredient=ingredient,
                        quantity=ing.get('quantity') or 0, unit=ing.get('unit', ''),
                    )
                for tag in r.get('tags', []):
                    tag_obj, _ = Tag.objects.get_or_create(
                        name=tag.get('name', 'tag'), category=tag.get('category', 'other')
                    )
                    recipe.tags.add(tag_obj)
                created_recipes += 1

        return Response({
            'detail': 'Import terminé.',
            'recipes_created': created_recipes,
            'cookbooks_created': created_cookbooks,
        }, status=201)
