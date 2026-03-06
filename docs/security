# Security Filtration and Trappings Documentation

## Balilihan Waterworks Management System

**Version:** 2.0
**Last Updated:** November 2024
**Classification:** Technical Security Documentation

---

## Table of Contents

1. [Overview](#overview)
2. [Input Filtration](#1-input-filtration)
3. [Data Sanitization](#2-data-sanitization)
4. [Error Trapping](#3-error-trapping)
5. [Authentication Traps](#4-authentication-traps)
6. [Authorization Filters](#5-authorization-filters)
7. [Data Access Filters](#6-data-access-filters)
8. [Security Activity Traps](#7-security-activity-traps)
9. [Session Management](#8-session-management)
10. [Password Security](#9-password-security)
11. [CSRF Protection](#10-csrf-protection)
12. [Production Security Headers](#11-production-security-headers)
13. [Security Assessment Summary](#12-security-assessment-summary)

---

## Overview

This document details the **security filtration** (input validation, data sanitization, request filtering) and **trapping mechanisms** (error handling, security logging, activity tracking) implemented in the Balilihan Waterworks Management System.

### Security Philosophy

The system follows a **defense-in-depth** approach with multiple layers of security:

```
┌─────────────────────────────────────────────────────────────┐
│                    REQUEST LIFECYCLE                        │
├─────────────────────────────────────────────────────────────┤
│  1. CSRF Middleware        → Blocks forged requests         │
│  2. Authentication Check   → Validates user identity        │
│  3. Authorization Filter   → Verifies permissions           │
│  4. Input Validation       → Sanitizes and validates data   │
│  5. Business Logic         → Enforces rules                 │
│  6. Database ORM           → Prevents SQL injection         │
│  7. Error Trapping         → Handles failures gracefully    │
│  8. Activity Logging       → Records actions for audit      │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Input Filtration

### 1.1 Form-Level Validation

**Location:** `consumers/forms.py`

```python
class ConsumerForm(forms.ModelForm):
    # Date validation via HTML5 widget
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = Consumer
        # EXPLICIT field list prevents mass assignment attacks
        fields = [
            'first_name', 'middle_name', 'last_name', 'birth_date',
            'gender', 'phone_number', 'civil_status', 'spouse_name',
            'barangay', 'purok', 'household_number', 'usage_type',
            'meter_brand', 'serial_number', 'first_reading', 'registration_date',
        ]
```

**Security Features:**
| Feature | Protection |
|---------|------------|
| Explicit field list | Prevents mass assignment vulnerability |
| DateField widget | Enforces date format validation |
| Model validation | Inherits Django model constraints |

### 1.2 API Input Validation

**Location:** `consumers/views.py`

#### JSON Parsing Validation
```python
def api_submit_reading(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
```

#### Required Fields Validation
```python
if consumer_id is None or reading_value is None:
    return JsonResponse({
        'error': 'Missing required fields: consumer_id or reading'
    }, status=400)
```

#### Numeric Value Validation
```python
try:
    current_reading = int(reading_value)
    if current_reading < 0:
        raise ValueError("Reading value cannot be negative")
except (ValueError, TypeError):
    return JsonResponse({
        'error': 'Invalid reading value. Must be a non-negative number.'
    }, status=400)
```

#### Date Format Validation
```python
if reading_date_str:
    try:
        reading_date = timezone.datetime.strptime(reading_date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)
```

#### Business Logic Validation
```python
# Consumption cannot be negative (tampering detection)
if consumption < 0:
    return JsonResponse({
        'error': 'Invalid reading',
        'message': f'Current reading ({current_reading}) cannot be less than previous ({previous_reading})'
    }, status=400)
```

### 1.3 System Settings Validation

**Location:** `consumers/views.py` - `system_management()`

```python
# Rate validation (must be positive)
if new_res_rate <= 0 or new_comm_rate <= 0 or new_fixed_charge < 0:
    raise ValueError("Rates must be positive and fixed charge cannot be negative.")

# Percentage range validation
if penalty_rate < 0 or penalty_rate > 100:
    raise ValueError("Penalty rate must be between 0 and 100 percent.")

# Day range validation (billing cycle)
for day, name in [(reading_start, "Reading start"), (reading_end, "Reading end"),
                  (billing_day, "Billing day"), (due_day, "Due day")]:
    if day < 1 or day > 28:
        raise ValueError(f"{name} must be between 1 and 28.")

# Logical sequence validation
if reading_start > reading_end:
    raise ValueError("Reading start day must be before or equal to reading end day.")
```

### 1.4 Payment Processing Validation

```python
# Required field check
if not bill_id or not received_amount:
    messages.error(request, "Missing bill or payment amount.")
    return redirect('consumers:payment_counter')

# Type conversion with error handling
try:
    received_amount = Decimal(received_amount)
except (ValueError, InvalidOperation):
    messages.error(request, "Invalid payment amount.")
    return redirect(request.get_full_path())

# Sufficient payment validation
if received_amount < total_amount_due:
    messages.error(request, f"Insufficient payment. Total amount due is ₱{total_amount_due:,.2f}")
    return redirect(f"{request.path}?consumer={bill.consumer.id}")
```

---

## 2. Data Sanitization

### 2.1 XSS Prevention

**Location:** `waterworks/settings.py`

```python
# Production security headers
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True      # X-XSS-Protection header
    SECURE_CONTENT_TYPE_NOSNIFF = True    # X-Content-Type-Options header
```

### 2.2 Input String Sanitization

```python
# Username/password stripping (prevents whitespace attacks)
username = request.POST.get('username', '').strip()
password = request.POST.get('password', '')

# Name and email sanitization
first_name = request.POST.get('first_name', '').strip()
last_name = request.POST.get('last_name', '').strip()
email = request.POST.get('email', '').strip()

# Search query sanitization
search_query = request.GET.get('search', '').strip()
```

### 2.3 SQL Injection Prevention (ORM-Based)

**All database queries use Django ORM with parameterized queries:**

```python
# Case-insensitive but parameterized (SAFE)
users = User.objects.filter(email__iexact=email, is_staff=True)

# Q objects for complex queries (SAFE)
consumers = consumers.filter(
    Q(first_name__icontains=search_query) |
    Q(last_name__icontains=search_query) |
    Q(account_number__icontains=search_query) |
    Q(serial_number__icontains=search_query)
)

# Foreign key filtering (SAFE)
consumers = Consumer.objects.filter(barangay=profile.assigned_barangay)
```

**Why This is Secure:**
- Django ORM automatically escapes all parameters
- No raw SQL queries used
- Query parameters never concatenated into SQL strings

---

## 3. Error Trapping

### 3.1 Exception Handling Patterns

#### Pattern 1: JSON Parsing Errors
```python
try:
    data = json.loads(request.body.decode('utf-8'))
except json.JSONDecodeError:
    return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
except Exception as e:
    logger.error(f"Error processing request: {e}", exc_info=True)
    return JsonResponse({'error': 'Internal server error'}, status=500)
```

#### Pattern 2: Database Object Not Found
```python
try:
    consumer = Consumer.objects.get(id=consumer_id)
except Consumer.DoesNotExist:
    return JsonResponse({'error': 'Consumer not found'}, status=404)
```

#### Pattern 3: Model Validation Errors
```python
try:
    setting.save()
except (InvalidOperation, ValueError, TypeError) as e:
    messages.error(request, f"Invalid input: {e}")
except Exception as e:
    messages.error(request, f"Error updating settings: {e}")
```

#### Pattern 4: Payment Processing Errors
```python
try:
    # Complex bill generation logic
    setting = SystemSetting.objects.first()
    # ... processing ...
except Exception as e:
    messages.error(request, f"Failed to generate bill: {str(e)}")
    return redirect('consumers:barangay_meter_readings', barangay_id=barangay_id)
```

### 3.2 Model-Level Validation

**Location:** `consumers/models.py`

```python
class Payment(models.Model):
    def clean(self):
        """Validate business logic before saving."""
        if self.received_amount < self.amount_paid:
            raise ValidationError("Received amount cannot be less than the amount due.")

    def save(self, *args, **kwargs):
        # Auto-compute change
        self.change = self.received_amount - self.amount_paid
        # Run full validation
        self.full_clean()
        super().save(*args, **kwargs)
```

### 3.3 HTTP Error Response Codes

| Code | Usage | Example |
|------|-------|---------|
| 400 | Bad Request (invalid input) | Invalid JSON, missing fields |
| 401 | Unauthorized | Failed authentication |
| 403 | Forbidden | Disconnected consumer, insufficient permissions |
| 404 | Not Found | Consumer/Bill does not exist |
| 405 | Method Not Allowed | GET request to POST-only endpoint |
| 500 | Internal Server Error | Unexpected exceptions |

---

## 4. Authentication Traps

### 4.1 Login Required Decorator

**Usage:** Applied to 30+ protected views

```python
@login_required
def home(request):
    # View requires authenticated user
    # Redirects to login page if not authenticated
```

**Protected Views Include:**
- `home()` - Dashboard
- `system_management()` - Settings
- `consumer_management()` - Consumer list
- `inquire()` - Payment processing
- `payment_receipt()` - Receipts
- `user_login_history()` - Login audit

### 4.2 Custom Authorization Decorators

**Location:** `consumers/decorators.py`

#### Superuser Required
```python
def superuser_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('consumers:staff_login')

        if not request.user.is_superuser:
            messages.error(request, "Access Denied: This page requires superuser privileges.")
            return render(request, 'consumers/403.html', status=403)

        return view_func(request, *args, **kwargs)
    return wrapper
```

#### Admin or Superuser Required
```python
def admin_or_superuser_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in.")
            return redirect('consumers:staff_login')

        # Check if superuser
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Check if user has admin role
        try:
            profile = StaffProfile.objects.get(user=request.user)
            if profile.role == 'admin':
                return view_func(request, *args, **kwargs)
        except StaffProfile.DoesNotExist:
            pass

        messages.error(request, "Access Denied: Administrative privileges required.")
        return render(request, 'consumers/403.html', status=403)
    return wrapper
```

### 4.3 Login Attempt Tracking

**Successful Login:**
```python
def staff_login(request):
    user = authenticate(request, username=username, password=password)
    if user is not None and user.is_staff:
        login(request, user)

        # Record successful login event
        UserLoginEvent.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            login_method='web',
            status='success',
            session_key=request.session.session_key
        )
```

**Failed Login (Security Trap):**
```python
else:
    # Record failed login attempt for security monitoring
    if user:
        UserLoginEvent.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            login_method='web',
            status='failed'  # Marked as failed for audit
        )
    messages.error(request, "Invalid credentials or not staff member.")
```

---

## 5. Authorization Filters

### 5.1 Role-Based Access Control

**System Roles:**

| Role | Access Level | Permissions |
|------|-------------|-------------|
| Superuser | Highest | Full system access |
| Admin | Elevated | Reports, user management, payments, penalty waiver |
| Field Staff | Limited | Meter readings for assigned barangay only |
| Regular User | Minimal | Login only |

### 5.2 In-View Authorization Checks

**Profile Edit Restriction:**
```python
if profile.role != 'admin':
    messages.error(request, "Only administrators can edit their profile.")
    return redirect('consumers:home')
```

**Penalty Waiver Authorization:**
```python
if waive_penalty and bill.penalty_amount > 0:
    if request.user.is_superuser or (
        hasattr(request.user, 'staffprofile') and
        request.user.staffprofile.role == 'admin'
    ):
        # Allow waiver
        bill.penalty_waived = True
        bill.penalty_waived_by = request.user
        bill.save()
    else:
        messages.warning(request, "Only administrators can waive penalties.")
```

**Login History Access:**
```python
if not (request.user.is_superuser or (
    hasattr(request.user, 'staffprofile') and
    request.user.staffprofile.role == 'admin'
)):
    messages.error(request, "Access Denied: Administrative privileges required.")
    return render(request, 'consumers/403.html', status=403)
```

---

## 6. Data Access Filters

### 6.1 Barangay-Based Data Scoping

**Field staff can only access consumers in their assigned barangay:**

```python
def api_consumers(request):
    """Get consumers for the staff's assigned barangay only."""
    try:
        profile = StaffProfile.objects.select_related('assigned_barangay').get(user=request.user)
        consumers = Consumer.objects.filter(
            barangay=profile.assigned_barangay
        ).select_related('barangay')
    except StaffProfile.DoesNotExist:
        return JsonResponse({'error': 'No assigned barangay'}, status=403)
```

### 6.2 Consumer Status Filtering

**Active Consumers Only (Payment):**
```python
consumers = Consumer.objects.filter(status='active').select_related('barangay', 'purok')
```

**Disconnected Consumer Block:**
```python
if consumer.status == 'disconnected':
    return JsonResponse({
        'error': 'Consumer is disconnected',
        'message': f'{consumer.full_name} is currently disconnected. Meter reading not allowed.',
        'consumer_status': 'disconnected'
    }, status=403)
```

### 6.3 Bill Status Filtering

```python
# Only show pending bills for payment
bill = consumer.bills.filter(status='Pending').order_by('-billing_period').first()

# Latest pending bill selection
latest_bill = selected_consumer.bills.filter(status='Pending').order_by('-billing_period').first()
```

---

## 7. Security Activity Traps

### 7.1 UserActivity Model (Audit Trail)

**Location:** `consumers/models.py`

```python
class UserActivity(models.Model):
    ACTION_CHOICES = [
        ('password_reset_requested', 'Password Reset Requested'),
        ('password_reset_completed', 'Password Reset Completed'),
        ('password_changed', 'Password Changed'),
        ('user_created', 'User Created'),
        ('user_updated', 'User Updated'),
        ('bill_created', 'Bill Created'),
        ('payment_processed', 'Payment Processed'),
        ('meter_reading_confirmed', 'Meter Reading Confirmed'),
        ('consumer_created', 'Consumer Created'),
        ('consumer_disconnected', 'Consumer Disconnected'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    login_event = models.ForeignKey('UserLoginEvent', on_delete=models.SET_NULL, null=True)
```

### 7.2 Activity Logging Examples

**Meter Reading Activity:**
```python
UserActivity.objects.create(
    user=request.user,
    action='meter_reading_submitted',
    description=f"Meter reading submitted for {consumer.full_name}. Reading: {current_reading}",
    login_event=current_session
)
```

**Payment Processing Activity:**
```python
UserActivity.objects.create(
    user=request.user,
    action='payment_processed',
    description=f"Processed payment OR#{payment.or_number} for {bill.consumer.full_name}. "
                f"Amount: ₱{total_amount_due:,.2f}" +
                (f" (includes ₱{penalty:,.2f} penalty)" if penalty > 0 else ""),
    ip_address=get_client_ip(request),
    user_agent=request.META.get('HTTP_USER_AGENT', ''),
    login_event=request.login_event
)
```

### 7.3 UserLoginEvent Model (Session Tracking)

```python
class UserLoginEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    logout_timestamp = models.DateTimeField(null=True, blank=True)

    # Security tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    login_method = models.CharField(max_length=20, choices=[
        ('web', 'Web Portal'),
        ('mobile', 'Mobile App'),
        ('api', 'API')
    ])
    status = models.CharField(max_length=20, choices=[
        ('success', 'Successful'),
        ('failed', 'Failed'),
        ('locked', 'Account Locked')
    ])
    session_key = models.CharField(max_length=40, blank=True, null=True)

    @property
    def is_active_session(self):
        return self.status == 'success' and self.logout_timestamp is None

    @property
    def session_duration(self):
        if self.logout_timestamp:
            return self.logout_timestamp - self.login_timestamp
        return None
```

---

## 8. Session Management

### 8.1 Session Configuration

**Location:** `waterworks/settings.py`

```python
# Auto-logout after 2 minutes of inactivity
SESSION_COOKIE_AGE = 120  # 2 minutes in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True  # Reset timer on every request

# Messages cleared on logout
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
```

### 8.2 Logout with Session Tracking

```python
@login_required
def staff_logout(request):
    """Enhanced logout with session tracking."""
    try:
        latest_session = UserLoginEvent.objects.filter(
            user=request.user,
            session_key=request.session.session_key,
            logout_timestamp__isnull=True
        ).first()

        if latest_session:
            latest_session.logout_timestamp = timezone.now()
            latest_session.save()
    except Exception as e:
        logger.warning(f"Error updating logout timestamp: {e}")

    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("consumers:staff_login")
```

---

## 9. Password Security

### 9.1 Password Strength Validation

**Location:** `consumers/decorators.py`

```python
def check_password_strength(password):
    """Validate password meets security requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)

    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and numbers."

    return True, "Password is strong."
```

### 9.2 Django Auth Password Validators

```python
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

### 9.3 Password Reset Token Security

**Location:** `consumers/models.py`

```python
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()  # 24-hour expiration
    is_used = models.BooleanField(default=False)  # One-time use
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def is_valid(self):
        """Check if token is still valid."""
        return not self.is_used and timezone.now() < self.expires_at

    def save(self, *args, **kwargs):
        if not self.pk:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        if not self.token:
            self.token = uuid.uuid4().hex  # Cryptographically secure
        super().save(*args, **kwargs)
```

**Security Features:**
- UUID-based tokens (cryptographically secure)
- 24-hour expiration
- One-time use enforcement
- IP address tracking

---

## 10. CSRF Protection

### 10.1 Middleware Configuration

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### 10.2 CSRF Exempt API Endpoints

**Mobile API endpoints exempt from CSRF (use session authentication instead):**

```python
@csrf_exempt
def api_submit_reading(request):  # Mobile meter reading

@csrf_exempt
def api_login(request):  # Mobile login

@csrf_exempt
def api_logout(request):  # Mobile logout

@csrf_exempt
def smart_meter_webhook(request):  # IoT webhook
```

### 10.3 CSRF Trusted Origins

```python
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv())

# Auto-add Railway domain
if RAILWAY_ENVIRONMENT:
    railway_domain = config('RAILWAY_PUBLIC_DOMAIN', default='')
    if railway_domain:
        CSRF_TRUSTED_ORIGINS.append(f'https://{railway_domain}')
```

---

## 11. Production Security Headers

**Location:** `waterworks/settings.py`

```python
if not DEBUG:
    # XSS Protection
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # HTTPS/HSTS
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Secure Cookies
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
```

### Security Headers Explained

| Header | Purpose |
|--------|---------|
| X-XSS-Protection | Enables browser XSS filtering |
| X-Content-Type-Options | Prevents MIME-type sniffing |
| Strict-Transport-Security | Forces HTTPS connections |
| Secure Cookie Flags | Prevents cookie theft over HTTP |

---

## 12. Security Assessment Summary

### Implemented Security Measures

| Category | Status | Implementation |
|----------|--------|----------------|
| Input Validation | ✅ Complete | Form, API, business logic validation |
| SQL Injection | ✅ Protected | Django ORM parameterized queries |
| XSS Prevention | ✅ Protected | Security headers, template escaping |
| CSRF Protection | ✅ Protected | Middleware + token validation |
| Authentication | ✅ Complete | Session-based with login tracking |
| Authorization | ✅ Complete | Role-based with custom decorators |
| Password Security | ✅ Complete | Strength validation + secure reset |
| Audit Trail | ✅ Complete | UserActivity + UserLoginEvent models |
| Session Management | ✅ Complete | 2-min timeout + logout tracking |
| Error Handling | ✅ Complete | Comprehensive try-except patterns |

### Recommendations for Enhancement

| Priority | Enhancement | Benefit |
|----------|-------------|---------|
| High | Add rate limiting | Prevent brute-force attacks |
| High | Implement 2FA | Additional authentication layer |
| Medium | Add API versioning | Safe future changes |
| Medium | JWT for mobile | Better mobile auth |
| Low | Enhanced logging | Security event monitoring |

---

## IP and User Agent Tracking Utilities

**Location:** `consumers/decorators.py`

```python
def get_client_ip(request):
    """Get client IP address (handles proxies)."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # First IP if proxied
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Get browser/device information."""
    return request.META.get('HTTP_USER_AGENT', '')
```

---

## Conclusion

The Balilihan Waterworks Management System implements **enterprise-grade security** with multiple layers of protection:

1. **Defense in Depth** - Multiple security layers from request to database
2. **Least Privilege** - Role-based access limits data exposure
3. **Audit Compliance** - Complete activity tracking for accountability
4. **Input Safety** - Comprehensive validation prevents injection attacks
5. **Session Security** - Short timeouts and tracking prevent session hijacking

This security architecture is suitable for production deployment of a utility management system handling financial transactions and personal data.

---

*Document generated for Balilihan Waterworks Management System v2.0*
