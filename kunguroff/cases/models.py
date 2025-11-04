from django.db import models
from django.contrib.auth import get_user_model
from clients.models import Trustor

User = get_user_model()

class CaseCategory(models.Model):
    CATEGORY_TYPES = [
        ('civil_economic', 'Гражданские - Экономические дела'),
        ('administrative', 'Административные дела'),
        ('civil_administrative', 'Гражданский – Административный'),
        ('criminal', 'Уголовные дела'),
        ('offenses', 'Правонарушения'),
    ]
    
    name = models.CharField(max_length=50, choices=CATEGORY_TYPES, unique=True, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    class Meta:
        verbose_name = "Категория дела"
        verbose_name_plural = "Категории дел"
    
    def __str__(self):
        return self.get_name_display()

class CaseStage(models.Model):
    category = models.ForeignKey(
        CaseCategory, 
        on_delete=models.CASCADE, 
        related_name='stages',
        verbose_name="Категория дела"
    )
    name = models.CharField(max_length=100, verbose_name="Название этапа")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    class Meta:
        verbose_name = "Этап дела"
        verbose_name_plural = "Этапы дел"
        ordering = ['category', 'order']
        unique_together = ['category', 'order']
    
    def __str__(self):
        return f"{self.category} - {self.name}"

class StageField(models.Model):
    FIELD_TYPES = [
        ('text', 'Текст'),
        ('file', 'Файл'),
        ('date', 'Дата'),
        ('select', 'Выбор из списка'),
        ('number', 'Число'),
    ]
    
    stage = models.ForeignKey(
        CaseStage, 
        on_delete=models.CASCADE, 
        related_name='fields',
        verbose_name="Этап дела"
    )
    name = models.CharField(max_length=100, verbose_name="Название поля")
    field_type = models.CharField(max_length=10, choices=FIELD_TYPES, verbose_name="Тип поля")
    is_required = models.BooleanField(default=False, verbose_name="Обязательное поле")
    options = models.TextField(
        blank=True, 
        help_text="Для полей типа 'select' укажите варианты через запятую",
        verbose_name="Варианты выбора"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    
    class Meta:
        verbose_name = "Поле этапа"
        verbose_name_plural = "Поля этапов"
        ordering = ['stage', 'order']
    
    def __str__(self):
        return f"{self.stage} - {self.name}"

class Case(models.Model):
    STATUS_CHOICES = [
        ('open', 'Открыто'),
        ('in_progress', 'В процессе'),
        ('paused', 'Приостановлено'),
        ('completed', 'Завершено'),
        ('archived', 'Архив'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Статья ук - описание")
    description = models.TextField(blank=True, verbose_name="Описание")
    category = models.ForeignKey(
        CaseCategory, 
        on_delete=models.PROTECT, 
        related_name='cases',
        verbose_name="Категория дела"
    )
    responsible_lawyer = models.ManyToManyField(
        User, 
        blank=True,
        null=True,
        related_name='cases',
        verbose_name="Ответственный юрист/адвокат"
    )
    manager = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='managed_cases',
        verbose_name="Менеджер"
    )
    current_stage = models.ForeignKey(
        CaseStage, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Текущий этап"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='open',
        verbose_name="Статус дела"
    )
    progress = models.PositiveIntegerField(default=0, verbose_name="Прогресс (%)")
    
    # Судебная информация
    court_name = models.CharField(max_length=300, blank=True, verbose_name="Наименование суда")
    case_number = models.CharField(max_length=100, blank=True, verbose_name="Номер дела в суде")
    judge_name = models.CharField(max_length=200, blank=True, verbose_name="ФИО судьи")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Дело"
        verbose_name_plural = "Дела"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def main_trustor(self):
        """Основной доверитель по делу"""
        main_participant = self.participants.filter(main_participant=True).first()
        return main_participant.trustor if main_participant else None
    
    @property
    def all_trustors(self):
        """Все доверители по делу"""
        return [participant.trustor for participant in self.participants.all()]
    
    @property
    def participants_by_role(self):
        """Участники дела сгруппированные по ролям"""
        from django.db.models import Count
        return self.participants.values('role__role_name').annotate(count=Count('id'))
    
    def get_responsible_lawyers_names(self):
        """Возвращает строку с именами ответственных юристов"""
        return ", ".join([lawyer.get_full_name() or lawyer.username 
                         for lawyer in self.responsible_lawyer.all()])
    def calculate_progress(self):
        """Метод для расчета прогресса дела на основе заполненных обязательных полей"""
        total_required = 0
        completed_required = 0
        
        # Проверяем, что у дела есть категория и связанные этапы
        if not self.category:
            self.progress = 0
            self.save()
            return self.progress
            
        for stage in self.category.stages.all():
            required_fields = stage.fields.filter(is_required=True)
            
            for field in required_fields:
                total_required += 1
                # Проверяем, существует ли документ для этого поля
                if self.documents.filter(stage=stage, field=field).exists():
                    completed_required += 1
        
        print(f"DEBUG: total_required={total_required}, completed_required={completed_required}")
        
        if total_required > 0:
            new_progress = int((completed_required / total_required) * 100)
        else:
            new_progress = 0
        
        # Сохраняем только если прогресс изменился
        if self.progress != new_progress:
            self.progress = new_progress
            self.save(update_fields=['progress', 'updated_at'])
        
        return self.progress

class CaseDocument(models.Model):
    case = models.ForeignKey(
        Case, 
        on_delete=models.CASCADE, 
        related_name='documents',
        verbose_name="Дело"
    )
    stage = models.ForeignKey(
        CaseStage, 
        on_delete=models.CASCADE,
        verbose_name="Этап"
    )
    field = models.ForeignKey(
        StageField, 
        on_delete=models.CASCADE,
        verbose_name="Поле"
    )
    text_value = models.TextField(blank=True, verbose_name="Текстовое значение")
    file_value = models.FileField(
        upload_to='case_documents/%Y/%m/%d/', 
        blank=True,
        verbose_name="Файл"
    )
    date_value = models.DateField(null=True, blank=True, verbose_name="Дата")
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Кем создано"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Документ дела"
        verbose_name_plural = "Документы дел"
        unique_together = ['case', 'stage', 'field']
    
    def __str__(self):
        return f"{self.case} - {self.stage} - {self.field}"
    
    def save(self, *args, **kwargs):
        """Переопределяем save для автоматического пересчета прогресса"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # После сохранения документа пересчитываем прогресс дела
        if is_new:
            self.case.calculate_progress()

class CaseParticipantRole(models.Model):
    """Роли участников дела в зависимости от категории"""
    
    category = models.ForeignKey(
        CaseCategory, 
        on_delete=models.CASCADE, 
        related_name='participant_roles',
        verbose_name="Категория дела"
    )
    role_code = models.CharField(max_length=50, verbose_name="Код роли")
    role_name = models.CharField(max_length=100, verbose_name="Название роли")
    description = models.TextField(blank=True, verbose_name="Описание роли")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    
    
    
    class Meta:
        verbose_name = "Роль участника дела"
        verbose_name_plural = "Роли участников дела"
        ordering = ['category', 'order']
        unique_together = ['category', 'role_code']
    
    def __str__(self):
        return f"{self.category} - {self.role_name}"
    
    @classmethod
    def get_roles_for_category(cls, category_name):
        """Получить роли для конкретной категории дела"""
        role_mapping = {
            'civil_economic': [
                ('plaintiff', 'Истец'),
                ('defendant', 'Ответчик'),
                ('third_party', 'Третьи лица'),
                ('prosecutor', 'Прокурор'),
                ('other_representative', 'Лица, обращающиеся в суд в защиту прав других лиц'),
                ('trustor', 'Доверитель'),
            ],
            'civil_administrative': [
                ('plaintiff', 'Истец'),
                ('defendant', 'Ответчик'),
                ('third_party', 'Третьи лица'),
                ('prosecutor', 'Прокурор'),
                ('other_representative', 'Лица, обращающиеся в суд в защиту прав других лиц'),
                ('trustor', 'Доверитель'),
            ],
            'administrative': [
                ('applicant', 'Заявитель'),
                ('respondent', 'Ответчик'),
                ('third_party', 'Третьи лица'),
                ('prosecutor', 'Прокурор'),
                ('other_representative', 'Лица, обращающиеся в суд в защиту прав других лиц'),
                ('trustor', 'Доверитель'),
            ],
            'criminal': [
                ('applicant', 'Заявитель'),
                ('witness', 'Свидетель'),
                ('suspect', 'Подозреваемый'),
                ('accused', 'Обвиняемый'),
                ('acquitted', 'Оправданный'),
                ('convicted', 'Осужденный'),
                ('trustor', 'Доверитель'),
            ],
            'offenses': [
                ('violator', 'Лицо, привлекаемое за совершение правонарушения'),
                ('victim', 'Пострадавший'),
                ('witness', 'Свидетель'),
                ('legal_representative', 'Законный представитель'),
                ('representative', 'Представитель'),
                ('trustor', 'Доверитель'),
            ],
        }
        return role_mapping.get(category_name, [])

class CaseParticipant(models.Model):
    """Участник дела с определенной ролью"""
    
    case = models.ForeignKey(
        Case, 
        on_delete=models.CASCADE, 
        related_name='participants',
        verbose_name="Дело"
    )
    trustor = models.ForeignKey(
        Trustor, 
        on_delete=models.CASCADE, 
        related_name='case_participants',
        verbose_name="Доверитель"
    )
    role = models.ForeignKey(
        CaseParticipantRole, 
        on_delete=models.CASCADE,
        verbose_name="Статус в деле"
    )
    main_participant = models.BooleanField(
        default=False,
        verbose_name="Основной доверитель",
        help_text="Является ли этот доверитель основным по делу"
    )
    
    # Дополнительная информация об участии
    representation_basis = models.TextField(
        blank=True,
        verbose_name="Основание представительства"
    )
    powers_details = models.TextField(
        blank=True,
        verbose_name="Сведения о полномочиях"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Участник дела"
        verbose_name_plural = "Участники дела"
        unique_together = ['case', 'trustor', 'role']
    
    def __str__(self):
        return f"{self.trustor} - {self.role.role_name} в деле {self.case}"
    
    def save(self, *args, **kwargs):
        """Если отмечаем как основного, снимаем отметку с других участников"""
        if self.main_participant:
            CaseParticipant.objects.filter(
                case=self.case, 
                main_participant=True
            ).exclude(pk=self.pk).update(main_participant=False)
        super().save(*args, **kwargs)