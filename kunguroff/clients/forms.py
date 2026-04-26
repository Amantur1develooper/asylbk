from django import forms
from .models import Trustor
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()


class ClientForm(forms.ModelForm):

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Номер телефона: '+99655090400'. До 15 цифр."
    )
    phone = forms.CharField(
        validators=[phone_regex],
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+996…'}),
        label="Телефон"
    )

    primary_contact = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role__in=['lawyer', 'advocate', 'managing_partner_advocate']).order_by('last_name', 'first_name'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Ответственные юристы/адвокаты"
    )

    class Meta:
        model = Trustor
        fields = [
            'entity_type',
            # Физ. лицо
            'first_name', 'last_name', 'middle_name',
            'passport_series', 'passport_number', 'passport_issued_by',
            'passport_issue_date',
            'preventive_measure', 'preventive_measure_date', 'preventive_measure_details',
            'location_status', 'location_details',
            # Юр. лицо
            'company_name', 'legal_form', 'reg_number',
            'director_name', 'contact_person',
            # Общие
            'phone', 'email',
            'registration_address', 'residence_address',
            'inn', 'notes', 'primary_contact',
        ]
        widgets = {
            'entity_type': forms.RadioSelect(attrs={'class': 'entity-type-radio'}),

            # Физ. лицо
            'first_name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'last_name':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество (необязательно)'}),
            'passport_series': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID / AN'}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234567'}),
            'passport_issued_by': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Кем и когда выдан'}),
            'passport_issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'preventive_measure': forms.Select(attrs={'class': 'form-select'}),
            'preventive_measure_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'preventive_measure_details': forms.TextInput(attrs={'class': 'form-control'}),
            'location_status': forms.Select(attrs={'class': 'form-select'}),
            'location_details': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Уточнение'}),

            # Юр. лицо
            'company_name':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Полное наименование'}),
            'legal_form':     forms.Select(attrs={'class': 'form-select'}),
            'reg_number':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': '№ свидетельства о регистрации'}),
            'director_name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ФИО директора / руководителя'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Контактное лицо в организации'}),

            # Общие
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'registration_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Юридический / регистрационный адрес'}),
            'residence_address':    forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Фактический адрес'}),
            'inn':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0000000000000'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Дополнительная информация'}),
        }
        labels = {
            'entity_type':    'Тип доверителя',
            'first_name':     'Имя *',
            'last_name':      'Фамилия *',
            'middle_name':    'Отчество',
            'company_name':   'Наименование организации *',
            'legal_form':     'Орг.-правовая форма',
            'reg_number':     'Рег. номер',
            'director_name':  'Руководитель',
            'contact_person': 'Контактное лицо',
            'registration_address': 'Юр. / рег. адрес',
            'residence_address':    'Фактический адрес',
            'inn':   'ИНН',
            'notes': 'Заметки',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.role in ['lawyer', 'advocate', 'managing_partner_advocate']:
            self.fields['primary_contact'].initial = [user]

        # Все поля необязательны по умолчанию — валидация делается в clean()
        for f in self.fields.values():
            f.required = False

    def clean(self):
        data = super().clean()
        etype = data.get('entity_type', 'individual')

        if etype == 'individual':
            if not data.get('first_name'):
                self.add_error('first_name', 'Укажите имя.')
            if not data.get('last_name'):
                self.add_error('last_name', 'Укажите фамилию.')
        else:
            if not data.get('company_name'):
                self.add_error('company_name', 'Укажите наименование организации.')

        return data

    def clean_passport_number(self):
        data = self.cleaned_data.get('passport_number', '')
        if data:
            if not data.isdigit():
                raise forms.ValidationError("Только цифры.")
            if len(data) != 7:
                raise forms.ValidationError("Должно быть 7 цифр.")
        return data

    def clean_inn(self):
        data = self.cleaned_data.get('inn', '')
        if data:
            if not data.isdigit():
                raise forms.ValidationError("ИНН — только цифры.")
            if len(data) not in [10, 12, 14]:
                raise forms.ValidationError("ИНН: 10, 12 или 14 цифр.")
        return data
