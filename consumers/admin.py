# consumers/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import (
    Consumer, Barangay, Purok, MeterBrand, MeterReading, 
    Bill, Payment, SystemSetting, StaffProfile, UserLoginEvent
)

# NEW: Admin for User Login Events
@admin.register(UserLoginEvent)
class UserLoginEventAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_timestamp'] # Columns to show in the list view
    list_filter = ['login_timestamp', 'user']  # Filters on the right side
    search_fields = ['user__username', 'user__first_name', 'user__last_name'] # Search bar
    ordering = ['-login_timestamp']            # Order by most recent first
    readonly_fields = ['user', 'login_timestamp'] # Make fields read-only to prevent editing

    # Optional: Customize how the list view looks
    def has_add_permission(self, request):
        # Prevent adding events manually through the admin
        return False

    def has_change_permission(self, request, obj=None):
        # Prevent changing events through the admin (they are read-only)
        return False


# ----------------------------
# Staff Profile Integration
# ----------------------------
class StaffProfileInline(admin.StackedInline):
    model = StaffProfile
    can_delete = False
    verbose_name_plural = 'Staff Profile'
    extra = 0

class CustomUserAdmin(UserAdmin):
    inlines = (StaffProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# ----------------------------
# Core Area Models
# ----------------------------

@admin.register(Barangay)
class BarangayAdmin(admin.ModelAdmin):
    list_display = ['name', 'consumer_count']
    search_fields = ['name']
    ordering = ['name']

    def consumer_count(self, obj):
        # Use the default reverse foreign key name 'consumer_set'
        # This accesses all Consumer objects related to this Barangay object
        return obj.consumer_set.count()
    consumer_count.short_description = 'Consumers'

@admin.register(Purok)
class PurokAdmin(admin.ModelAdmin):
    list_display = ['name', 'barangay', 'consumer_count'] # Display name, linked barangay, and consumer count
    list_filter = ['barangay'] # Allow filtering by barangay in the admin list view
    search_fields = ['name', 'barangay__name'] # Allow searching by purok name or parent barangay name
    ordering = ['barangay__name', 'name'] # Order puroks first by their barangay's name, then by purok name

    def consumer_count(self, obj):
        """
        Calculates the number of consumers associated with this Purok.
        Uses the reverse foreign key relationship from Consumer to Purok.
        """
        # Use the default reverse foreign key name 'consumer_set'
        # This accesses all Consumer objects related to this Purok object
        return obj.consumer_set.count()
    consumer_count.short_description = 'Consumers' # Sets the column name in the admin list view

# ... (other admin registrations) ...

@admin.register(MeterBrand)
class MeterBrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'consumer_count']
    search_fields = ['name']

    def consumer_count(self, obj):
        return obj.consumers.count()
    consumer_count.short_description = 'Consumers'

# ----------------------------
# Meter Reading Management
# ----------------------------
@admin.register(MeterReading)
class MeterReadingAdmin(admin.ModelAdmin):
    list_display = ['consumer_account', 'reading_date', 'reading_value', 'source', 'is_confirmed_status']
    list_filter = ['is_confirmed', 'reading_date', 'source', 'consumer__barangay']
    search_fields = ['consumer__first_name', 'consumer__last_name', 'consumer__account_number']
    date_hierarchy = 'reading_date'
    ordering = ['-reading_date']
    readonly_fields = ['is_confirmed']

    def consumer_account(self, obj):
        return format_html(
            '<strong>{}</strong><br>{} {}',
            obj.consumer.account_number,
            obj.consumer.first_name,
            obj.consumer.last_name
        )
    consumer_account.short_description = 'Consumer'

    def is_confirmed_status(self, obj):
        if obj.is_confirmed:
            return format_html('<span class="badge bg-success">Confirmed</span>')
        return format_html('<span class="badge bg-warning text-dark">Pending</span>')
    is_confirmed_status.short_description = 'Status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'consumer', 'consumer__barangay', 'consumer__purok'
        )

# ----------------------------
# Consumer Management
# ----------------------------
@admin.register(Consumer)
class ConsumerAdmin(admin.ModelAdmin):
    list_display = ['account_number_tag', 'full_name', 'contact_info', 'location_info', 'meter_info', 'status_tag']
    list_filter = ['barangay', 'purok', 'usage_type', 'meter_brand', 'status', 'registration_date']
    search_fields = ['first_name', 'middle_name', 'last_name', 'phone_number', 'serial_number', 'account_number']
    list_per_page = 50

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'middle_name', 'last_name', 'birth_date', 'gender', 'civil_status', 'spouse_name')
        }),
        ('Contact & Household', {
            'fields': ('phone_number', 'household_number')
        }),
        ('Location', {
            'fields': ('barangay', 'purok')
        }),
        ('Meter Information', {
            'fields': ('usage_type', 'meter_brand', 'serial_number', 'first_reading', 'registration_date')
        }),
        ('System', {
            'fields': ('status', 'account_number'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change and not obj.account_number:
            last_consumer = Consumer.objects.order_by('-id').first()
            next_num = 1
            if last_consumer and last_consumer.account_number:
                try:
                    num = int(last_consumer.account_number.split('-')[-1])
                    next_num = num + 1
                except (ValueError, IndexError):
                    pass
            obj.account_number = f"BW-{next_num:04d}"
        super().save_model(request, obj, form, change)

    def full_name(self, obj):
        return f"{obj.first_name} {obj.middle_name or ''} {obj.last_name}".strip()
    full_name.short_description = 'Name'

    def contact_info(self, obj):
        return obj.phone_number or "—"
    contact_info.short_description = 'Phone'

    def location_info(self, obj):
        return format_html(
            "{}<br><small>{}</small>",
            obj.barangay.name if obj.barangay else "—",
            obj.purok.name if obj.purok else "—"
        )
    location_info.short_description = 'Barangay / Purok'

    def meter_info(self, obj):
        return format_html(
            "{}<br><small>{}</small>",
            obj.serial_number or "—",
            obj.meter_brand.name if obj.meter_brand else "—"
        )
    meter_info.short_description = 'Meter'

    def account_number_tag(self, obj):
        return format_html(
            '<code style="background:#f0f0f0; padding:2px 6px; border-radius:3px;">{}</code>',
            obj.account_number or "—"
        )
    account_number_tag.short_description = 'Account #'

    def status_tag(self, obj):
        color = "success" if obj.status == "active" else "warning" if obj.status == "pending" else "danger"
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_tag.short_description = 'Status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'barangay', 'purok', 'meter_brand'
        )

# ----------------------------
# Billing & Payment
# ----------------------------
@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['consumer_account', 'billing_period', 'total_amount', 'status', 'due_date']
    list_filter = ['status', 'billing_period', 'due_date', 'consumer__barangay']
    search_fields = ['consumer__account_number', 'consumer__first_name', 'consumer__last_name']
    ordering = ['-billing_period']
    readonly_fields = ['total_amount']

    def consumer_account(self, obj):
        return format_html(
            '<strong>{}</strong><br>{} {}',
            obj.consumer.account_number,
            obj.consumer.first_name,
            obj.consumer.last_name
        )
    consumer_account.short_description = 'Consumer'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('consumer')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['or_number', 'consumer_account', 'amount_paid', 'received_amount', 'payment_date']
    list_filter = ['payment_date', 'bill__consumer__barangay']
    search_fields = ['or_number', 'bill__consumer__account_number']
    ordering = ['-payment_date']
    readonly_fields = ['or_number', 'payment_date']

    def consumer_account(self, obj):
        return obj.bill.consumer.account_number
    consumer_account.short_description = 'Account #'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('bill__consumer')

# ----------------------------
# System Settings
# ----------------------------
@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    # Update list_display to show the new fields
    list_display = ['id', 'residential_rate_per_cubic', 'commercial_rate_per_cubic', 'updated_at']
    # Optionally, customize the form fields shown when editing
    # fields = ['residential_rate_per_cubic', 'commercial_rate_per_cubic'] # Show only these fields in the edit form

# ... (register other models if needed) ...

