from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.core.mail import send_mail
from .models import Workspace, Invitation, Membership
from .serializers import WorkspaceSerializer, InvitationSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

User = get_user_model()


class WorkspaceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Workspace.objects.filter(memberships__user=self.request.user).distinct()

    def perform_create(self, serializer):
        workspace = serializer.save(owner=self.request.user)
        Membership.objects.create(user=self.request.user, workspace=workspace, role='admin')

    @action(detail=True, methods=['post'], url_path='invite')
    def invite(self, request, pk=None):
        workspace = self.get_object()
        if not Membership.objects.filter(user=request.user, workspace=workspace, role='admin').exists():
            return Response({"detail": "Only admins can invite."}, status=403)
        serializer = InvitationSerializer(data=request.data)
        if serializer.is_valid():
            invitation = serializer.save(workspace=workspace, invited_by=request.user)
            invite_url = f"http://yourfrontend.com/invite/{invitation.token}"
            send_mail(
                subject="You're invited to a workspace",
                message=f"You've been invited to join '{workspace.name}'. Click here to accept: {invite_url}",
                from_email="no-reply@collabsphere.com",
                recipient_list=[invitation.email],
            )
            return Response({"detail": "Invitation sent successfully."})
        return Response(serializer.errors, status=400)
    
    @action(detail=True, methods=['get'], url_path='members')
    def view_members(self, request, pk=None):
        workspace = self.get_object()
        if not Membership.objects.filter(user=request.user, workspace=workspace).exists():
            return Response({"detail": "You are not authorized to this workspace."}, status=403)
        members = Membership.objects.filter(workspace=workspace).select_related('user')
        data = [
            {
                "username": m.user.full_name,
                "email": m.user.email,
                "role": m.role
            }
            for m in members
        ]
        return Response(data)
    
    @action(detail=True, methods=['delete'], url_path='members/(?P<user_id>[^/.]+)')
    def remove_member(self, request, pk=None, **kwargs):
        user_id = kwargs.get('user_id')
        workspace = Workspace.objects.get(pk=pk)
        try:
            requester_membership = Membership.objects.get(user=request.user, workspace=workspace)
        except Membership.DoesNotExist:
            return Response({"detail": "you are not authenticated"}, status=403)
        if requester_membership.role != 'admin':
            return Response({"detail": "You are not the admin of this workspace."}, status=403)
        try:
            user_to_remove = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)
        if user_to_remove == request.user:
            return Response({"detail": "you can not remove yourself"}, status=400)
        try:
            membership = Membership.objects.get(user=user_to_remove, workspace=workspace)
        except Membership.DoesNotExist:
            return Response({"detail": "you can not remove yourself"}, status=400)
        membership.delete()
        return Response({"detail": "Removed Successfully"}, status=204)
    
    @action(detail=True, methods=['post'], url_path='leave')
    def leave_workspace(self, request, pk=None):
        workspace = Workspace.objects.get(pk=pk)
        try:
            membership = Membership.objects.get(user=request.user, workspace=workspace)
        except Membership.DoesNotExist:
            return Response({"detail": "you are not authenticated"}, status=403)
        if membership.role!='admin':
            admin_count = Membership.objects.filter(workspace=workspace, role='admin').count()
            if admin_count <= 1:
              return Response({"detail": "You are the last admin. Assign another admin before leaving."}, status=400)

        membership.delete()
        return Response({"detail": "You have left the workspace."}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_invitation(request, token):
    try:
        invitation = Invitation.objects.get(token=token, accepted=False)
    except Invitation.DoesNotExist:
        return Response({"detail": "Invalid or expired invitation."}, status=400)
    if Membership.objects.filter(user=request.user, workspace=invitation.workspace).exists():
        return Response({"detail": "You are already a member of this workspace."}, status=400)
    Membership.objects.create(
        user=request.user,
        workspace=invitation.workspace,
        role=invitation.role
    )
    invitation.accepted = True
    invitation.save()

    return Response({"detail": "You have joined the workspace."})
