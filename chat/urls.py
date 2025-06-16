from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'rooms', ChatRoomViewSet, basename='chat-room')

urlpatterns = [
    path('', include(router.urls)),
]
