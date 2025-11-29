# consumers/context_processors.py
"""
Context processors to make data available to all templates.
"""
from django.db import models as django_models
from .models import Notification


def notifications(request):
    """
    Add unread notifications to template context for authenticated users.
    Only shows notifications for admins and superusers.
    Auto-archives notifications older than 30 days.
    """
    if request.user.is_authenticated:
        # Check if user is admin or superuser
        is_admin = request.user.is_superuser or (
            hasattr(request.user, 'staffprofile') and
            request.user.staffprofile.role == 'admin'
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

            return {
                'unread_notifications': unread_notifications,
                'unread_notifications_count': unread_count
            }

    return {
        'unread_notifications': [],
        'unread_notifications_count': 0
    }
