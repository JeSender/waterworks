# consumers/decorators.py
"""
Custom decorators for enhanced security and access control.
Used for protecting sensitive views in the thesis/research project.
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect


def superuser_required(view_func):
    """
    Decorator that requires the user to be a superuser.
    This adds an extra layer of security for sensitive administrative functions.

    Usage:
        @superuser_required
        def my_admin_view(request):
            # Only superusers can access this
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            # Redirect to login if not authenticated
            messages.error(request, "You must be logged in to access this page.")
            return redirect('consumers:staff_login')

        if not request.user.is_superuser:
            # Return forbidden response if not a superuser
            messages.error(request, "Access Denied: This page requires superuser privileges.")
            return render(request, 'consumers/403.html', status=403)

        return view_func(request, *args, **kwargs)
    return wrapper


def admin_or_superuser_required(view_func):
    """
    Decorator that requires the user to be either a superuser or have admin role in StaffProfile.
    Provides more flexible access control.

    Usage:
        @admin_or_superuser_required
        def my_admin_view(request):
            # Admins and superusers can access this
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('consumers:staff_login')

        # Check if superuser
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Check if user has admin role in StaffProfile
        try:
            from .models import StaffProfile
            profile = StaffProfile.objects.get(user=request.user)
            if profile.role == 'admin':
                return view_func(request, *args, **kwargs)
        except StaffProfile.DoesNotExist:
            pass

        # If neither superuser nor admin, deny access
        messages.error(request, "Access Denied: Administrative privileges required.")
        return render(request, 'consumers/403.html', status=403)

    return wrapper


def log_activity(activity_description):
    """
    Decorator that logs user activities for audit trail.
    Useful for tracking who performed what action and when.

    Usage:
        @log_activity("User deleted consumer")
        def delete_consumer(request, consumer_id):
            # This action will be logged
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Execute the view function first
            response = view_func(request, *args, **kwargs)

            # Log the activity (you can extend this to write to a database)
            if request.user.is_authenticated:
                from .models import UserLoginEvent
                import logging
                logger = logging.getLogger('security_audit')
                logger.info(f"{activity_description} - User: {request.user.username} - IP: {get_client_ip(request)}")

            return response
        return wrapper
    return decorator


def get_client_ip(request):
    """
    Helper function to get the client's IP address from the request.
    Handles proxies and forwarded requests.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """
    Helper function to get the user agent (browser/device info) from the request.
    """
    return request.META.get('HTTP_USER_AGENT', '')


def check_password_strength(password):
    """
    Helper function to check password strength.
    Returns tuple: (is_strong: bool, message: str)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)

    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and numbers."

    return True, "Password is strong."
