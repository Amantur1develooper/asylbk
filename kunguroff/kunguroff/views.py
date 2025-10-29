from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from cases.models import Case
from clients.models import Trustor 

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Получаем дела в зависимости от роли пользователя
        if user.role in ['lawyer', 'advocate']:
            cases = Case.objects.filter(responsible_lawyer=user)
        elif user.role == 'manager':
            # Менеджеры видят дела своей команды
            # Здесь нужно доработать логику определения команды
            cases = Case.objects.all()
        else:
            # Директора и админы видят все дела
            cases = Case.objects.all()
        
        # Статистика для дашборда
        context['cases_count'] = cases.count()
        context['active_cases'] = cases.filter(status='in_progress').count()
        context['clients_count'] = Trustor.objects.count()
        context['today_events'] = 0  # Заглушка, нужно реализовать модель событий
        
        # Недавние дела
        context['recent_cases'] = cases.order_by('-created_at')[:5]
        
        # Ближайшие события (заглушка)
        context['upcoming_events'] = []
        
        return context
    

from django.contrib.auth import logout
from django.shortcuts import redirect

def user_logout(request):
    logout(request)  # очищает сессию пользователя
    return redirect('login')  # перенаправляем на страницу входа
