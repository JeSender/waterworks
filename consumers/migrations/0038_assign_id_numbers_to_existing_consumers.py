# Generated migration to assign id_numbers to existing consumers without one

from django.db import migrations
from datetime import datetime
import re


def assign_id_numbers(apps, schema_editor):
    """
    Assign id_numbers to all consumers that don't have one.
    Format: YYYYMMXXXX (based on their created_at date)
    """
    Consumer = apps.get_model('consumers', 'Consumer')

    # Get consumers without id_number
    consumers_without_id = Consumer.objects.filter(
        id_number__isnull=True
    ) | Consumer.objects.filter(id_number='')

    if not consumers_without_id.exists():
        print("All consumers already have id_numbers")
        return

    # Group by month of creation
    updated_count = 0

    for consumer in consumers_without_id:
        # Use created_at date for the prefix, or current date if not available
        if consumer.created_at:
            year_month = consumer.created_at.strftime('%Y%m')
        else:
            year_month = datetime.now().strftime('%Y%m')

        # Find max sequential for this month
        pattern = f'^{year_month}(\\d{{4}})$'
        existing_ids = Consumer.objects.exclude(
            id_number__isnull=True
        ).exclude(
            id_number=''
        ).values_list('id_number', flat=True)

        max_seq = 0
        for id_num in existing_ids:
            match = re.match(pattern, str(id_num))
            if match:
                seq = int(match.group(1))
                if seq > max_seq:
                    max_seq = seq

        # Generate new id_number
        new_seq = max_seq + 1
        while True:
            new_id = f'{year_month}{new_seq:04d}'
            if not Consumer.objects.filter(id_number=new_id).exists():
                consumer.id_number = new_id
                consumer.save(update_fields=['id_number'])
                updated_count += 1
                break
            new_seq += 1
            if new_seq > 9999:
                print(f"WARNING: ID number limit reached for {year_month}")
                break

    print(f"Assigned id_numbers to {updated_count} consumers")


def reverse_migration(apps, schema_editor):
    """Reverse is a no-op - we don't want to lose id_numbers"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('consumers', '0037_remove_account_number'),
    ]

    operations = [
        migrations.RunPython(assign_id_numbers, reverse_migration),
    ]
