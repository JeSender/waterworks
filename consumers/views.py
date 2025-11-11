from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Max
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime, timedelta
from django.urls import reverse
from decimal import Decimal, InvalidOperation
from django.core.paginator import Paginator
import uuid
import json
import csv
from datetime import datetime, date
from .models import (
    Consumer, Barangay, Purok, MeterReading, Bill, SystemSetting, Payment, StaffProfile, UserLoginEvent
)
from .forms import ConsumerForm
import openpyxl
from openpyxl.styles import Font, PatternFill
from django.db.models import Count, Q, Max, OuterRef, Subquery
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# NEW: API View for submitting meter readings from the Android app (Updated to match app data format)
@csrf_exempt # Be careful with CSRF in production, consider using proper tokens for mobile apps
def api_submit_reading(request):
    """API endpoint for Android app to submit meter readings."""
    if request.method != 'POST':
        print("Error submitting reading: Method not allowed") # Add print here for clarity
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        # Parse JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))
        print(f"DEBUG: Received JSON  {data}") # Log the received data

        # Extract data from the request - MATCHING ANDROID APP FORMAT
        consumer_id = data.get('consumer_id') # Expecting consumer ID from app
        reading_value = data.get('reading')   # Expecting 'reading' key from app
        # Optional: Check if reading_date is sent, otherwise default to today
        reading_date_str = data.get('reading_date') # Expecting 'reading_date' key from app, can be None initially

        print(f"DEBUG: Parsed - consumer_id: {consumer_id}, reading_value: {reading_value}, reading_date: {reading_date_str}") # Log parsed values

        # Validate required fields (assuming reading_date is sent by the app now, or use today's date)
        if consumer_id is None or reading_value is None:
            error_msg = f"Missing required fields: consumer_id or reading. Received: consumer_id={consumer_id}, reading={reading_value}, reading_date={reading_date_str}"
            print(f"Error submitting reading: {error_msg}") # More detailed print
            return JsonResponse({'error': 'Missing required fields: consumer_id or reading'}, status=400)

        # Get the consumer based on ID (as sent by the app)
        try:
            consumer = Consumer.objects.get(id=consumer_id) # Use id instead of account_number
            print(f"DEBUG: Found consumer: {consumer}") # Log consumer lookup
        except Consumer.DoesNotExist:
            error_msg = f"Consumer not found for id: {consumer_id}"
            print(f"Error submitting reading: {error_msg}") # Print specific error
            return JsonResponse({'error': 'Consumer not found'}, status=404)

        # Determine the reading date
        if reading_date_str:
            # Parse the date string if provided by the app
            try:
                reading_date = timezone.datetime.strptime(reading_date_str, '%Y-%m-%d').date()
                print(f"DEBUG: Parsed date from app: {reading_date}") # Log date parsing
            except ValueError:
                error_msg = f"Invalid date format: {reading_date_str}. Expected YYYY-MM-DD."
                print(f"Error submitting reading: {error_msg}") # Print specific error
                return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)
        else:
            # Use the current date if no date is provided by the app
            print("DEBUG: No reading_date provided by app, using today's date.")
            reading_date = timezone.now().date()

        # Validate reading value (should be a positive number, handle potential float from app)
        try:
            # Convert to int, assuming the app sends an integer or a float that represents an integer
            # If the app sends a float representing a non-integer reading, this might need adjustment
            reading_value = int(reading_value) # Convert float to int
            if reading_value < 0:
                raise ValueError("Reading value cannot be negative")
            print(f"DEBUG: Validated reading value: {reading_value}") # Log value validation
        except (ValueError, TypeError):
            error_msg = f"Invalid reading value: {reading_value}. Must be a non-negative number."
            print(f"Error submitting reading: {error_msg}") # Print specific error
            return JsonResponse({'error': 'Invalid reading value. Must be a non-negative number.'}, status=400)

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
                print(f"Error submitting reading: {error_msg}")
                return JsonResponse({'error': error_msg}, status=400)
            else:
                # If it's unconfirmed, update the existing record
                existing_reading.reading_value = reading_value
                existing_reading.source = 'mobile_app' # Update source to reflect API submission
                existing_reading.save()
                print(f"Info: Updated existing unconfirmed reading {existing_reading.id} for {consumer.account_number} on {reading_date}.")
                # Return success response for update
                return JsonResponse({
                    'status': 'success',
                    'message': 'Meter reading updated successfully',
                    'reading_id': existing_reading.id,
                    'consumer_name': f"{consumer.first_name} {consumer.last_name}",
                    'account_number': consumer.account_number,
                    'reading_value': existing_reading.reading_value,
                    'reading_date': existing_reading.reading_date.isoformat()
                })

        except MeterReading.DoesNotExist:
            # If no existing reading for the date, create a new one (original behavior)
            reading = MeterReading.objects.create(
                consumer=consumer,
                reading_date=reading_date,
                reading_value=reading_value,
                source='mobile_app' # Mark source as coming from the mobile app
            )
            success_msg = f"Successfully created reading: {reading.id} for {consumer.account_number}"
            print(f"Info: {success_msg}") # Print success info
            # Return success response for creation
            return JsonResponse({
                'status': 'success',
                'message': 'Meter reading submitted successfully',
                'reading_id': reading.id,
                'consumer_name': f"{consumer.first_name} {consumer.last_name}",
                'account_number': consumer.account_number,
                'reading_value': reading.reading_value,
                'reading_date': reading.reading_date.isoformat()
            })

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in request body: {e}"
        print(f"Error submitting reading: {error_msg}") # Print specific error
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        # Log the error for debugging (consider using logging module)
        print(f"Error submitting reading: {e}") # This should catch unexpected errors
        return JsonResponse({'error': 'Internal server error'}, status=500)





@csrf_exempt
def api_login(request):
    """Login API for Android app"""
    if request.method != 'POST':    
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            # Get staff's assigned barangay
            try:
                profile = StaffProfile.objects.get(user=user)
                
                # --- NEW: Record the login event ---
                # Create a new UserLoginEvent record for this successful login
                UserLoginEvent.objects.create(
                    user=user,
                    login_timestamp=timezone.now() # Automatically sets the current time
                )
                # --- END NEW ---
                
                return JsonResponse({
                    'status': 'success',
                    'token': request.session.session_key,
                    'barangay': profile.assigned_barangay.name
                })
            except StaffProfile.DoesNotExist:
                # Still record the login even if there's no profile
                UserLoginEvent.objects.create(
                    user=user,
                    login_timestamp=timezone.now()
                )
                return JsonResponse({'error': 'No assigned barangay'}, status=403)
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        # Log the error for debugging (consider using logging module)
        print(f"Error during API login: {e}")
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
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# consumers/views.py (Update the api_consumers function)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Consumer, MeterReading, StaffProfile # Import MeterReading and StaffProfile

# ... (other imports remain the same) ...

@login_required
def api_consumers(request):
    """Get consumers for the staff's assigned barangay, including the latest confirmed reading value."""
    try:
        profile = StaffProfile.objects.get(user=request.user)
        consumers = Consumer.objects.filter(barangay=profile.assigned_barangay)

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



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from decimal import Decimal, InvalidOperation
from .models import Consumer, SystemSetting, StaffProfile, Barangay # Import necessary models
from django.utils import timezone # Import timezone for login time

# consumers/views.py

# ... (other imports remain the same) ...
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse # Make sure JsonResponse is imported
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from datetime import date
from .models import ( # Import your models
    Consumer, Barangay, Purok, MeterReading, Bill, SystemSetting, Payment, StaffProfile
)
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
        # Log the error for debugging (consider using logging module)
        print(f"Error fetching rates: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

# ... (rest of your views) ...# consumers/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.utils import timezone # Import timezone if needed for login time elsewhere
from .models import SystemSetting, StaffProfile # Import SystemSetting and StaffProfile

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
            # Get the new rates from the form
            new_res_rate_str = request.POST.get("residential_rate_per_cubic")
            new_comm_rate_str = request.POST.get("commercial_rate_per_cubic")

            # Validate and convert to Decimal
            new_res_rate = Decimal(new_res_rate_str)
            new_comm_rate = Decimal(new_comm_rate_str)

            if new_res_rate <= 0 or new_comm_rate <= 0:
                raise ValueError("Rates must be positive.")

            # Store old rates for the success message
            old_res_rate = setting.residential_rate_per_cubic
            old_comm_rate = setting.commercial_rate_per_cubic

            # Update the setting object
            setting.residential_rate_per_cubic = new_res_rate
            setting.commercial_rate_per_cubic = new_comm_rate
            setting.save() # Save the changes to the database

            # Send success message
            messages.success(
                request,
                f"✅ Rates updated successfully! Residential: ₱{old_res_rate:.2f} -> ₱{new_res_rate:.2f}, "
                f"Commercial: ₱{old_comm_rate:.2f} -> ₱{new_comm_rate:.2f}"
            )
        except (InvalidOperation, ValueError, TypeError) as e:
            messages.error(request, f"❌ Invalid rate(s) entered: {e}")
        except Exception as e:
            messages.error(request, f"❌ Error updating rates: {e}")

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
from django.contrib.auth import logout

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
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            consumer = get_object_or_404(Consumer, id=data['consumer_id'])
            MeterReading.objects.create(
                consumer=consumer,
                reading_value=data['reading'],
                reading_date=data['date'],
                source='smart_meter'
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)


# ======================
# AUTH VIEWS
# ======================

def staff_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('consumers:home')
        else:
            messages.error(request, "Invalid credentials or not staff")
    return render(request, 'consumers/login.html')


@login_required
def staff_logout(request):
    logout(request)
    return redirect("consumers:staff_login")


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

    # Handle report filter
    selected_month = request.GET.get('month', current_month)
    selected_year = request.GET.get('year', current_year)

    # Get delinquent bills for the selected month/year
    delinquent_bills = Bill.objects.filter(
        status='Pending',
        billing_period__month=selected_month,
        billing_period__year=selected_year
    ).select_related('consumer').order_by('-billing_period')

    context = {
        'connected_count': connected_count,
        'disconnected_count': disconnected_count,
        'delinquent_count': delinquent_count,
        'delinquent_bills': delinquent_bills,
        'selected_month': int(selected_month),
        'selected_year': int(selected_year),
    }
    return render(request, 'consumers/home.html', context)




# ======================
# CONSUMER STATUS FILTERS
# ======================

@login_required
def connected_consumers(request):
    consumers = Consumer.objects.filter(status='active')
    return render(request, 'consumers/consumer_list_filtered.html', {
        'title': 'Connected Consumers',
        'consumers': consumers
    })


# 1. LIST VIEW: Show all disconnected consumers (no ID needed)
@login_required
def disconnected_consumers_list(request):
    consumers = Consumer.objects.filter(status='disconnected')
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

    consumers = Consumer.objects.filter(bills__in=bills).distinct()
    
    return render(request, 'consumers/consumer_list_filtered.html', {
        'title': 'Delinquent Consumers',
        'consumers': consumers,
        'selected_month': month,
        'selected_year': year
    })


# ======================
# CONSUMER MANAGEMENT
# ======================


@login_required
def consumer_management(request):
    """Display consumer list with filters and modal form"""
    search_query = request.GET.get('search', '').strip()
    barangay_filter = request.GET.get('barangay', '').strip()

    consumers = Consumer.objects.all()
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
    """Handle adding a new consumer via modal form"""
    if request.method == "POST":
        form = ConsumerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Consumer added successfully!")
            return redirect('consumers:consumer_management')
        else:
            # Re-render the management page WITH the invalid form
            messages.error(request, "❌ Please correct the errors below.")
            search_query = ''
            barangay_filter = ''
            consumers = Consumer.objects.all()
            paginator = Paginator(consumers, 10)
            page_obj = paginator.get_page(1)

            context = {
                'consumers': page_obj,
                'form': form,  # Pass the invalid form to show errors in modal
                'search_query': search_query,
                'barangays': Barangay.objects.all(),
                'barangay_filter': barangay_filter,
            }
            return render(request, 'consumers/consumer_management.html', context)
    
    # If not POST, redirect to list
    return redirect('consumers:consumer_management')


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


# Keep these (they're fine)
def consumer_list(request):
    consumers = Consumer.objects.select_related('barangay', 'purok').all()
    query = request.GET.get('q')
    if query:
        consumers = consumers.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )
    return render(request, 'consumers/consumer_list.html', {'consumers': consumers})


def consumer_detail(request, consumer_id):
    consumer = get_object_or_404(Consumer, id=consumer_id)
    latest_bills = consumer.bills.filter(status='Pending').order_by('-billing_period')[:3]
    return render(request, 'consumers/consumer_detail.html', {
        'consumer': consumer,
        'latest_bills': latest_bills
    })
# consumers/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Consumer, Bill, Payment # ... other models ...
from django.db.models import Sum, Count # <-- Ensure this is present
import json
import csv
from django.http import HttpResponse
from datetime import datetime, timedelta
# ... other imports ...

# ... other view functions ...
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
import json

# ... other imports ...

from django.shortcuts import render
from django.db.models import Sum, Count
from .models import Payment, Bill
from django.shortcuts import render
from django.db.models import Sum, Count
from .models import Payment, Bill
from django.http import HttpResponse

def reports(request):
    report_type = request.GET.get('report_type', 'revenue')
    month_year = request.GET.get('month_year')
    ajax = request.GET.get('ajax', False)

    selected_year = int(month_year.split('-')[0]) if month_year else None
    selected_month = int(month_year.split('-')[1]) if month_year else None

    revenue_report_data = []
    delinquency_report_data = []
    summary_report_data = []

    total_revenue = total_delinquency = total_summary = 0

    if report_type == 'revenue' and month_year:
        revenue_report_data = Payment.objects.filter(
            payment_date__year=selected_year,
            payment_date__month=selected_month
        ).select_related('bill__consumer')
        total_revenue = revenue_report_data.aggregate(total=Sum('received_amount'))['total'] or 0

    elif report_type == 'delinquency' and month_year:
        delinquency_report_data = Bill.objects.filter(
            billing_period__year=selected_year,
            billing_period__month=selected_month,
            is_paid=False
        ).select_related('consumer')
        total_delinquency = delinquency_report_data.aggregate(total=Sum('total_amount'))['total'] or 0

    elif report_type == 'summary' and month_year:
        summary_report_data = Payment.objects.filter(
            payment_date__year=selected_year,
            payment_date__month=selected_month
        ).values('bill__consumer__full_name').annotate(
            total_paid=Sum('received_amount'),
            count=Count('id')
        )
        total_summary = summary_report_data.aggregate(total=Sum('total_paid'))['total'] or 0

    context = {
        'report_type': report_type,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'revenue_report_data': revenue_report_data,
        'total_revenue': total_revenue,
        'delinquency_report_data': delinquency_report_data,
        'total_delinquency': total_delinquency,
        'summary_report_data': summary_report_data,
        'total_summary': total_summary
    }

    if ajax:
        return render(request, 'consumers/report_fragment.html', context)

    return render(request, 'consumers/reports.html', context)


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

    return render(request, 'consumers/meter_reading_overview.html', {
        'barangay_data': barangay_data,
        'current_month': current_month,
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

            setting = SystemSetting.objects.first()
            rate = setting.rate_per_cubic if setting else Decimal('22.50')
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
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Subquery, OuterRef, Max
from django.utils import timezone
from datetime import date
from .models import MeterReading, Consumer

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
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from decimal import Decimal, InvalidOperation
from .models import MeterReading, Bill, Consumer, SystemSetting

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
        rate = setting.rate_per_cubic if setting else Decimal('22.50')
        fixed_charge = Decimal('50.00')

        total_amount = (Decimal(consumption) * rate) + fixed_charge

        Bill.objects.create(
            consumer=consumer,
            previous_reading=previous, # Will be None if this is the first reading
            current_reading=current,
            billing_period=current.reading_date.replace(day=1), # First day of the month
            due_date=current.reading_date.replace(day=20), # 20th of the month
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
    Display a list of user login events.
    """
    # Fetch all login events, ordered by most recent first
    login_events = UserLoginEvent.objects.select_related('user').order_by('-login_timestamp')

    context = {
        'login_events': login_events,
    }
    return render(request, 'consumers/user_login_history.html', context)


@login_required
def consumer_bill(request, consumer_id):
    """
    Display all bills for a specific consumer.
    Optimized with select_related to reduce database queries.
    """
    consumer = get_object_or_404(Consumer, id=consumer_id)
    bills = consumer.bills.select_related(
        'current_reading__consumer',
        'previous_reading__consumer'
    ).order_by('-billing_period')
    
    return render(request, 'consumers/consumer_bill.html', {
        'consumer': consumer, 
        'bills': bills
        
        
 })
    