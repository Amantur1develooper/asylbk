from django.contrib import admin
from .models import CalendarEvent, EventNotification

@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'event_type', 'start_time', 'end_time', 'priority', 
        'trustor', 'case', 'owner', 'enable_notifications'
    ]
    list_filter = [
        'event_type', 'priority', 'start_time', 'enable_notifications',
        'owner', 'trustor'
    ]
    search_fields = [
        'title', 'description', 'trustor__first_name', 
        'trustor__last_name', 'case__title'
    ]
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['participants']
    
    fieldsets = (
        (None, {
            'fields': ('event_type', 'title', 'description')
        }),
        ('Время и место', {
            'fields': ('start_time', 'end_time', 'location')
        }),
        ('Дополнительная информация', {
            'fields': ('priority', 'case', 'trustor', 'owner', 'participants')
        }),
        ('Уведомления', {
            'fields': (
                'enable_notifications', 
                'notify_1_day', 
                'notify_12_hours', 
                'notify_3_hours', 
                'notify_1_hour', 
                'notify_30_minutes', 
                'notify_10_minutes', 
                'notify_1_minute'
            )
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('trustor', 'case', 'owner')

@admin.register(EventNotification)
class EventNotificationAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'notification_type', 'scheduled_time', 'sent', 'sent_at']
    list_filter = ['sent', 'notification_type', 'scheduled_time']
    readonly_fields = ['created_at']
    search_fields = ['event__title', 'user__username']