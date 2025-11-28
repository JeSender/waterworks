"""
Backfill ID Numbers Script

This script can be run in Django shell or as a standalone script
to generate ID numbers for all consumers who don't have one.

Usage Option 1 (Django Shell):
    python manage.py shell
    >>> exec(open('backfill_id_numbers.py').read())

Usage Option 2 (Management Command - Recommended):
    python manage.py assign_id_numbers

Usage Option 3 (Direct execution):
    python manage.py shell < backfill_id_numbers.py
"""

from consumers.models import Consumer
from datetime import datetime

print("=" * 60)
print("BACKFILL ID NUMBERS SCRIPT")
print("=" * 60)

# Get all consumers without id_number (handles both NULL and empty string)
consumers_without_id = Consumer.objects.filter(
    id_number__isnull=True
) | Consumer.objects.filter(
    id_number=''
)

total = consumers_without_id.count()

print(f"\nFound {total} consumers without ID numbers")

if total == 0:
    print("✓ All consumers already have ID numbers!")
    print("\nExamples of existing ID numbers:")
    for consumer in Consumer.objects.filter(id_number__isnull=False).order_by('id_number')[:5]:
        print(f"  {consumer.id_number} - {consumer.full_name}")
else:
    print("\nGenerating ID numbers...")
    print("-" * 60)

    success_count = 0
    error_count = 0

    for i, consumer in enumerate(consumers_without_id, 1):
        try:
            # Trigger auto-generation by saving
            consumer.save()
            success_count += 1
            print(f"  [{i}/{total}] Generated ID {consumer.id_number} for {consumer.full_name}")

        except Exception as e:
            error_count += 1
            print(f"  [ERROR] Failed for {consumer.full_name}: {str(e)}")

    print("-" * 60)
    print(f"\n✓ Successfully generated {success_count} ID numbers")

    if error_count > 0:
        print(f"✗ Failed to generate {error_count} ID numbers")

    print("\nExamples of newly generated ID numbers:")
    for consumer in Consumer.objects.filter(id_number__isnull=False).order_by('-id')[:5]:
        print(f"  {consumer.id_number} - {consumer.full_name}")

print("\n" + "=" * 60)
print("SCRIPT COMPLETED")
print("=" * 60)
