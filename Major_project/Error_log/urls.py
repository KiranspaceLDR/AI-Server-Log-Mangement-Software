# Error_log/urls.py

from django.urls import path
from .views import compile_and_search,home, protected_view, register,dashboard

urlpatterns = [
    path('', home, name='home'),
    path('protected/', protected_view, name='protected_view'),
    path('register/', register, name='register'),
    path('upload_file/', compile_and_search, name='upload_file'),
    path('dashboard/', dashboard, name='dashboard'),
    
    # Add more paths for other languages as needed
]
