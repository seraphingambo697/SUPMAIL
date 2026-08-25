from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'cookbook', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']
