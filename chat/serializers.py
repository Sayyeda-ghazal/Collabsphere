from rest_framework import serializers
from .models import ChatRoom, ChatMessage
from accounts.models import CustomUser

class ChatRoomSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=CustomUser.objects.all())

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'is_group', 'members', 'created_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.id')

    class Meta:
        model = ChatMessage
        fields = ['id', 'room', 'sender', 'content', 'sent_at']
