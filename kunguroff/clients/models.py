# from django.db import models
# from django.contrib.auth import get_user_model
# from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

class Trustor(models.Model):
    """Модель доверителя (бывший клиент)"""
    
    # Основная информация
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=100, blank=True, verbose_name="Отчество")
    
    # Контактная информация
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Номер телефона должен быть в формате: '+999999999'. Допускается до 15 цифр."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, verbose_name="Телефон")
    email = models.EmailField(blank=True, verbose_name="Email")
    
    # Паспортные данные
    passport_series = models.CharField(max_length=14, verbose_name="Серия паспорта")
    passport_number = models.CharField(max_length=7, verbose_name="Номер паспорта")
    passport_issued_by = models.TextField(verbose_name="Кем выдан")
    passport_issue_date = models.DateField(verbose_name="Дата выдачи")
    registration_address = models.TextField(verbose_name="Адрес регистрации")
    residence_address = models.TextField(blank=True, verbose_name="Адрес проживания")
    
    # Дополнительная информация
    inn = models.CharField(max_length=14, blank=True, verbose_name="ИНН")
    notes = models.TextField(blank=True, verbose_name="Заметки")
    
    # Связи
    
    primary_contact = models.ManyToManyField(
        User, 
        
        null=True, 
        blank=True,
        related_name='trustors',
        verbose_name="Ответственные (юрист/адвокат)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Доверитель"
        verbose_name_plural = "Доверители"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()
    
    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()
    
    def get_primary_contact_names(self):
        """Возвращает строку с именами ответственных юристов"""
        return ", ".join([lawyer.get_full_name() or lawyer.username 
                         for lawyer in self.primary_contact.all()])
# User = get_user_model()
