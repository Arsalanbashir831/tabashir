from .views import GenerateResponse
from django.urls import path

urlpatterns = [
    path('generate/', GenerateResponse.as_view(), name='generate_ai_response'),
]