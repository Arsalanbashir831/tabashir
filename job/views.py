import re
from datetime import datetime, timedelta
from collections import defaultdict

from django.db.models import Avg, Count, Q
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Job, JobUserRelation, UserRecommendation
from .serializers import (
    JobSerializer,
    JobUserRelationSerializer,
    RecommendationSerializer
)
from .utils import refresh_user_recommendations


# ---------------------------------------------------
# Basic Job Search with Filters
# ---------------------------------------------------
class JobSearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        qs = Job.objects.all()
        params = request.data

        if title := params.get('title'):
            qs = qs.filter(job_title__icontains=title)
        if city := params.get('city'):
            qs = qs.filter(vacancy_city__icontains=city)
        if exp := params.get('experience'):
            qs = qs.filter(experience__icontains=exp)
        if lang := params.get('language'):
            qs = qs.filter(languages__icontains=lang)
        if qual := params.get('qualification'):
            qs = qs.filter(academic_qualification__icontains=qual)
        if date_from := params.get('date_from'):
            qs = qs.filter(job_date__gte=date_from)
        if date_to := params.get('date_to'):
            qs = qs.filter(job_date__lte=date_to)

        serializer = JobSerializer(qs, many=True)
        return Response(serializer.data)


# ---------------------------------------------------
# List of All Skills (from `languages` field)
# ---------------------------------------------------
class SkillListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        skills = set()
        for job in Job.objects.exclude(languages__isnull=True):
            for sk in job.languages.split(','):
                s = sk.strip()
                if s:
                    skills.add(s)
        return Response(sorted(skills))


# ---------------------------------------------------
# Salary Trends per Month for a Given Skill
# ---------------------------------------------------
class SalaryTrendView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        skill = request.data.get('skill', '').lower()
        now = datetime.now()
        trends = defaultdict(list)

        for job in Job.objects.filter(job_description__icontains=skill).exclude(salary__isnull=True):
            # parse month key
            if not job.job_date:
                continue
            key = job.job_date.strftime('%Y-%m')
            # extract first numeric part of salary
            nums = re.findall(r'\d+', job.salary)
            if not nums:
                continue
            val = int(nums[0])
            trends[key].append(val)

        # build response: average per month
        result = []
        for i in range(12):
            month = (now.replace(day=1) - timedelta(days=30 * i)).strftime('%Y-%m')
            vals = trends.get(month, [])
            avg = sum(vals) / len(vals) if vals else 0
            result.append({'month': month, 'average_salary': round(avg, 2)})

        return Response(result)



# ---------------------------------------------------
# Count Matching Jobs by Onsite vs Hybrid for a Skill
# ---------------------------------------------------
class MatchingJobsStatsView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        skill = request.data.get('skill', '').lower()
        qs = Job.objects.filter(job_description__icontains=skill)
        onsite = qs.filter(job_description__icontains='onsite').count()
        hybrid = qs.filter(job_description__icontains='hybrid').count()
        other = qs.count() - onsite - hybrid
        return Response({
            'skill': skill,
            'total': qs.count(),
            'onsite': onsite,
            'hybrid': hybrid,
            'other': other,
        })



# ---------------------------------------------------
# Global Demand Last Month for a Skill
# ---------------------------------------------------
class GlobalDemandView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        skill = request.data.get('skill', '').lower()
        one_month_ago = datetime.now() - timedelta(days=30)
        count = Job.objects.filter(
            job_description__icontains=skill,
            job_date__gte=one_month_ago.date()
        ).count()
        return Response({
            'skill': skill,
            'demand_last_month': count,
        })



# ---------------------------------------------------
# (Existing Views Below)
# ---------------------------------------------------

class JobListView(generics.ListAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]


class JobDetailView(generics.RetrieveAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]


class JobUserRelationView(generics.ListCreateAPIView):
    queryset = JobUserRelation.objects.all()
    serializer_class = JobUserRelationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecommendationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = request.user.recommendations.select_related('job')
        if not qs.exists():
            qs = refresh_user_recommendations(request.user)
        serializer = RecommendationSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        qs = refresh_user_recommendations(request.user)
        serializer = RecommendationSerializer(qs, many=True)
        return Response(serializer.data)


class JobsByRelationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        relation = request.query_params.get("relation")
        user = request.user

        if relation:
            relations = JobUserRelation.objects.filter(user=user, relation=relation).select_related("job")
            jobs = [r.job for r in relations]
            return Response(JobSerializer(jobs, many=True).data)
        else:
            # Group jobs by each relation
            all_relations = JobUserRelation.objects.filter(user=user).select_related("job")
            grouped = defaultdict(list)

            for rel in all_relations:
                grouped[rel.relation].append(rel.job)

            return Response({
                key: JobSerializer(value, many=True).data for key, value in grouped.items()
            })