from django.urls import path

from . import views

app_name = 'surveys'

urlpatterns = [
    # Внутренняя статистика/результаты — должны идти раньше <slug:slug>/,
    # иначе 'manage' будет распознан как slug опросника.
    path('manage/', views.survey_manage_list, name='manage_list'),
    path('manage/<int:pk>/', views.survey_manage_detail, name='manage_detail'),
    path('manage/<int:pk>/export/', views.survey_manage_export, name='manage_export'),

    path('<slug:slug>/', views.survey_detail, name='detail'),
    path('<slug:slug>/thanks/', views.survey_thanks, name='thanks'),
]
