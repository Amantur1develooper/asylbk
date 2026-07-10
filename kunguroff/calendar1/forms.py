# calendar/forms.py
from django import forms
from django.utils import timezone
from datetime import timedelta, datetime

from .models import CalendarEvent
from users.models import User


def _telegram_users():
    """Пользователи с привязанным активным Telegram-аккаунтом."""
    return User.objects.filter(
        telegram_account__is_active=True,
    ).select_related('telegram_account').order_by('last_name', 'first_name', 'username')


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


class QuickReminderForm(forms.ModelForm):
    """Максимально простая форма напоминания: текст, дата, время и кому уведомить в Telegram."""

    date = forms.DateField(
        label="Дата",
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control form-control-lg'},
            format='%Y-%m-%d',
        ),
        input_formats=['%Y-%m-%d'],
    )
    time = forms.TimeField(
        label="Время",
        widget=forms.TimeInput(
            attrs={'type': 'time', 'class': 'form-control form-control-lg'},
            format='%H:%M',
        ),
        input_formats=['%H:%M'],
    )
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        label="Кому уведомить в Telegram",
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = CalendarEvent
        fields = ['title', 'participants']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'О чём напомнить?',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['participants'].queryset = _telegram_users()

        instance = kwargs.get('instance')
        if instance and instance.pk and instance.start_time:
            local_dt = timezone.localtime(instance.start_time)
            self.fields['date'].initial = local_dt.date()
            self.fields['time'].initial = local_dt.time()

    def save(self, commit=True):
        instance = super().save(commit=False)

        dt = datetime.combine(self.cleaned_data['date'], self.cleaned_data['time'])
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
        instance.start_time = dt
        instance.end_time = dt

        instance.event_type = 'reminder'
        instance.enable_notifications = True

        if commit:
            instance.save()
            self.save_m2m()
        return instance
