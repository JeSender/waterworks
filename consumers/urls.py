# consumers/urls.py
from django.urls import path
from . import views
from django.shortcuts import redirect

app_name = 'consumers'

urlpatterns = [
    # Auth - Redirect root to staff login
    path('', lambda request: redirect('consumers:staff_login')), 
    path('login/', views.staff_login, name='staff_login'), # Use staff_login for web UI
    path('logout/', views.staff_logout, name='staff_logout'),

    # Dashboard / Home
    path('home/', views.home, name='home'),
    path('dashboard/print/', views.home_print, name='home_print'),
   
    # Consumer Management
    path('consumer-management/', views.consumer_management, name='consumer_management'),
    path('consumer/add/', views.add_consumer, name='add_consumer'),
    path('consumers/', views.consumer_list, name='consumer_list'),
    path('consumer/<int:consumer_id>/', views.consumer_detail, name='consumer_detail'),
    path('consumer/<int:consumer_id>/edit/', views.edit_consumer, name='edit_consumer'),
    path('consumer/<int:consumer_id>/bills/', views.consumer_bill, name='consumer_bill'),

       # Main entry point: Barangay overview dashboard (shows all barangays with status counts)
    path('meter-readings/', views.meter_reading_overview, name='meter_readings'),

    # Detailed view: Shows latest meter reading per consumer in a specific barangay
    path('meter-readings/barangay/<int:barangay_id>/', views.barangay_meter_readings, name='barangay_meter_readings'),

    # Bulk action: Confirms all unconfirmed readings in the selected barangay (use with caution)
    path('meter-readings/barangay/<int:barangay_id>/confirm-all/', views.confirm_all_readings, name='confirm_all_readings'),

    # Export: Generates Excel file of latest readings for the selected barangay
    path('meter-readings/barangay/<int:barangay_id>/export/', views.export_barangay_readings, name='export_barangay_readings'),

    # Single action: Confirms one meter reading and generates a bill
    path('meter-readings/<int:reading_id>/confirm/', views.confirm_reading, name='confirm_reading'),
    path('meter-readings/barangay/<int:barangay_id>/confirm-selected/', views.confirm_selected_readings, name='confirm_selected_readings'),
   
    # Smart Meter Webhook
    path('smart-meter-webhook/', views.smart_meter_webhook, name='smart_meter_webhook'),

    # Consumer Status Filters
    path('connected-consumers/', views.connected_consumers, name='connected_consumers'),
    path('disconnected-consumers/', views.disconnected_consumers, name='disconnected_consumers'),
    path('delinquent-consumers/', views.delinquent_consumers, name='delinquent_consumers'),
    path('delinquent-consumers/export/', views.export_delinquent_consumers, name='export_delinquent_consumers'),

    # AJAX
    path('ajax/load-puroks/', views.load_puroks, name='ajax_load_puroks'),

    # Reports & Settings
    path('reports/', views.reports, name='reports'),
    path('system-management/', views.system_management, name='system_management'),
    
    # Payment
    path('payment/', views.inquire, name='inquire'),
    path('payment/receipt/<int:payment_id>/', views.payment_receipt, name='payment_receipt'),

   # --- API Endpoints for Android App ---
    # Login API (as defined in views.py)
    path('api/login/', views.api_login, name='api_login'),
    # Get consumers API (as defined in views.py)
    path('api/consumers/', views.api_consumers, name='api_consumers'),
    # Submit reading API - This matches the Android app call and the view function name
    path('api/meter-readings/', views.api_submit_reading, name='api_submit_reading'), # Corrected name and path
    # NEW: API endpoint for fetching the current water rate
    path('api/rate/', views.api_get_current_rate, name='api_get_current_rate'),
    # --- End API Endpoints ---
]

# Removed duplicate entries for user_login, user_logout, system_management, consumer_list_for_staff
# These were conflicting with the earlier definitions and are not needed for the web UI.
# The web UI uses staff_login, staff_logout, etc.