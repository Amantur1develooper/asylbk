from django.urls import path
from . import views

app_name = 'ratings'

urlpatterns = [
    path('', views.RatingsDashboardView.as_view(), name='dashboard'),
    path('lawyers/', views.LawyerRankingView.as_view(), name='lawyer_ranking'),
    path('cases/', views.CaseAnalysisView.as_view(), name='case_analysis'),
    path('reports/', views.PerformanceReportView.as_view(), name='performance_reports'),
]