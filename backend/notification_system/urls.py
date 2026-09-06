import os
from pathlib import Path
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.views.static import serve

FRONTEND_DIR = settings.BASE_DIR.parent / 'frontend'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('notifications.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    re_path(r'^(?P<path>(css|js|sw\.js).*)$', serve, {'document_root': str(FRONTEND_DIR)}),
]
