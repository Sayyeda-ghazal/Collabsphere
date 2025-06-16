from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspaceViewSet, accept_invitation

router = DefaultRouter()
router.register(r'workspaces', WorkspaceViewSet, basename='workspace')

urlpatterns = [
    path('', include(router.urls)),
    path('invitations/accept/<str:token>/', accept_invitation, name='accept-invitation'),
]

