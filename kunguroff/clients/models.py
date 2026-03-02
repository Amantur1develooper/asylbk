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
        message="Номер телефона должен быть в формате: '+99655090400'. Допускается до 15 цифр."
    )
    phone = models.CharField(validators=[phone_regex],blank=True, null=True, max_length=17, verbose_name="Телефон")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    
    # Паспортные данные
    passport_series = models.CharField(max_length=14,blank=True, null=True, verbose_name="Серия паспорта")
    passport_number = models.CharField(max_length=7,blank=True, null=True, verbose_name="Номер паспорта")
    passport_issued_by = models.TextField(blank=True, null=True, verbose_name="Кем выдан")
    passport_issue_date = models.DateField(blank=True, null=True, verbose_name="Дата выдачи")
    registration_address = models.TextField(blank=True, null=True, verbose_name="Адрес регистрации")
    residence_address = models.TextField(blank=True, null=True, verbose_name="Адрес проживания")
    
    # Дополнительная информация
    inn = models.CharField(max_length=14, null=True, blank=True, verbose_name="ИНН")
    notes = models.TextField(blank=True, null=True, verbose_name="Заметки")
    
    # Связи
    
    primary_contact = models.ManyToManyField(
        User, 
        
        null=True, 
        blank=True,
        related_name='trustors',
        verbose_name="Ответственные (юрист/адвокат)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name="Дата обновления")
    representatives = models.ManyToManyField(
        "self",
        through="TrustorRepresentation",
        symmetrical=False,
        related_name="represented_trustors",
        blank=True,
        verbose_name="Представители"
    )
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

class TrustorRepresentation(models.Model):
    trustor = models.ForeignKey(
        Trustor,
        on_delete=models.CASCADE,
        related_name="representation_links",
        verbose_name="Доверитель"
    )
    representative = models.ForeignKey(
        Trustor,
        on_delete=models.CASCADE,
        related_name="as_representative_links",
        verbose_name="Представитель"
    )

    basis = models.CharField(max_length=255, blank=True, default="", verbose_name="Основание (доверенность/ордер)")
    doc_number = models.CharField(max_length=100, blank=True, default="", verbose_name="№ документа")
    issue_date = models.DateField(null=True, blank=True, verbose_name="Дата выдачи")
    expires_at = models.DateField(null=True, blank=True, verbose_name="Срок действия до")
    notes = models.TextField(blank=True, default="", verbose_name="Заметки")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Связь доверитель-представитель"
        verbose_name_plural = "Связи доверитель-представитель"
        unique_together = ("trustor", "representative")

    def __str__(self):
        return f"{self.representative} представляет {self.trustor}"