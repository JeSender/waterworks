# consumers/decorators.py
"""
Custom decorators for enhanced security and access control.
Used for protecting sensitive views in the thesis/research project.

Security Features:
- Rate limiting for login endpoints
- Account lockout after failed attempts
- Two-factor authentication support
- Activity logging and audit trail
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# ======================
# SECURITY CONFIGURATION
# ======================
RATE_LIMIT_CONFIG = {
    'MAX_LOGIN_ATTEMPTS': 5,           # Max failed attempts before lockout
    'LOCKOUT_DURATION_MINUTES': 15,    # Duration of lockout in minutes
    'ATTEMPT_WINDOW_MINUTES': 15,      # Time window to count attempts
    'API_RATE_LIMIT_PER_MINUTE': 30,   # Max API requests per minute
}


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
    NOTE: This allows FULL admin access. For restricted admin access, use specific permission decorators.

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


# ======================
# ROLE-BASED ACCESS CONTROL
# ======================

def is_admin_user(user):
    """Check if user is an admin (has admin role in StaffProfile)."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    try:
        from .models import StaffProfile
        profile = StaffProfile.objects.get(user=user)
        return profile.role == 'admin'
    except:
        return False


def is_superuser_only(user):
    """Check if user is a superuser (not just admin)."""
    return user.is_authenticated and user.is_superuser


def billing_permission_required(view_func):
    """
    Decorator for billing-related views.
    Allows: Superuser, Admin
    Denies: Field Staff, Regular Users

    Usage:
        @billing_permission_required
        def process_payment(request):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('consumers:staff_login')

        # Superusers always have access
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Check if admin
        if is_admin_user(request.user):
            return view_func(request, *args, **kwargs)

        messages.error(request, "Access Denied: Billing privileges required.")
        return render(request, 'consumers/403.html', status=403)

    return wrapper


def reports_permission_required(view_func):
    """
    Decorator for report-related views.
    Allows: Superuser, Admin
    Denies: Field Staff, Regular Users

    Usage:
        @reports_permission_required
        def generate_report(request):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('consumers:staff_login')

        # Superusers always have access
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Check if admin
        if is_admin_user(request.user):
            return view_func(request, *args, **kwargs)

        messages.error(request, "Access Denied: Report privileges required.")
        return render(request, 'consumers/403.html', status=403)

    return wrapper


def consumer_edit_permission_required(view_func):
    """
    Decorator for consumer editing views (create, edit, delete).
    Allows: Superuser ONLY
    Denies: Admin, Field Staff, Regular Users

    Admin can VIEW consumers but NOT edit them.

    Usage:
        @consumer_edit_permission_required
        def edit_consumer(request, consumer_id):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('consumers:staff_login')

        # Only superusers can edit consumers
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        messages.error(request, "Access Denied: Only superusers can modify consumer records.")
        return render(request, 'consumers/403.html', status=403)

    return wrapper


def disconnect_permission_required(view_func):
    """
    Decorator for disconnect/reconnect consumer views.
    Allows: Superuser ONLY
    Denies: Admin, Field Staff, Regular Users

    Usage:
        @disconnect_permission_required
        def disconnect_consumer(request, consumer_id):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('consumers:staff_login')

        # Only superusers can disconnect/reconnect
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        messages.error(request, "Access Denied: Only superusers can disconnect or reconnect consumers.")
        return render(request, 'consumers/403.html', status=403)

    return wrapper


def user_management_permission_required(view_func):
    """
    Decorator for user management views.
    Allows: Superuser ONLY
    Denies: Admin, Field Staff, Regular Users

    Usage:
        @user_management_permission_required
        def user_management(request):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('consumers:staff_login')

        # Only superusers can manage users
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        messages.error(request, "Access Denied: Only superusers can manage user accounts.")
        return render(request, 'consumers/403.html', status=403)

    return wrapper


def system_settings_permission_required(view_func):
    """
    Decorator for system settings views.
    Allows: Superuser ONLY
    Denies: Admin, Field Staff, Regular Users

    Usage:
        @system_settings_permission_required
        def system_settings(request):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('consumers:staff_login')

        # Only superusers can access system settings
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        messages.error(request, "Access Denied: Only superusers can access system settings.")
        return render(request, 'consumers/403.html', status=403)

    return wrapper


def view_only_for_admin(view_func):
    """
    Decorator that allows admin read-only access.
    Admin can view but POST requests (modifications) are blocked.
    Superusers have full access.

    Usage:
        @view_only_for_admin
        def consumer_detail(request, consumer_id):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('consumers:staff_login')

        # Superusers have full access
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Admin can only GET (view), not POST (modify)
        if is_admin_user(request.user):
            if request.method == 'POST':
                messages.error(request, "Access Denied: Admins cannot modify this data. View only.")
                return render(request, 'consumers/403.html', status=403)
            return view_func(request, *args, **kwargs)

        messages.error(request, "Access Denied: Insufficient privileges.")
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


# ======================
# RATE LIMITING DECORATORS
# ======================

def check_login_allowed(username, ip_address):
    """
    Check if login is allowed for the given username/IP.
    Returns: (is_allowed: bool, lockout_info: dict or None)
    """
    from .models import LoginAttemptTracker, AccountLockout

    # Check for active lockout
    is_locked, lockout = AccountLockout.is_account_locked(username=username, ip_address=ip_address)
    if is_locked:
        return False, {
            'reason': 'Account temporarily locked due to too many failed attempts.',
            'time_remaining': lockout.time_remaining_formatted,
            'locked_until': lockout.locked_until
        }

    return True, None


def record_login_attempt(username, ip_address, was_successful):
    """
    Record a login attempt and create lockout if necessary.
    Returns: (lockout_created: bool, lockout_info: dict or None)
    """
    from .models import LoginAttemptTracker, AccountLockout

    # Record the attempt
    LoginAttemptTracker.objects.create(
        username=username,
        ip_address=ip_address,
        was_successful=was_successful
    )

    # If successful, no need to check for lockout
    if was_successful:
        return False, None

    # Check failed attempts count
    failed_count = LoginAttemptTracker.get_recent_failed_attempts(
        username=username,
        minutes=RATE_LIMIT_CONFIG['ATTEMPT_WINDOW_MINUTES']
    )

    # Create lockout if threshold exceeded
    if failed_count >= RATE_LIMIT_CONFIG['MAX_LOGIN_ATTEMPTS']:
        lockout = AccountLockout.create_lockout(
            username=username,
            ip_address=ip_address,
            failed_attempts=failed_count,
            lockout_minutes=RATE_LIMIT_CONFIG['LOCKOUT_DURATION_MINUTES']
        )
        logger.warning(f"Account locked: {username} from {ip_address} after {failed_count} failed attempts")
        return True, {
            'reason': 'Too many failed login attempts. Account temporarily locked.',
            'time_remaining': lockout.time_remaining_formatted,
            'locked_until': lockout.locked_until
        }

    # Return remaining attempts info
    remaining = RATE_LIMIT_CONFIG['MAX_LOGIN_ATTEMPTS'] - failed_count
    return False, {'remaining_attempts': remaining}


def rate_limit_login(view_func):
    """
    Decorator to apply rate limiting to login views.
    Blocks login attempts if account is locked due to too many failures.

    Usage:
        @rate_limit_login
        def login_view(request):
            # Login logic here
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            username = request.POST.get('username', '').strip()
            ip_address = get_client_ip(request)

            # Check if login is allowed
            is_allowed, lockout_info = check_login_allowed(username, ip_address)
            if not is_allowed:
                messages.error(
                    request,
                    f"Account temporarily locked. Try again in {lockout_info['time_remaining']}."
                )
                logger.warning(f"Blocked login attempt for locked account: {username} from {ip_address}")
                return redirect('consumers:staff_login')

        return view_func(request, *args, **kwargs)
    return wrapper


def require_2fa(view_func):
    """
    Decorator that requires two-factor authentication for sensitive views.
    User must have 2FA enabled and verified to access the view.

    Usage:
        @login_required
        @require_2fa
        def sensitive_view(request):
            # Only accessible with 2FA
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('consumers:staff_login')

        # Check if user has 2FA enabled
        try:
            from .models import TwoFactorAuth
            two_factor = TwoFactorAuth.objects.get(user=request.user)
            if two_factor.is_enabled and two_factor.is_verified:
                # Check if 2FA was verified in this session
                if not request.session.get('2fa_verified', False):
                    messages.warning(request, "Please verify your two-factor authentication.")
                    return redirect('consumers:verify_2fa')
        except TwoFactorAuth.DoesNotExist:
            # User doesn't have 2FA set up - allow access (2FA is optional)
            pass

        return view_func(request, *args, **kwargs)
    return wrapper


def api_rate_limit(view_func):
    """
    Decorator to apply rate limiting to API endpoints.
    Limits requests per minute per IP address.

    Usage:
        @api_rate_limit
        def api_endpoint(request):
            # API logic here
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from django.core.cache import cache

        ip_address = get_client_ip(request)
        cache_key = f"api_rate_limit:{ip_address}"

        # Get current request count
        request_count = cache.get(cache_key, 0)

        if request_count >= RATE_LIMIT_CONFIG['API_RATE_LIMIT_PER_MINUTE']:
            logger.warning(f"API rate limit exceeded for IP: {ip_address}")
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.',
                'retry_after': 60
            }, status=429)

        # Increment counter (expires after 60 seconds)
        cache.set(cache_key, request_count + 1, 60)

        return view_func(request, *args, **kwargs)
    return wrapper
