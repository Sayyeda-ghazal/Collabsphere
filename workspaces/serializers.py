from rest_framework import serializers
from .models import Invitation, Membership, Workspace

class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ['id', 'name', 'description', 'created_at', 'owner']
        read_only_fields = ['id', 'created_at', 'owner']

    def get_role(self, obj):
        user = self.context['request'].user
        membership = Membership.objects.filter(user=user, workspace=obj).first()
        return membership.role if membership else None

    def create(self, validated_data):
        return Workspace.objects.create(**validated_data)
   


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ['id', 'email', 'workspace', 'role']
        extra_kwargs = {
            'workspace': {'read_only': True},
        }