# waterworks/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def healthcheck(request):
    """Simple healthcheck endpoint for Railway deployment"""
    return HttpResponse("OK", status=200)

urlpatterns = [
    path('health/', healthcheck, name='healthcheck'),
    path('admin/', admin.site.urls),
    # Redirect root (/) to staff login
    path('', lambda request: redirect('consumers:staff_login'), name='root_redirect'),
    # Include all consumer app URLs under root namespace
    path('', include('consumers.urls')),
]