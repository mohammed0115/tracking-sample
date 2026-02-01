from django.core.management.base import BaseCommand
from Samples.models import Sample, RFIDTag
from django.utils import timezone
from datetime import date

class Command(BaseCommand):
    help = 'Seed the database with sample data for Samples and RFIDTag.'

    def handle(self, *args, **kwargs):
        # Create RFID tags
        rfid1, _ = RFIDTag.objects.get_or_create(uid='RFID-AX92-7781')
        rfid2, _ = RFIDTag.objects.get_or_create(uid='RFID-BB12-1234')
        rfid3, _ = RFIDTag.objects.get_or_create(uid='RFID-CC34-5678')

        # Create samples
        samples = [
            {
                'sample_number': '20230422001',
                'sample_type': 'دم',
                'category': 'جنائية',
                'person_name': 'يوسف أحمد',
                'collected_date': date(2026, 2, 1),
                'location': 'الرياض',
                'rfid': rfid1,
                'status': 'pending',
            },
            {
                'sample_number': '20230422002',
                'sample_type': 'لعاب',
                'category': 'جنائية',
                'person_name': 'سارة محمد',
                'collected_date': date(2026, 2, 1),
                'location': 'جدة',
                'rfid': rfid2,
                'status': 'checked',
            },
            {
                'sample_number': '20230422003',
                'sample_type': 'شعر',
                'category': 'طب شرعي',
                'person_name': 'خالد علي',
                'collected_date': date(2026, 2, 1),
                'location': 'مكة',
                'rfid': rfid3,
                'status': 'approved',
            },
        ]

        for sample_data in samples:
            sample, created = Sample.objects.get_or_create(
                sample_number=sample_data['sample_number'],
                defaults=sample_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created sample {sample.sample_number}"))
            else:
                self.stdout.write(self.style.WARNING(f"Sample {sample.sample_number} already exists"))

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))
