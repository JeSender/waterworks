# Generated migration to remove deprecated account_number field

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('consumers', '0036_fix_empty_account_numbers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consumer',
            name='account_number',
        ),
    ]
