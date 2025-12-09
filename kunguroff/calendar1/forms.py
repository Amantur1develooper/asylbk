# calendar/forms.py
from django import forms
from django.utils import timezone
from datetime import timedelta

from .models import CalendarEvent


class CalendarEventForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = [
            'event_type', 'title', 'description', 'start_time', 'end_time',
            'location', 'priority', 'case', 'trustor', 'participants',
            'enable_notifications', 'notify_1_day', 'notify_12_hours',
            'notify_3_hours', 'notify_1_hour', 'notify_30_minutes',
            'notify_10_minutes', 'notify_1_minute'
        ]
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control datetimepicker',
                    'autocomplete': 'off',
                    'placeholder': 'Выберите дату и время начала'
                },
                format='%Y-%m-%dT%H:%M',
            ),
            'end_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control datetimepicker',
                    'autocomplete': 'off',
                    'placeholder': 'Выберите дату и время окончания'
                },
                format='%Y-%m-%dT%H:%M',
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Разрешаем формат с "T", который шлёт <input type="datetime-local">
        fmt = '%Y-%m-%dT%H:%M'
        self.fields['start_time'].input_formats = [fmt]
        self.fields['end_time'].input_formats = [fmt]
