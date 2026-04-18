from django.urls import path
from . import views

app_name = 'directory'

urlpatterns = [
    path('',              views.DirectoryListView.as_view(),       name='list'),
    path('add/',          views.OrganizationCreateView.as_view(),  name='add'),
    path('<int:pk>/',     views.OrganizationDetailView.as_view(),  name='detail'),
    path('<int:pk>/edit/',views.OrganizationUpdateView.as_view(),  name='edit'),
    path('<int:pk>/del/', views.OrganizationDeleteView.as_view(),  name='delete'),
    path('region/add/',   views.RegionCreateView.as_view(),        name='region_add'),
]
