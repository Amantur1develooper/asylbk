from django import forms
from .models import ScheduleEntry


class ScheduleEntryForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg'}),
        label="Дата"
    )

    class Meta:
        model = ScheduleEntry
        fields = ['date', 'time', 'client_name', 'opposing_party', 'court',
                  'responsible_staff', 'case_description', 'notes']
        widgets = {
            'time': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Например: 10:00 или 10:00-11:30',
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
