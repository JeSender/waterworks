"""
Django management command to assign account numbers to consumers that don't have one.
Usage: python manage.py assign_account_numbers

This command safely assigns account codes to old consumers without duplicates.
The Consumer model's save() method handles duplicate prevention automatically.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from consumers.models import Consumer


class Command(BaseCommand):
    help = 'Assigns 5-digit account numbers to all consumers without one'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)

        # Find consumers without account numbers
        consumers_without_account = Consumer.objects.filter(
            account_number=''
        ).order_by('created_at')

        total_count = consumers_without_account.count()

        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('✓ All consumers already have account numbers!'))
            return

        self.stdout.write(f'Found {total_count} consumers without account numbers.')

        if dry_run:
            self.stdout.write(self.style.WARNING('\n--- DRY RUN MODE (no changes will be made) ---'))
            for i, consumer in enumerate(consumers_without_account, 1):
                self.stdout.write(f'  [{i}] Would assign code to: {consumer.first_name} {consumer.last_name}')
            self.stdout.write(f'\nTotal: {total_count} consumers would be updated')
            return

        self.stdout.write('Assigning account numbers...\n')

        # Process each consumer - the model's save() method handles uniqueness
        updated_count = 0
        errors = []

        with transaction.atomic():
            for consumer in consumers_without_account:
                try:
                    # Clear account_number to trigger auto-generation
                    consumer.account_number = ''
                    consumer.save()  # Model's save() will auto-assign unique code

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Assigned {consumer.account_number} to {consumer.first_name} {consumer.last_name}'
                        )
                    )
                    updated_count += 1

                except Exception as e:
                    error_msg = f'  ✗ Failed for {consumer.first_name} {consumer.last_name}: {str(e)}'
                    self.stdout.write(self.style.ERROR(error_msg))
                    errors.append(error_msg)

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✓ Successfully assigned account numbers to {updated_count} consumers!'))

        if errors:
            self.stdout.write(self.style.ERROR(f'✗ {len(errors)} errors occurred:'))
            for error in errors:
                self.stdout.write(error)
