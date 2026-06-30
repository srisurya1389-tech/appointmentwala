from django.core.management.base import BaseCommand
from django.utils import timezone
from booking.models import ProviderProfile, AvailabilitySlot
import datetime

class Command(BaseCommand):
    help = 'Seed sample provider profile and availability slots'

    def handle(self, *args, **kwargs):
        ProviderProfile.objects.get_or_create(id=1, defaults={
            'name': 'Dr. Priya Sharma',
            'title': 'General Physician & Consultant',
            'specialization': 'General Medicine, Preventive Care',
            'bio': 'With over 10 years of experience, I provide personalised consultations focused on your health and well-being. Book an appointment and let\'s work together on your goals.',
            'phone': '+91 98765 43210',
            'email': 'priya@appointease.in',
            'location': 'Sunshine Clinic, MG Road, Mumbai',
            'years_experience': 10,
            'consultation_fee': 500,
            'languages': 'English, Hindi, Marathi',
        })
        self.stdout.write(self.style.SUCCESS('Provider profile created'))

        today = timezone.now().date()
        times = [
            (datetime.time(9,0),  datetime.time(9,30)),
            (datetime.time(10,0), datetime.time(10,30)),
            (datetime.time(11,0), datetime.time(11,30)),
            (datetime.time(14,0), datetime.time(14,30)),
            (datetime.time(15,0), datetime.time(15,30)),
            (datetime.time(16,0), datetime.time(16,30)),
        ]
        count = 0
        for offset in range(1, 8):
            d = today + datetime.timedelta(days=offset)
            if d.weekday() >= 5: continue
            for s, e in times:
                _, created = AvailabilitySlot.objects.get_or_create(date=d, start_time=s, end_time=e)
                if created: count += 1
        self.stdout.write(self.style.SUCCESS(f'Created {count} slots. Run: python manage.py runserver'))
