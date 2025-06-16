from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import UploadedDocument
from .serializers import UploadedDocumentSerializer
from workspaces.models import Membership

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = UploadedDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UploadedDocument.objects.filter(workspace__memberships__user=self.request.user).distinct()

    def perform_create(self, serializer):
        workspace = serializer.validated_data['workspace']
        if not Membership.objects.filter(user=self.request.user, workspace=workspace).exists():
            raise PermissionDenied("You are not a member of this workspace.")
        serializer.save(uploaded_by=self.request.user)
