# consumers/models.py
from django.db import models
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid
from django.contrib.auth.models import User

class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    assigned_barangay = models.ForeignKey('Barangay', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, default='field_staff')  # field_staff, admin

    def __str__(self):
        return f"{self.user.username} - {self.assigned_barangay.name}"

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

    # 🔑 UPDATED: Account Number (Auto-generated with 5-digit padding)
    account_number = models.CharField(max_length=20, unique=True, blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Connected or Disconnected consumer"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # --- AUTO-GENERATE GLOBAL account_number with 5-digit padding ---
        if not self.account_number:
            # Find the highest existing number suffix
            # This query gets the maximum integer value of the part after 'BW-'
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT MAX(CAST(SUBSTR(account_number, 4) AS INTEGER))
                    FROM consumers_consumer
                    WHERE account_number LIKE 'BW-_____' -- Ensures format BW- followed by exactly 5 characters
                """)
                row = cursor.fetchone()
                last_num = row[0] if row and row[0] is not None else -1 # Handle case where no records exist

            new_num = last_num + 1
            # Format as BW-00000, BW-00001, ..., BW-00010, etc.
            self.account_number = f'BW-{new_num:05d}' # Use :05d for 5-digit padding
        # --- END AUTO-GENERATE account_number ---
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.account_number} - {self.first_name} {self.last_name}"

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
# System Settings (Optional but Useful)
# ----------------------------
class SystemSetting(models.Model):
    rate_per_cubic = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('22.50'))
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Current Rate: ₱{self.rate_per_cubic}/m³"
    
    
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
