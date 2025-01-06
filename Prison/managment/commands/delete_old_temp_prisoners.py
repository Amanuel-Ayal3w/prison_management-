from django.core.management.base import BaseCommand
from django.utils import timezone
from Prison.models import Temp_prisoner
from datetime import timedelta

class Command(BaseCommand):
    help = 'Delete Temp_prisoner entries older than 48 hours'

    def handle(self, *args, **kwargs):
        cutoff_time = timezone.now() - timedelta(hours=48)
        Temp_prisoner.objects.filter(created__lt=cutoff_time).delete()
        self.stdout.write(self.style.SUCCESS('Deleted old temp_prisoner entries'))
