from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Container, Note

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model, covering authentication and profile details.
    """
    class Meta:
        model = User
        # Fields based on Entity: User 
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username']

class ContainerSerializer(serializers.ModelSerializer):
    """
    Serializer for the P.A.R.A. structure.
    """
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Container
        # Fields based on Entity: Container 
        fields = ['id', 'name', 'type', 'description', 'created_at', 'updated_at', 'owner']
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner']

class NoteSerializer(serializers.ModelSerializer):
    """
    Serializer for the Note model, including contextual linking to containers.
    """
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Note
        # Fields based on Entity: Note [cite: 14]
        fields = [
            'id', 'title', 'content', 'is_archived', 
            'created_at', 'updated_at', 'owner', 'containers'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner']