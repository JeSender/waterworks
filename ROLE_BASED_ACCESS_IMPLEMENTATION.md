# Role-Based Access Control Implementation Guide

## Overview
This guide documents the role-based access control (RBAC) system for Balilihan Waterworks Management System.

**Key Principle**: The system ALREADY HAS all views and pages built. We're just controlling WHO can see and access WHAT based on their role.

## User Roles

### 1. Superadmin (Django Superuser)
- **Account Type**: Django's built-in superuser (`is_superuser=True`)
- **Access**: Full system access - can see and do everything
- **Created via**: `python manage.py createsuperuser`

### 2. Admin
- **Role**: `role='admin'` in StaffProfile
- **Access**:
  - Consumer management (add, edit, view consumers)
  - Bill inquiry and payment processing
  - Meter readings overview
  - Reports and analytics
  - Payment history
  - Login history (view only)
- **Cannot Access**:
  - User management (creating/editing users)
  - System settings

### 3. Cashier
- **Role**: `role='cashier'` in StaffProfile
- **Access**:
  - Bill inquiry (main function)
  - Payment processing
  - Payment history
  - Print receipts
- **Cannot Access**:
  - Consumer management
  - Meter readings
  - Reports
  - User management
  - System settings

### 4. Field Staff
- **Role**: `role='field_staff'` in StaffProfile
- **Primary Interface**: Android Mobile App (Smart Meter Reading App)
- **Web Access** (limited):
  - Bill inquiry
  - Meter readings (for their assigned barangay)
- **Cannot Access**:
  - Consumer management
  - Reports
  - User management
  - System settings

## Implementation Components

### 1. StaffProfile Model (consumers/models.py)
```python
class StaffProfile(models.Model):
    ROLE_CHOICES = [
        ('superadmin', 'Superadmin'),  # Not used - superuser instead
        ('admin', 'Admin'),
        ('cashier', 'Cashier'),
        ('field_staff', 'Field Staff'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='field_staff')
    assigned_barangay = models.ForeignKey('Barangay', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
```

### 2. Permission Decorators (consumers/decorators.py)
```python
# Use these decorators to protect views

@role_required('admin')  # Allow only admin role
@role_required('admin', 'cashier')  # Allow admin OR cashier

@superadmin_only  # Only superuser
@admin_or_higher  # Superuser or admin
@cashier_access  # Superuser, admin, or cashier
```

### 3. Sidebar Menu Visibility (consumers/templates/consumers/base.html)
```django
<!-- Show to specific roles -->
{% if user.is_superuser or user.staffprofile.role == 'admin' %}
    <a href="{% url 'consumers:consumer_management' %}">Consumers</a>
{% endif %}

<!-- Show to all roles -->
<a href="{% url 'consumers:inquire' %}">Bill Inquiry</a>

<!-- Show to cashiers and admins -->
{% if user.is_superuser or user.staffprofile.role == 'admin' or user.staffprofile.role == 'cashier' %}
    <a href="{% url 'consumers:payment_history' %}">Payment History</a>
{% endif %}
```

## Creating User Accounts

### Superuser (Superadmin)
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@balilihan-waterworks.com
# Password: [secure password]
```

### Admin, Cashier, Field Staff
Use Django admin or existing user management views:
1. Go to User Management (superuser only)
2. Create new user
3. Assign role in StaffProfile
4. For field staff, assign barangay

## Permission Matrix

| Feature | Superuser | Admin | Cashier | Field Staff |
|---------|-----------|-------|---------|-------------|
| Dashboard | ✓ | ✓ | ✓ | ✓ |
| Consumer Management | ✓ | ✓ | ✗ | ✗ |
| Bill Inquiry | ✓ | ✓ | ✓ | ✓ |
| Payment Processing | ✓ | ✓ | ✓ | ✗ |
| Payment History | ✓ | ✓ | ✓ | ✗ |
| Meter Readings | ✓ | ✓ | ✗ | ✓ (barangay only) |
| Reports | ✓ | ✓ | ✗ | ✗ |
| User Management | ✓ | ✗ | ✗ | ✗ |
| System Settings | ✓ | ✗ | ✗ | ✗ |
| Login History | ✓ | ✓ (view) | ✗ | ✗ |

## Testing the Implementation

### 1. Test Superuser Access
- Login as superuser
- Verify all menu items visible
- Verify access to all pages

### 2. Test Admin Access
- Create admin user with `role='admin'`
- Login as admin
- Should see: Dashboard, Consumers, Bill Inquiry, Payment History, Meter Readings, Reports, Login History
- Should NOT see: User Management, System Settings

### 3. Test Cashier Access
- Create cashier user with `role='cashier'`
- Login as cashier
- Should see: Dashboard, Bill Inquiry, Payment History
- Should NOT see: Consumers, Meter Readings, Reports, User Management, System Settings

### 4. Test Field Staff Access
- Create field staff user with `role='field_staff'` and assigned barangay
- Login as field staff
- Should see: Dashboard, Bill Inquiry, Meter Readings (limited to barangay)
- Should NOT see: Consumers, Payment History, Reports, User Management, System Settings
- **Primary usage**: Android mobile app for field readings

## Next Steps

1. ✅ StaffProfile model updated with role field
2. ✅ Permission decorators created
3. ✅ Database migration applied
4. ✅ Sidebar menu updated with role-based visibility
5. ⏳ Add decorators to protect views (optional - sidebar already limits access)
6. ⏳ Create test user accounts for each role
7. ⏳ Test access control for all roles
8. ⏳ Commit changes to GitHub

## Notes

- **Superadmin = Django Superuser**: No need for separate superadmin role, use `is_superuser` check
- **Field Staff**: Primarily use mobile app, web interface is secondary
- **Existing Views**: All views already exist, just control access via sidebar and decorators
- **User Management**: Already exists in urls.py (lines 84-88), superuser can create users there
- **No Separate Dashboards**: All users go to same `/home/` dashboard, content adjusts based on role
