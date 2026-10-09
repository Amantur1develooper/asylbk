from django.urls import path

from . import views

app_name = 'surveys'

urlpatterns = [
    path('<slug:slug>/', views.survey_detail, name='detail'),
    path('<slug:slug>/thanks/', views.survey_thanks, name='thanks'),
]
