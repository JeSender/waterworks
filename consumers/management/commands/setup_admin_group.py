"""
Management command to set up the Admin group with restricted permissions.

Usage:
    python manage.py setup_admin_group

This creates/updates the 'Admin' group with the following permissions:
- CAN: View consumers, billing, reports, meter readings, payments
- CANNOT: Edit/create/delete consumers, manage users, access system settings, disconnect consumers
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Set up the Admin group with restricted permissions (billing and reports only)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Setting up Admin group with restricted permissions...'))

        # Create or get the Admin group
        admin_group, created = Group.objects.get_or_create(name='Admin')

        if created:
            self.stdout.write(self.style.SUCCESS('Created new Admin group'))
        else:
            self.stdout.write(self.style.WARNING('Admin group already exists - updating permissions'))
            # Clear existing permissions to reset
            admin_group.permissions.clear()

        # Get content type for Consumer model (where custom permissions are defined)
        try:
            from consumers.models import Consumer
            consumer_ct = ContentType.objects.get_for_model(Consumer)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting Consumer model: {e}'))
            return

        # Permissions Admin CAN have (from custom permissions)
        admin_can_permissions = [
            'view_consumer_data',    # Can view consumer data (read-only)
            'view_billing',          # Can view billing records
            'manage_billing',        # Can manage billing (create bills, process payments)
            'view_reports',          # Can view reports
            'generate_reports',      # Can generate and download reports
        ]

        # Permissions Admin CANNOT have (superuser only)
        admin_cannot_permissions = [
            'edit_consumer_data',    # Cannot edit consumer information
            'create_consumer',       # Cannot create new consumers
            'delete_consumer',       # Cannot delete consumers
            'disconnect_consumer',   # Cannot disconnect/reconnect consumers
            'manage_users',          # Cannot manage user accounts
            'manage_settings',       # Cannot access system settings
        ]

        # Add standard Django permissions for viewing
        standard_view_permissions = [
            ('view_consumer', consumer_ct),
            ('view_meterreading', ContentType.objects.get(app_label='consumers', model='meterreading')),
            ('view_bill', ContentType.objects.get(app_label='consumers', model='bill')),
            ('view_payment', ContentType.objects.get(app_label='consumers', model='payment')),
            ('view_barangay', ContentType.objects.get(app_label='consumers', model='barangay')),
            ('view_purok', ContentType.objects.get(app_label='consumers', model='purok')),
        ]

        permissions_added = 0
        permissions_not_found = []

        # Add custom permissions (defined in Consumer.Meta.permissions)
        for perm_codename in admin_can_permissions:
            try:
                perm = Permission.objects.get(
                    codename=perm_codename,
                    content_type=consumer_ct
                )
                admin_group.permissions.add(perm)
                permissions_added += 1
                self.stdout.write(f'  + Added: {perm_codename}')
            except Permission.DoesNotExist:
                permissions_not_found.append(perm_codename)
                self.stdout.write(self.style.WARNING(f'  ! Not found: {perm_codename} (run migrations first)'))

        # Add standard view permissions
        for perm_codename, content_type in standard_view_permissions:
            try:
                perm = Permission.objects.get(
                    codename=perm_codename,
                    content_type=content_type
                )
                admin_group.permissions.add(perm)
                permissions_added += 1
                self.stdout.write(f'  + Added: {perm_codename}')
            except Permission.DoesNotExist:
                permissions_not_found.append(perm_codename)
                self.stdout.write(self.style.WARNING(f'  ! Not found: {perm_codename}'))

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Admin group setup complete!'))
        self.stdout.write(f'  Permissions added: {permissions_added}')

        if permissions_not_found:
            self.stdout.write(self.style.WARNING(f'  Permissions not found: {len(permissions_not_found)}'))
            self.stdout.write(self.style.NOTICE('  Run "python manage.py migrate" to create custom permissions'))

        # Print summary of what Admin CAN and CANNOT do
        self.stdout.write('')
        self.stdout.write(self.style.NOTICE('=== ADMIN ROLE SUMMARY ==='))
        self.stdout.write(self.style.SUCCESS('Admin CAN:'))
        self.stdout.write('  - View consumer data (read-only)')
        self.stdout.write('  - Manage billing (create bills, process payments)')
        self.stdout.write('  - Generate and download reports')
        self.stdout.write('  - View meter readings')
        self.stdout.write('  - View payment records')
        self.stdout.write('')
        self.stdout.write(self.style.ERROR('Admin CANNOT:'))
        self.stdout.write('  - Edit/modify consumer information')
        self.stdout.write('  - Create new consumers')
        self.stdout.write('  - Delete consumers')
        self.stdout.write('  - Disconnect/reconnect consumers')
        self.stdout.write('  - Manage user accounts')
        self.stdout.write('  - Access system settings')
        self.stdout.write('  - Change field staff assignments')
