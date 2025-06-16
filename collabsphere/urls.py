from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/workspaces/', include('workspaces.urls')),
    path('api/documents/', include('documents.urls')),
    path('api/chat/', include('chat.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
