from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserRecommendation
from .utils import refresh_user_recommendations
from .serializers import RecommendationSerializer

class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # if none exist, compute & store
        qs = request.user.recommendations.select_related('job')
        if not qs.exists():
            qs = refresh_user_recommendations(request.user)
        serializer = RecommendationSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        # forced refresh
        qs = refresh_user_recommendations(request.user)
        serializer = RecommendationSerializer(qs, many=True)
        return Response(serializer.data)
