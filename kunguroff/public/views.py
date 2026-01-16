from django.shortcuts import render
from .telegram import send_telegram_message, format_consultation
from django.db import transaction
from .telegram_notify import notify_consultation_request

from django.views.generic import TemplateView, ListView, DetailView
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import SiteSettings, Practice, Staff, PublicCase, NewsPost
from .forms import ConsultationRequestForm

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
        obj = form.save()

        # отправляем в телеграм только после успешного коммита в БД
        transaction.on_commit(lambda: notify_consultation_request(obj.id))

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
