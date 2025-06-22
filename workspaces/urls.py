from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspaceMembersView, WorkspaceViewSet, accept_invitation

router = DefaultRouter()
router.register(r'workspaces', WorkspaceViewSet, basename='workspace')

urlpatterns = [
    path('', include(router.urls)),
    path('invitations/accept/<str:token>/', accept_invitation, name='accept-invitation'),
    path('<int:workspace_id>/view-members/', WorkspaceMembersView.as_view(), name='workspace-members'),
]

