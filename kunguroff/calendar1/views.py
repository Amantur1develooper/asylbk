from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from datetime import datetime, timedelta
from django.utils import timezone
from core.permissions import LawyerRequiredMixin, OwnerOrManagerMixin
from .models import CalendarEvent
# from kunguroff.calendar1 import models
from django.db.models import Q
class CalendarView(LawyerRequiredMixin, ListView):
    template_name = 'calendar/calendar.html'
    context_object_name = 'events'
    
    def get_queryset(self):
        user = self.request.user
        # Пользователь видит свои события и события, где он участник
        return CalendarEvent.objects.filter(
            Q(owner=user) | Q(participants=user)
        ).distinct().order_by('start_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем параметры фильтрации
        view = self.request.GET.get('view', 'month')
        year = int(self.request.GET.get('year', timezone.now().year))
        month = int(self.request.GET.get('month', timezone.now().month))
        
        context['view'] = view
        context['year'] = year
        context['month'] = month
        
        return context

class EventListView(LawyerRequiredMixin, ListView):
    model = CalendarEvent
    template_name = 'calendar/event_list.html'
    context_object_name = 'events'
    paginate_by = 20
    
    def get_queryset(self):
        user = self.request.user
        queryset = CalendarEvent.objects.filter(
            Q(owner=user) | Q(participants=user)
        ).distinct()
        
        # Фильтрация по типу события
        event_type = self.request.GET.get('type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Фильтрация по дате
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(start_time__gte=date_from)
        if date_to:
            queryset = queryset.filter(start_time__lte=date_to)
        
        # Фильтрация по приоритету
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset.order_by('-start_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        return context

class EventCreateView(LawyerRequiredMixin, CreateView):
    model = CalendarEvent
    template_name = 'calendar/event_form.html'
    fields = [
        'event_type', 'title', 'description', 'start_time', 'end_time',
        'location', 'priority', 'case', 'client', 'participants'
    ]
    success_url = reverse_lazy('calendar:event_list')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Ограничиваем выбор участников сотрудниками фирмы
        form.fields['participants'].queryset = form.fields['participants'].queryset.exclude(
            role='external_lawyer'
        )
        return form

class EventUpdateView(OwnerOrManagerMixin, UpdateView):
    model = CalendarEvent
    template_name = 'calendar/event_form.html'
    fields = [
        'event_type', 'title', 'description', 'start_time', 'end_time',
        'location', 'priority', 'case', 'client', 'participants'
    ]
    
    def get_success_url(self):
        return reverse_lazy('calendar:event_detail', kwargs={'pk': self.object.pk})
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['participants'].queryset = form.fields['participants'].queryset.exclude(
            role='external_lawyer'
        )
        return form

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
    success_url = reverse_lazy('calendar:event_list')

class CalendarJsonView(LawyerRequiredMixin, View):
    """JSON-представление для полного календаря"""
    def get(self, request, *args, **kwargs):
        user = request.user
        start = request.GET.get('start')
        end = request.GET.get('end')
        
        events = CalendarEvent.objects.filter(
            Q(owner=user) | Q(participants=user),
            start_time__gte=start,
            end_time__lte=end
        ).distinct()
        
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
                    'priority': event.priority,
                    'description': event.description,
                    'location': event.location,
                    'url': reverse_lazy('calendar:event_detail', kwargs={'pk': event.pk})
                }
            })
        
        return JsonResponse(events_data, safe=False)
    
    def get_event_color(self, event):
        colors = {
            'meeting': '#3788D8',  # Синий
            'deadline': '#DC3545',  # Красный
            'reminder': '#20C997',  # Зеленый
            'personal': '#6F42C1',  # Фиолетовый
        }
        return colors.get(event.event_type, '#6C757D')  # Серый по умолчанию