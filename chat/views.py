from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from workspaces.models import Membership
from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
import pusher
from django.conf import settings

pusher_client = pusher.Pusher(
    app_id=settings.PUSHER_APP_ID,
    key=settings.PUSHER_KEY,
    secret=settings.PUSHER_SECRET,
    cluster=settings.PUSHER_CLUSTER,
    ssl=True
)

class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        workspace = serializer.save(created_by=self.request.user)
        Membership.objects.create(user=self.request.user, workspace=workspace, role='admin')

        room = ChatRoom.objects.create(
            workspace=workspace,
            name=f"{workspace.name} Chat",
            is_group=True
        )
        room.members.add(self.request.user)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        room = get_object_or_404(ChatRoom, pk=pk)
        if not room.members.filter(id=request.user.id).exists():
            raise PermissionDenied("You are not a member of this room.")

        messages = room.messages.all().order_by('-sent_at')[:50]  # last 50
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        room = get_object_or_404(ChatRoom, pk=pk)
        if not room.members.filter(id=request.user.id).exists():
            raise PermissionDenied("You are not a member of this room.")

        message = ChatMessage.objects.create(
            room=room,
            sender=request.user,
            content=request.data.get("content", "")
        )

        pusher_client.trigger(f'chat-room-{room.id}', 'new-message', {
            'id': message.id,
            'sender': request.user.id,
            'content': message.content,
            'sent_at': str(message.sent_at),
        })

        return Response(ChatMessageSerializer(message).data, status=status.HTTP_201_CREATED)
