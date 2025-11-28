# consumers/models.py
from django.db import models
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid
from django.contrib.auth.models import User



# Enhanced Model to track user login events with security features
class UserLoginEvent(models.Model):
    """
    Stores comprehensive information about user login attempts and sessions.
    Includes security tracking features for audit and monitoring purposes.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="The user who logged in.")
    login_timestamp = models.DateTimeField(default=timezone.now, help_text="The date and time the user logged in.", db_index=True)

    # Security tracking fields
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP address of the login attempt")
    user_agent = models.TextField(blank=True, help_text="Browser/device information")
    login_method = models.CharField(max_length=20, default='web', choices=[
        ('web', 'Web Portal'),
        ('mobile', 'Mobile App'),
        ('api', 'API')
    ], help_text="Method used to login")
    status = models.CharField(max_length=20, default='success', choices=[
        ('success', 'Successful'),
        ('failed', 'Failed'),
        ('locked', 'Account Locked')
    ], help_text="Login attempt status")

    # Session tracking
    session_key = models.CharField(max_length=40, blank=True, null=True, help_text="Django session key")
    logout_timestamp = models.DateTimeField(null=True, blank=True, help_text="When the user logged out")

    class Meta:
        ordering = ['-login_timestamp']
        indexes = [
            models.Index(fields=['login_timestamp']),
            models.Index(fields=['user', 'login_timestamp']),
            models.Index(fields=['status']),
        ]
        verbose_name = "User Login Event"
        verbose_name_plural = "User Login Events"

    def __str__(self):
        return f"{self.user.username} - {self.status} - {self.login_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    @property
    def session_duration(self):
        """Calculate session duration if logged out"""
        if self.logout_timestamp:
            return self.logout_timestamp - self.login_timestamp
        return None

    @property
    def session_duration_formatted(self):
        """Return formatted session duration string"""
        if self.logout_timestamp:
            duration = self.logout_timestamp - self.login_timestamp
            total_seconds = int(duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            if hours > 0:
                return f"{hours}h {minutes}m"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        return None

    @property
    def is_active_session(self):
        """Check if session is still active"""
        return self.status == 'success' and self.logout_timestamp is None

    @property
    def activities_count(self):
        """Get count of activities during this session"""
        return self.activities.count() if hasattr(self, 'activities') else 0

    def get_session_activities(self):
        """Get all activities that occurred during this login session"""
        if hasattr(self, 'activities'):
            return self.activities.all()
        return []


class LoginAttemptTracker(models.Model):
    """
    Tracks login attempts for rate limiting and account lockout.
    Implements brute-force protection.
    """
    ip_address = models.GenericIPAddressField(db_index=True)
    username = models.CharField(max_length=150, db_index=True)
    attempt_time = models.DateTimeField(default=timezone.now, db_index=True)
    was_successful = models.BooleanField(default=False)

    class Meta:
        ordering = ['-attempt_time']
        indexes = [
            models.Index(fields=['ip_address', 'attempt_time']),
            models.Index(fields=['username', 'attempt_time']),
        ]
        verbose_name = "Login Attempt"
        verbose_name_plural = "Login Attempts"

    def __str__(self):
        status = "Success" if self.was_successful else "Failed"
        return f"{self.username} from {self.ip_address} - {status} at {self.attempt_time}"

    @classmethod
    def get_recent_failed_attempts(cls, ip_address=None, username=None, minutes=15):
        """Get count of failed attempts in the last N minutes."""
        cutoff_time = timezone.now() - timezone.timedelta(minutes=minutes)
        queryset = cls.objects.filter(
            attempt_time__gte=cutoff_time,
            was_successful=False
        )
        if ip_address:
            queryset = queryset.filter(ip_address=ip_address)
        if username:
            queryset = queryset.filter(username=username)
        return queryset.count()

    @classmethod
    def cleanup_old_attempts(cls, hours=24):
        """Remove attempts older than N hours."""
        cutoff_time = timezone.now() - timezone.timedelta(hours=hours)
        deleted, _ = cls.objects.filter(attempt_time__lt=cutoff_time).delete()
        return deleted


class AccountLockout(models.Model):
    """
    Tracks account lockouts after too many failed login attempts.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=150, db_index=True)
    ip_address = models.GenericIPAddressField(db_index=True)
    locked_at = models.DateTimeField(default=timezone.now)
    locked_until = models.DateTimeField()
    reason = models.CharField(max_length=255, default="Too many failed login attempts")
    failed_attempts = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True, help_text="Is this lockout still in effect?")

    class Meta:
        ordering = ['-locked_at']
        indexes = [
            models.Index(fields=['username', 'is_active']),
            models.Index(fields=['ip_address', 'is_active']),
        ]
        verbose_name = "Account Lockout"
        verbose_name_plural = "Account Lockouts"

    def __str__(self):
        return f"{self.username} locked until {self.locked_until}"

    @property
    def is_locked(self):
        """Check if lockout is still in effect."""
        if not self.is_active:
            return False
        if timezone.now() >= self.locked_until:
            self.is_active = False
            self.save(update_fields=['is_active'])
            return False
        return True

    @property
    def time_remaining(self):
        """Get remaining lockout time in seconds."""
        if not self.is_locked:
            return 0
        return max(0, int((self.locked_until - timezone.now()).total_seconds()))

    @property
    def time_remaining_formatted(self):
        """Get human-readable remaining time."""
        seconds = self.time_remaining
        if seconds <= 0:
            return "Unlocked"
        minutes, secs = divmod(seconds, 60)
        if minutes > 0:
            return f"{minutes}m {secs}s"
        return f"{secs}s"

    @classmethod
    def is_account_locked(cls, username=None, ip_address=None):
        """Check if account or IP is currently locked."""
        now = timezone.now()
        queryset = cls.objects.filter(is_active=True, locked_until__gt=now)

        if username:
            lockout = queryset.filter(username=username).first()
            if lockout:
                return True, lockout

        if ip_address:
            lockout = queryset.filter(ip_address=ip_address).first()
            if lockout:
                return True, lockout

        return False, None

    @classmethod
    def create_lockout(cls, username, ip_address, failed_attempts, lockout_minutes=15):
        """Create a new lockout record."""
        user = None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            pass

        lockout = cls.objects.create(
            user=user,
            username=username,
            ip_address=ip_address,
            locked_until=timezone.now() + timezone.timedelta(minutes=lockout_minutes),
            failed_attempts=failed_attempts
        )
        return lockout


class TwoFactorAuth(models.Model):
    """
    Two-Factor Authentication settings for admin accounts.
    Uses TOTP (Time-based One-Time Password).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='two_factor')
    secret_key = models.CharField(max_length=32, help_text="Base32 encoded secret key")
    is_enabled = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False, help_text="Has the user verified their 2FA setup?")
    backup_codes = models.TextField(blank=True, help_text="JSON list of backup codes")
    created_at = models.DateTimeField(default=timezone.now)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Two-Factor Authentication"
        verbose_name_plural = "Two-Factor Authentications"

    def __str__(self):
        status = "Enabled" if self.is_enabled else "Disabled"
        return f"{self.user.username} - 2FA {status}"

    def generate_secret(self):
        """Generate a new secret key."""
        import secrets
        import base64
        # Generate 20 random bytes and encode as base32
        random_bytes = secrets.token_bytes(20)
        self.secret_key = base64.b32encode(random_bytes).decode('utf-8')
        return self.secret_key

    def get_totp_uri(self):
        """Generate TOTP URI for QR code."""
        return f"otpauth://totp/Waterworks:{self.user.username}?secret={self.secret_key}&issuer=Balilihan%20Waterworks"

    def verify_token(self, token):
        """Verify a TOTP token."""
        import hmac
        import struct
        import time
        import base64
        import hashlib

        try:
            token = int(token)
        except (ValueError, TypeError):
            return False

        # Get current time step (30-second intervals)
        current_time = int(time.time())

        # Check current and adjacent time windows for clock drift
        for time_offset in [-1, 0, 1]:
            time_step = (current_time // 30) + time_offset
            expected_token = self._generate_totp(time_step)
            if token == expected_token:
                self.last_used_at = timezone.now()
                self.save(update_fields=['last_used_at'])
                return True
        return False

    def _generate_totp(self, time_step):
        """Generate TOTP for a given time step."""
        import hmac
        import struct
        import base64
        import hashlib

        key = base64.b32decode(self.secret_key, casefold=True)
        msg = struct.pack('>Q', time_step)
        hmac_hash = hmac.new(key, msg, hashlib.sha1).digest()
        offset = hmac_hash[-1] & 0x0f
        code = struct.unpack('>I', hmac_hash[offset:offset + 4])[0]
        code = (code & 0x7fffffff) % 1000000
        return code

    def generate_backup_codes(self, count=8):
        """Generate backup codes for account recovery."""
        import secrets
        import json
        codes = [secrets.token_hex(4).upper() for _ in range(count)]
        self.backup_codes = json.dumps(codes)
        self.save(update_fields=['backup_codes'])
        return codes

    def verify_backup_code(self, code):
        """Verify and consume a backup code."""
        import json
        if not self.backup_codes:
            return False

        codes = json.loads(self.backup_codes)
        code = code.upper().replace('-', '').replace(' ', '')

        if code in codes:
            codes.remove(code)
            self.backup_codes = json.dumps(codes)
            self.save(update_fields=['backup_codes'])
            return True
        return False

    @property
    def remaining_backup_codes(self):
        """Get count of remaining backup codes."""
        import json
        if not self.backup_codes:
            return 0
        return len(json.loads(self.backup_codes))


class PasswordResetToken(models.Model):
    """
    Stores password reset tokens for secure password recovery.
    Tokens expire after 24 hours for security.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Password Reset Token"
        verbose_name_plural = "Password Reset Tokens"

    def __str__(self):
        return f"{self.user.username} - {self.token[:10]}... - {'Used' if self.is_used else 'Active'}"

    def is_valid(self):
        """Check if token is still valid (not expired and not used)"""
        return not self.is_used and timezone.now() < self.expires_at

    def save(self, *args, **kwargs):
        if not self.pk:  # Only set expires_at on creation
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        if not self.token:
            self.token = uuid.uuid4().hex
        super().save(*args, **kwargs)


class UserActivity(models.Model):
    """
    Tracks important user activities for audit and security purposes.
    """
    ACTION_CHOICES = [
        ('password_reset_requested', 'Password Reset Requested'),
        ('password_reset_completed', 'Password Reset Completed'),
        ('password_changed', 'Password Changed'),
        ('user_created', 'User Created'),
        ('user_updated', 'User Updated'),
        ('user_deleted', 'User Deleted'),
        ('bill_created', 'Bill Created'),
        ('payment_processed', 'Payment Processed'),
        ('meter_reading_confirmed', 'Meter Reading Confirmed'),
        ('meter_reading_submitted', 'Meter Reading Submitted'),
        ('consumer_created', 'Consumer Created'),
        ('consumer_updated', 'Consumer Updated'),
        ('consumer_disconnected', 'Consumer Disconnected'),
        ('consumer_reconnected', 'Consumer Reconnected'),
        ('system_settings_updated', 'System Settings Updated'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='targeted_activities')
    login_event = models.ForeignKey('UserLoginEvent', on_delete=models.SET_NULL, null=True, blank=True, related_name='activities', help_text="The login session during which this activity occurred")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "User Activity"
        verbose_name_plural = "User Activities"

    def __str__(self):
        return f"{self.user.username if self.user else 'System'} - {self.get_action_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


# ... (rest of your existing models) ...

class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    assigned_barangay = models.ForeignKey('Barangay', on_delete=models.CASCADE, null=True, blank=True, help_text="Required for field staff only")
    role = models.CharField(max_length=20, default='field_staff')  # field_staff, admin
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True, help_text="Profile photo for admin users")

    def __str__(self):
        if self.assigned_barangay:
            return f"{self.user.username} - {self.assigned_barangay.name}"
        return f"{self.user.username} - {self.role.title()}"

    @property
    def role_display(self):
        """Return a short display name for the role"""
        role_map = {
            'admin': 'Admin',
            'field_staff': 'Staff',
        }
        return role_map.get(self.role, 'Staff')

# ----------------------------
# Choice Fields
# ----------------------------
GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]

CIVIL_STATUS_CHOICES = [
    ('Single', 'Single'),
    ('Married', 'Married'),
    ('Widowed', 'Widowed'),
    ('Divorced', 'Divorced'),
]

USAGE_TYPE_CHOICES = [
    ('Residential', 'Residential'),
    ('Commercial', 'Commercial'),
]

STATUS_CHOICES = [
    ('active', 'Connected'),
    ('disconnected', 'Disconnected'),
]

BILL_STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Paid', 'Paid'),
    ('Overdue', 'Overdue'),
]

# ----------------------------
# Dynamic Reference Models
# ----------------------------
class Barangay(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Purok(models.Model):
    name = models.CharField(max_length=100)
    barangay = models.ForeignKey(Barangay, on_delete=models.CASCADE, related_name='puroks')

    def __str__(self):
        return f"{self.name} ({self.barangay.name})"


class MeterBrand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# consumers/models.py (Relevant part updated)
from django.db import models
# ... (your other imports) ...

# ----------------------------
# Main Consumer Model
# ----------------------------
class Consumer(models.Model):
    # Personal Information
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15)

    # Household Information
    civil_status = models.CharField(max_length=10, choices=CIVIL_STATUS_CHOICES)
    spouse_name = models.CharField(max_length=50, blank=True, null=True)
    barangay = models.ForeignKey(Barangay, on_delete=models.SET_NULL, null=True)
    purok = models.ForeignKey(Purok, on_delete=models.SET_NULL, null=True)
    household_number = models.CharField(max_length=20)

    # Water Meter Information
    usage_type = models.CharField(max_length=20, choices=USAGE_TYPE_CHOICES)
    meter_brand = models.ForeignKey(MeterBrand, on_delete=models.SET_NULL, null=True)
    serial_number = models.CharField(max_length=50)
    first_reading = models.IntegerField()
    registration_date = models.DateField()

    # 🔑 Auto-generated Account Number
    account_number = models.CharField(max_length=20, unique=True, blank=True)

    # Status & Disconnection
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Connected or Disconnected consumer"
    )
    disconnect_reason = models.CharField(max_length=200, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ========================
    # Properties
    # ========================
    @property
    def full_name(self):
        """Returns the full name with optional middle name."""
        middle = f" {self.middle_name}" if self.middle_name else ""
        return f"{self.first_name}{middle} {self.last_name}".strip()

    @property
    def is_delinquent(self):
        """Check if consumer has overdue unpaid bills."""
        from django.utils import timezone
        return self.bills.filter(
            status='Pending',
            due_date__lt=timezone.now().date()
        ).exists()

    @property
    def pending_bills_count(self):
        """Count of pending bills for this consumer."""
        return self.bills.filter(status='Pending').count()

    @property
    def overdue_bills_count(self):
        """Count of overdue unpaid bills."""
        from django.utils import timezone
        return self.bills.filter(
            status='Pending',
            due_date__lt=timezone.now().date()
        ).count()

    # ========================
    # Methods
    # ========================
    def save(self, *args, **kwargs):
        # Auto-generate Account Number if not set
        # Format: 5-digit sequential (00001-99999)
        # Example: 00001, 00002, 00003, etc.
        if not self.account_number:
            # Find the highest existing account number
            latest_consumer = Consumer.objects.exclude(
                pk=self.pk  # Exclude self if updating
            ).exclude(
                account_number=''  # Exclude empty account numbers
            ).order_by('-account_number').first()

            if latest_consumer and latest_consumer.account_number.isdigit():
                # Get next sequence number
                last_num = int(latest_consumer.account_number)
                new_num = last_num + 1
            else:
                # Start from 1 if no consumers exist
                new_num = 1

            # Generate 5-digit Account Number (00001-99999)
            self.account_number = f'{new_num:05d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.account_number} - {self.full_name}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status'], name='consumer_status_idx'),
            models.Index(fields=['barangay', 'status'], name='consumer_brgy_status_idx'),
        ]
        permissions = [
            # Consumer Management Permissions
            ("view_consumer_data", "Can view consumer data (read-only)"),
            ("edit_consumer_data", "Can edit consumer information"),
            ("create_consumer_account", "Can create new consumers"),
            ("remove_consumer", "Can delete/remove consumers"),
            ("disconnect_consumer", "Can disconnect/reconnect consumers"),

            # Billing Permissions
            ("manage_billing", "Can manage billing (create bills, process payments)"),
            ("view_billing", "Can view billing records"),

            # Reports Permissions
            ("generate_reports", "Can generate and download reports"),
            ("view_reports", "Can view reports"),

            # User Management Permissions
            ("manage_users", "Can manage user accounts"),

            # System Settings Permissions
            ("manage_settings", "Can access system settings"),
        ]

# ----------------------------
# Meter Reading Model
# ----------------------------
class MeterReading(models.Model):
    consumer = models.ForeignKey(
        Consumer, 
        on_delete=models.CASCADE, 
        related_name='meter_readings'
    )
    reading_date = models.DateField()
    reading_value = models.IntegerField()  # cumulative meter value
    source = models.CharField(max_length=50, default='manual')
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-reading_date', '-created_at']
        indexes = [
            models.Index(fields=['consumer', 'is_confirmed'], name='reading_consumer_conf_idx'),
            models.Index(fields=['reading_date'], name='reading_date_idx'),
            models.Index(fields=['consumer', 'is_confirmed', '-reading_date'], name='reading_latest_idx'),
        ]
        # Removed unique_together to allow multiple readings on same date for testing/demo

    def __str__(self):
        return f"{self.consumer} - {self.reading_value} on {self.reading_date}"


# ----------------------------
# Bill Model (Final Version)
# ----------------------------
class Bill(models.Model):
    consumer = models.ForeignKey(
        Consumer,
        on_delete=models.CASCADE,
        related_name='bills'
    )

    previous_reading = models.ForeignKey(
        'MeterReading',
        on_delete=models.PROTECT,
        related_name='bills_as_previous',
        null=True,
        blank=True,
        help_text="The meter reading from the previous billing cycle"
    )

    current_reading = models.ForeignKey(
        'MeterReading',
        on_delete=models.PROTECT,
        related_name='bills_as_current',
        help_text="The latest meter reading used for this bill"
    )

    billing_period = models.DateField(help_text="First day of the billing month (e.g., 2025-10-01)")
    due_date = models.DateField()

    consumption = models.PositiveIntegerField(help_text="in cubic meters")
    rate_per_cubic = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('22.50'))
    fixed_charge = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('50.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # -------------------------
    # PENALTY TRACKING FIELDS
    # -------------------------
    penalty_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Calculated penalty amount for late payment"
    )
    penalty_applied_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when penalty was first applied"
    )
    penalty_waived = models.BooleanField(
        default=False,
        help_text="Whether the penalty has been waived by admin"
    )
    penalty_waived_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='waived_penalties',
        help_text="Admin who waived the penalty"
    )
    penalty_waived_reason = models.CharField(
        max_length=255,
        blank=True,
        help_text="Reason for waiving the penalty"
    )
    penalty_waived_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when penalty was waived"
    )
    days_overdue = models.IntegerField(
        default=0,
        help_text="Number of days the bill is/was overdue"
    )

    status = models.CharField(
        max_length=20,
        choices=BILL_STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-billing_period']
        indexes = [
            models.Index(fields=['consumer', 'status'], name='bill_consumer_status_idx'),
            models.Index(fields=['due_date'], name='bill_due_date_idx'),
            models.Index(fields=['status', 'due_date'], name='bill_status_due_idx'),
        ]
        verbose_name = "Utility Bill"
        verbose_name_plural = "Utility Bills"

    @property
    def is_overdue(self):
        """Check if bill is overdue (past due date and not paid)"""
        if self.status == 'Paid':
            return False
        return timezone.now().date() > self.due_date

    @property
    def current_days_overdue(self):
        """Calculate current days overdue"""
        if self.status == 'Paid' or not self.is_overdue:
            return 0
        return (timezone.now().date() - self.due_date).days

    @property
    def effective_penalty(self):
        """Return the effective penalty (0 if waived)"""
        if self.penalty_waived:
            return Decimal('0.00')
        return self.penalty_amount

    @property
    def total_amount_due(self):
        """Total amount including penalty (if not waived)"""
        return self.total_amount + self.effective_penalty

    def __str__(self):
        penalty_str = f" + ₱{self.penalty_amount} penalty" if self.penalty_amount > 0 and not self.penalty_waived else ""
        return f"Bill for {self.consumer} | {self.billing_period.strftime('%B %Y')} | ₱{self.total_amount}{penalty_str} ({self.status})"


# ----------------------------
# consumers/models.py
from django.db import models
from decimal import Decimal # Import Decimal

# ... (other imports remain the same) ...

# ============================================================================
# SYSTEM SETTINGS MODEL (Singleton)
# ============================================================================
# Configures billing rates, reading schedule, and billing cycle.
#
# BILLING WORKFLOW:
# 1. Reading Period: Field staff submit readings (reading_start_day to reading_end_day)
# 2. Admin Confirmation: Admin reviews and confirms readings
# 3. Bill Generation: Bill created instantly when reading is confirmed
# 4. Payment Due: Consumer pays before due_day_of_month
#
# FOR TESTING: You can test the full flow anytime - bills are generated
# instantly when admin confirms a reading, regardless of schedule settings.
# ============================================================================
class SystemSetting(models.Model):
    """
    System-wide configuration for water rates, reading schedule, billing, and penalties.

    The schedule fields help organize the monthly billing cycle:
    - Reading period: When field staff should submit meter readings
    - Billing period: The billing cycle start date shown on bills
    - Due date: Payment deadline shown on bills
    - Penalty: Late payment charges applied after due date

    Bills are created INSTANTLY when admin confirms a reading.

    TIERED RATE STRUCTURE:
    - Tier 1 (1-5 m³): Minimum charge (flat rate)
    - Tier 2 (6-10 m³): Rate per cubic meter
    - Tier 3 (11-20 m³): Rate per cubic meter
    - Tier 4 (21-50 m³): Rate per cubic meter
    - Tier 5 (51+ m³): Rate per cubic meter
    """
    # -------------------------
    # RESIDENTIAL TIERED RATES
    # -------------------------
    # Tier 1: 1-5 cubic meters (minimum charge)
    residential_minimum_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('75.00'),
        help_text="Minimum charge for 1-5 m³ consumption (₱)"
    )
    # Tier 2: 6-10 cubic meters
    residential_tier2_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('15.00'),
        help_text="Rate for 6-10 m³ consumption (₱/m³)"
    )
    # Tier 3: 11-20 cubic meters
    residential_tier3_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('16.00'),
        help_text="Rate for 11-20 m³ consumption (₱/m³)"
    )
    # Tier 4: 21-50 cubic meters
    residential_tier4_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('17.00'),
        help_text="Rate for 21-50 m³ consumption (₱/m³)"
    )
    # Tier 5: 51+ cubic meters
    residential_tier5_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('18.00'),
        help_text="Rate for 51+ m³ consumption (₱/m³)"
    )

    # -------------------------
    # COMMERCIAL TIERED RATES
    # -------------------------
    # Tier 1: 1-5 cubic meters (minimum charge)
    commercial_minimum_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('100.00'),
        help_text="Minimum charge for 1-5 m³ consumption (₱)"
    )
    # Tier 2: 6-10 cubic meters
    commercial_tier2_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('18.00'),
        help_text="Rate for 6-10 m³ consumption (₱/m³)"
    )
    # Tier 3: 11-20 cubic meters
    commercial_tier3_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('20.00'),
        help_text="Rate for 11-20 m³ consumption (₱/m³)"
    )
    # Tier 4: 21-50 cubic meters
    commercial_tier4_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('22.00'),
        help_text="Rate for 21-50 m³ consumption (₱/m³)"
    )
    # Tier 5: 51+ cubic meters
    commercial_tier5_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('24.00'),
        help_text="Rate for 51+ m³ consumption (₱/m³)"
    )

    # Legacy fields (kept for backward compatibility, not used in new calculation)
    residential_rate_per_cubic = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('22.50'),
        help_text="[LEGACY] Rate for residential consumers (₱ / m³)"
    )
    commercial_rate_per_cubic = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('25.00'),
        help_text="[LEGACY] Rate for commercial consumers (₱ / m³)"
    )
    fixed_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="[LEGACY] Fixed charge - no longer used with tiered rates"
    )

    # -------------------------
    # READING SCHEDULE
    # -------------------------
    # Defines the window when field staff should submit meter readings
    reading_start_day = models.IntegerField(
        default=1,
        help_text="Day of month when reading period starts (1-28)"
    )
    reading_end_day = models.IntegerField(
        default=10,
        help_text="Day of month when reading period ends (1-28)"
    )

    # -------------------------
    # BILLING SCHEDULE
    # -------------------------
    # These affect the dates displayed on generated bills
    billing_day_of_month = models.IntegerField(
        default=1,
        help_text="Day shown as billing period start on bills (1-28)"
    )
    due_day_of_month = models.IntegerField(
        default=20,
        help_text="Day when payment is due (1-28)"
    )

    # -------------------------
    # PENALTY SETTINGS
    # -------------------------
    PENALTY_TYPE_CHOICES = [
        ('percentage', 'Percentage of Bill'),
        ('fixed', 'Fixed Amount'),
    ]

    penalty_enabled = models.BooleanField(
        default=True,
        help_text="Enable/disable late payment penalties"
    )
    penalty_type = models.CharField(
        max_length=20,
        choices=PENALTY_TYPE_CHOICES,
        default='percentage',
        help_text="Type of penalty calculation"
    )
    penalty_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('25.00'),
        help_text="Penalty rate in percentage (default: 25% of bill amount)"
    )
    fixed_penalty_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('50.00'),
        help_text="Fixed penalty amount in pesos (used if penalty_type is 'fixed')"
    )
    penalty_grace_period_days = models.IntegerField(
        default=0,
        help_text="Number of days after due date before penalty is applied (0 = immediate, penalty starts day after due date)"
    )
    max_penalty_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Maximum penalty cap (0 = no cap, penalty is full percentage of bill)"
    )

    # -------------------------
    # METADATA
    # -------------------------
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Rates: Res ₱{self.residential_rate_per_cubic}, Comm ₱{self.commercial_rate_per_cubic}"

    # Optional: Override save to enforce singleton pattern (only one instance)
    def save(self, *args, **kwargs):
        # Ensure only one instance exists by deleting others before saving
        self.__class__.objects.exclude(id=self.id).delete()
        super().save(*args, **kwargs)

    class Meta:
        # Optional: Add constraints here if needed, e.g., to ensure only one row
        # constraints = [
        #     models.UniqueConstraint(fields=[], name='unique_system_setting_singleton')
        # ]
        # Or just ensure id=1 is always used implicitly as shown in the view
        pass

# ... (rest of your models like Consumer, Barangay, etc.) ...
    
    
class Payment(models.Model):
    bill = models.ForeignKey(
        'Bill',
        on_delete=models.CASCADE,
        related_name='payments',
        help_text="The bill being paid"
    )
    # -------------------------
    # ORIGINAL BILL AMOUNT
    # -------------------------
    original_bill_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Original bill amount before penalty"
    )
    # -------------------------
    # PENALTY INFORMATION
    # -------------------------
    penalty_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Penalty amount included in this payment"
    )
    penalty_waived = models.BooleanField(
        default=False,
        help_text="Whether penalty was waived for this payment"
    )
    days_overdue_at_payment = models.IntegerField(
        default=0,
        help_text="Number of days overdue at the time of payment"
    )
    # -------------------------
    # PAYMENT AMOUNTS
    # -------------------------
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total amount paid (bill + penalty)"
    )
    received_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Cash amount received from the consumer"
    )
    change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Change to return to the consumer"
    )
    or_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Official Receipt number (auto-generated)"
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time of payment"
    )
    # -------------------------
    # PAYMENT PROCESSING INFO
    # -------------------------
    processed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payments',
        help_text="Staff who processed the payment"
    )
    remarks = models.TextField(
        blank=True,
        help_text="Additional notes or remarks about the payment"
    )

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['payment_date'], name='payment_date_idx'),
            models.Index(fields=['bill'], name='payment_bill_idx'),
        ]

    def clean(self):
        """Validate business logic before saving."""
        if self.received_amount < self.amount_paid:
            raise ValidationError("Received amount cannot be less than the amount due.")

    def save(self, *args, **kwargs):
        # Auto-compute change
        self.change = self.received_amount - self.amount_paid

        # Auto-generate OR number if not set (e.g., during initial save)
        if not self.or_number:
            date_str = timezone.now().strftime('%Y%m%d')
            unique_suffix = uuid.uuid4().hex[:6].upper()
            self.or_number = f"OR-{date_str}-{unique_suffix}"

        # Run full validation
        self.full_clean()

        super().save(*args, **kwargs)

    @property
    def total_with_penalty(self):
        """Total amount including any penalty"""
        return self.original_bill_amount + self.penalty_amount

    def __str__(self):
        penalty_info = f" (incl. ₱{self.penalty_amount} penalty)" if self.penalty_amount > 0 else ""
        return f"OR#{self.or_number} - {self.bill.consumer.account_number}{penalty_info}"


# ============================================================================
# NOTIFICATION MODEL - For real-time notifications in header dropdown
# ============================================================================
class Notification(models.Model):
    """
    Stores system notifications for admin/superuser users.
    Used for meter reading alerts, payment notifications, etc.
    """
    NOTIFICATION_TYPES = [
        ('meter_reading', 'Meter Reading Submitted'),
        ('payment', 'Payment Processed'),
        ('bill_generated', 'Bill Generated'),
        ('consumer_registered', 'New Consumer Registered'),
        ('system_alert', 'System Alert'),
    ]

    # Who should see this notification (null = all admins/superusers)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                           help_text="Specific user to notify (null = all admins)")

    # Notification details
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES,
                                       help_text="Type of notification")
    title = models.CharField(max_length=200, help_text="Short notification title")
    message = models.TextField(help_text="Notification message")

    # Related object (for redirects)
    related_object_id = models.IntegerField(null=True, blank=True,
                                          help_text="ID of related object (e.g., MeterReading ID)")
    redirect_url = models.CharField(max_length=500, blank=True,
                                   help_text="URL to redirect when clicked")

    # Status
    is_read = models.BooleanField(default=False, help_text="Has the user read this notification?")
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True, help_text="When was it marked as read")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_read', '-created_at']),
            models.Index(fields=['notification_type', '-created_at']),
        ]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        user_str = self.user.username if self.user else "All Admins"
        return f"{self.title} - {user_str} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def mark_as_read(self):
        """Mark this notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    @property
    def time_ago(self):
        """Human-readable time ago string"""
        from django.utils.timesince import timesince
        return timesince(self.created_at)
