from rest_framework import serializers
from workspaces.models import Membership
from .models import ChatRoom, ChatMessage
from rest_framework.exceptions import PermissionDenied
from accounts.models import CustomUser

class ChatRoomSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'is_group', 'workspace', 'members', 'created_at']
        read_only_fields = ['id', 'created_at']
 

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.id')

    class Meta:
        model = ChatMessage
        fields = ['id', 'room', 'sender', 'content', 'sent_at']
