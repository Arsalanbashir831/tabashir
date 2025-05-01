from rest_framework import serializers
from job.models import Job, UserRecommendation

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields ='__all__'

class RecommendationSerializer(serializers.ModelSerializer):
    job = JobSerializer()
    class Meta:
        model = UserRecommendation
        fields = ['job', 'score', 'updated']
