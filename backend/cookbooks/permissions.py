from rest_framework import permissions

from .models import CookbookMembership


def get_membership(user, cookbook):
    try:
        return CookbookMembership.objects.get(cookbook=cookbook, user=user)
    except CookbookMembership.DoesNotExist:
        return None


class IsCookbookMember(permissions.BasePermission):
    """Autorise uniquement les membres du cookbook (lecture au minimum)."""

    def has_object_permission(self, request, view, obj):
        cookbook = obj if hasattr(obj, 'memberships') else obj.cookbook
        return get_membership(request.user, cookbook) is not None


class IsCookbookEditor(permissions.BasePermission):
    """Autorise uniquement créateur/éditeur à modifier."""

    def has_object_permission(self, request, view, obj):
        cookbook = obj if hasattr(obj, 'memberships') else obj.cookbook
        membership = get_membership(request.user, cookbook)
        if membership is None:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return membership.can_edit()


class IsCookbookCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        cookbook = obj if hasattr(obj, 'memberships') else obj.cookbook
        membership = get_membership(request.user, cookbook)
        return membership is not None and membership.role == CookbookMembership.ROLE_CREATOR
