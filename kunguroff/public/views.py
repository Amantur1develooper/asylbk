from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import SiteSettings, Practice, Staff, PublicCase, NewsPost, Vacancy
from .forms import ConsultationRequestForm


def _can_manage(user):
    return user.is_superuser or user.role in ('manager', 'director', 'deputy_director', 'managing_partner_advocate')

def get_settings():
    return SiteSettings.objects.first()

class HomeView(TemplateView):
    template_name = "public/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["site"] = get_settings()
        ctx["practices"] = Practice.objects.all()[:6]
        ctx["team"] = Staff.objects.all()[:6]
        ctx["cases"] = PublicCase.objects.filter(is_published=True)[:6]
        ctx["news"] = NewsPost.objects.filter(is_published=True)[:3]
        ctx["form"] = ConsultationRequestForm()
        return ctx

def consultation_create(request):
    if request.method != "POST":
        return redirect("public:home")

    form = ConsultationRequestForm(request.POST)
    if form.is_valid():
        form.save()  # уведомление отправляется через сигнал в signals.py (один раз)
        messages.success(request, "Заявка отправлена! Мы свяжемся с вами в ближайшее время.")
    else:
        messages.error(request, "Проверьте поля формы.")
    return redirect(request.META.get("HTTP_REFERER", "/"))



class StaffListView(ListView):
    template_name = "public/staff_list.html"
    model = Staff
    context_object_name = "staff"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["site"] = get_settings()
        return ctx

class CaseListView(ListView):
    template_name = "public/case_list.html"
    model = PublicCase
    context_object_name = "cases"

    def get_queryset(self):
        return PublicCase.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["site"] = get_settings()
        return ctx

class CaseDetailView(DetailView):
    template_name = "public/case_detail.html"
    model = PublicCase
    slug_field = "slug"
    slug_url_kwarg = "slug"
    context_object_name = "case"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["site"] = get_settings()
        return ctx


class NewsListView(ListView):
    template_name = "public/news_list.html"
    model = NewsPost
    context_object_name = "posts"

    def get_queryset(self):
        return NewsPost.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["site"] = get_settings()
        return ctx

class NewsDetailView(DetailView):
    template_name = "public/news_detail.html"
    model = NewsPost
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["site"] = get_settings()
        return ctx

class AboutView(TemplateView):
    template_name = "public/about.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["site"] = get_settings()
        return ctx

class ContactView(TemplateView):
    template_name = "public/contact.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["site"] = get_settings()
        ctx["form"] = ConsultationRequestForm()
        return ctx


# ── PUBLIC: Вакансии ──────────────────────────────────────────────
class VacancyListView(ListView):
    template_name = "public/vacancies.html"
    model = Vacancy
    context_object_name = "vacancies"

    def get_queryset(self):
        return Vacancy.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["site"] = get_settings()
        return ctx


# ── CRM: управление вакансиями ────────────────────────────────────
class VacancyManageMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not _can_manage(request.user):
            messages.error(request, "Нет доступа.")
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)


class VacancyManageListView(VacancyManageMixin, ListView):
    template_name = "vacancy/vacancy_list.html"
    model = Vacancy
    context_object_name = "vacancies"
    queryset = Vacancy.objects.all()


class VacancyCreateView(VacancyManageMixin, CreateView):
    template_name = "vacancy/vacancy_form.html"
    model = Vacancy
    fields = ["title", "department", "employment", "salary",
              "description", "requirements", "conditions", "is_active"]
    success_url = reverse_lazy("public:vacancy_manage_list")

    def form_valid(self, form):
        messages.success(self.request, "Вакансия создана.")
        return super().form_valid(form)


class VacancyUpdateView(VacancyManageMixin, UpdateView):
    template_name = "vacancy/vacancy_form.html"
    model = Vacancy
    fields = ["title", "department", "employment", "salary",
              "description", "requirements", "conditions", "is_active"]
    success_url = reverse_lazy("public:vacancy_manage_list")

    def form_valid(self, form):
        messages.success(self.request, "Вакансия обновлена.")
        return super().form_valid(form)


class VacancyDeleteView(VacancyManageMixin, DeleteView):
    template_name = "vacancy/vacancy_confirm_delete.html"
    model = Vacancy
    success_url = reverse_lazy("public:vacancy_manage_list")

    def form_valid(self, form):
        messages.success(self.request, "Вакансия удалена.")
        return super().form_valid(form)
