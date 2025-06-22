from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import CustomUser
from workspaces.models import Membership, Workspace
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
        workspace = serializer.validated_data.get("workspace")
        members = serializer.validated_data.get("members", [])

        if not Membership.objects.filter(workspace=workspace, user=self.request.user).exists():
            raise PermissionDenied("You are not a member of this workspace.")

        # Validate members are part of workspace
        valid_members = CustomUser.objects.filter(
            id__in=[member.id for member in members],
            memberships__workspace=workspace
        ).distinct()

        chat_room = serializer.save()
        chat_room.members.set(valid_members)
        chat_room.members.add(self.request.user)



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
    
    @action(detail=True, methods=['post'], url_path='add-member')
    def add_member(self, request, pk=None):
        room = self.get_object()

        if not room.members.filter(id=request.user.id).exists():
            raise PermissionDenied("You're not a member of this room.")

        user_id = request.data.get("user_id")
        try:
            user = User.objects.get(id=user_id)
            room.members.add(user)
            return Response({"detail": "User added successfully."})
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)

