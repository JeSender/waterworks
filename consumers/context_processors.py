# consumers/context_processors.py
"""
Context processors to make data available to all templates.
"""
from django.db import models as django_models
from .models import Notification, MeterReading


def notifications(request):
    """
    Add unread notifications to template context for authenticated users.
    Only shows notifications for admins and superusers.
    Auto-archives notifications older than 30 days.
    Also provides count of pending proof readings for sidebar badge.
    """
    if request.user.is_authenticated:
        # Check if user is admin or superuser
        is_admin = request.user.is_superuser or (
            hasattr(request.user, 'staffprofile') and
            request.user.staffprofile.role in ['admin', 'superadmin']
        )

        # Check if user is cashier or admin (for showing pending readings)
        is_staff = is_admin or (
            hasattr(request.user, 'staffprofile') and
            request.user.staffprofile.role == 'cashier'
        )

        if is_admin:
            # Auto-archive old notifications (older than 30 days)
            Notification.archive_old_notifications()

            # Get unread, non-archived notifications for this user or global notifications
            unread_notifications = Notification.objects.filter(
                is_read=False,
                is_archived=False
            ).filter(
                django_models.Q(user=request.user) | django_models.Q(user__isnull=True)
            ).order_by('-created_at')[:10]  # Limit to 10 most recent

            unread_count = Notification.objects.filter(
                is_read=False,
                is_archived=False
            ).filter(
                django_models.Q(user=request.user) | django_models.Q(user__isnull=True)
            ).count()

            # Count pending proof readings for sidebar badge
            pending_proof_count = MeterReading.objects.filter(
                is_confirmed=False,
                is_rejected=False,
                source='app_manual'  # Manual entry from Smart Meter Reader app
            ).count()

            return {
                'unread_notifications': unread_notifications,
                'unread_notifications_count': unread_count,
                'pending_proof_readings_count': pending_proof_count
            }

        elif is_staff:
            # Staff members can see pending proof readings count
            pending_proof_count = MeterReading.objects.filter(
                is_confirmed=False,
                is_rejected=False,
                source='app_manual'  # Manual entry from Smart Meter Reader app
            ).count()

            return {
                'unread_notifications': [],
                'unread_notifications_count': 0,
                'pending_proof_readings_count': pending_proof_count
            }

    return {
        'unread_notifications': [],
        'unread_notifications_count': 0,
        'pending_proof_readings_count': 0
    }
