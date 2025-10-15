from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    ROLE_CHOICES = [
        ('director', 'Директор'),
        ('deputy_director', 'Зам.директора'),
        ('manager', 'Менеджер'),
        ('lawyer', 'Юрист'),
        ('advocate', 'Адвокат'),
        ('accountant', 'Бухгалтер'),
        ('hr', 'HR-менеджер'),
        ('admin', 'Админ'),
        ('trainee', 'Стажер'),
        ('external_lawyer', 'Внешний юрист'),
    ]
    
    POSITION_CHOICES = [
        ('trainee', 'Стажер'),
        ('assistant', 'Помощник'),
        ('senior_assistant', 'Ст. помощник'),
        ('junior_lawyer', 'Мл. Юрист'),
        ('lawyer', 'Юрист'),
        ('senior_lawyer', 'Ст. Юрист'),
        ('leading_lawyer', 'Ведущий Юр.'),
        ('chief_lawyer', 'Главный юр.'),
        ('partner_advocate', 'Партнер – Адвокат'),
        ('senior_partner_advocate', 'Старший партнер-Адвокат'),
        ('managing_partner_advocate', 'Управ.партнер-Адвокат'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='lawyer')
    position = models.CharField(max_length=30, choices=POSITION_CHOICES, blank=True)
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Номер телефона должен быть в формате: '+999999999'. Допускается до 15 цифр."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    # Паспортные данные (шифровать на уровне приложения)
    passport_series = models.CharField(max_length=4, blank=True)
    passport_number = models.CharField(max_length=6, blank=True)
    passport_issued_by = models.TextField(blank=True)
    passport_issue_date = models.DateField(null=True, blank=True)
    registration_address = models.TextField(blank=True)
    
    # Трудовые данные
    hire_date = models.DateField(null=True, blank=True)
    contract_file = models.FileField(upload_to='employee_contracts/', blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        
        
class PracticeType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Тип стажировки"
        verbose_name_plural = "Типы стажировки"

class TraineeProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='trainee_profile'
    )
    practice_type = models.ForeignKey(
        PracticeType, 
        on_delete=models.PROTECT,
        verbose_name="Тип стажировки"
    )
    curator = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'role__in': ['lawyer', 'advocate']},
        related_name='trainees',
        verbose_name="Куратор"
    )
    program_description = models.TextField(blank=True, verbose_name="Описание программы")
    
    # Документы стажера
    diploma = models.FileField(upload_to='trainee_documents/', blank=True, verbose_name="Диплом")
    passport_copy = models.FileField(upload_to='trainee_documents/', blank=True, verbose_name="Копия паспорта")
    application = models.FileField(upload_to='trainee_documents/', blank=True, verbose_name="Заявление")
    practice_contract = models.FileField(upload_to='trainee_documents/', verbose_name="Договор стажировки")
    
    def __str__(self):
        return f"Стажер: {self.user.get_full_name()}"
    
    class Meta:
        verbose_name = "Профиль стажера"
        verbose_name_plural = "Профили стажеров"