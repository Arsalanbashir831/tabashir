from .views import GenerateResponse, GenerateInterviewQAView, GenerateSkillQAsView, GenerateQAsFromResumeView
from django.urls import path

urlpatterns = [
    path('generate/', GenerateResponse.as_view(), name='generate_ai_response'),
    path('generate-questions/', GenerateInterviewQAView.as_view(), name='generate_interview_questions'),
    path('generate-skill-qas/', GenerateSkillQAsView.as_view(), name='generate-skill-qas'),
    path(
      'generate-qa-from-resume/',
      GenerateQAsFromResumeView.as_view(),
      name='generate-qa-from-resume'
    ),
]