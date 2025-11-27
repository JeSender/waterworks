# Generated manually for performance optimization
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consumers', '0022_update_penalty_defaults'),
    ]

    operations = [
        # Add indexes to Consumer model
        migrations.AddIndex(
            model_name='consumer',
            index=models.Index(fields=['status'], name='consumer_status_idx'),
        ),
        migrations.AddIndex(
            model_name='consumer',
            index=models.Index(fields=['barangay', 'status'], name='consumer_brgy_status_idx'),
        ),

        # Add indexes to Bill model
        migrations.AddIndex(
            model_name='bill',
            index=models.Index(fields=['consumer', 'status'], name='bill_consumer_status_idx'),
        ),
        migrations.AddIndex(
            model_name='bill',
            index=models.Index(fields=['due_date'], name='bill_due_date_idx'),
        ),
        migrations.AddIndex(
            model_name='bill',
            index=models.Index(fields=['status', 'due_date'], name='bill_status_due_idx'),
        ),

        # Add indexes to MeterReading model
        migrations.AddIndex(
            model_name='meterreading',
            index=models.Index(fields=['consumer', 'is_confirmed'], name='reading_consumer_conf_idx'),
        ),
        migrations.AddIndex(
            model_name='meterreading',
            index=models.Index(fields=['reading_date'], name='reading_date_idx'),
        ),
        migrations.AddIndex(
            model_name='meterreading',
            index=models.Index(fields=['consumer', 'is_confirmed', '-reading_date'], name='reading_latest_idx'),
        ),

        # Add indexes to Payment model
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['payment_date'], name='payment_date_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['bill'], name='payment_bill_idx'),
        ),
    ]
