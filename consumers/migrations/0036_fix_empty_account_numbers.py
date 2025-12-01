# Migration placeholder - account_number field is being removed in 0037
# This migration is now a no-op

from django.db import migrations


def noop(apps, schema_editor):
    """No operation - account_number is removed in next migration"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('consumers', '0035_update_tiered_rates_values'),
    ]

    operations = [
        migrations.RunPython(noop, noop),
    ]
