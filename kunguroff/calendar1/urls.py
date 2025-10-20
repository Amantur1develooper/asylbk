from django.urls import path
from . import views

app_name = 'calendar'

urlpatterns = [
    path('', views.CalendarView.as_view(), name='calendar'),
    path('QuickEventCreateView/',views.QuickEventCreateView.as_view(),name='quick_event_create'),
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/create/', views.EventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/<int:pk>/update/', views.EventUpdateView.as_view(), name='event_update'),
    path('events/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
    path('events/json/', views.CalendarJsonView.as_view(), name='calendar_json'),
]