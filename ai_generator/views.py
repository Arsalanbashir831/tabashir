from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import requests

API_KEY = settings.DEEPSEEK_API_KEY
# Create your views here.
from openai import OpenAI

client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.ai")

class GenerateResponse(APIView):
    permission_classes = [IsAuthenticated]
    @csrf_exempt
    def post(self, request):
        try:
            prompt = request.data.get('prompt')
            if not prompt:
                return Response("Prompt is required", status=status.HTTP_400_BAD_REQUEST)   
            if not request.user.is_authenticated:
                return Response("User is not authenticated", status=status.HTTP_401_UNAUTHORIZED)
            use_user_info = request.data.get('use_user_info', False)
            user = request.user
            info = {
                "title": user.title,
                "experience": user.experience_years,
                "education": user.education,
                "skills": user.skills
            }
            
            if use_user_info:
                prompt = f"Following is the user info {info}.\n\n{prompt}"

            url = "https://api.deepseek.com/chat/completions"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            }

            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a helpful Resume Assistant to generate resume content."},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return Response(content, status=status.HTTP_200_OK)
            else:
                return Response(response.text, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)