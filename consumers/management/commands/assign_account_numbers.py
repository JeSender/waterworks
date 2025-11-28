"""
Django management command to assign account numbers to consumers that don't have one.
Usage: python manage.py assign_account_numbers
"""
from django.core.management.base import BaseCommand
from consumers.models import Consumer


class Command(BaseCommand):
    help = 'Assigns 5-digit account numbers to all consumers without one'

    def handle(self, *args, **options):
        # Find consumers without account numbers
        consumers_without_account = Consumer.objects.filter(
            account_number=''
        ).order_by('created_at')

        total_count = consumers_without_account.count()

        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('✓ All consumers already have account numbers!'))
            return

        self.stdout.write(f'Found {total_count} consumers without account numbers.')
        self.stdout.write('Assigning account numbers...')

        # Get the highest existing account number
        latest_consumer = Consumer.objects.exclude(
            account_number=''
        ).order_by('-account_number').first()

        if latest_consumer and latest_consumer.account_number.isdigit():
            start_num = int(latest_consumer.account_number) + 1
        else:
            start_num = 1

        # Assign account numbers sequentially
        updated_count = 0
        for consumer in consumers_without_account:
            account_num = f'{start_num:05d}'
            consumer.account_number = account_num
            consumer.save(update_fields=['account_number'])

            self.stdout.write(
                f'  Assigned {account_num} to {consumer.first_name} {consumer.last_name}'
            )

            start_num += 1
            updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Successfully assigned account numbers to {updated_count} consumers!')
        )
