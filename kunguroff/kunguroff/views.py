from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Avg
from django.utils import timezone
import json

from cases.models import Case
from clients.models import Trustor


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Дела по роли
        if user.role in ['lawyer', 'advocate', 'managing_partner_advocate']:
            cases = Case.objects.filter(responsible_lawyer=user)
        else:
            cases = Case.objects.all()

        # ── Карточки статистики ──
        context['cases_count']   = cases.count()
        context['active_cases']  = cases.filter(status='in_progress').count()
        context['clients_count'] = Trustor.objects.count()

        # события сегодня из calendar1
        try:
            from calendar1.models import Event
            today = timezone.localdate()
            context['today_events'] = Event.objects.filter(
                date=today, assigned_to=user
            ).count()
            context['upcoming_events'] = Event.objects.filter(
                date__gte=today, assigned_to=user
            ).order_by('date', 'start_time')[:5]
        except Exception:
            context['today_events']    = 0
            context['upcoming_events'] = []

        # Недавние дела
        context['recent_cases'] = cases.order_by('-created_at')[:5]

        # ── Данные для графиков ──

        # 1. Дела по статусам
        status_labels = []
        status_data   = []
        status_colors = []
        STATUS_COLORS = {
            'open':        '#6c757d',
            'in_progress': '#0d6efd',
            'paused':      '#ffc107',
            'completed':   '#198754',
            'archived':    '#adb5bd',
        }
        STATUS_NAMES = {
            'open':        'Открыто',
            'in_progress': 'В процессе',
            'paused':      'Приостановлено',
            'completed':   'Завершено',
            'archived':    'Архив',
        }
        for row in cases.values('status').annotate(cnt=Count('id')).order_by('status'):
            status_labels.append(STATUS_NAMES.get(row['status'], row['status']))
            status_data.append(row['cnt'])
            status_colors.append(STATUS_COLORS.get(row['status'], '#999'))

        context['chart_status_labels'] = json.dumps(status_labels, ensure_ascii=False)
        context['chart_status_data']   = json.dumps(status_data)
        context['chart_status_colors'] = json.dumps(status_colors)

        # 2. Дела по категориям — количество + средний прогресс
        cat_labels   = []
        cat_counts   = []
        cat_progress = []
        for row in (
            cases
            .values('category__name')
            .annotate(cnt=Count('id'), avg_prog=Avg('progress'))
            .order_by('-cnt')
        ):
            from cases.models import CaseCategory
            # Получаем читаемое название категории
            try:
                cat = CaseCategory.objects.get(name=row['category__name'])
                label = cat.get_name_display()
            except Exception:
                label = row['category__name'] or '—'
            cat_labels.append(label)
            cat_counts.append(row['cnt'])
            cat_progress.append(round(row['avg_prog'] or 0, 1))

        context['chart_cat_labels']   = json.dumps(cat_labels,   ensure_ascii=False)
        context['chart_cat_counts']   = json.dumps(cat_counts)
        context['chart_cat_progress'] = json.dumps(cat_progress)

        # 3. Новые дела по месяцам (последние 6 мес.)
        from django.db.models.functions import TruncMonth
        from datetime import date
        from dateutil.relativedelta import relativedelta
        month_labels = []
        month_data   = []
        today_date = date.today()
        for i in range(5, -1, -1):
            m = today_date - relativedelta(months=i)
            count = cases.filter(
                created_at__year=m.year,
                created_at__month=m.month
            ).count()
            month_labels.append(f'{m.month:02d}.{m.year}')
            month_data.append(count)

        context['chart_month_labels'] = json.dumps(month_labels)
        context['chart_month_data']   = json.dumps(month_data)

        return context
    

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView

def user_logout(request):
    logout(request)
    return redirect('login')


class SmartLoginView(LoginView):
    """Если пользователь уже вошёл — сразу перенаправляем на дашборд."""
    template_name = 'login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
