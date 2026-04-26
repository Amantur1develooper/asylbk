from django.urls import path
from . import views

app_name = 'knowledge'

urlpatterns = [
    path('',            views.PostListView.as_view(), name='list'),
    path('add/',        views.post_create,            name='create'),
    path('<int:pk>/',   views.PostDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/',   views.post_edit,   name='edit'),
    path('<int:pk>/delete/', views.post_delete, name='delete'),
]
