# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import CalendarEvent

@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'event_type_display', 
        'start_time', 
        'end_time', 
        'priority_display',
        'case_link',
        'client_display',
        'owner_link',
        'is_ongoing_display',
        'is_past_display'
    ]
    
    list_filter = [
        'event_type',
        'priority',
        'start_time',
        'end_time',
        'created_at',
        'owner'
    ]
    
    search_fields = [
        'title',
        'description',
        'location',
        'case__title',
        'client__username',
        'client__first_name',
        'client__last_name'
        'owner__username',
        'owner__first_name',
        'owner__last_name'
    ]
    
    filter_horizontal = ['participants']
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'event_type',
                'title',
                'description',
                'priority'
            )
        }),
        ('Время и место', {
            'fields': (
                'start_time',
                'end_time',
                'location'
            )
        }),
        ('Связи', {
            'fields': (
                'case',
                'client',
                'owner',
                'participants'
            )
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['created_at', 'updated_at']
        return self.readonly_fields
    
    def event_type_display(self, obj):
        return dict(CalendarEvent.EVENT_TYPES).get(obj.event_type, obj.event_type)
    event_type_display.short_description = 'Тип события'
    
    def priority_display(self, obj):
        priority_classes = {
            'low': 'secondary',
            'medium': 'info',
            'high': 'danger'
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            priority_classes.get(obj.priority, 'secondary'),
            dict(CalendarEvent.PRIORITY_CHOICES).get(obj.priority, obj.priority)
        )
    priority_display.short_description = 'Приоритет'
    
    def case_link(self, obj):
        if obj.case:
            return format_html(
                '<a href="/admin/cases/case/{}/change/">{}</a>',
                obj.case.id,
                obj.case.title
            )
        return '-'
    case_link.short_description = 'Дело'
    
    def client_link(self, obj):
        if obj.client:
            return format_html(
                '<a href="/admin/clients/client/{}/change/">{}</a>',
                obj.client.id,
                obj.client.name
            )
        return '-'
    client_link.short_description = 'Клиент'
    
    def owner_link(self, obj):
        if obj.owner:
            return format_html(
                '<a href="/admin/auth/user/{}/change/">{}</a>',
                obj.owner.id,
                obj.owner.get_full_name() or obj.owner.username
            )
        return '-'
    owner_link.short_description = 'Владелец'
    def client_display(self, obj):
        if obj.client:
            # Используем строковое представление клиента вместо поля name
            return format_html(
                '<a href="/admin/clients/client/{}/change/">{}</a>',
                obj.client.id,
                str(obj.client)  # Используем __str__ метод модели Client
            )
        return '-'
    client_display.short_description = 'Клиент'
    
    def is_ongoing_display(self, obj):
        now = timezone.now()
        is_ongoing = obj.start_time <= now <= obj.end_time
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            'success' if is_ongoing else 'secondary',
            'Активно' if is_ongoing else 'Неактивно'
        )
    is_ongoing_display.short_description = 'Статус'
    
    def is_past_display(self, obj):
        is_past = obj.end_time < timezone.now()
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            'warning' if is_past else 'info',
            'Завершено' if is_past else 'Предстоящее'
        )
    is_past_display.short_description = 'Состояние'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'case', 'client', 'owner'
        )
    
    class Media:
        css = {
            'all': ('css/admin_calendar.css',)
        }