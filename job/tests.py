from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from job.models import Job, JobUserRelation, UserRecommendation
from user.models import User
from datetime import date, timedelta

class JobViewTests(APITestCase):
    def setUp(self):
        # Create user and get token
        self.user = User.objects.create_user(email="user@test.com", password="Test1234!")
        self.client = APIClient()
        res = self.client.post(reverse('token_obtain_pair'), {
            "email": "user@test.com",
            "password": "Test1234!"
        })
        self.token = res.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        # Create sample jobs
        self.job1 = Job.objects.create(
            job_title="Python Developer",
            job_description="Looking for onsite Python dev with Django experience",
            vacancy_city="New York",
            experience="3 years",
            languages="Python, Django",
            salary="6000 USD",
            job_date=date.today(),
        )
        self.job2 = Job.objects.create(
            job_title="React Engineer",
            job_description="Hybrid work. Must know React",
            vacancy_city="Remote",
            experience="2 years",
            languages="React, JavaScript",
            salary="7000 USD",
            job_date=date.today() - timedelta(days=40),
        )

    def test_list_jobs(self):
        res = self.client.get(reverse('job-list'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 2)

    def test_job_detail(self):
        res = self.client.get(reverse('job-detail', kwargs={"pk": self.job1.id}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['job_title'], "Python Developer")

    def test_job_search(self):
        res = self.client.get(reverse('job-search'), {'title': 'React'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['job_title'], "React Engineer")

    def test_skill_list(self):
        res = self.client.get(reverse('skill-list'))
        self.assertEqual(res.status_code, 200)
        self.assertIn("Python", res.data)
        self.assertIn("React", res.data)

    def test_salary_trend(self):
        res = self.client.get(reverse('salary-trends'), {'skill': 'python'})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(isinstance(res.data, list))
        self.assertIn('average_salary', res.data[0])

    def test_match_count(self):
        res = self.client.get(reverse('match-count'), {'skill': 'react'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['hybrid'], 1)
        self.assertEqual(res.data['onsite'], 0)

    def test_global_demand(self):
        res = self.client.get(reverse('global-demand'), {'skill': 'python'})
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(res.data['demand_last_month'], 1)

    def test_create_job_user_relation(self):
        res = self.client.post(reverse('job-user-relation'), {
    "job": self.job1.id,
    "relation": "bookmark"
    })

        self.assertEqual(res.status_code, 201, msg=res.data)

        self.assertEqual(JobUserRelation.objects.count(), 1)

    def test_get_recommendations(self):
        res = self.client.post(reverse('user-recommendations'))  # force refresh
        self.assertEqual(res.status_code, 200)
        self.assertTrue(isinstance(res.data, list))
