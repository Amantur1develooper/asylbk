from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    path('', views.ScheduleListView.as_view(), name='list'),
    path('add/', views.ScheduleCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.ScheduleUpdateView.as_view(), name='update'),
    path('<int:pk>/duplicate/', views.ScheduleDuplicateView.as_view(), name='duplicate'),
    path('<int:pk>/delete/', views.ScheduleDeleteView.as_view(), name='delete'),
]
