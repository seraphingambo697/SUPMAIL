from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import Cookbook, CookbookInvitation, CookbookMembership


class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CookbookMembership
        fields = ['id', 'user', 'role', 'joined_at']


class CookbookSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    memberships = MembershipSerializer(many=True, read_only=True)
    my_role = serializers.SerializerMethodField()
    recipe_count = serializers.SerializerMethodField()

    class Meta:
        model = Cookbook
        fields = [
            'id', 'name', 'description', 'owner', 'created_at', 'updated_at',
            'memberships', 'my_role', 'recipe_count',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def get_my_role(self, obj):
        user = self.context['request'].user
        m = obj.memberships.filter(user=user).first()
        return m.role if m else None

    def get_recipe_count(self, obj):
        return obj.recipes.count()

    def create(self, validated_data):
        request = self.context['request']
        cookbook = Cookbook.objects.create(owner=request.user, **validated_data)
        CookbookMembership.objects.create(
            cookbook=cookbook, user=request.user, role=CookbookMembership.ROLE_CREATOR
        )
        return cookbook


class CookbookInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CookbookInvitation
        fields = ['id', 'cookbook', 'invited_email', 'role', 'invited_by', 'created_at', 'accepted']
        read_only_fields = ['id', 'invited_by', 'created_at', 'accepted', 'cookbook']
