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
    
    # ИСПРАВЛЕНИЕ: Используем более удобный виджет для множественного выбора
    primary_contact = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role__in=['lawyer', 'advocate']).order_by('last_name', 'first_name'),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select select2-multiple',
            'data-placeholder': 'Выберите ответственных юристов...',
            'style': 'width: 100%'
        }),
        label="Ответственные юристы/адвокаты"
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
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите отчество (необязательно)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'email@example.com'
            }),
            'passport_series': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ID/NC'
            }),
            'passport_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1234567'
            }),
            'passport_issued_by': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Кем и когда выдан паспорт'
            }),
            'passport_issue_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }, format='%Y-%m-%d'),
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
                'placeholder': '0000000000'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Дополнительная информация о клиенте'
            }),
        }
        labels = {
            'first_name': 'Имя*',
            'last_name': 'Фамилия*',
            'middle_name': 'Отчество',
            'email': 'Email',
            'passport_series': 'Серия паспорта*',
            'passport_number': 'Номер паспорта*',
            'passport_issued_by': 'Кем и когда выдан*',
            'passport_issue_date': 'Дата выдачи*',
            'registration_address': 'Адрес регистрации*',
            'residence_address': 'Адрес проживания',
            'inn': 'ИНН',
            'notes': 'Заметки',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # ДОБАВЛЕНО: Для юристов/адвокатов автоматически выбираем текущего пользователя,
        # но оставляем возможность выбрать других
        if user and user.role in ['lawyer', 'advocate']:
            # Устанавливаем начальное значение - текущий пользователь
            self.fields['primary_contact'].initial = [user]
        
        # ДОБАВЛЕНО: Делаем поля обязательными
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['passport_series'].required = True
        self.fields['passport_number'].required = True
        self.fields['passport_issued_by'].required = True
        self.fields['passport_issue_date'].required = True
        self.fields['registration_address'].required = True
    
    def clean_passport_series(self):
        data = self.cleaned_data.get('passport_series', '')
        if data and not (2 == len(data) ):  # Увеличил до 4 символов
            raise forms.ValidationError("Серия паспорта должна содержать от 2 до 4 символов.")
        return data
    
    def clean_passport_number(self):
        data = self.cleaned_data['passport_number']
        if data and not data.isdigit():
            raise forms.ValidationError("Номер паспорта должен содержать только цифры")
        if data and len(data) != 7:
            raise forms.ValidationError("Номер паспорта должен содержать 7 цифр")
        return data
    
    def clean_inn(self):
        data = self.cleaned_data['inn']
        if data and not data.isdigit():
            raise forms.ValidationError("ИНН должен содержать только цифры")
        if data and len(data) not in [10, 12, 14]:
            raise forms.ValidationError("ИНН должен содержать 10 или 12 цифр")
        return data