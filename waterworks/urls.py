from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('consumers:staff_login')),  # default root → login
    path('', include('consumers.urls')),  # include app urls (only once!)
]
