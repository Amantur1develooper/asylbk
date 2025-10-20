from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from core.permissions import LawyerRequiredMixin, OwnerOrManagerMixin
from cases.models import Case
from .models import CalendarEvent
from .models import CalendarEvent

from django.views.generic import TemplateView
from django.utils import timezone
from datetime import datetime, timedelta
from .models import CalendarEvent  # ⬅️ ДОБАВЬТЕ ЭТОТ ИМПОРТ!

class CalendarView(TemplateView):
    template_name = 'calendar/calendar.html'
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем текущую дату
        today = timezone.now().date()
        
        try:
            # ⬇️ Теперь CalendarEvent доступен
            today_events = CalendarEvent.objects.filter(
                start_time__date=today
            ).select_related('case', 'owner')
            
            # События на неделю
            week_start = today
            week_end = today + timedelta(days=7)
            week_events = CalendarEvent.objects.filter(
                start_time__date__range=[week_start, week_end]
            ).select_related('case', 'owner')
            
            context.update({
                'today_events': today_events,
                'week_events': week_events,
                'today': today,
            })
            
        except Exception as e:
            # Обработка ошибок
            context.update({
                'today_events': [],
                'week_events': [],
                'today': today,
                'error': str(e)
            })
        
        return context
# class CalendarView(LawyerRequiredMixin, TemplateView):
#     template_name = 'calendar/calendar.html'
    
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         user = self.request.user
        
#         # Получаем параметры для календаря
#         view = self.request.GET.get('view', 'month')
#         date_str = self.request.GET.get('date')
        
#         if date_str:
#             try:
#                 current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
#             except ValueError:
#                 current_date = timezone.now().date()
#         else:
#             current_date = timezone.now().date()
        
#         # События на сегодня
#         today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         today_end = today_start + timedelta(days=1)
        
#         today_events = CalendarEvent.objects.filter(
#             Q(owner=user) | Q(participants=user),
#             start_time__range=[today_start, today_end]
#         ).order_by('start_time')
        
#         # Доступные типы событий и приоритеты для фильтров
#         from .models import CalendarEvent
#         event_types = CalendarEvent.EVENT_TYPES
#         priorities = CalendarEvent.PRIORITY_CHOICES
        
#         # Дела пользователя для фильтра
#         if user.role in ['lawyer', 'advocate']:
#             user_cases = Case.objects.filter(responsible_lawyer=user)
#         else:
#             user_cases = Case.objects.all()
        
#         context.update({
#             'view': view,
#             'current_date': current_date,
#             'today': timezone.now().date(),
#             'today_events': today_events,
#             'event_types': event_types,
#             'priorities': priorities,
#             'user_cases': user_cases,
#         })
        
#         return context

class EventListView(LawyerRequiredMixin, ListView):
    model = CalendarEvent
    template_name = 'calendar/event_list.html'
    context_object_name = 'events'
    paginate_by = 20
    
    @property
    def event_types(self):
        return CalendarEvent.EVENT_TYPES
    
    @property
    def priorities(self):
        return CalendarEvent.PRIORITY_CHOICES
    
    def get_queryset(self):
        user = self.request.user
        queryset = CalendarEvent.objects.filter(
            Q(owner=user) | Q(participants=user)
        ).distinct()
        
        # Фильтрация по типу события
        event_type = self.request.GET.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Фильтрация по дате
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(start_time__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(start_time__date__lte=date_to)
        
        # Фильтрация по приоритету
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Фильтрация по делу
        case_id = self.request.GET.get('case')
        if case_id:
            queryset = queryset.filter(case_id=case_id)
        
        return queryset.order_by('start_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Статистика
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        context['today'] = timezone.now().date()
        context['today_events_count'] = CalendarEvent.objects.filter(
            Q(owner=user) | Q(participants=user),
            start_time__range=[today_start, today_end]
        ).count()
        
        context['upcoming_events_count'] = CalendarEvent.objects.filter(
            Q(owner=user) | Q(participants=user),
            start_time__gt=timezone.now()
        ).count()
        
        return context
 
class EventCreateView(LawyerRequiredMixin, CreateView):
    model = CalendarEvent
    template_name = 'calendar/event_form.html'
    fields = [
        'event_type', 'title', 'description', 'start_time', 'end_time',
        'location', 'priority', 'case', 'trustor', 'participants',
        'enable_notifications', 'notify_1_day', 'notify_12_hours',
        'notify_3_hours', 'notify_1_hour', 'notify_30_minutes',
        'notify_10_minutes', 'notify_1_minute'
    ]
    success_url = reverse_lazy('calendar1:event_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Настройка виджетов для полей даты и времени
        form.fields['start_time'].widget.attrs.update({'class': 'datetimepicker'})
        form.fields['end_time'].widget.attrs.update({'class': 'datetimepicker'})
        
        # Ограничиваем выбор участников сотрудниками фирмы
        form.fields['participants'].queryset = form.fields['participants'].queryset.exclude(
            role='external_lawyer'
        )
        
        # Ограничиваем выбор дел только делами пользователя
        user = self.request.user
        if user.role in ['lawyer', 'advocate']:
            form.fields['case'].queryset = form.fields['case'].queryset.filter(
                responsible_lawyer=user
            )
        
        return form
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Событие успешно создано!')
        return super().form_valid(form)

class EventUpdateView(OwnerOrManagerMixin, UpdateView):
    model = CalendarEvent
    template_name = 'calendar/event_form.html'
    fields = [
        'event_type', 'title', 'description', 'start_time', 'end_time',
        'location', 'priority', 'case', 'trustor', 'participants',
        'enable_notifications', 'notify_1_day', 'notify_12_hours',
        'notify_3_hours', 'notify_1_hour', 'notify_30_minutes',
        'notify_10_minutes', 'notify_1_minute'
    ]
    
    def get_success_url(self):
        return reverse_lazy('calendar1:event_detail', kwargs={'pk': self.object.pk})
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['start_time'].widget.attrs.update({'class': 'datetimepicker'})
        form.fields['end_time'].widget.attrs.update({'class': 'datetimepicker'})
        form.fields['participants'].queryset = form.fields['participants'].queryset.exclude(
            role='external_lawyer'
        )
        return form
    
    def form_valid(self, form):
        messages.success(self.request, 'Событие успешно обновлено!')
        return super().form_valid(form)

class EventDetailView(LawyerRequiredMixin, DetailView):
    model = CalendarEvent
    template_name = 'calendar/event_detail.html'
    context_object_name = 'event'
    
    def get_queryset(self):
        user = self.request.user
        return CalendarEvent.objects.filter(
            Q(owner=user) | Q(participants=user)
        ).distinct()

class EventDeleteView(OwnerOrManagerMixin, DeleteView):
    model = CalendarEvent
    template_name = 'calendar/event_confirm_delete.html'
    success_url = reverse_lazy('calendar1:event_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Событие успешно удалено!')
        return super().delete(request, *args, **kwargs)

class CalendarJsonView(LawyerRequiredMixin, View):
    """JSON-представление для полного календаря"""
    def get(self, request, *args, **kwargs):
        user = request.user
        start = request.GET.get('start')
        end = request.GET.get('end')
        
        events = CalendarEvent.objects.filter(
            Q(owner=user) | Q(participants=user)
        )
        
        if start:
            events = events.filter(start_time__gte=start)
        if end:
            events = events.filter(end_time__lte=end)
        
        events_data = []
        for event in events:
            events_data.append({
                'id': event.id,
                'title': event.title,
                'start': event.start_time.isoformat(),
                'end': event.end_time.isoformat(),
                'allDay': event.is_all_day,
                'backgroundColor': self.get_event_color(event),
                'borderColor': self.get_event_color(event),
                'textColor': '#ffffff',
                'extendedProps': {
                    'type': event.event_type,
                    'type_display': event.get_event_type_display(),
                    'priority': event.priority,
                    'description': event.description,
                    'location': event.location,
                    'url': reverse_lazy('calendar1:event_detail', kwargs={'pk': event.pk})
                }
            })
        
        return JsonResponse(events_data, safe=False)
    
    def get_event_color(self, event):
        colors = {
            'meeting': '#3788D8',  # Синий
            'deadline': '#DC3545',  # Красный
            'reminder': '#20C997',  # Зеленый
            'personal': '#6F42C1',  # Фиолетовый
            'court_hearing': '#FD7E14',  # Оранжевый
            'client_meeting': '#E83E8C',  # Розовый
            'document_deadline': '#6F42C1',  # Фиолетовый
        }
        return colors.get(event.event_type, '#6C757D')

class QuickEventCreateView(LawyerRequiredMixin, View):
    """Быстрое создание события через AJAX"""
    def post(self, request, *args, **kwargs):
        try:
            title = request.POST.get('title')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            event_type = request.POST.get('event_type', 'meeting')
            
            event = CalendarEvent.objects.create(
                title=title,
                start_time=start_time,
                end_time=end_time,
                event_type=event_type,
                owner=request.user
            )
            
            return JsonResponse({
                'success': True,
                'event': {
                    'id': event.id,
                    'title': event.title,
                    'start': event.start_time.isoformat(),
                    'end': event.end_time.isoformat(),
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})