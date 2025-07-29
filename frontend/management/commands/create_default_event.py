from django.core.management.base import BaseCommand
from frontend.models import MasterclassEvent

class Command(BaseCommand):
    help = 'Create a default Masterclass Event if none exists.'

    def handle(self, *args, **options):
        if not MasterclassEvent.objects.exists():
            MasterclassEvent.objects.create(
                title='Upcoming Masterclass',
                date_range='August 2nd & 3rd, 2025',
                description='Default event created for schedule editing.'
            )
            self.stdout.write(self.style.SUCCESS('Default Masterclass Event created.'))
        else:
            self.stdout.write(self.style.WARNING('A Masterclass Event already exists.'))
