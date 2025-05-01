from rest_framework import serializers
from job.models import Job, UserRecommendation, JobUserRelation


# -------------------
# JOB
# -------------------

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'


# -------------------
# RECOMMENDATIONS
# -------------------

class RecommendationSerializer(serializers.ModelSerializer):
    job = JobSerializer()

    class Meta:
        model = UserRecommendation
        fields = ['job', 'score', 'updated']


# -------------------
# RELATIONS (bookmarked, viewed, etc.)
# -------------------

class JobUserRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobUserRelation
        fields = ['id', 'user', 'job', 'relation', 'timestamp']
        read_only_fields = ['timestamp', 'user']
