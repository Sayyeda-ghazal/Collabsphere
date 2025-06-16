from rest_framework import serializers
from .models import Invitation, Workspace

class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ['id', 'name', 'description', 'created_at', 'owner']
        read_only_fields = ['id', 'created_at', 'owner']

    def create(self, validated_data):
         return Workspace.objects.create(**validated_data)   


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ['id', 'email', 'workspace', 'role']
        extra_kwargs = {
            'workspace': {'read_only': True},
        }