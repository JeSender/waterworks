# waterworks/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static

@csrf_exempt
def healthcheck(request):
    """Simple healthcheck endpoint for Railway deployment"""
    return HttpResponse("OK", status=200)

def custom_404_view(request, exception=None):
    """Custom 404 error page"""
    return render(request, 'consumers/404.html', status=404)

def custom_500_view(request):
    """Custom 500 error page"""
    return render(request, 'consumers/500.html', status=500)

urlpatterns = [
    path('health/', healthcheck, name='healthcheck'),
    path('admin/', admin.site.urls),
    # Redirect root (/) to staff login
    path('', lambda request: redirect('consumers:staff_login'), name='root_redirect'),
    # Include all consumer app URLs under root namespace
    path('', include('consumers.urls')),
]

# Custom error handlers
handler404 = custom_404_view
handler500 = custom_500_view