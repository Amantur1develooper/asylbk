from django.urls import path
from . import views

app_name = "public"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("consultation/", views.consultation_create, name="consultation_create"),

    path("staff/", views.StaffListView.as_view(), name="staff"),
    path("cases/", views.CaseListView.as_view(), name="cases"),
    path("cases/<slug:slug>/", views.CaseDetailView.as_view(), name="case_detail"),

    path("news/", views.NewsListView.as_view(), name="news"),
    path("news/<slug:slug>/", views.NewsDetailView.as_view(), name="news_detail"),

    path("about/", views.AboutView.as_view(), name="about"),
    path("contacts/", views.ContactView.as_view(), name="contacts"),
]
