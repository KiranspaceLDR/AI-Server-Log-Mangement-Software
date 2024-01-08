# Major_project/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Error_log.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    
]
