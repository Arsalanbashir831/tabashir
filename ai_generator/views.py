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
        
        

class GenerateInterviewQAView(APIView):
    """
    POST /job/generate-questions/
    {
      "title": "Software Engineer",
      "include_profile": true
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        title = request.data.get("title")
        include_profile = request.data.get("include_profile", False)

        if not title:
            return Response(
                {"detail": "Field 'title' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Load your API key from env
        
        if not API_KEY:
            return Response(
                {"detail": "DeepSeek API key not configured."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Build system + user messages
        messages = [
            {"role": "system", "content": "You are a helpful interview assistant."}
        ]

        # Base prompt
        prompt = f"Generate 10 question and answer pairs for an interview based on the job title: {title}."

        # If asked, append user profile details
        if include_profile:
            user = request.user
            skills = ", ".join(user.skills or [])
            profile_snippet = (
                f" The candidate has the following background:\n"
                f"- Title: {user.title or 'N/A'}\n"
                f"- Experience: {user.experience_years or 0} years\n"
                f"- Education: {user.education or 'N/A'}\n"
                f"- Skills: {skills or 'None'}"
            )
            prompt += profile_snippet

        messages.append({"role": "user", "content": prompt})

        # Call DeepSeek (or OpenAI) chat endpoint
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "stream": False
        }
        resp = requests.post(url, headers=headers, json=payload)

        if resp.status_code != 200:
            return Response(
                {"detail": "Error from AI service", "response": resp.text},
                status=status.HTTP_502_BAD_GATEWAY
            )

        data = resp.json()
        # Extract the generated Q&A text
        qa_text = data["choices"][0]["message"]["content"]

        return Response({"qa": qa_text})
    
    
    
# ai/views.py
# ai/views.py

import os
import json
import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

SYSTEM_PROMPT = """
You are an interview coach assistant. You will receive a skill name, and optionally the candidate's profile details.
Generate exactly 10 interview question-and-answer pairs that test the candidate on this skill.
Return your output as a JSON array of objects, each with keys:
  - "question": the question string
  - "answer": the model answer string

Example INPUT (with no profile):
Skill: Python

Example OUTPUT:
[
  {
    "question": "What is a Python list and how do you iterate over it?",
    "answer": "A Python list is an ordered collection. You can iterate using for loops, e.g., for item in my_list: ..."
  },
  ...
]

Example INPUT (with profile):
Skill: Python  
Profile: Title: Software Engineer, Experience: 4 years, Education: BS Computer Science, Skills: Python, Django, REST

Example OUTPUT:
[
  {
    "question": "With your 4 years of Python experience, explain list comprehensions and provide an example.",
    "answer": "A list comprehension is a compact syntax for creating lists. For example: [x*2 for x in range(5)] ..."
  },
  ...
]
Now parse the user’s input and output exactly 10 objects in that JSON array format.
"""

SYSTEM_PROMPT = """
You are an interview coach assistant. You will receive a skill name, and optionally the candidate's profile details.
Generate exactly 10 interview question-and-answer pairs that test the candidate on this skill.
Return your output as a JSON array of objects, each with keys:
  - "question": the question string
  - "answer": the model answer string

Example INPUT (with no profile):
Skill: Python

Example OUTPUT:
[
  {
    "question": "What is a Python list and how do you iterate over it?",
    "answer": "A Python list is an ordered collection. You can iterate using for loops, e.g., for item in my_list: ..."
  },
  ...
]
Now parse the user’s input and output exactly 10 objects in that JSON array format.
"""

class GenerateSkillQAsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        skill = request.data.get("skill")
        include_profile = bool(request.data.get("include_profile", False))

        if not skill:
            return Response({"detail": "Field 'skill' is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Build the user prompt
        lines = [f"Skill: {skill}"]
        if include_profile:
            user = request.user
            profile = (
                f"Profile: Title: {user.title or 'N/A'}, "
                f"Experience: {user.experience_years or 0} years, "
                f"Education: {user.education or 'N/A'}, "
                f"Skills: {', '.join(user.skills or []) or 'None'}"
            )
            lines.append(profile)
        user_input = "\n".join(lines)

        # Prepare API call
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return Response({"detail": "DeepSeek API key not configured."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_input}
            ],
            "stream": False
        }

        try:
            r = requests.post(url, headers=headers, json=payload, timeout=400)
        except requests.RequestException as e:
            return Response({"detail": "AI service request failed", "error": str(e)},
                            status=status.HTTP_502_BAD_GATEWAY)

        if r.status_code != 200:
            return Response({"detail": "AI service error",
                             "status": r.status_code,
                             "body": r.text},
                            status=status.HTTP_502_BAD_GATEWAY)

        # Extract and parse the JSON array from the content string
        # Extract and parse the JSON array from the content string
        try:
            resp_data = r.json()
            content_raw = resp_data["choices"][0]["message"]["content"]
            print("Raw content from AI:", content_raw) # Added for debugging

            # --- Start of fix ---
            # Remove potential Markdown code block fences and trim whitespace
            if content_raw.startswith("```json"):
                content = content_raw.split("```json\n", 1)[1].rsplit("\n```", 1)[0]
            elif content_raw.startswith("```"):
                 content = content_raw.split("```\n", 1)[1].rsplit("\n```", 1)[0]
            else:
                 content = content_raw # Assume no fences if standard markers aren't found

            content = content.strip() # Remove leading/trailing whitespace just in case
            # --- End of fix ---

            print("Cleaned content for JSON parsing:", content) # Added for debugging
            qa_list = json.loads(content) # Parse the cleaned string

        except (ValueError, KeyError, IndexError, json.JSONDecodeError) as e: # Added IndexError
            return Response({"detail": "Invalid or malformed JSON from AI",
                             "error": str(e),
                             "raw_response_body": r.text, # Include full raw body for debugging
                             "extracted_content": content_raw if 'content_raw' in locals() else 'N/A' # Show what was extracted
                             },
                            status=status.HTTP_502_BAD_GATEWAY)

        # Validate structure: list of exactly 10 objects with question & answer
        if (not isinstance(qa_list, list) or
            len(qa_list) != 10 or
            not all(isinstance(item, dict) for item in qa_list) or
            not all("question" in item and "answer" in item for item in qa_list)
        ):
            return Response({"detail": "Unexpected format from AI", "data": qa_list},
                            status=status.HTTP_502_BAD_GATEWAY)

        return Response(qa_list, status=status.HTTP_200_OK)