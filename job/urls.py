from django.urls import path
from .views import (
    JobListView, JobDetailView, JobSearchView, SkillListView,
    SalaryTrendView, MatchingJobsStatsView, GlobalDemandView,
    JobUserRelationView, RecommendationView,
)

urlpatterns = [
    path('jobs/', JobListView.as_view(), name='job-list'),
    path('jobs/<int:pk>/', JobDetailView.as_view(), name='job-detail'),
    path('search/', JobSearchView.as_view(), name='job-search'),
    path('skills/', SkillListView.as_view(), name='skill-list'),
    path('stats/salary-trends/', SalaryTrendView.as_view(), name='salary-trends'),
    path('stats/match-count/', MatchingJobsStatsView.as_view(), name='match-count'),
    path('stats/global-demand/', GlobalDemandView.as_view(), name='global-demand'),

    path('interactions/', JobUserRelationView.as_view(), name='job-user-relation'),
    path('recommendations/', RecommendationView.as_view(), name='user-recommendations'),
]
