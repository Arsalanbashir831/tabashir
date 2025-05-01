from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from user.models import User
from resume.models import Resume
from django.core.files.uploadedfile import SimpleUploadedFile
import json


class ResumeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='Test1234!')
        self.other_user = User.objects.create_user(email='otheruser@example.com', password='Test1234!')

        self.client = APIClient()
        token_res = self.client.post(reverse('token_obtain_pair'), {
            "email": "testuser@example.com",
            "password": "Test1234!"
        })
        self.token = token_res.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.resume_data = {
            'title': 'Senior Python Developer',
            'resume_property': {
                'experience': '5 years',
                'skills': ['Python', 'Django'],
                'education': 'BS Computer Science'
            }
        }

    def test_create_resume(self):
        response = self.client.post(
            reverse('resume-list-create'),
            data=json.dumps(self.resume_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Resume.objects.count(), 1)
        self.assertEqual(Resume.objects.first().title, 'Senior Python Developer')

    def test_list_resumes(self):
        Resume.objects.create(user=self.user, title='Resume 1')
        Resume.objects.create(user=self.user, title='Resume 2')
        Resume.objects.create(user=self.other_user, title='Other user resume')

        response = self.client.get(reverse('resume-list-create'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)  # only own resumes

    def test_resume_detail_view(self):
        resume = Resume.objects.create(user=self.user, title='Detail Resume')
        response = self.client.get(reverse('resume-detail', kwargs={'pk': resume.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Detail Resume')

    def test_resume_update(self):
        resume = Resume.objects.create(user=self.user, title='Old Title')
        response = self.client.patch(
            reverse('resume-detail', kwargs={'pk': resume.id}),
            data={'title': 'New Title'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        resume.refresh_from_db()
        self.assertEqual(resume.title, 'New Title')

    def test_resume_delete(self):
        resume = Resume.objects.create(user=self.user, title='Temp Resume')
        response = self.client.delete(reverse('resume-detail', kwargs={'pk': resume.id}))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Resume.objects.count(), 0)

    def test_resume_upload_with_file(self):
        file = SimpleUploadedFile("resume.pdf", b"PDF content", content_type="application/pdf")
        response = self.client.post(
            reverse('resume-list-create'),
            data={'title': 'Resume with File', 'file': file},
            format='multipart'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Resume.objects.first().file.name.endswith('resume.pdf'))

    def test_resume_access_denied_for_other_user(self):
        resume = Resume.objects.create(user=self.other_user, title='Private Resume')
        response = self.client.get(reverse('resume-detail', kwargs={'pk': resume.id}))
        self.assertEqual(response.status_code, 404)
