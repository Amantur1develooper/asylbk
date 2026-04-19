from django.urls import path
from . import views

app_name = "public"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("consultation/", views.consultation_create, name="consultation_create"),

    path("staff/", views.StaffListView.as_view(), name="staff"),
    path("casess/", views.CaseListView.as_view(), name="casess"),
    path("casess/<slug:slug>/", views.CaseDetailView.as_view(), name="case_detail"),

    path("news/", views.NewsListView.as_view(), name="news"),
    path("news/<slug:slug>/", views.NewsDetailView.as_view(), name="news_detail"),

    path("about/", views.AboutView.as_view(), name="about"),
    path("contacts/", views.ContactView.as_view(), name="contacts"),

    # Public vacancies
    path("vacancies/", views.VacancyListView.as_view(), name="vacancies"),

    # CRM vacancy management
    path("manage/vacancies/", views.VacancyManageListView.as_view(), name="vacancy_manage_list"),
    path("manage/vacancies/add/", views.VacancyCreateView.as_view(), name="vacancy_create"),
    path("manage/vacancies/<int:pk>/edit/", views.VacancyUpdateView.as_view(), name="vacancy_edit"),
    path("manage/vacancies/<int:pk>/delete/", views.VacancyDeleteView.as_view(), name="vacancy_delete"),
]
