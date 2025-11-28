"""
Management command to assign ID numbers to all consumers.

Usage:
    python manage.py assign_id_numbers

This command will:
1. Find all consumers without ID numbers
2. Call save() on each consumer to auto-generate ID numbers
3. Display progress and results
"""

from django.core.management.base import BaseCommand
from consumers.models import Consumer


class Command(BaseCommand):
    help = 'Assign ID numbers to all consumers who do not have one'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting ID number assignment...'))

        # Get all consumers without ID numbers
        consumers_without_id = Consumer.objects.filter(
            id_number__isnull=True
        ).order_by('created_at')

        total = consumers_without_id.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS('All consumers already have ID numbers!'))
            return

        self.stdout.write(f'Found {total} consumers without ID numbers')
        self.stdout.write('Assigning ID numbers...')

        # Process each consumer
        success_count = 0
        error_count = 0

        for i, consumer in enumerate(consumers_without_id, 1):
            try:
                # Save will trigger the auto-generation logic
                consumer.save()
                success_count += 1

                # Show progress every 10 consumers
                if i % 10 == 0:
                    self.stdout.write(f'  Processed {i}/{total} consumers...')

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'  Error processing consumer {consumer.id}: {e}')
                )

        # Final summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Successfully assigned ID numbers to {success_count} consumers'))

        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Failed to process {error_count} consumers'))

        # Show some examples
        self.stdout.write('')
        self.stdout.write('Examples of assigned ID numbers:')
        for consumer in Consumer.objects.filter(id_number__isnull=False).order_by('id_number')[:5]:
            self.stdout.write(
                f'  {consumer.id_number} - {consumer.account_number} - {consumer.first_name} {consumer.last_name}'
            )
