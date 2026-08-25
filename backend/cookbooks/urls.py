from rest_framework.routers import DefaultRouter

from .views import CookbookViewSet, MyInvitationsView

router = DefaultRouter()
router.register('cookbooks', CookbookViewSet, basename='cookbook')
router.register('invitations', MyInvitationsView, basename='invitation')

urlpatterns = router.urls
