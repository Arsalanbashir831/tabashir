from django.urls import path
from .views import ResumeListCreateView, ResumeDetailView, ResumeListView, ResumeDeleteView

urlpatterns = [
    path('', ResumeListCreateView.as_view(), name='resume-list-create'),
    path('', ResumeListView.as_view(), name='resume-list'),
    path('<int:pk>/', ResumeDetailView.as_view(), name='resume-detail'),
    path('<int:pk>/', ResumeDeleteView.as_view(), name='resume-delete'),
    
]
