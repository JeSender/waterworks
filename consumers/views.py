from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Max, Count, Sum, OuterRef, Subquery, Value
from django.db.models.functions import Concat, TruncMonth
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date
try:
    from dateutil.relativedelta import relativedelta
except Exception:
    # Fallback: approximate relativedelta by using a timedelta of ~30 days per month
    # This keeps existing subtraction usages like relativedelta(months=5) working
    from datetime import timedelta as _td
    def relativedelta(months=0, **kwargs):
        return _td(days=30 * int(months))
from decimal import Decimal, InvalidOperation
import uuid
import json
import csv
import openpyxl
from openpyxl.styles import Font, PatternFill
from .models import (
    Consumer, Barangay, Purok, MeterReading, Bill, SystemSetting, Payment,
    StaffProfile, UserLoginEvent, MeterBrand, PasswordResetToken, UserActivity
)
from .forms import ConsumerForm


# Helper function to get previous confirmed reading
def get_previous_reading(consumer):
    """Get the most recent confirmed meter reading for a consumer."""
    latest_reading = MeterReading.objects.filter(
        consumer=consumer,
        is_confirmed=True
    ).order_by('-reading_date', '-created_at').first()

    return latest_reading.reading_value if latest_reading else 0


# Helper function to calculate water bill
def calculate_water_bill(consumer, consumption):
    """Calculate water bill based on consumption and consumer type."""
    # Get system settings for rates
    settings = SystemSetting.objects.first()

    if not settings:
        # Fallback to default rates if no settings exist
        residential_rate = Decimal('22.50')
        commercial_rate = Decimal('25.00')
        fixed_charge = Decimal('50.00')
    else:
        residential_rate = settings.residential_rate_per_cubic
        commercial_rate = settings.commercial_rate_per_cubic
        fixed_charge = settings.fixed_charge

    # Determine rate based on usage type
    if consumer.usage_type == 'Commercial':
        rate = commercial_rate
    else:
        rate = residential_rate

    # Calculate total: (consumption × rate) + fixed charge
    consumption_charge = Decimal(str(consumption)) * rate
    total_amount = consumption_charge + fixed_charge

    return float(rate), float(total_amount)


# NEW: API View for submitting meter readings from the Android app (Updated to match app data format)
@csrf_exempt # Be careful with CSRF in production, consider using proper tokens for mobile apps
def api_submit_reading(request):
    """
    API endpoint for Android app to submit meter readings.

    Returns complete bill details including:
    - status, message
    - consumer_name, account_number, reading_date
    - previous_reading, current_reading, consumption
    - rate, total_amount, field_staff_name
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        # Parse JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))

        # Extract data from the request - MATCHING ANDROID APP FORMAT
        consumer_id = data.get('consumer_id') # Expecting consumer ID from app
        reading_value = data.get('reading')   # Expecting 'reading' key from app
        # Optional: Check if reading_date is sent, otherwise default to today
        reading_date_str = data.get('reading_date') # Expecting 'reading_date' key from app, can be None initially

        # Validate required fields (assuming reading_date is sent by the app now, or use today's date)
        if consumer_id is None or reading_value is None:
            return JsonResponse({'error': 'Missing required fields: consumer_id or reading'}, status=400)

        # Get the consumer based on ID (as sent by the app)
        try:
            consumer = Consumer.objects.get(id=consumer_id) # Use id instead of account_number
        except Consumer.DoesNotExist:
            return JsonResponse({'error': 'Consumer not found'}, status=404)

        # Determine the reading date
        if reading_date_str:
            # Parse the date string if provided by the app
            try:
                reading_date = timezone.datetime.strptime(reading_date_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)
        else:
            # Use the current date if no date is provided by the app
            reading_date = timezone.now().date()

        # Validate reading value (should be a positive number, handle potential float from app)
        try:
            # Convert to int, assuming the app sends an integer or a float that represents an integer
            # If the app sends a float representing a non-integer reading, this might need adjustment
            current_reading = int(reading_value) # Convert float to int
            if current_reading < 0:
                raise ValueError("Reading value cannot be negative")
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid reading value. Must be a non-negative number.'}, status=400)

        # Get previous reading
        previous_reading = get_previous_reading(consumer)

        # Calculate consumption
        consumption = current_reading - previous_reading

        # Validate consumption (current should be >= previous)
        if consumption < 0:
            return JsonResponse({
                'error': 'Invalid reading',
                'message': f'Current reading ({current_reading}) cannot be less than previous reading ({previous_reading})'
            }, status=400)

        # Calculate bill
        rate, total_amount = calculate_water_bill(consumer, consumption)

        # Get field staff name
        field_staff_name = "System"  # Default
        if request.user.is_authenticated:
            field_staff_name = request.user.get_full_name() or request.user.username

        # --- NEW LOGIC: Check for existing unconfirmed reading on the same date ---
        try:
            existing_reading = MeterReading.objects.get(
                consumer=consumer,
                reading_date=reading_date
            )
            # If an existing reading is found for the same date
            if existing_reading.is_confirmed:
                # If it's already confirmed, don't allow updates
                error_msg = f"Reading for {consumer.account_number} on {reading_date} is already confirmed and cannot be updated via API."
                return JsonResponse({'error': error_msg}, status=400)
            else:
                # If it's unconfirmed, update the existing record
                existing_reading.reading_value = current_reading
                existing_reading.source = 'mobile_app' # Update source to reflect API submission
                existing_reading.save()

        except MeterReading.DoesNotExist:
            # If no existing reading for the date, create a new one (original behavior)
            reading = MeterReading.objects.create(
                consumer=consumer,
                reading_date=reading_date,
                reading_value=current_reading,
                source='mobile_app', # Mark source as coming from the mobile app
                is_confirmed=True  # Auto-confirm readings from mobile app
            )

        # Return complete bill details (ALL 11 REQUIRED FIELDS)
        return JsonResponse({
            'status': 'success',
            'message': 'Reading submitted successfully',
            'consumer_name': f"{consumer.first_name} {consumer.last_name}",
            'account_number': consumer.account_number,
            'reading_date': str(reading_date),
            'previous_reading': int(previous_reading),
            'current_reading': int(current_reading),
            'consumption': int(consumption),
            'rate': rate,
            'total_amount': total_amount,
            'field_staff_name': field_staff_name
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        # Log unexpected errors (Railway will capture this in logs)
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error submitting reading: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)





@csrf_exempt
def api_login(request):
    """Enhanced API login for Android app with security tracking."""
    from .decorators import get_client_ip, get_user_agent

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        # Get security information
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)

        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            # Get staff's assigned barangay
            try:
                profile = StaffProfile.objects.get(user=user)

                # Record successful mobile login event
                UserLoginEvent.objects.create(
                    user=user,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    login_method='mobile',
                    status='success',
                    session_key=request.session.session_key
                )

                return JsonResponse({
                    'status': 'success',
                    'token': request.session.session_key,
                    'barangay': profile.assigned_barangay.name,
                    'user': {
                        'username': user.username,
                        'full_name': user.get_full_name()
                    }
                })
            except StaffProfile.DoesNotExist:
                # Still record the login even if there's no profile
                UserLoginEvent.objects.create(
                    user=user,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    login_method='mobile',
                    status='success'
                )
                return JsonResponse({'error': 'No assigned barangay'}, status=403)
        else:
            # Record failed login attempt
            if user:
                UserLoginEvent.objects.create(
                    user=user,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    login_method='mobile',
                    status='failed'
                )
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        # Log unexpected errors (Railway will capture this in logs)
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error during API login: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)



@csrf_exempt
@login_required
def api_create_reading(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        consumer_id = data.get('consumer_id')
        reading_value = data.get('reading_value')
        reading_date = data.get('reading_date')  # YYYY-MM-DD

        # Validate consumer belongs to staff's barangay
        profile = StaffProfile.objects.get(user=request.user)
        consumer = Consumer.objects.get(id=consumer_id, barangay=profile.assigned_barangay)

        MeterReading.objects.create(
            consumer=consumer,
            reading_value=reading_value,
            reading_date=reading_date,
            source='field_app'
        )
        return JsonResponse({'status': 'success'})
    except StaffProfile.DoesNotExist:
        return JsonResponse({'error': 'Staff profile not found'}, status=403)
    except Consumer.DoesNotExist:
        return JsonResponse({'error': 'Consumer not found or not in assigned barangay'}, status=404)
    except Exception as e:
        # Log error but don't expose details
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"API create reading error: {e}", exc_info=True)
        return JsonResponse({'error': 'Failed to create reading'}, status=400)

# consumers/views.py (Update the api_consumers function)


# ... (other imports remain the same) ...

@login_required
def api_consumers(request):
    """Get consumers for the staff's assigned barangay, including the latest confirmed reading value."""
    try:
        profile = StaffProfile.objects.select_related('assigned_barangay').get(user=request.user)
        consumers = Consumer.objects.filter(barangay=profile.assigned_barangay).select_related('barangay')

        data = []
        for consumer in consumers:
            # Find the latest confirmed reading for this specific consumer
            latest_confirmed_reading_obj = MeterReading.objects.filter(
                consumer=consumer,
                is_confirmed=True
            ).order_by('-reading_date').first() # Get the most recent one

            # Extract the reading value, or default to 0 if no confirmed reading exists
            latest_confirmed_reading_value = latest_confirmed_reading_obj.reading_value if latest_confirmed_reading_obj else 0

            # Append consumer data including the latest confirmed reading value
            data.append({
                'id': consumer.id,
                'account_number': consumer.account_number,
                'name': f"{consumer.first_name} {consumer.last_name}",
                'serial_number': consumer.serial_number,
                # NEW: Add the latest confirmed reading value to the response
                'latest_confirmed_reading': latest_confirmed_reading_value
            })

        return JsonResponse(data, safe=False)
    except StaffProfile.DoesNotExist:
        return JsonResponse({'error': 'No assigned barangay'}, status=403)

# ... (other views remain the same) ...


# ======================
# SYSTEM SETTINGS
# ======================

# consumers/views.py




# consumers/views.py

# ... (other imports remain the same) ...
# ... (other imports remain the same) ...

# ... (your existing functions like api_login, api_consumers, api_submit_reading, system_management, etc.) ...

# NEW: API View for fetching the current water rates (Residential & Commercial)
@login_required # Ensure the user (app) is authenticated
def api_get_current_rates(request):
    """
    API endpoint for the Android app to fetch the current residential and commercial water rates.
    """
    try:
        # Get the first (or only) SystemSetting object (singleton pattern)
        setting = SystemSetting.objects.first()
        if not setting:
            # Handle the case where no SystemSetting exists
            return JsonResponse({'error': 'System settings not configured.'}, status=500)

        # Return the rates as JSON
        return JsonResponse({
            'status': 'success',
            # NEW: Return both residential and commercial rates
            'residential_rate_per_cubic': float(setting.residential_rate_per_cubic), # Convert Decimal to float for JSON
            'commercial_rate_per_cubic': float(setting.commercial_rate_per_cubic),   # Convert Decimal to float for JSON
            'updated_at': setting.updated_at.isoformat() # Include the last update timestamp
        })

    except Exception as e:
        # Log unexpected errors (Railway will capture this in logs)
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching rates: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)

# ... (rest of your views) ...# consumers/views.py

# ... (other imports remain the same) ...

@login_required
def system_management(request):
    """
    Manage system-wide settings like residential and commercial water rates.
    Focuses only on rate settings, removes user-specific info like login time/barangay.
    """
    # Get the first (or only) SystemSetting instance (assumes singleton pattern)
    setting, created = SystemSetting.objects.get_or_create(id=1)

    if request.method == "POST":
        try:
            # Get the new values from the form
            new_res_rate_str = request.POST.get("residential_rate_per_cubic")
            new_comm_rate_str = request.POST.get("commercial_rate_per_cubic")
            new_fixed_charge_str = request.POST.get("fixed_charge")
            billing_day = request.POST.get("billing_day_of_month")
            due_day = request.POST.get("due_day_of_month")

            # Validate and convert to Decimal
            new_res_rate = Decimal(new_res_rate_str)
            new_comm_rate = Decimal(new_comm_rate_str)
            new_fixed_charge = Decimal(new_fixed_charge_str)
            billing_day = int(billing_day)
            due_day = int(due_day)

            if new_res_rate <= 0 or new_comm_rate <= 0 or new_fixed_charge < 0:
                raise ValueError("Rates must be positive and fixed charge cannot be negative.")

            if billing_day < 1 or billing_day > 28 or due_day < 1 or due_day > 28:
                raise ValueError("Billing and due days must be between 1 and 28.")

            # Update the setting object
            setting.residential_rate_per_cubic = new_res_rate
            setting.commercial_rate_per_cubic = new_comm_rate
            setting.fixed_charge = new_fixed_charge
            setting.billing_day_of_month = billing_day
            setting.due_day_of_month = due_day
            setting.save() # Save the changes to the database

            # Send success message
            messages.success(request, "✅ System settings updated successfully!")
        except (InvalidOperation, ValueError, TypeError) as e:
            messages.error(request, f"❌ Invalid input: {e}")
        except Exception as e:
            messages.error(request, f"❌ Error updating settings: {e}")

        # Redirect back to the system management page after processing POST
        return redirect("consumers:system_management")

    # For GET requests, just pass the setting object to the template
    context = {
        "setting": setting, # Pass the setting object containing both rates
        # Removed assigned_barangay and login_time from context
    }
    # Render the template with the context
    return render(request, "consumers/system_management.html", context)

# ... (your other views remain the same) ...
# NEW: View for field staff to see their assigned consumers
@login_required
def consumer_list_for_staff(request):
    """Display consumers for the logged-in staff member's assigned barangay."""
    try:
        profile = StaffProfile.objects.get(user=request.user)
        assigned_barangay = profile.assigned_barangay
        consumers = Consumer.objects.filter(barangay=assigned_barangay)
    except StaffProfile.DoesNotExist:
        messages.error(request, "User profile not found. Please contact an administrator.")
        return redirect('consumers:login') # Or another appropriate page

    # Get login time from session
    login_time_iso = request.session.get('login_time')
    login_time_str = None
    if login_time_iso:
        try:
            login_time_obj = timezone.datetime.fromisoformat(login_time_iso.replace('Z', '+00:00'))
            login_time_str = login_time_obj.strftime("%b %d, %Y %H:%M:%S")
        except ValueError:
            login_time_str = "Unknown"

    context = {
        'consumers': consumers,
        'assigned_barangay': assigned_barangay,
        'login_time': login_time_str,
        'user': request.user, # Pass user for username display
    }
    return render(request, 'consumers/consumer_list_for_staff.html', context) # Create this template

# Example logout view

def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('consumers:login') # Redirect to login page



# ======================
# EXPORT DELINQUENT CONSUMERS
# ======================

@login_required
def export_delinquent_consumers(request):
    month = request.GET.get('month')
    year = request.GET.get('year')

    # Use billing_period (not billing_date)
    bills = Bill.objects.filter(status='Pending')
    if month and year:
        bills = bills.filter(billing_period__month=month, billing_period__year=year)

    consumers = Consumer.objects.filter(bills__in=bills).distinct()

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="delinquent_consumers_{month or "all"}_{year or "all"}.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(['First Name', 'Middle Name', 'Last Name', 'Phone', 'Barangay', 'Serial', 'Pending Bills'])

    for consumer in consumers:
        pending_bills = consumer.bills.filter(status='Pending')
        total_pending = sum(b.total_amount for b in pending_bills)  # Use total_amount
        writer.writerow([
            consumer.first_name,
            consumer.middle_name or "",
            consumer.last_name,
            consumer.phone_number,
            consumer.barangay.name if consumer.barangay else "",
            consumer.serial_number,
            total_pending
        ])

    return response


# ======================
# SMART METER WEBHOOK
# ======================

@csrf_exempt
def smart_meter_webhook(request):
    """
    Webhook endpoint for IoT smart meters to submit readings.
    Requires API key authentication via X-API-Key header.
    Set SMART_METER_API_KEY in .env file.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    # Authenticate using API key from header
    from decouple import config
    expected_api_key = config('SMART_METER_API_KEY', default='')
    provided_api_key = request.META.get('HTTP_X_API_KEY', '')

    if not expected_api_key:
        # API key not configured - reject all requests for security
        return JsonResponse({'error': 'Webhook not configured'}, status=503)

    if provided_api_key != expected_api_key:
        # Invalid or missing API key
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # Process the webhook data
    try:
        data = json.loads(request.body)

        # Validate required fields
        required_fields = ['consumer_id', 'reading', 'date']
        if not all(field in data for field in required_fields):
            return JsonResponse({
                'error': 'Missing required fields',
                'required': required_fields
            }, status=400)

        # Get consumer
        consumer = get_object_or_404(Consumer, id=data['consumer_id'])

        # Validate reading value
        reading_value = int(data['reading'])
        if reading_value < 0:
            return JsonResponse({'error': 'Reading value cannot be negative'}, status=400)

        # Create meter reading
        MeterReading.objects.create(
            consumer=consumer,
            reading_value=reading_value,
            reading_date=data['date'],
            source='smart_meter'
        )
        return JsonResponse({'status': 'success', 'message': 'Reading recorded'})

    except Consumer.DoesNotExist:
        return JsonResponse({'error': 'Consumer not found'}, status=404)
    except (ValueError, TypeError) as e:
        return JsonResponse({'error': 'Invalid data format'}, status=400)
    except Exception as e:
        # Log error but don't expose details
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Smart meter webhook error: {e}", exc_info=True)
        return JsonResponse({'error': 'Processing failed'}, status=500)


# ======================
# AUTH VIEWS
# ======================

def staff_login(request):
    """Enhanced staff login with security tracking."""
    from .decorators import get_client_ip, get_user_agent

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        # Get security information
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)

        if user is not None and user.is_staff:
            # Successful login
            login(request, user)

            # Record login event
            UserLoginEvent.objects.create(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                login_method='web',
                status='success',
                session_key=request.session.session_key
            )

            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            return redirect('consumers:home')
        else:
            # Failed login attempt
            if user:
                # User exists but not staff - record failed attempt
                UserLoginEvent.objects.create(
                    user=user,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    login_method='web',
                    status='failed'
                )
            messages.error(request, "Invalid credentials or not staff member.")

    return render(request, 'consumers/login.html')


@login_required
def staff_logout(request):
    """Enhanced logout with session tracking."""
    # Update the latest active session for this user
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
        # Log error but don't prevent logout
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error updating logout timestamp: {e}")

    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("consumers:staff_login")


# ======================
# PROFILE MANAGEMENT
# ======================

@login_required
def edit_profile(request):
    """
    Allow admin users to edit their profile and upload photo.
    """
    from .decorators import get_client_ip, get_user_agent

    try:
        profile = request.user.staffprofile
    except StaffProfile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('consumers:home')

    # Only allow admin to edit profile
    if profile.role != 'admin':
        messages.error(request, "Only administrators can edit their profile.")
        return redirect('consumers:home')

    if request.method == 'POST':
        updated = False

        # Update user information
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()

        if first_name and first_name != request.user.first_name:
            request.user.first_name = first_name
            updated = True
        if last_name and last_name != request.user.last_name:
            request.user.last_name = last_name
            updated = True
        if email and email != request.user.email:
            request.user.email = email
            updated = True

        if updated:
            request.user.save()

        # Handle profile photo upload
        if 'profile_photo' in request.FILES:
            photo = request.FILES['profile_photo']

            # Delete old photo if exists
            if profile.profile_photo:
                profile.profile_photo.delete(save=False)

            # Save new photo
            profile.profile_photo = photo
            profile.save()

            # Log activity
            UserActivity.objects.create(
                user=request.user,
                action='user_updated',
                description=f'{request.user.username} updated profile photo',
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                target_user=request.user
            )

            messages.success(request, "Profile photo updated successfully!")
            updated = True

        if updated:
            messages.success(request, "Profile updated successfully!")
        else:
            messages.info(request, "No changes were made.")

        return redirect('consumers:edit_profile')

    return render(request, 'consumers/edit_profile.html', {
        'profile': profile
    })


# ======================
# PASSWORD RECOVERY
# ======================

def forgot_password_request(request):
    """
    Password reset request page for superuser/admin accounts.
    Staff accounts are managed directly by admin through user management.
    """
    from .decorators import get_client_ip, get_user_agent

    if request.method == "POST":
        username = request.POST.get('username')

        try:
            user = User.objects.get(username=username)

            # Only allow password reset for superuser and admin staff
            if not (user.is_superuser or (user.is_staff and user.groups.filter(name='Admin').exists())):
                messages.error(request, "Password reset is only available for administrators. Please contact your administrator for password assistance.")
                return redirect('consumers:forgot_password')

            # Check if user already has a valid token
            existing_token = PasswordResetToken.objects.filter(
                user=user,
                is_used=False,
                expires_at__gt=timezone.now()
            ).first()

            if existing_token:
                # Use existing valid token
                token = existing_token
            else:
                # Create new password reset token
                token = PasswordResetToken.objects.create(
                    user=user,
                    ip_address=get_client_ip(request)
                )

            # Log the activity
            UserActivity.objects.create(
                user=user,
                action='password_reset_requested',
                description=f'Password reset requested for {user.username}',
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request)
            )

            # For thesis project: Display the reset link directly instead of sending email
            reset_url = request.build_absolute_uri(
                reverse('consumers:password_reset_confirm', kwargs={'token': token.token})
            )

            # Store reset URL in session to display on next page
            request.session['reset_url'] = reset_url
            request.session['reset_username'] = user.username

            messages.success(request, "Password reset link generated successfully!")
            return redirect('consumers:forgot_password')

        except User.DoesNotExist:
            messages.error(request, "No account found with that username.")
            return redirect('consumers:forgot_password')

    # Get reset URL from session if available
    reset_url = request.session.pop('reset_url', None)
    reset_username = request.session.pop('reset_username', None)

    return render(request, 'consumers/forgot_password.html', {
        'reset_url': reset_url,
        'reset_username': reset_username
    })


def password_reset_confirm(request, token):
    """
    Confirm password reset with token and set new password.
    """
    from .decorators import get_client_ip, get_user_agent

    try:
        reset_token = PasswordResetToken.objects.get(token=token)

        # Check if token is valid
        if not reset_token.is_valid():
            messages.error(request, "This password reset link has expired or has already been used.")
            return redirect('consumers:staff_login')

        if request.method == "POST":
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            # Validate passwords match
            if new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, 'consumers/reset_password.html', {
                    'token': token,
                    'username': reset_token.user.username
                })

            # Validate password strength
            if len(new_password) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
                return render(request, 'consumers/reset_password.html', {
                    'token': token,
                    'username': reset_token.user.username
                })

            # Set new password
            user = reset_token.user
            user.set_password(new_password)
            user.save()

            # Mark token as used
            reset_token.is_used = True
            reset_token.save()

            # Log the activity
            UserActivity.objects.create(
                user=user,
                action='password_reset_completed',
                description=f'Password reset completed for {user.username}',
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                target_user=user
            )

            messages.success(request, "Your password has been reset successfully! You can now login with your new password.")
            return redirect('consumers:password_reset_complete')

        return render(request, 'consumers/reset_password.html', {
            'token': token,
            'username': reset_token.user.username
        })

    except PasswordResetToken.DoesNotExist:
        messages.error(request, "Invalid password reset link.")
        return redirect('consumers:staff_login')


def password_reset_complete(request):
    """
    Password reset success confirmation page.
    """
    return render(request, 'consumers/reset_complete.html')


# ======================
# DASHBOARD
# ======================


@login_required
def home(request):
    """Staff dashboard showing key metrics and delinquent bills."""
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Get counts
    connected_count = Consumer.objects.filter(status='active').count()
    disconnected_count = Consumer.objects.filter(status='disconnected').count()

    # Delinquent count (consumers with pending bills older than today)
    delinquent_count = Consumer.objects.filter(
        bills__status='Pending',
        bills__billing_period__lt=datetime.now().date()
    ).distinct().count()

    # Handle report filter - support both month_year and separate month/year
    month_year = request.GET.get('month_year')
    if month_year:
        try:
            selected_year, selected_month = month_year.split('-')
            selected_year = int(selected_year)
            selected_month = int(selected_month)
        except:
            selected_month = current_month
            selected_year = current_year
    else:
        selected_month = int(request.GET.get('month', current_month))
        selected_year = int(request.GET.get('year', current_year))

    # Get delinquent bills for the selected month/year
    delinquent_bills = Bill.objects.filter(
        status='Pending',
        billing_period__month=selected_month,
        billing_period__year=selected_year
    ).select_related('consumer', 'consumer__barangay').order_by('-billing_period')

    # Calculate total delinquent amount
    total_delinquent_amount = delinquent_bills.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0.00')

    # Chart Data: Monthly Revenue Trend (Last 6 months)
    end_date = datetime.now().date()
    start_date = end_date - relativedelta(months=5)

    monthly_payments = Payment.objects.filter(
        payment_date__gte=start_date,
        payment_date__lte=end_date
    ).annotate(
        month=TruncMonth('payment_date')
    ).values('month').annotate(
        total=Sum('amount_paid')
    ).order_by('month')

    revenue_labels = []
    revenue_data = []
    revenue_list = []  # For template iteration
    for item in monthly_payments:
        label = item['month'].strftime('%b %Y')
        amount = float(item['total'] or 0)
        revenue_labels.append(label)
        revenue_data.append(amount)
        revenue_list.append((label, amount))

    # Chart Data: Payment Status Distribution
    total_bills = Bill.objects.count()
    paid_bills = Bill.objects.filter(status='Paid').count()
    pending_bills = Bill.objects.filter(status='Pending').count()

    # Chart Data: Barangay Consumer Distribution
    barangay_data = Consumer.objects.values('barangay__name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    barangay_labels = [item['barangay__name'] or 'Unassigned' for item in barangay_data]
    barangay_counts = [item['count'] for item in barangay_data]

    # Chart Data: Monthly Consumption Trend
    monthly_consumption = Bill.objects.filter(
        billing_period__gte=start_date
    ).annotate(
        month=TruncMonth('billing_period')
    ).values('month').annotate(
        total_consumption=Sum('consumption')
    ).order_by('month')

    consumption_labels = []
    consumption_data = []
    for item in monthly_consumption:
        consumption_labels.append(item['month'].strftime('%b %Y'))
        consumption_data.append(float(item['total_consumption'] or 0))

    # Create a date object for proper month/year formatting in template
    from datetime import date
    selected_date = date(selected_year, selected_month, 1)

    context = {
        'connected_count': connected_count,
        'disconnected_count': disconnected_count,
        'delinquent_count': delinquent_count,
        'delinquent_bills': delinquent_bills,
        'total_delinquent_amount': total_delinquent_amount,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'selected_date': selected_date,  # For template date formatting
        # Chart data
        'revenue_labels': json.dumps(revenue_labels),
        'revenue_data': json.dumps(revenue_data),
        'revenue_list': revenue_list,  # For template iteration
        'paid_bills': paid_bills,
        'pending_bills': pending_bills,
        'barangay_labels': json.dumps(barangay_labels),
        'barangay_counts': json.dumps(barangay_counts),
        'consumption_labels': json.dumps(consumption_labels),
        'consumption_data': json.dumps(consumption_data),
        'total_bills': total_bills,
    }
    return render(request, 'consumers/home.html', context)




# ======================
# CONSUMER STATUS FILTERS
# ======================

@login_required
def connected_consumers(request):
    # Optimize query with select_related
    consumers = Consumer.objects.filter(status='active').select_related('barangay', 'purok')
    return render(request, 'consumers/consumer_list_filtered.html', {
        'title': 'Connected Consumers',
        'consumers': consumers
    })


# 1. LIST VIEW: Show all disconnected consumers (no ID needed)
@login_required
def disconnected_consumers_list(request):
    # Optimize query with select_related
    consumers = Consumer.objects.filter(status='disconnected').select_related('barangay', 'purok')
    return render(request, 'consumers/consumer_list_filtered.html', {
        'title': 'Disconnected Consumers',
        'consumers': consumers
    })

# 2. ACTION VIEW: Disconnect a specific consumer (requires ID)
@login_required
def disconnect_consumer(request, consumer_id):
    consumer = get_object_or_404(Consumer, id=consumer_id)
    if request.method == 'POST':
        consumer.status = 'disconnected'
        consumer.disconnect_reason = request.POST.get('reason', '')
        consumer.save()
        messages.success(request, f"{consumer.full_name} has been disconnected.")
        return redirect('consumers:disconnected_consumers')
    return render(request, 'consumers/confirm_disconnect.html', {'consumer': consumer})

@login_required
def reconnect_consumer(request, consumer_id):
    consumer = get_object_or_404(Consumer, id=consumer_id)
    if request.method == 'POST':
        consumer.status = 'active'
        consumer.disconnect_reason = ''  # Optional: clear reason
        consumer.save()
        messages.success(request, f"{consumer.full_name} has been reconnected.")
        return redirect('consumers:consumer_detail', consumer.id)
    # Optional: handle GET with confirmation, but POST-only is simpler
    return redirect('consumers:consumer_detail', consumer.id)


@login_required
def delinquent_consumers(request):
    month = request.GET.get('month')
    year = request.GET.get('year')

    bills = Bill.objects.filter(status='Pending')
    if month and year:
        bills = bills.filter(billing_period__month=month, billing_period__year=year)

    # Optimize query with select_related
    consumers = Consumer.objects.filter(bills__in=bills).select_related('barangay', 'purok').distinct()

    return render(request, 'consumers/consumer_list_filtered.html', {
        'title': 'Delinquent Consumers',
        'consumers': consumers,
        'selected_month': month,
        'selected_year': year
    })


@login_required
def delinquent_report_printable(request):
    """Printable delinquent report with receipt-style header"""
    from calendar import month_name

    month = request.GET.get('month')
    year = request.GET.get('year')

    if not month or not year:
        messages.error(request, 'Month and year are required')
        return redirect('consumers:home')

    # Get all pending bills for the specified month/year
    bills = Bill.objects.filter(
        status='Pending',
        billing_period__month=month,
        billing_period__year=year
    ).select_related(
        'consumer__barangay',
        'consumer__purok',
        'previous_reading',
        'current_reading'
    ).order_by('consumer__account_number')

    # Calculate totals
    total_amount = sum(bill.total_amount for bill in bills)
    total_consumers = bills.count()

    # Format month display
    month_display = f"{month_name[int(month)]} {year}"

    context = {
        'bills': bills,
        'total_amount': total_amount,
        'total_consumers': total_consumers,
        'month_display': month_display,
        'month': month,
        'year': year,
        'generated_date': timezone.now()
    }

    return render(request, 'consumers/delinquent_report_print.html', context)


# ======================
# CONSUMER MANAGEMENT
# ======================


@login_required
def consumer_management(request):
    """Display consumer list with filters and modal form"""
    search_query = request.GET.get('search', '').strip()
    barangay_filter = request.GET.get('barangay', '').strip()

    # Optimize query with select_related to avoid N+1 queries
    consumers = Consumer.objects.select_related('barangay', 'purok', 'meter_brand').all()
    if search_query:
        consumers = consumers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(serial_number__icontains=search_query)
        )
    if barangay_filter:
        consumers = consumers.filter(barangay__id=barangay_filter)

    # Always pass a fresh form for the modal
    form = ConsumerForm()

    # Pagination
    paginator = Paginator(consumers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'consumers': page_obj,
        'form': form,
        'search_query': search_query,
        'barangays': Barangay.objects.all(),
        'barangay_filter': barangay_filter,
    }
    return render(request, 'consumers/consumer_management.html', context)


@login_required
def add_consumer(request):
    """Handle adding a new consumer via full page form"""
    if request.method == "POST":
        form = ConsumerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Consumer added successfully!")
            return redirect('consumers:consumer_management')
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = ConsumerForm()

    return render(request, 'consumers/add_consumer.html', {'form': form})


@login_required
def edit_consumer(request, consumer_id):
    consumer = get_object_or_404(Consumer, id=consumer_id)
    if request.method == 'POST':
        form = ConsumerForm(request.POST, instance=consumer)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Consumer updated successfully!")
            return redirect('consumers:consumer_management')
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = ConsumerForm(instance=consumer)

    return render(request, 'consumers/edit_consumer.html', {'form': form, 'consumer': consumer})


@login_required
def consumer_list(request):
    """
    Enhanced consumer list view with filtering and statistics.
    """
    from datetime import datetime
    from django.db.models import Count

    # Base queryset with optimized queries
    consumers = Consumer.objects.select_related('barangay', 'purok', 'meter_brand').all()

    # Get all barangays for filter dropdown
    barangays = Barangay.objects.all().order_by('name')

    # Apply filters
    query = request.GET.get('q')
    barangay_filter = request.GET.get('barangay')
    status_filter = request.GET.get('status')

    if query:
        consumers = consumers.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(account_number__icontains=query) |
            Q(phone_number__icontains=query)
        )

    if barangay_filter:
        consumers = consumers.filter(barangay_id=barangay_filter)

    if status_filter:
        consumers = consumers.filter(status=status_filter)

    # Calculate statistics
    total_consumers = Consumer.objects.count()
    connected_count = Consumer.objects.filter(status='active').count()
    disconnected_count = Consumer.objects.filter(status='disconnected').count()

    # Consumers registered this month
    current_month = datetime.now().month
    current_year = datetime.now().year
    this_month_count = Consumer.objects.filter(
        registration_date__month=current_month,
        registration_date__year=current_year
    ).count()

    return render(request, 'consumers/consumer_list.html', {
        'consumers': consumers,
        'barangays': barangays,
        'total_consumers': total_consumers,
        'connected_count': connected_count,
        'disconnected_count': disconnected_count,
        'this_month_count': this_month_count,
    })


def consumer_detail(request, consumer_id):
    consumer = get_object_or_404(Consumer, id=consumer_id)
    latest_bills = consumer.bills.filter(status='Pending').order_by('-billing_period')[:3]
    return render(request, 'consumers/consumer_detail.html', {
        'consumer': consumer,
        'latest_bills': latest_bills
    })
# consumers/views.py

# ... other imports ...

# ... other view functions ...

# ... other imports ...


@login_required
def reports(request):
    """
    Simplified reports view - displays reports inline on the page.
    No AJAX, no modals, just simple form submission and display.
    """
    from datetime import datetime
    from calendar import month_name

    # Get parameters from GET or POST
    report_type = request.GET.get('report_type') or request.POST.get('report_type', 'revenue')
    month_year = request.GET.get('month_year') or request.POST.get('month_year')

    # Default to current month/year
    now = datetime.now()
    if month_year:
        try:
            selected_year = int(month_year.split('-')[0])
            selected_month = int(month_year.split('-')[1])
        except:
            selected_year = now.year
            selected_month = now.month
    else:
        selected_year = now.year
        selected_month = now.month

    # Format month/year for display
    month_year_value = f"{selected_year}-{selected_month:02d}"
    month_display = f"{month_name[selected_month]} {selected_year}"

    # Initialize report data
    report_data = None
    report_title = ""
    total_amount = 0
    record_count = 0

    # Generate report based on type
    if report_type == 'revenue':
        report_title = f"Revenue Report - {month_display}"
        report_data = Payment.objects.filter(
            payment_date__year=selected_year,
            payment_date__month=selected_month
        ).select_related('bill__consumer').order_by('payment_date')

        total_amount = report_data.aggregate(total=Sum('amount_paid'))['total'] or 0
        record_count = report_data.count()

    elif report_type == 'delinquency':
        report_title = f"Delinquent Accounts Report - {month_display}"
        report_data = Bill.objects.filter(
            billing_period__year=selected_year,
            billing_period__month=selected_month,
            status__in=['Pending', 'Overdue']
        ).select_related('consumer', 'consumer__barangay').order_by('consumer__account_number')

        total_amount = report_data.aggregate(total=Sum('total_amount'))['total'] or 0
        record_count = report_data.count()

    elif report_type == 'summary':
        report_title = f"Payment Summary Report - {month_display}"
        report_data = Payment.objects.filter(
            payment_date__year=selected_year,
            payment_date__month=selected_month
        ).values('bill__consumer__account_number').annotate(
            bill__consumer__full_name=Concat(
                'bill__consumer__first_name',
                Value(' '),
                'bill__consumer__middle_name',
                Value(' '),
                'bill__consumer__last_name'
            ),
            total_paid=Sum('amount_paid'),
            payment_count=Count('id')
        ).order_by('bill__consumer__account_number')

        total_amount = report_data.aggregate(total=Sum('total_paid'))['total'] or 0
        record_count = report_data.count()

    context = {
        'report_type': report_type,
        'month_year_value': month_year_value,
        'month_display': month_display,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'report_title': report_title,
        'report_data': report_data,
        'total_amount': total_amount,
        'record_count': record_count,
    }

    return render(request, 'consumers/reports.html', context)


@login_required
def export_report_excel(request):
    """Export report as Excel (.xlsx) file with formatting"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from io import BytesIO

    report_type = request.GET.get('report_type', 'revenue')
    month_year = request.GET.get('month_year')

    if not month_year:
        return HttpResponse("Month/Year parameter required", status=400)

    selected_year = int(month_year.split('-')[0])
    selected_month = int(month_year.split('-')[1])

    # Create workbook
    wb = Workbook()
    ws = wb.active

    # Month name for display
    from calendar import month_name
    month_display = month_name[selected_month]

    # Styling
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    title_font = Font(bold=True, size=14)
    total_font = Font(bold=True, size=11)
    total_fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    if report_type == 'revenue':
        # Revenue Report
        ws.title = f"Revenue {month_display} {selected_year}"

        # Title
        ws['A1'] = "BALILIHAN WATERWORKS - REVENUE REPORT"
        ws['A1'].font = title_font
        ws['A2'] = f"Period: {month_display} {selected_year}"
        ws['A3'] = f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}"

        # Headers
        headers = ['OR Number', 'Consumer Name', 'Account Number', 'Payment Date', 'Amount Paid', 'Change Given', 'Total Received']
        ws.append([])  # Empty row
        ws.append(headers)

        header_row = ws[5]
        for cell in header_row:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = border

        # Data
        payments = Payment.objects.filter(
            payment_date__year=selected_year,
            payment_date__month=selected_month
        ).select_related('bill__consumer').order_by('payment_date')

        total_amount = 0
        total_change = 0
        total_received = 0

        for payment in payments:
            consumer = payment.bill.consumer
            ws.append([
                payment.or_number,
                consumer.full_name,
                consumer.account_number,
                payment.payment_date.strftime('%Y-%m-%d'),
                float(payment.amount_paid),
                float(payment.change),
                float(payment.received_amount)
            ])
            total_amount += payment.amount_paid
            total_change += payment.change
            total_received += payment.received_amount

        # Total row
        total_row = ws.max_row + 1
        ws[f'A{total_row}'] = 'TOTAL'
        ws[f'A{total_row}'].font = total_font
        ws[f'E{total_row}'] = float(total_amount)
        ws[f'F{total_row}'] = float(total_change)
        ws[f'G{total_row}'] = float(total_received)

        for col in ['A', 'E', 'F', 'G']:
            ws[f'{col}{total_row}'].font = total_font
            ws[f'{col}{total_row}'].fill = total_fill
            ws[f'{col}{total_row}'].border = border

        # Format currency columns
        for row in range(6, ws.max_row + 1):
            for col in ['E', 'F', 'G']:
                ws[f'{col}{row}'].number_format = '₱#,##0.00'
                ws[f'{col}{row}'].border = border
                ws[f'{col}{row}'].alignment = Alignment(horizontal='right')

        filename = f"Revenue_Report_{month_display}_{selected_year}.xlsx"

    elif report_type == 'delinquency':
        # Delinquency Report
        ws.title = f"Delinquency {month_display}"

        # Title
        ws['A1'] = "BALILIHAN WATERWORKS - DELINQUENT ACCOUNTS REPORT"
        ws['A1'].font = title_font
        ws['A2'] = f"Period: {month_display} {selected_year}"
        ws['A3'] = f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}"

        # Headers
        headers = ['Account Number', 'Consumer Name', 'Barangay', 'Billing Period', 'Due Date', 'Amount Due', 'Status']
        ws.append([])
        ws.append(headers)

        header_row = ws[5]
        for cell in header_row:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = border

        # Data
        bills = Bill.objects.filter(
            billing_period__year=selected_year,
            billing_period__month=selected_month,
            status__in=['Pending', 'Overdue']
        ).select_related('consumer__barangay').order_by('consumer__account_number')

        total_due = 0

        for bill in bills:
            consumer = bill.consumer
            ws.append([
                consumer.account_number,
                consumer.full_name,
                consumer.barangay.name if consumer.barangay else 'N/A',
                bill.billing_period.strftime('%B %Y'),
                bill.due_date.strftime('%Y-%m-%d'),
                float(bill.total_amount),
                bill.status
            ])
            total_due += bill.total_amount

        # Total row
        total_row = ws.max_row + 1
        ws[f'A{total_row}'] = 'TOTAL DELINQUENT AMOUNT'
        ws[f'A{total_row}'].font = total_font
        ws[f'F{total_row}'] = float(total_due)
        ws[f'F{total_row}'].font = total_font
        ws[f'F{total_row}'].fill = total_fill
        ws[f'F{total_row}'].border = border
        ws[f'F{total_row}'].number_format = '₱#,##0.00'

        # Format currency column
        for row in range(6, ws.max_row):
            ws[f'F{row}'].number_format = '₱#,##0.00'
            ws[f'F{row}'].border = border
            ws[f'F{row}'].alignment = Alignment(horizontal='right')
            for col in ['A', 'B', 'C', 'D', 'E', 'G']:
                ws[f'{col}{row}'].border = border

        filename = f"Delinquency_Report_{month_display}_{selected_year}.xlsx"

    elif report_type == 'summary':
        # Summary Report
        ws.title = f"Summary {month_display}"

        # Title
        ws['A1'] = "BALILIHAN WATERWORKS - PAYMENT SUMMARY REPORT"
        ws['A1'].font = title_font
        ws['A2'] = f"Period: {month_display} {selected_year}"
        ws['A3'] = f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}"

        # Headers
        headers = ['Account Number', 'Consumer Name', 'Total Amount Paid', 'Number of Payments']
        ws.append([])
        ws.append(headers)

        header_row = ws[5]
        for cell in header_row:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = border

        # Data
        summary_data = Payment.objects.filter(
            payment_date__year=selected_year,
            payment_date__month=selected_month
        ).values('bill__consumer__account_number').annotate(
            bill__consumer__full_name=Concat(
                'bill__consumer__first_name',
                Value(' '),
                'bill__consumer__middle_name',
                Value(' '),
                'bill__consumer__last_name'
            ),
            total_paid=Sum('amount_paid'),
            count=Count('id')
        ).order_by('bill__consumer__account_number')

        total_amount = 0
        total_count = 0

        for item in summary_data:
            ws.append([
                item['bill__consumer__account_number'],
                item['bill__consumer__full_name'],
                float(item['total_paid']),
                item['count']
            ])
            total_amount += item['total_paid']
            total_count += item['count']

        # Total row
        total_row = ws.max_row + 1
        ws[f'A{total_row}'] = 'TOTAL'
        ws[f'A{total_row}'].font = total_font
        ws[f'C{total_row}'] = float(total_amount)
        ws[f'D{total_row}'] = total_count

        for col in ['A', 'B', 'C', 'D']:
            ws[f'{col}{total_row}'].font = total_font
            ws[f'{col}{total_row}'].fill = total_fill
            ws[f'{col}{total_row}'].border = border

        # Format currency column
        for row in range(6, ws.max_row + 1):
            ws[f'C{row}'].number_format = '₱#,##0.00'
            ws[f'C{row}'].alignment = Alignment(horizontal='right')
            for col in ['A', 'B', 'C', 'D']:
                ws[f'{col}{row}'].border = border

        filename = f"Payment_Summary_{month_display}_{selected_year}.xlsx"

    else:
        return HttpResponse("Invalid report type", status=400)

    # Auto-size columns
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width

    # Save to response
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


# ... other view functions ...
# ======================
# AJAX
# ======================

@login_required
def load_puroks(request):
    barangay_id = request.GET.get('barangay_id')
    puroks = Purok.objects.filter(barangay_id=barangay_id).order_by('name')
    purok_list = [{'id': p.id, 'name': p.name} for p in puroks]
    return JsonResponse(purok_list, safe=False)


# ======================
# METER READINGS (CORRECTED)
# ======================






def get_consumer_display_id(consumer):
    """Returns formatted ID like 'bw-00001' based on consumer.id"""
    return f"bw-{consumer.id:05d}"



@login_required
def meter_reading_overview(request):
    today = date.today()
    current_month = today.replace(day=1)

    # Get all barangays, annotate total consumers, and ORDER BY name for alphabetical sorting
    barangays = Barangay.objects.annotate(
        total_consumers=Count('consumer', distinct=True)
    ).order_by('name')  # 👈 This is the fix!

    barangay_data = []
    for b in barangays:
        consumer_ids = list(Consumer.objects.filter(barangay=b).values_list('id', flat=True))
        if not consumer_ids:
            ready = not_updated = 0
        else:
            ready = MeterReading.objects.filter(
                consumer_id__in=consumer_ids,
                reading_date__gte=current_month,
                is_confirmed=False
            ).count()

            updated_consumers = MeterReading.objects.filter(
                consumer_id__in=consumer_ids,
                reading_date__gte=current_month
            ).values_list('consumer_id', flat=True).distinct()
            not_updated = len(consumer_ids) - len(set(updated_consumers))

        barangay_data.append({
            'barangay': b,
            'ready_to_confirm': ready,
            'not_yet_updated': not_updated,
            'total_consumers': b.total_consumers,
        })

    # Calculate summary statistics for the overview page
    total_barangays = len(barangay_data)
    total_consumers_sum = sum(item['total_consumers'] for item in barangay_data)
    total_ready_sum = sum(item['ready_to_confirm'] for item in barangay_data)
    total_pending_sum = sum(item['not_yet_updated'] for item in barangay_data)

    return render(request, 'consumers/meter_reading_overview.html', {
        'barangay_data': barangay_data,
        'current_month': current_month,
        'total_barangays': total_barangays,
        'total_consumers_sum': total_consumers_sum,
        'total_ready_sum': total_ready_sum,
        'total_pending_sum': total_pending_sum,
    })

# ───────────────────────────────────────
# NEW: Barangay-Specific Readings (Enhanced)
# Shows the latest reading per consumer in the barangay,
# regardless of reading date or confirmation status.
# ───────────────────────────────────────
# consumers/views.py

@login_required
def barangay_meter_readings(request, barangay_id):
    barangay = get_object_or_404(Barangay, id=barangay_id)
    today = date.today()

    # Get all consumers in this barangay
    consumers = Consumer.objects.filter(barangay=barangay).select_related('barangay').order_by('id')

    readings_with_data = []
    for consumer in consumers:
        # Get latest reading for this consumer
        latest_reading = MeterReading.objects.filter(consumer=consumer).order_by('-reading_date').first()
        
        if latest_reading:
            # Find previous confirmed reading
            prev = MeterReading.objects.filter(
                consumer=consumer,
                is_confirmed=True,
                reading_date__lt=latest_reading.reading_date
            ).order_by('-reading_date').first()
            
            consumption = None
            if prev:
                consumption = latest_reading.reading_value - prev.reading_value
        else:
            latest_reading = None
            prev = None
            consumption = None

        readings_with_data.append({
            'consumer': consumer,
            'reading': latest_reading,
            'prev_reading': prev,
            'consumption': consumption,
            'display_id': get_consumer_display_id(consumer),
        })

    return render(request, 'consumers/barangay_meter_readings.html', {
        'barangay': barangay,
        'readings': readings_with_data,
        'today': today,
    })


# ───────────────────────────────────────
# NEW: Confirm All Readings in Barangay
# ───────────────────────────────────────
@login_required
def confirm_all_readings(request, barangay_id):
    if request.method != "POST":
        return redirect('consumers:barangay_meter_readings', barangay_id=barangay_id)

    barangay = get_object_or_404(Barangay, id=barangay_id)
    readings_to_confirm = MeterReading.objects.filter(
        consumer__barangay=barangay,
        is_confirmed=False
    ).select_related('consumer')

    success_count = 0
    for reading in readings_to_confirm:
        try:
            prev = MeterReading.objects.filter(
                consumer=reading.consumer,
                is_confirmed=True,
                reading_date__lt=reading.reading_date
            ).order_by('-reading_date').first()

            if not prev:
                first = MeterReading.objects.filter(consumer=reading.consumer).order_by('reading_date').first()
                if not first or first.id == reading.id:
                    continue
                prev = first

            if reading.reading_value < prev.reading_value:
                continue

            # Get system settings and determine rate based on usage type
            setting = SystemSetting.objects.first()
            if setting:
                # Use appropriate rate based on consumer's usage type
                if reading.consumer.usage_type == 'commercial':
                    rate = setting.commercial_rate_per_cubic
                else:  # residential or default
                    rate = setting.residential_rate_per_cubic
                fixed = setting.fixed_charge
            else:
                # Fallback to defaults if no settings exist
                rate = Decimal('22.50')
                fixed = Decimal('50.00')

            cons = reading.reading_value - prev.reading_value
            total = (Decimal(cons) * rate) + fixed

            Bill.objects.create(
                consumer=reading.consumer,
                previous_reading=prev,
                current_reading=reading,
                billing_period=reading.reading_date.replace(day=1),
                due_date=reading.reading_date.replace(day=20),
                consumption=cons,
                rate_per_cubic=rate,
                fixed_charge=fixed,
                total_amount=total,
                status='Pending'
            )
            reading.is_confirmed = True
            reading.save()
            success_count += 1
        except Exception:
            continue

    messages.success(request, f"✅ {success_count} readings confirmed.")
    return redirect('consumers:barangay_meter_readings', barangay_id=barangay_id)


# ───────────────────────────────────────
# NEW: Export to Excel
# ───────────────────────────────────────
@login_required
def export_barangay_readings(request, barangay_id):
    barangay = get_object_or_404(Barangay, id=barangay_id)
    current_month = date.today().replace(day=1)

    # Get latest reading per consumer in this barangay
    consumer_ids = Consumer.objects.filter(barangay=barangay).values_list('id', flat=True)
    if not consumer_ids:
        readings = MeterReading.objects.none()
    else:
        latest_date_subq = MeterReading.objects.filter(
            consumer=OuterRef('pk')
        ).order_by().values('consumer').annotate(
            max_date=Max('reading_date')
        ).values('max_date')[:1]

        readings = MeterReading.objects.select_related('consumer').filter(
            consumer__barangay=barangay,
            reading_date=Subquery(latest_date_subq)
        ).order_by('consumer__id')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{barangay.name} Readings"

    headers = [
        'ID Number',           # ← Changed from "Account ID"
        'Consumer Name',
        'Current',
        'Previous',
        'Consumption (m³)',
        'Date',
        'Status'
    ]
    ws.append(headers)

    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    for col in range(1, len(headers) + 1):
        ws.cell(1, col).fill = header_fill
        ws.cell(1, col).font = header_font

    for r in readings:
        prev = MeterReading.objects.filter(
            consumer=r.consumer,
            is_confirmed=True,
            reading_date__lt=r.reading_date
        ).order_by('-reading_date').first()
        cons = (r.reading_value - prev.reading_value) if prev else '—'
        display_id = get_consumer_display_id(r.consumer)

        ws.append([
            display_id,
            f"{r.consumer.first_name} {r.consumer.last_name}",
            r.reading_value,
            prev.reading_value if prev else '—',
            cons,
            r.reading_date.strftime('%Y-%m-%d'),
            'Confirmed' if r.is_confirmed else 'Pending'
        ])

    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 30)
        ws.column_dimensions[column].width = adjusted_width

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=Readings_{barangay.name}_{current_month.strftime("%Y-%m")}.xlsx'
    wb.save(response)
    return response


# ───────────────────────────────────────
# YOUR ORIGINAL VIEWS (UNCHANGED)
# ───────────────────────────────────────

# consumers/views.py

@login_required
def meter_readings(request):
    """
    Display the most recent meter reading for each consumer.
    Calculates consumption based on the latest *confirmed* previous reading
    for the *same consumer* that occurred *before* the current reading's date.
    """
    if request.method == "POST":
        consumer_id = request.POST.get('consumer')
        reading_value = request.POST.get('reading_value')
        reading_date_str = request.POST.get('reading_date')
        source = request.POST.get('source', 'manual')

        # 🔒 Validate required fields
        if not all([consumer_id, reading_value, reading_date_str]):
            messages.error(request, "All fields are required.")
            return redirect('consumers:meter_readings')

        try:
            reading_date = date.fromisoformat(reading_date_str)
            if reading_date > date.today():
                messages.error(request, "Reading date cannot be in the future.")
                return redirect('consumers:meter_readings')

            reading_value = int(reading_value)
            if reading_value < 0:
                messages.error(request, "Reading value must be a non-negative number.")
                return redirect('consumers:meter_readings')

            consumer = Consumer.objects.get(id=consumer_id)

            # 🔒 Prevent duplicate on same date
            existing = MeterReading.objects.filter(
                consumer=consumer,
                reading_date=reading_date
            ).first()

            if existing:
                if existing.is_confirmed:
                    messages.error(request, f"Reading on {reading_date} is already confirmed and cannot be updated.")
                    return redirect('consumers:meter_readings')
                existing.reading_value = reading_value
                existing.source = source
                existing.save()
                messages.success(request, f"✅ Reading updated for {consumer} on {reading_date}.")
            else:
                # ➕ Create new reading
                MeterReading.objects.create(
                    consumer=consumer,
                    reading_date=reading_date,
                    reading_value=reading_value,
                    source=source,
                    is_confirmed=False
                )
                messages.success(request, f"✅ New meter reading added for {consumer}!")

        except ValueError:
            messages.error(request, "Invalid date or reading value.")
        except Consumer.DoesNotExist:
            messages.error(request, "Selected consumer does not exist.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return redirect('consumers:meter_readings')

    # ✅ GET: Fetch the most recent reading for each consumer
    # Use a subquery to get the maximum reading_date for each consumer
    # This query gets the most recent reading for each consumer
    latest_readings = MeterReading.objects.select_related(
        'consumer',
        'consumer__barangay',
        'consumer__purok'
    ).order_by('consumer', '-reading_date') # Order by consumer first, then date descending

    # Use a list to store the processed readings with their calculated data
    readings_with_data = []

    # Dictionary to keep track of the latest confirmed reading seen for each consumer
    # Key: consumer.id, Value: MeterReading object (the last confirmed one found so far while iterating)
    latest_confirmed_per_consumer = {}

    for r in latest_readings:
        # Check if the current reading (r) is confirmed. If so, update the dictionary.
        if r.is_confirmed:
            latest_confirmed_per_consumer[r.consumer.id] = r

        # Find the PREVIOUS confirmed reading specifically for THIS reading (r)
        # Look for the latest confirmed reading for the same consumer that happened BEFORE r.reading_date
        prev_confirmed_for_current = MeterReading.objects.filter(
            consumer=r.consumer,
            is_confirmed=True,
            reading_date__lt=r.reading_date
        ).order_by('-reading_date').first()

        consumption = None
        if prev_confirmed_for_current:
            # Calculate consumption based on the specific previous confirmed reading found
            if r.reading_value >= prev_confirmed_for_current.reading_value:
                consumption = r.reading_value - prev_confirmed_for_current.reading_value
            else:
                # This should ideally not happen if readings are non-decreasing, but handle gracefully
                consumption = 0 # Or set to None and display an error/warning if needed
        else:
            # If no previous confirmed reading exists, treat it as the first reading.
            # Consumption is the current reading value itself (since previous is 0).
            # This handles the case where the Android app sends the very first reading for a consumer.
            consumption = r.reading_value

        # Append the reading object along with its calculated previous reading and consumption
        readings_with_data.append({
            'reading': r,
            'prev_reading': prev_confirmed_for_current, # This is the reading object itself
            'consumption': consumption
        })

    # Fetch consumers for the dropdown in the form (if you add the form back later)
    consumers = Consumer.objects.select_related('barangay', 'purok').all()
    return render(request, 'consumers/meter_readings.html', {
        'readings': readings_with_data,
        'consumers': consumers,
        'today': date.today(),  # ✅ For max date in form (if form is added back)
    })


# consumers/views.py

@login_required
def confirm_reading(request, reading_id):
    """
    Confirm a meter reading and generate a bill for the consumer.
    If this is the first reading for the consumer, the consumption is calculated as the current reading value.
    """
    current = get_object_or_404(MeterReading, id=reading_id)
    consumer = current.consumer
    barangay_id = consumer.barangay.id

    # Check if the reading is already confirmed
    if current.is_confirmed:
        messages.error(request, "This reading is already confirmed and billed.")
        return redirect('consumers:barangay_meter_readings', barangay_id=barangay_id)

    # Validate date
    if current.reading_date > date.today():
        messages.error(request, "Reading date cannot be in the future.")
        return redirect('consumers:barangay_meter_readings', barangay_id=barangay_id)

    # Check for duplicates on the same date
    duplicate = MeterReading.objects.filter(
        consumer=consumer,
        reading_date=current.reading_date
    ).exclude(id=current.id).first()
    if duplicate:
        messages.error(request, f"Another reading already exists on {current.reading_date}.")
        return redirect('consumers:barangay_meter_readings', barangay_id=barangay_id)

    # Find the previous confirmed reading
    previous = MeterReading.objects.filter(
        consumer=consumer,
        is_confirmed=True,
        reading_date__lt=current.reading_date
    ).order_by('-reading_date').first()

    # Calculate consumption
    if previous:
        # Use the previous confirmed reading for calculation
        if current.reading_value < previous.reading_value:
            messages.error(request, f"Current reading ({current.reading_value}) < previous ({previous.reading_value}).")
            return redirect('consumers:barangay_meter_readings', barangay_id=barangay_id)
        elif current.reading_value == previous.reading_value:
            messages.warning(request, "Zero consumption. Bill will be generated.")
        consumption = current.reading_value - previous.reading_value
    else:
        # This is the first reading for the consumer, so treat previous as 0
        # Consumption is the full current reading value
        consumption = current.reading_value

    # Generate bill
    try:
        setting = SystemSetting.objects.first()

        # Apply correct rate based on consumer usage type
        if setting:
            if consumer.usage_type == 'Residential':
                rate = setting.residential_rate_per_cubic
            else:  # Commercial
                rate = setting.commercial_rate_per_cubic
            fixed_charge = setting.fixed_charge
            billing_day = setting.billing_day_of_month
            due_day = setting.due_day_of_month
        else:
            # Fallback rates if SystemSetting doesn't exist
            rate = Decimal('22.50') if consumer.usage_type == 'Residential' else Decimal('25.00')
            fixed_charge = Decimal('50.00')
            billing_day = 1
            due_day = 20

        total_amount = (Decimal(consumption) * rate) + fixed_charge

        Bill.objects.create(
            consumer=consumer,
            previous_reading=previous, # Will be None if this is the first reading
            current_reading=current,
            billing_period=current.reading_date.replace(day=billing_day),
            due_date=current.reading_date.replace(day=due_day),
            consumption=consumption,
            rate_per_cubic=rate,
            fixed_charge=fixed_charge,
            total_amount=total_amount,
            status='Pending'
        )

        # Mark the reading as confirmed
        current.is_confirmed = True
        current.save()

        messages.success(request, f"✅ Bill successfully generated for {get_consumer_display_id(consumer)}!")

    except Exception as e:
        messages.error(request, f"Failed to generate bill: {str(e)}")
        return redirect('consumers:barangay_meter_readings', barangay_id=barangay_id)

    return redirect('consumers:barangay_meter_readings', barangay_id=barangay_id)

# consumers/views.py

@login_required
def confirm_selected_readings(request, barangay_id):
    if request.method != "POST":
        return redirect('consumers:barangay_meter_readings', barangay_id=barangay_id)

    barangay = get_object_or_404(Barangay, id=barangay_id)
    reading_ids = request.POST.getlist('reading_ids')
    consumer_ids = request.POST.getlist('consumer_ids')  # For consumers with no reading (optional)

    success_count = 0

    # Process selected readings
    for reading_id in reading_ids:
        try:
            reading = MeterReading.objects.get(id=reading_id)
            if reading.is_confirmed:
                continue

            consumer = reading.consumer
            prev = MeterReading.objects.filter(
                consumer=consumer,
                is_confirmed=True,
                reading_date__lt=reading.reading_date
            ).order_by('-reading_date').first()

            if not prev:
                first = MeterReading.objects.filter(consumer=consumer).order_by('reading_date').first()
                if not first or first.id == reading.id:
                    continue
                prev = first

            if reading.reading_value < prev.reading_value:
                continue

            setting = SystemSetting.objects.first()
            rate = setting.rate_per_cubic if setting else Decimal('22.50')
            fixed = Decimal('50.00')
            cons = reading.reading_value - prev.reading_value
            total = (Decimal(cons) * rate) + fixed

            Bill.objects.create(
                consumer=consumer,
                previous_reading=prev,
                current_reading=reading,
                billing_period=reading.reading_date.replace(day=1),
                due_date=reading.reading_date.replace(day=20),
                consumption=cons,
                rate_per_cubic=rate,
                fixed_charge=fixed,
                total_amount=total,
                status='Pending'
            )
            reading.is_confirmed = True
            reading.save()
            success_count += 1
        except Exception:
            continue

    messages.success(request, f"✅ {success_count} readings confirmed.")
    return redirect('consumers:barangay_meter_readings', barangay_id=barangay_id)

# consumers/views.py

@login_required
def inquire(request):
    """
    Handles both:
    - GET: Area/consumer selection
    - POST: Payment processing
    """
    if request.method == "POST":
        # Handle payment submission
        bill_id = request.POST.get('bill_id')
        received_amount = request.POST.get('received_amount')

        if not bill_id or not received_amount:
            messages.error(request, "Missing bill or payment amount.")
            return redirect('consumers:payment_counter')

        try:
            bill = get_object_or_404(Bill, id=bill_id)
            received_amount = Decimal(received_amount)
            amount_due = bill.total_amount

            if received_amount < amount_due:
                messages.error(request, f"Insufficient payment. Amount due is ₱{amount_due}.")
                return redirect(request.get_full_path())  # Stay on same consumer

            # Create payment
            payment = Payment.objects.create(
                bill=bill,
                amount_paid=amount_due,
                received_amount=received_amount,
                change=received_amount - amount_due,
                payment_date=timezone.now(),
                or_number=f"OR-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            )

            # Mark bill as paid
            bill.status = 'Paid'
            bill.save()

            messages.success(request, f"Payment processed successfully! OR: {payment.or_number}")
            return redirect('consumers:payment_receipt', payment_id=payment.id)

        except (ValueError, InvalidOperation):
            messages.error(request, "Invalid payment amount.")
            return redirect(request.get_full_path())
        except Exception as e:
            messages.error(request, f"Error processing payment: {e}")
            return redirect(request.get_full_path())

    # ===== GET REQUEST (your existing logic) =====
    selected_barangay = request.GET.get('barangay')
    selected_purok = request.GET.get('purok')
    selected_consumer_id = request.GET.get('consumer')
    
    barangays = Barangay.objects.all()
    puroks = Purok.objects.none()
    consumers = Consumer.objects.none()
    consumer_bills = {}
    selected_consumer = None
    latest_bill = None

    if selected_consumer_id:
        selected_consumer = get_object_or_404(Consumer, id=selected_consumer_id)
        latest_bill = selected_consumer.bills.filter(status='Pending').order_by('-billing_period').first()

    if selected_barangay:
        puroks = Purok.objects.filter(barangay_id=selected_barangay)
        consumers = Consumer.objects.filter(barangay_id=selected_barangay)
        if selected_purok:
            consumers = consumers.filter(purok_id=selected_purok)
        for c in consumers:
            bill = c.bills.filter(status='Pending').order_by('-billing_period').first()
            consumer_bills[c.id] = bill

    context = {
        'barangays': barangays,
        'puroks': puroks,
        'consumers': consumers,
        'consumer_bills': consumer_bills,
        'selected_barangay': selected_barangay,
        'selected_purok': selected_purok,
        'selected_consumer': selected_consumer,
        'latest_bill': latest_bill,
    }
    return render(request, 'consumers/inquire.html', context)

@login_required
def payment_receipt(request, payment_id):
    """
    Display a printable official receipt for a payment.
    Ensures the payment exists and belongs to a valid bill/consumer.
    """
    payment = get_object_or_404(
        Payment.objects.select_related('bill__consumer'),
        id=payment_id
    )
    return render(request, 'consumers/receipt.html', {'payment': payment})

@login_required
def user_login_history(request):
    """
    Enhanced login history with filtering, search, and analytics.
    Restricted to superusers and admins for security.
    """
    from .decorators import admin_or_superuser_required
    from django.db.models import Count, Q
    from datetime import timedelta
    from django.core.paginator import Paginator

    # Security check - only admins and superusers
    if not (request.user.is_superuser or (hasattr(request.user, 'staffprofile') and request.user.staffprofile.role == 'admin')):
        messages.error(request, "Access Denied: Administrative privileges required to view login history.")
        return render(request, 'consumers/403.html', status=403)

    # Get filter parameters
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    method_filter = request.GET.get('method', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    # Base query
    login_events = UserLoginEvent.objects.select_related('user').all()

    # Apply filters
    if search_query:
        login_events = login_events.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(ip_address__icontains=search_query)
        )

    if status_filter:
        login_events = login_events.filter(status=status_filter)

    if method_filter:
        login_events = login_events.filter(login_method=method_filter)

    if date_from:
        login_events = login_events.filter(login_timestamp__gte=date_from)

    if date_to:
        from datetime import datetime
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
        date_to_end = date_to_obj.replace(hour=23, minute=59, second=59)
        login_events = login_events.filter(login_timestamp__lte=date_to_end)

    # Order by most recent
    login_events = login_events.order_by('-login_timestamp')

    # Analytics
    total_logins = login_events.count()
    successful_logins = login_events.filter(status='success').count()
    failed_logins = login_events.filter(status='failed').count()
    active_sessions = login_events.filter(status='success', logout_timestamp__isnull=True).count()

    # Recent activity (last 24 hours)
    last_24_hours = timezone.now() - timedelta(hours=24)
    recent_logins = login_events.filter(login_timestamp__gte=last_24_hours).count()

    # Top users
    top_users = User.objects.annotate(
        login_count=Count('userloginevent')
    ).filter(login_count__gt=0).order_by('-login_count')[:5]

    # Pagination
    paginator = Paginator(login_events, 25)  # 25 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'login_events': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'method_filter': method_filter,
        'date_from': date_from,
        'date_to': date_to,
        # Analytics
        'total_logins': total_logins,
        'successful_logins': successful_logins,
        'failed_logins': failed_logins,
        'active_sessions': active_sessions,
        'recent_logins': recent_logins,
        'top_users': top_users,
    }
    return render(request, 'consumers/user_login_history.html', context)


@login_required
def consumer_bill(request, consumer_id):
    """
    Display all bills for a specific consumer with summary statistics.
    Optimized with select_related to reduce database queries.
    """
    from django.db.models import Sum
    from datetime import datetime

    consumer = get_object_or_404(Consumer, id=consumer_id)
    bills = consumer.bills.select_related(
        'current_reading__consumer',
        'previous_reading__consumer'
    ).order_by('-billing_period')

    # Calculate summary statistics
    total_billed = bills.aggregate(total=Sum('total_amount'))['total'] or 0
    outstanding_balance = bills.filter(status='Pending').aggregate(total=Sum('total_amount'))['total'] or 0
    outstanding_balance += bills.filter(status='Overdue').aggregate(total=Sum('total_amount'))['total'] or 0

    return render(request, 'consumers/consumer_bill.html', {
        'consumer': consumer,
        'bills': bills,
        'total_billed': total_billed,
        'outstanding_balance': outstanding_balance,
        'today': datetime.now(),
    })


# ======================
# USER MANAGEMENT (SECURE)
# ======================

@login_required
def admin_verification(request):
    """
    Admin verification - requires password re-entry before accessing user management.
    Provides extra security layer for sensitive operations.
    """
    from .decorators import get_client_ip
    from django.contrib.auth import authenticate

    # Only superusers and admins can access this page
    if not (request.user.is_superuser or (hasattr(request.user, 'staffprofile') and request.user.staffprofile.role == 'admin')):
        messages.error(request, "Access Denied: Administrative privileges required.")
        return render(request, 'consumers/403.html', status=403)

    if request.method == 'POST':
        password = request.POST.get('password', '')
        destination = request.POST.get('destination', 'user_management')

        # Verify the password
        user = authenticate(username=request.user.username, password=password)

        if user is not None and user == request.user:
            # Password verified - store verification in session with timestamp
            request.session['admin_verified'] = True
            request.session['admin_verified_time'] = timezone.now().isoformat()

            # Log the verification
            UserLoginEvent.objects.create(
                user=request.user,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                login_method='web',
                status='success',
                session_key=request.session.session_key
            )

            messages.success(request, "Admin verification successful!")

            # Redirect to requested destination
            if destination == 'django_admin':
                return redirect('/admin/')
            else:
                return redirect('consumers:user_management')
        else:
            # Failed verification
            messages.error(request, "Incorrect password. Verification failed.")
            UserLoginEvent.objects.create(
                user=request.user,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                login_method='web',
                status='failed'
            )

    return render(request, 'consumers/admin_verification.html')


@login_required
def user_management(request):
    """
    Custom user management interface with enhanced security.
    Only accessible by superusers with admin verification.
    """
    from .decorators import superuser_required, get_client_ip
    from django.db.models import Count, Q
    from django.core.paginator import Paginator

    # Security check - only superusers and admins
    if not (request.user.is_superuser or (hasattr(request.user, 'staffprofile') and request.user.staffprofile.role == 'admin')):
        messages.error(request, "Access Denied: Administrative privileges required to manage users.")
        return render(request, 'consumers/403.html', status=403)

    # Check if admin verification is required and not expired
    admin_verified = request.session.get('admin_verified', False)
    admin_verified_time_str = request.session.get('admin_verified_time')

    # Check if verification has expired (15 minutes = 900 seconds)
    verification_expired = False
    if admin_verified and admin_verified_time_str:
        try:
            from datetime import timedelta
            verified_time = timezone.datetime.fromisoformat(admin_verified_time_str)
            if timezone.is_naive(verified_time):
                verified_time = timezone.make_aware(verified_time)
            time_since_verification = timezone.now() - verified_time
            if time_since_verification > timedelta(minutes=15):
                verification_expired = True
                # Clear expired verification
                request.session.pop('admin_verified', None)
                request.session.pop('admin_verified_time', None)
        except (ValueError, TypeError):
            verification_expired = True

    if not admin_verified or verification_expired:
        # Redirect to verification page
        if verification_expired:
            messages.warning(request, "Admin verification expired. Please verify again.")
        else:
            messages.warning(request, "Admin verification required to access User Management.")
        return redirect('consumers:admin_verification')

    # Get filter parameters
    search_query = request.GET.get('search', '').strip()
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')

    # Base query
    users = User.objects.all()

    # Apply filters
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    if role_filter:
        if role_filter == 'superuser':
            users = users.filter(is_superuser=True)
        elif role_filter == 'staff':
            users = users.filter(is_staff=True, is_superuser=False)
        elif role_filter == 'regular':
            users = users.filter(is_staff=False, is_superuser=False)

    if status_filter:
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'inactive':
            users = users.filter(is_active=False)

    # Annotate with login count
    users = users.annotate(
        login_count=Count('userloginevent')
    ).select_related('staffprofile').order_by('-date_joined')

    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    superusers = User.objects.filter(is_superuser=True).count()

    # Available barangays for assignment
    barangays = Barangay.objects.all()

    context = {
        'users': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'superusers': superusers,
        'barangays': barangays,
    }
    return render(request, 'consumers/user_management.html', context)


@login_required
def create_user(request):
    """Create a new user with security validations."""
    from .decorators import check_password_strength
    from django.contrib.auth.hashers import make_password

    if not (request.user.is_superuser or (hasattr(request.user, 'staffprofile') and request.user.staffprofile.role == 'admin')):
        messages.error(request, "Access Denied: Administrative privileges required to create users.")
        return redirect('consumers:user_management')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        is_staff = request.POST.get('is_staff') == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'
        assigned_barangay_id = request.POST.get('assigned_barangay')
        role = request.POST.get('role', 'field_staff')

        # Validation
        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect('consumers:user_management')

        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('consumers:user_management')

        # Check password strength
        is_strong, msg = check_password_strength(password)
        if not is_strong:
            messages.error(request, f"Weak password: {msg}")
            return redirect('consumers:user_management')

        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' already exists.")
            return redirect('consumers:user_management')

        # Only superusers can create other superusers
        if is_superuser and not request.user.is_superuser:
            messages.error(request, "Access Denied: Only superusers can create other superusers.")
            return redirect('consumers:user_management')

        try:
            # Create user
            user = User.objects.create(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                is_staff=is_staff,
                is_superuser=is_superuser,
                is_active=True
            )
            user.set_password(password)
            user.save()

            # Create staff profile if barangay assigned
            if assigned_barangay_id:
                barangay = Barangay.objects.get(id=assigned_barangay_id)
                StaffProfile.objects.create(
                    user=user,
                    assigned_barangay=barangay,
                    role=role
                )

            messages.success(request, f"User '{username}' created successfully!")
            return redirect('consumers:user_management')

        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
            return redirect('consumers:user_management')

    return redirect('consumers:user_management')


@login_required
def edit_user(request, user_id):
    """Edit user details with security checks."""
    if not (request.user.is_superuser or (hasattr(request.user, 'staffprofile') and request.user.staffprofile.role == 'admin')):
        messages.error(request, "Access Denied: Administrative privileges required to edit users.")
        return redirect('consumers:user_management')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_active = request.POST.get('is_active') == 'on'

        # Only allow changing superuser status if current user is superuser
        if request.user.is_superuser:
            user.is_superuser = request.POST.get('is_superuser') == 'on'

        user.save()

        # Update staff profile
        assigned_barangay_id = request.POST.get('assigned_barangay')
        role = request.POST.get('role', 'field_staff')

        if assigned_barangay_id:
            barangay = Barangay.objects.get(id=assigned_barangay_id)
            profile, created = StaffProfile.objects.get_or_create(user=user)
            profile.assigned_barangay = barangay
            profile.role = role
            profile.save()

        messages.success(request, f"User '{user.username}' updated successfully!")
        return redirect('consumers:user_management')

    return redirect('consumers:user_management')


@login_required
def delete_user(request, user_id):
    """Delete a user with confirmation."""
    if not (request.user.is_superuser or (hasattr(request.user, 'staffprofile') and request.user.staffprofile.role == 'admin')):
        messages.error(request, "Access Denied: Administrative privileges required to delete users.")
        return redirect('consumers:user_management')

    user = get_object_or_404(User, id=user_id)

    # Prevent self-deletion
    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('consumers:user_management')

    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"User '{username}' deleted successfully!")
        return redirect('consumers:user_management')

    return redirect('consumers:user_management')


@login_required
def reset_user_password(request, user_id):
    """Reset user password (superuser and admin)."""
    from .decorators import check_password_strength

    if not (request.user.is_superuser or (hasattr(request.user, 'staffprofile') and request.user.staffprofile.role == 'admin')):
        messages.error(request, "Access Denied: Administrative privileges required to reset passwords.")
        return redirect('consumers:user_management')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('consumers:user_management')

        # Check password strength
        is_strong, msg = check_password_strength(new_password)
        if not is_strong:
            messages.error(request, f"Weak password: {msg}")
            return redirect('consumers:user_management')

        user.set_password(new_password)
        user.save()
        messages.success(request, f"Password reset successfully for user '{user.username}'!")
        return redirect('consumers:user_management')

    return redirect('consumers:user_management')


# ===========================
# DATABASE DOCUMENTATION VIEW
# ===========================
@login_required
def database_documentation(request):
    """Display database schema, tables, and test data in a user-friendly UI."""

    # Get database statistics
    context = {
        # Table counts
        'total_consumers': Consumer.objects.count(),
        'total_barangays': Barangay.objects.count(),
        'total_puroks': Purok.objects.count(),
        'total_meter_brands': MeterBrand.objects.count(),
        'total_meter_readings': MeterReading.objects.count(),
        'total_bills': Bill.objects.count(),
        'total_payments': Payment.objects.count(),
        'total_users': User.objects.count(),

        # Sample data - Barangays
        'barangays': Barangay.objects.all().order_by('name')[:10],

        # Sample data - Puroks
        'puroks': Purok.objects.select_related('barangay').all()[:10],

        # Sample data - Meter Brands
        'meter_brands': MeterBrand.objects.all(),

        # Sample data - Consumers
        'consumers': Consumer.objects.select_related('barangay', 'purok', 'meter_brand').all()[:8],

        # Sample data - Meter Readings
        'meter_readings': MeterReading.objects.select_related('consumer').order_by('-reading_date')[:10],

        # Sample data - Bills
        'bills': Bill.objects.select_related('consumer', 'current_reading', 'previous_reading').order_by('-billing_period')[:10],

        # Sample data - Payments
        'payments': Payment.objects.select_related('bill', 'bill__consumer').order_by('-payment_date')[:10],

        # System Settings
        'system_settings': SystemSetting.objects.first(),
    }

    # Calculate sample billing amounts for display
    if context['system_settings']:
        settings = context['system_settings']
        # Residential example (15 m³)
        residential_consumption = 15
        residential_water_charge = settings.residential_rate_per_cubic * residential_consumption
        residential_total = residential_water_charge + settings.fixed_charge

        # Commercial example (30 m³)
        commercial_consumption = 30
        commercial_water_charge = settings.commercial_rate_per_cubic * commercial_consumption
        commercial_total = commercial_water_charge + settings.fixed_charge

        context.update({
            'residential_consumption': residential_consumption,
            'residential_water_charge': residential_water_charge,
            'residential_total': residential_total,
            'commercial_consumption': commercial_consumption,
            'commercial_water_charge': commercial_water_charge,
            'commercial_total': commercial_total,
        })

    # Database schema information
    context['database_tables'] = [
            {
                'name': 'Barangay',
                'model': 'consumers_barangay',
                'description': 'Stores barangay (village) information',
                'fields': [
                    {'name': 'id', 'type': 'INTEGER', 'constraints': 'PRIMARY KEY', 'description': 'Auto-increment ID'},
                    {'name': 'name', 'type': 'VARCHAR(100)', 'constraints': 'UNIQUE, NOT NULL', 'description': 'Barangay name'},
                ]
            },
            {
                'name': 'Purok',
                'model': 'consumers_purok',
                'description': 'Stores purok (zone) information within barangays',
                'fields': [
                    {'name': 'id', 'type': 'INTEGER', 'constraints': 'PRIMARY KEY', 'description': 'Auto-increment ID'},
                    {'name': 'name', 'type': 'VARCHAR(100)', 'constraints': 'NOT NULL', 'description': 'Purok name'},
                    {'name': 'barangay_id', 'type': 'INTEGER', 'constraints': 'FOREIGN KEY', 'description': 'Reference to Barangay'},
                ]
            },
            {
                'name': 'MeterBrand',
                'model': 'consumers_meterbrand',
                'description': 'Stores water meter brand information',
                'fields': [
                    {'name': 'id', 'type': 'INTEGER', 'constraints': 'PRIMARY KEY', 'description': 'Auto-increment ID'},
                    {'name': 'name', 'type': 'VARCHAR(100)', 'constraints': 'UNIQUE, NOT NULL', 'description': 'Meter brand name'},
                ]
            },
            {
                'name': 'Consumer',
                'model': 'consumers_consumer',
                'description': 'Main consumer information table with personal, household, and meter details',
                'fields': [
                    {'name': 'id', 'type': 'INTEGER', 'constraints': 'PRIMARY KEY', 'description': 'Auto-increment ID'},
                    {'name': 'account_number', 'type': 'VARCHAR(20)', 'constraints': 'UNIQUE, AUTO', 'description': 'Format: BW-XXXXX'},
                    {'name': 'first_name', 'type': 'VARCHAR(50)', 'constraints': 'NOT NULL', 'description': 'First name'},
                    {'name': 'middle_name', 'type': 'VARCHAR(50)', 'constraints': 'NULL', 'description': 'Middle name'},
                    {'name': 'last_name', 'type': 'VARCHAR(50)', 'constraints': 'NOT NULL', 'description': 'Last name'},
                    {'name': 'birth_date', 'type': 'DATE', 'constraints': 'NOT NULL', 'description': 'Date of birth'},
                    {'name': 'gender', 'type': 'VARCHAR(10)', 'constraints': 'NOT NULL', 'description': 'Male/Female/Other'},
                    {'name': 'phone_number', 'type': 'VARCHAR(15)', 'constraints': 'NOT NULL', 'description': 'Contact number'},
                    {'name': 'status', 'type': 'VARCHAR(20)', 'constraints': "DEFAULT 'active'", 'description': 'active/disconnected'},
                ]
            },
            {
                'name': 'MeterReading',
                'model': 'consumers_meterreading',
                'description': 'Stores meter reading records with confirmation status',
                'fields': [
                    {'name': 'id', 'type': 'INTEGER', 'constraints': 'PRIMARY KEY', 'description': 'Auto-increment ID'},
                    {'name': 'consumer_id', 'type': 'INTEGER', 'constraints': 'FOREIGN KEY', 'description': 'Reference to Consumer'},
                    {'name': 'reading_date', 'type': 'DATE', 'constraints': 'NOT NULL', 'description': 'Date of reading'},
                    {'name': 'reading_value', 'type': 'INTEGER', 'constraints': 'NOT NULL', 'description': 'Cumulative meter value'},
                    {'name': 'is_confirmed', 'type': 'BOOLEAN', 'constraints': 'DEFAULT FALSE', 'description': 'Confirmation status'},
                ]
            },
            {
                'name': 'Bill',
                'model': 'consumers_bill',
                'description': 'Stores billing information with consumption and payment status',
                'fields': [
                    {'name': 'id', 'type': 'INTEGER', 'constraints': 'PRIMARY KEY', 'description': 'Auto-increment ID'},
                    {'name': 'consumer_id', 'type': 'INTEGER', 'constraints': 'FOREIGN KEY', 'description': 'Reference to Consumer'},
                    {'name': 'billing_period', 'type': 'DATE', 'constraints': 'NOT NULL', 'description': 'First day of billing month'},
                    {'name': 'consumption', 'type': 'INTEGER', 'constraints': 'NOT NULL', 'description': 'Water consumption (m³)'},
                    {'name': 'total_amount', 'type': 'DECIMAL(10,2)', 'constraints': 'NOT NULL', 'description': 'Total bill amount'},
                    {'name': 'status', 'type': 'VARCHAR(20)', 'constraints': "DEFAULT 'Pending'", 'description': 'Pending/Paid/Overdue'},
                ]
            },
            {
                'name': 'Payment',
                'model': 'consumers_payment',
                'description': 'Records all payment transactions with OR numbers',
                'fields': [
                    {'name': 'id', 'type': 'INTEGER', 'constraints': 'PRIMARY KEY', 'description': 'Auto-increment ID'},
                    {'name': 'bill_id', 'type': 'INTEGER', 'constraints': 'FOREIGN KEY', 'description': 'Reference to Bill'},
                    {'name': 'amount_paid', 'type': 'DECIMAL(10,2)', 'constraints': 'NOT NULL', 'description': 'Bill amount'},
                    {'name': 'or_number', 'type': 'VARCHAR(50)', 'constraints': 'UNIQUE, AUTO', 'description': 'Official Receipt number'},
                    {'name': 'payment_date', 'type': 'DATETIME', 'constraints': 'AUTO', 'description': 'Payment timestamp'},
                ]
            },
            {
                'name': 'SystemSetting',
                'model': 'consumers_systemsetting',
                'description': 'System-wide configuration settings for billing rates',
                'fields': [
                    {'name': 'id', 'type': 'INTEGER', 'constraints': 'PRIMARY KEY', 'description': 'Auto-increment ID'},
                    {'name': 'residential_rate_per_cubic', 'type': 'DECIMAL(10,2)', 'constraints': 'DEFAULT 22.50', 'description': 'Residential rate (₱/m³)'},
                    {'name': 'commercial_rate_per_cubic', 'type': 'DECIMAL(10,2)', 'constraints': 'DEFAULT 25.00', 'description': 'Commercial rate (₱/m³)'},
                    {'name': 'fixed_charge', 'type': 'DECIMAL(10,2)', 'constraints': 'DEFAULT 50.00', 'description': 'Fixed monthly charge'},
                ]
            },
        ]

    return render(request, 'consumers/database_documentation.html', context)
