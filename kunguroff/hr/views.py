from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import Employee
from .forms import EmployeeForm


def hr_access(user):
    return user.is_superuser or user.role in ('manager', 'director', 'deputy_director')


class HRAccessMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not hr_access(request.user):
            messages.error(request, 'Нет доступа к отделу кадров.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


class EmployeeListView(HRAccessMixin, ListView):
    model = Employee
    template_name = 'hr/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20

    def get_queryset(self):
        qs = Employee.objects.all()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(full_name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class EmployeeDetailView(HRAccessMixin, DetailView):
    model = Employee
    template_name = 'hr/employee_detail.html'
    context_object_name = 'employee'


class EmployeeCreateView(HRAccessMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr/employee_form.html'
    success_url = reverse_lazy('hr:employee_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Сотрудник «{form.instance.full_name}» добавлен.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Добавить сотрудника'
        return ctx


class EmployeeUpdateView(HRAccessMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr/employee_form.html'
    success_url = reverse_lazy('hr:employee_list')

    def form_valid(self, form):
        messages.success(self.request, f'Данные «{form.instance.full_name}» обновлены.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Редактировать: {self.object.full_name}'
        return ctx


class EmployeeDeleteView(HRAccessMixin, DeleteView):
    model = Employee
    template_name = 'hr/employee_confirm_delete.html'
    success_url = reverse_lazy('hr:employee_list')

    def form_valid(self, form):
        messages.success(self.request, 'Сотрудник удалён.')
        return super().form_valid(form)
