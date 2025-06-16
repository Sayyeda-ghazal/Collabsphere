from django.db import models
from django.conf import settings
from workspaces.models import Workspace

class UploadedDocument(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='uploaded_documents')
    file = models.FileField(upload_to='workspace_documents/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
