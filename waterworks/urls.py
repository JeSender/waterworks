# waterworks/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    # Redirect root (/) to staff login
    path('', lambda request: redirect('consumers:staff_login'), name='root_redirect'),
    # Include all consumer app URLs under root namespace
    path('', include('consumers.urls')),
]