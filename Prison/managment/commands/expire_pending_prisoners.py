# your_app/management/commands/expire_pending_prisoners.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from Prison.models import Temp_prisoner, Notification, User
from datetime import timedelta

class Command(BaseCommand):
    help = 'Expire pending prisoners older than 48 hours from date of arrest'

    def handle(self, *args, **kwargs):
        expiration_time = timezone.now() - timedelta(hours=48)
        expired_prisoners = Temp_prisoner.objects.filter(status='pending', pri_date_of_arrest__lte=expiration_time)

        for prisoner in expired_prisoners:
            prisoner.status = 'expired'
            prisoner.save()

            # Notify all officers in the prison
            officers = User.objects.filter(prison=prisoner.prison)
            for officer in officers:
                Notification.objects.create(
                    user=officer,
                    message=f'The status for {prisoner.pri_fname} {prisoner.pri_lname} has expired.'
                )

            # Notify the related court
            court_users = User.objects.filter(court=prisoner.court)
            for court_user in court_users:
                Notification.objects.create(
                    user=court_user,
                    message=f'The status for {prisoner.pri_fname} {prisoner.pri_lname} has expired.'
                )

            self.stdout.write(self.style.SUCCESS(f'Prisoner {prisoner.pk} has been expired and notifications sent.'))

        self.stdout.write(self.style.SUCCESS('Expired pending prisoners older than 48 hours from date of arrest.'))
