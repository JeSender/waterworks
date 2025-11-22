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
        ('consumer_disconnected', 'Consumer Disconnected'),
        ('consumer_reconnected', 'Consumer Reconnected'),
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

    # ========================
    # Methods
    # ========================
    def save(self, *args, **kwargs):
        # Auto-generate account_number if not set
        if not self.account_number:
            # Use Django ORM instead of raw SQL to prevent SQL injection
            # Get all existing account numbers that match the pattern
            existing_accounts = Consumer.objects.filter(
                account_number__startswith='BW-'
            ).exclude(
                pk=self.pk  # Exclude self if updating
            ).values_list('account_number', flat=True)

            # Extract numeric parts and find max
            numbers = []
            for acc in existing_accounts:
                try:
                    # Extract number after 'BW-'
                    num_part = acc.split('-')[1]
                    if num_part.isdigit() and len(num_part) == 5:
                        numbers.append(int(num_part))
                except (IndexError, ValueError):
                    continue

            # Get next number
            last_num = max(numbers) if numbers else 0
            new_num = last_num + 1
            self.account_number = f'BW-{new_num:05d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.account_number} - {self.full_name}"

    # ... (rest of your model, if any) ...

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
        ordering = ['-reading_date']
        unique_together = ['consumer', 'reading_date']

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

    status = models.CharField(
        max_length=20, 
        choices=BILL_STATUS_CHOICES, 
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-billing_period']
        verbose_name = "Utility Bill"
        verbose_name_plural = "Utility Bills"

    def __str__(self):
        return f"Bill for {self.consumer} | {self.billing_period.strftime('%B %Y')} | ₱{self.total_amount} ({self.status})"


# ----------------------------
# consumers/models.py
from django.db import models
from decimal import Decimal # Import Decimal

# ... (other imports remain the same) ...

class SystemSetting(models.Model):
    """
    Model to store system-wide settings.
    This version includes separate rates for Residential and Commercial usage.
    """
    # --- NEW: Add fields for separate rates ---
    residential_rate_per_cubic = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('22.50'), # Default residential rate
        help_text="Rate applied to residential consumers (₱ / m³)"
    )
    commercial_rate_per_cubic = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('25.00'), # Default commercial rate
        help_text="Rate applied to commercial consumers (₱ / m³)"
    )
    # --- END NEW ---

    # Billing configuration
    fixed_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('50.00'),
        help_text="Fixed charge added to every bill (₱)"
    )
    billing_day_of_month = models.IntegerField(
        default=1,
        help_text="Day of month for billing period (1-28)"
    )
    due_day_of_month = models.IntegerField(
        default=20,
        help_text="Day of month for bill due date (1-28)"
    )

    # Optional: Keep a field to track when the settings were last updated
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
    amount_paid = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Actual amount due from the bill"
    )
    received_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Cash amount received from the consumer"
    )
    change = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
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

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ['-payment_date']

    def clean(self):
        """Validate business logic before saving."""
        if self.received_amount < self.amount_paid:
            raise ValidationError("Received amount cannot be less than the amount due.")
        if self.amount_paid != self.bill.total_amount:
            raise ValidationError("Amount paid must match the bill's total amount.")

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

    def __str__(self):
        return f"OR#{self.or_number} - {self.bill.consumer.account_number}"
