# Generated migration to convert admin role to superadmin

from django.db import migrations


def convert_admin_to_superadmin(apps, schema_editor):
    """
    Convert all 'admin' roles to 'superadmin' since we're removing the admin role.
    New role structure: superadmin, cashier, field_staff
    """
    StaffProfile = apps.get_model('consumers', 'StaffProfile')

    # Update all admin roles to superadmin
    updated = StaffProfile.objects.filter(role='admin').update(role='superadmin')

    if updated > 0:
        print(f"Converted {updated} admin user(s) to superadmin role")


def reverse_migration(apps, schema_editor):
    """
    Reverse: convert superadmin back to admin (if needed)
    """
    StaffProfile = apps.get_model('consumers', 'StaffProfile')
    StaffProfile.objects.filter(role='superadmin').update(role='admin')


class Migration(migrations.Migration):

    dependencies = [
        ('consumers', '0029_add_archived_user_model'),
    ]

    operations = [
        migrations.RunPython(convert_admin_to_superadmin, reverse_migration),
    ]
