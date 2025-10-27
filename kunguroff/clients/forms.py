from django import forms
from .models import Trustor
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

class ClientForm(forms.ModelForm):
    # Валидаторы для полей
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Номер телефона должен быть в формате: '+999999999'. Допускается до 15 цифр."
    )
    
    phone = forms.CharField(
        validators=[phone_regex],
        max_length=17,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+79991234567'
        }),
        label="Телефон"
    )
    
    # Переопределяем поле для выбора основного контакта
    primary_contact = forms.ModelChoiceField(
        queryset=User.objects.filter(role__in=['lawyer', 'advocate']),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Ответственный юрист/адвокат"
    )
    
    class Meta:
        model = Trustor
        fields = [
            'first_name', 'last_name', 'middle_name',
            'phone', 'email',
            'passport_series', 'passport_number', 'passport_issued_by',
            'passport_issue_date', 'registration_address', 'residence_address',
            'inn', 'notes', 'primary_contact'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'passport_series': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': '[0-9]{14}',
                'title': '14 цифры серии паспорта'
            }),
            'passport_number': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': '[0-9]{7}',
                'title': '7 цифр номера паспорта'
            }),
            'passport_issued_by': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Кем и когда выдан паспорт'
            }),
            'passport_issue_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            },
                             format='%Y-%m-%d' ),  # важно для отображения                      
            'registration_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Адрес регистрации'
            }),
            'residence_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Адрес проживания (если отличается от регистрации)'
            }),
            'inn': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': '[0-9]{10,12,14}',
                'title': '10 или 12 цифр ИНН'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Дополнительная информация о клиенте'
            }),
        }
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'middle_name': 'Отчество',
            'email': 'Email',
            'passport_series': 'Серия паспорта',
            'passport_number': 'Номер паспорта',
            'passport_issued_by': 'Кем и когда выдан',
            'passport_issue_date': 'Дата выдачи',
            'registration_address': 'Адрес регистрации',
            'residence_address': 'Адрес проживания',
            'inn': 'ИНН',
            'notes': 'Заметки',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Если пользователь - юрист/адвокат, ограничиваем выбор только собой
        if user and user.role in ['lawyer', 'advocate']:
            self.fields['primary_contact'].queryset = User.objects.filter(pk=user.pk)
            self.fields['primary_contact'].initial = user
            self.fields['primary_contact'].empty_label = None
    
    def clean_passport_series(self):
        data = self.cleaned_data['passport_series']
        if data and not data.isdigit():
            raise forms.ValidationError("Серия паспорта должна содержать только цифры")
        return data
    
    def clean_passport_number(self):
        data = self.cleaned_data['passport_number']
        if data and not data.isdigit():
            raise forms.ValidationError("Номер паспорта должен содержать только цифры")
        return data
    
    def clean_inn(self):
        data = self.cleaned_data['inn']
        if data and not data.isdigit():
            raise forms.ValidationError("ИНН должен содержать только цифры")
        if data and len(data) not in [10, 12, 14]:
            raise forms.ValidationError("ИНН должен содержать 10 или 12 цифр")
        return data