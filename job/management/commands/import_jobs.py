import csv
from django.core.management.base import BaseCommand
from job.models import Job
from django.utils.dateparse import parse_date

class Command(BaseCommand):
    help = 'Import jobs from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        count = 0
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Job.objects.create(
                    entity=row.get('entity', ''),
                    nationality=row.get('nationality', ''),
                    gender=row.get('gender', ''),
                    job_title=row.get('job_title', ''),
                    academic_qualification=row.get('academic_qualification', ''),
                    experience=row.get('experience', ''),
                    languages=row.get('languages', ''),
                    salary=row.get('salary', ''),
                    vacancy_city=row.get('vacancy_city', ''),
                    working_hours=row.get('working_hours', ''),
                    working_days=row.get('working_days', ''),
                    application_email=row.get('application_email', ''),
                    job_description=row.get('job_description', ''),
                    job_date=parse_date(row.get('job_date', '')),
                    link=row.get('link', ''),
                    phone=row.get('phone', ''),
                    source=row.get('source', ''),
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} jobs."))
