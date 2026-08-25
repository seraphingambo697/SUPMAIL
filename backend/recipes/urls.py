from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, IngredientViewSet, RecipeViewSet, TagViewSet

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('tags', TagViewSet, basename='tag')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('comments', CommentViewSet, basename='comment')

urlpatterns = router.urls
