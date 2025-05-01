import csv
from django.core.management.base import BaseCommand
from job.models import Job
from django.utils.dateparse import parse_date

def truncate(val, limit=1000):
    return val[:limit] if val else ''

class Command(BaseCommand):
    help = 'Cleans and re-imports all job records from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        # Step 1: Clean database
        deleted_count, _ = Job.objects.all().delete()
        self.stdout.write(self.style.WARNING(f"🧹 Deleted {deleted_count} existing job(s)."))

        # Step 2: Import jobs from CSV
        count = 0
        errors = 0

        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    Job.objects.create(
                        entity=truncate(row.get('entity')),
                        nationality=truncate(row.get('nationality'), 100),
                        gender=truncate(row.get('gender'), 50),
                        job_title=truncate(row.get('job_title')),
                        academic_qualification=truncate(row.get('academic_qualification')),
                        experience=truncate(row.get('experience')),
                        languages=truncate(row.get('languages')),
                        salary=truncate(row.get('salary')),
                        vacancy_city=truncate(row.get('vacancy_city')),
                        working_hours=truncate(row.get('working_hours')),
                        working_days=truncate(row.get('working_days')),
                        application_email=row.get('application_email'),
                        job_description=truncate(row.get('job_description')),
                        job_date=parse_date(row.get('job_date', '')),
                        link=truncate(row.get('link')),
                        phone=truncate(row.get('phone')),
                        source=truncate(row.get('source')),
                    )
                    count += 1
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"❌ Error on row {count + errors + 1}: {e}"))
                    errors += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Imported {count} jobs with {errors} error(s)."))
