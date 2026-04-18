from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q

from .models import Organization, Region
from .forms import OrganizationForm, RegionForm


def can_edit(user):
    return user.is_superuser or user.role in ('manager', 'director', 'deputy_director')


class DirectoryListView(LoginRequiredMixin, ListView):
    model = Organization
    template_name = 'directory/list.html'
    context_object_name = 'organizations'
    paginate_by = 30

    def get_queryset(self):
        qs = Organization.objects.select_related('region')
        q        = self.request.GET.get('q', '').strip()
        org_type = self.request.GET.get('type', '')
        region   = self.request.GET.get('region', '')
        district = self.request.GET.get('district', '').strip()

        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(head_name__icontains=q) |
                Q(district__icontains=q) |
                Q(phone__icontains=q)
            )
        if org_type:
            qs = qs.filter(org_type=org_type)
        if region:
            qs = qs.filter(region_id=region)
        if district:
            qs = qs.filter(district__icontains=district)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['regions']   = Region.objects.all()
        ctx['org_types'] = Organization.ORG_TYPES
        ctx['q']         = self.request.GET.get('q', '')
        ctx['sel_type']  = self.request.GET.get('type', '')
        ctx['sel_region']= self.request.GET.get('region', '')
        ctx['sel_dist']  = self.request.GET.get('district', '')
        ctx['can_edit']  = can_edit(self.request.user)
        # Уникальные районы для фильтра
        ctx['districts'] = (
            Organization.objects.exclude(district='')
            .values_list('district', flat=True)
            .distinct()
            .order_by('district')
        )
        return ctx


class OrganizationDetailView(LoginRequiredMixin, DetailView):
    model = Organization
    template_name = 'directory/detail.html'
    context_object_name = 'org'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['can_edit'] = can_edit(self.request.user)
        return ctx


class OrganizationCreateView(LoginRequiredMixin, CreateView):
    model = Organization
    form_class = OrganizationForm
    template_name = 'directory/form.html'
    success_url = reverse_lazy('directory:list')

    def dispatch(self, request, *args, **kwargs):
        if not can_edit(request.user):
            messages.error(request, 'Нет прав для добавления.')
            return redirect('directory:list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'«{form.instance.name}» добавлена.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Добавить организацию'
        return ctx


class OrganizationUpdateView(LoginRequiredMixin, UpdateView):
    model = Organization
    form_class = OrganizationForm
    template_name = 'directory/form.html'
    success_url = reverse_lazy('directory:list')

    def dispatch(self, request, *args, **kwargs):
        if not can_edit(request.user):
            messages.error(request, 'Нет прав для редактирования.')
            return redirect('directory:list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, f'«{form.instance.name}» обновлена.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Редактировать: {self.object.name}'
        return ctx


class OrganizationDeleteView(LoginRequiredMixin, DeleteView):
    model = Organization
    template_name = 'directory/confirm_delete.html'
    success_url = reverse_lazy('directory:list')

    def dispatch(self, request, *args, **kwargs):
        if not can_edit(request.user):
            messages.error(request, 'Нет прав для удаления.')
            return redirect('directory:list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Запись удалена.')
        return super().form_valid(form)


# --- Управление регионами (только суперпользователь/директор) ---
class RegionCreateView(LoginRequiredMixin, CreateView):
    model = Region
    form_class = RegionForm
    template_name = 'directory/region_form.html'
    success_url = reverse_lazy('directory:list')

    def dispatch(self, request, *args, **kwargs):
        if not can_edit(request.user):
            return redirect('directory:list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, f'Регион «{form.instance.name}» добавлен.')
        return super().form_valid(form)
