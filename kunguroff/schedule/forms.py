from django import forms
from .models import ScheduleEntry
from users.models import User


def _telegram_users():
    """Пользователи с привязанным активным Telegram-аккаунтом."""
    return User.objects.filter(
        telegram_account__is_active=True,
    ).select_related('telegram_account').order_by('last_name', 'first_name', 'username')


class ScheduleEntryForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control form-control-lg'},
            format='%Y-%m-%d',
        ),
        input_formats=['%Y-%m-%d'],
        label="Дата"
    )

    notify_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        label="Уведомить в Telegram",
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notify_users'].queryset = _telegram_users()

    class Meta:
        model = ScheduleEntry
        fields = ['date', 'time', 'client_name', 'opposing_party', 'court',
                  'responsible_staff', 'case_description', 'notes', 'notify_users']
        widgets = {
            'time': forms.TextInput(attrs={
                'type': 'time',
                'class': 'form-control form-control-lg',
                'placeholder': '10:00',
            }),
            'client_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'ФИО клиента или название организации',
            }),
            'opposing_party': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'ФИО / данные второй стороны (необязательно)',
            }),
            'court': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Суд, следственный орган, место встречи',
            }),
            'responsible_staff': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Ответственный сотрудник',
            }),
            'case_description': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'УД / ГД / АД / и т.д.',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Дополнительные примечания',
            }),
        }
