# waterworks/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

@csrf_exempt
def healthcheck(request):
    """Simple healthcheck endpoint for Vercel deployment"""
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

    # Django's built-in password reset views
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='consumers/password_reset.html',
             email_template_name='consumers/emails/password_reset_email.txt',
             html_email_template_name='consumers/emails/password_reset_email.html',
             subject_template_name='consumers/emails/password_reset_subject.txt',
             success_url='/password-reset/done/'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='consumers/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='consumers/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='consumers/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # Redirect root (/) to staff login (HEAD returns 200 for Render health check)
    path('', lambda request: HttpResponse("OK", status=200) if request.method == 'HEAD' else redirect('consumers:staff_login'), name='root_redirect'),
    # Include all consumer app URLs under root namespace
    path('', include('consumers.urls')),
]

# Custom error handlers
handler404 = custom_404_view
handler500 = custom_500_view