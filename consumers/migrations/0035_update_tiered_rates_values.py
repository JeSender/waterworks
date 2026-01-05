# Generated migration to update SystemSetting tiered rates

from decimal import Decimal
from django.db import migrations


def update_tiered_rates(apps, schema_editor):
    """
    Update SystemSetting with correct tiered rates.
    These rates will be used for all future bill calculations.
    """
    SystemSetting = apps.get_model('consumers', 'SystemSetting')

    # Get or create the system setting
    setting = SystemSetting.objects.first()

    if setting:
        # Update RESIDENTIAL rates
        setting.residential_minimum_charge = Decimal('75.00')   # Tier 1 (1-5 m³)
        setting.residential_tier2_rate = Decimal('15.00')       # Tier 2 (6-10 m³)
        setting.residential_tier3_rate = Decimal('16.00')       # Tier 3 (11-20 m³)
        setting.residential_tier4_rate = Decimal('17.00')       # Tier 4 (21-50 m³)
        setting.residential_tier5_rate = Decimal('50.00')       # Tier 5 (51+ m³)

        # Update COMMERCIAL rates
        setting.commercial_minimum_charge = Decimal('100.00')   # Tier 1 (1-5 m³)
        setting.commercial_tier2_rate = Decimal('18.00')        # Tier 2 (6-10 m³)
        setting.commercial_tier3_rate = Decimal('20.00')        # Tier 3 (11-20 m³)
        setting.commercial_tier4_rate = Decimal('22.00')        # Tier 4 (21-50 m³)
        setting.commercial_tier5_rate = Decimal('30.00')        # Tier 5 (51+ m³)

        setting.save()
        print("SystemSetting tiered rates updated successfully!")
    else:
        # Create new SystemSetting with correct rates
        SystemSetting.objects.create(
            residential_minimum_charge=Decimal('75.00'),
            residential_tier2_rate=Decimal('15.00'),
            residential_tier3_rate=Decimal('16.00'),
            residential_tier4_rate=Decimal('17.00'),
            residential_tier5_rate=Decimal('50.00'),
            commercial_minimum_charge=Decimal('100.00'),
            commercial_tier2_rate=Decimal('18.00'),
            commercial_tier3_rate=Decimal('20.00'),
            commercial_tier4_rate=Decimal('22.00'),
            commercial_tier5_rate=Decimal('30.00'),
        )
        print("SystemSetting created with correct tiered rates!")


def reverse_migration(apps, schema_editor):
    """Reverse is a no-op - we don't want to lose rate data"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('consumers', '0034_add_manual_reading_confirmation_fields'),
    ]

    operations = [
        migrations.RunPython(update_tiered_rates, reverse_migration),
    ]
