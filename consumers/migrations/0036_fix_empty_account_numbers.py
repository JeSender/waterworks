# Generated migration to fix empty account_numbers

from django.db import migrations


def fix_empty_account_numbers(apps, schema_editor):
    """
    Fix consumers with empty account_number by setting it to match id_number.
    This prevents unique constraint violations.
    """
    Consumer = apps.get_model('consumers', 'Consumer')

    # Find consumers with empty account_number but valid id_number
    consumers_to_fix = Consumer.objects.filter(
        account_number__in=['', None]
    ).exclude(
        id_number__in=['', None]
    )

    fixed_count = 0
    for consumer in consumers_to_fix:
        consumer.account_number = consumer.id_number
        consumer.save(update_fields=['account_number'])
        fixed_count += 1

    if fixed_count > 0:
        print(f"✅ Fixed {fixed_count} consumers with empty account_number")


def reverse_migration(apps, schema_editor):
    """Reverse is a no-op"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('consumers', '0035_update_tiered_rates_values'),
    ]

    operations = [
        migrations.RunPython(fix_empty_account_numbers, reverse_migration),
    ]
