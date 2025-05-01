from django.db import models
from user.models import User



class Job(models.Model):
    entity = models.TextField(null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=128, null=True, blank=True)
    job_title = models.TextField()
    academic_qualification = models.TextField(null=True, blank=True)
    experience = models.TextField(null=True, blank=True)
    languages = models.TextField(null=True, blank=True)
    salary = models.TextField(null=True, blank=True)
    vacancy_city = models.TextField(null=True, blank=True)
    working_hours = models.TextField(null=True, blank=True)
    working_days = models.TextField(null=True, blank=True)
    application_email = models.EmailField(null=True, blank=True)
    job_description = models.TextField(null=True, blank=True)
    job_date = models.DateField(null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    source = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.job_title} ({self.entity})"



class JobUserRelation(models.Model):
    RELATION_CHOICES = [
        ('viewed', 'Viewed'),
        ('bookmark', 'Bookmarked'),
        ('interview', 'Interview Scheduled'),
        ('offer', 'Offered'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    relation = models.CharField(max_length=20, choices=RELATION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job', 'relation')

    def __str__(self):
        return f"{self.user.email} {self.relation} {self.job.job_title}"

class UserRecommendation(models.Model):
    user      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    job       = models.ForeignKey(Job,  on_delete=models.CASCADE)
    score     = models.FloatField()
    updated   = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-score']