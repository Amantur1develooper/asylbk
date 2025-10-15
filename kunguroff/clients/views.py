from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from cases.models import Case
from .models import Trustor 
from .forms import ClientForm

# Список всех клиентов
class ClientListView(ListView):
    model = Trustor
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    paginate_by = 20
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        # Фильтрация по роли пользователя
        user = self.request.user
        if user.role in ['lawyer', 'advocate']:
            # Юристы видят только своих клиентов
            return Trustor.objects.filter(primary_contact=user)
        else:
            # Директора и менеджеры видят всех клиентов
            return Trustor.objects.all()

# Детальная информация о клиенте
class ClientDetailView(DetailView):
    model = Trustor
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        # Ограничиваем доступ юристам/адвокатам только к своим доверителям
        user = self.request.user
        if user.role in ['lawyer', 'advocate']:
            return Trustor.objects.filter(primary_contact=user)
        return Trustor.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trustor = self.object
        # Получаем все дела через участников
        cases = (Case.objects
                 .filter(participants__trustor=trustor)
                 .select_related("category", "responsible_lawyer"))
        context["cases"] = cases
        return context

# class ClientDetailView(DetailView):
#     model = Trustor
#     template_name = 'clients/client_detail.html'
#     context_object_name = 'client'
    
#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)
    
#     def get_queryset(self):
#         # Проверка прав доступа
#         user = self.request.user
#         if user.role in ['lawyer', 'advocate']:
#             return Trustor.objects.filter(primary_contact=user)
#         return Trustor.objects.all()

# Создание нового клиента
class ClientCreateView(CreateView):
    model = Trustor
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Только определенные роли могут создавать клиентов
        allowed_roles = ['manager', 'lawyer', 'advocate', 'director', 'deputy_director']
        if self.request.user.role not in allowed_roles:
            return redirect('permission_denied')
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        # Автоматически устанавливаем текущего пользователя как основного контакта
        # если он юрист/адвокат
        if self.request.user.role in ['lawyer', 'advocate']:
            form.instance.primary_contact = self.request.user
        return super().form_valid(form)

# Редактирование клиента
class ClientUpdateView(UpdateView):
    model = Trustor
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Проверка прав доступа
        client = self.get_object()
        user = self.request.user
        allowed_roles = ['manager', 'director', 'deputy_director']
        
        # Юристы могут редактировать только своих клиентов
        if user.role in ['lawyer', 'advocate'] and client.primary_contact != user:
            return redirect('permission_denied')
        
        # Менеджеры и директора могут редактировать всех
        if user.role not in allowed_roles + ['lawyer', 'advocate']:
            return redirect('permission_denied')
            
        return super().dispatch(*args, **kwargs)

# Удаление клиента
class ClientDeleteView(DeleteView):
    model = Trustor
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:client_list')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Только директора и зам.директора могут удалять клиентов
        user = self.request.user
        if user.role not in ['director', 'deputy_director']:
            return redirect('permission_denied')
        return super().dispatch(*args, **kwargs)