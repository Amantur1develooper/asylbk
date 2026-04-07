from django.contrib import admin
from .models import ScheduleEntry


@admin.register(ScheduleEntry)
class ScheduleEntryAdmin(admin.ModelAdmin):
    list_display = ['date', 'time', 'client_name', 'court', 'responsible_staff', 'case_description']
    list_filter = ['date', 'responsible_staff']
    search_fields = ['client_name', 'court', 'responsible_staff', 'notes']
    date_hierarchy = 'date'
    ordering = ['date', 'time']
