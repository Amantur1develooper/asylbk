from django.urls import path
from . import views
from .views import CaseDocumentDeleteView

app_name = "cases"
    

urlpatterns = [
    path('', views.CaseListView.as_view(), name='case_list'),
    # path('ajax/field-info/<int:field_id>/', views.field_info, name='field_info'),
    path('<int:pk>/', views.CaseDetailView.as_view(), name='case_detail'),
    path('create/', views.CaseCreateView.as_view(), name='case_create'),
    path('<int:pk>/update/', views.CaseUpdateView.as_view(), name='case_update'),
    path('<int:pk>/delete/', views.CaseDeleteView.as_view(), name='case_delete'),
    path('<int:pk>/add-document/', views.CaseDocumentCreateView.as_view(), name='case_add_document'),
    path('ajax/category-stages/', views.CategoryStagesView.as_view(), name='ajax_category_stages'),
    # ... другие маршруты ...
    path('ajax/load-stages/', views.ajax_load_stages, name='ajax_load_stages'),
    path('ajax/load-stage-fields/', views.ajax_load_stage_fields, name='ajax_load_stage_fields'),
    path('ajax/load-field-info/<int:field_id>/', views.ajax_load_field_info, name='ajax_load_field_info'),

    path(
        "<int:case_id>/stages/<int:stage_id>/fields/<int:field_id>/delete/",
        CaseDocumentDeleteView.as_view(),
        name="document_delete",
    ),

    
    path('<int:case_pk>/participants/add/', views.CaseParticipantCreateView.as_view(), name='case_add_participant'),
    path('participants/<int:pk>/update/', views.CaseParticipantUpdateView.as_view(), name='case_update_participant'),
    path('participants/<int:pk>/delete/', views.CaseParticipantDeleteView.as_view(), name='case_delete_participant'),
    path('ajax/load-participant-roles/', views.ajax_load_participant_roles, name='ajax_load_participant_roles'),
   
 
 
  
      
]