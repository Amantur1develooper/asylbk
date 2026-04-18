from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Employee(models.Model):
    """Карточка сотрудника — отдел кадров."""

    POSITION_CHOICES = [
        ('lawyer', 'Адвокат'),
        ('advocate', 'Юрист'),
        ('manager', 'Менеджер'),
        ('accountant', 'Бухгалтер'),
        ('hr', 'HR-специалист'),
        ('other', 'Другое'),
    ]

    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    position = models.CharField(
        max_length=50, choices=POSITION_CHOICES, blank=True,
        verbose_name='Должность'
    )
    phone = models.CharField(max_length=30, blank=True, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    hire_date = models.DateField(null=True, blank=True, verbose_name='Дата приёма')
    notes = models.TextField(blank=True, verbose_name='Примечания')

    # Документы — все необязательные
    passport_copy = models.FileField(
        upload_to='hr/passports/', blank=True, null=True,
        verbose_name='Копия паспорта'
    )
    resume = models.FileField(
        upload_to='hr/resumes/', blank=True, null=True,
        verbose_name='Резюме'
    )
    personal_file = models.FileField(
        upload_to='hr/personal_files/', blank=True, null=True,
        verbose_name='Личное дело'
    )
    work_book = models.FileField(
        upload_to='hr/work_books/', blank=True, null=True,
        verbose_name='Трудовая книжка'
    )
    no_criminal_record = models.FileField(
        upload_to='hr/criminal_records/', blank=True, null=True,
        verbose_name='Справка о несудимости'
    )
    diploma = models.FileField(
        upload_to='hr/diplomas/', blank=True, null=True,
        verbose_name='Диплом'
    )
    autobiography = models.FileField(
        upload_to='hr/autobiographies/', blank=True, null=True,
        verbose_name='Автобиография'
    )
    job_application = models.FileField(
        upload_to='hr/job_applications/', blank=True, null=True,
        verbose_name='Заявление на работу'
    )
    employment_contract = models.FileField(
        upload_to='hr/contracts/', blank=True, null=True,
        verbose_name='Трудовой договор'
    )
    mj_notification = models.FileField(
        upload_to='hr/mj_notifications/', blank=True, null=True,
        verbose_name='Уведомление МЮ КР'
    )
    bar_notification = models.FileField(
        upload_to='hr/bar_notifications/', blank=True, null=True,
        verbose_name='Уведомление Адвокатуры КР'
    )

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='hr_created', verbose_name='Добавил'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Сотрудник (кадры)'
        verbose_name_plural = 'Сотрудники (кадры)'
        ordering = ['full_name']

    def __str__(self):
        return self.full_name

    def get_documents(self):
        """Возвращает список (label, file) для всех документов."""
        fields = [
            ('Копия паспорта', self.passport_copy),
            ('Резюме', self.resume),
            ('Личное дело', self.personal_file),
            ('Трудовая книжка', self.work_book),
            ('Справка о несудимости', self.no_criminal_record),
            ('Диплом', self.diploma),
            ('Автобиография', self.autobiography),
            ('Заявление на работу', self.job_application),
            ('Трудовой договор', self.employment_contract),
            ('Уведомление МЮ КР', self.mj_notification),
            ('Уведомление Адвокатуры КР', self.bar_notification),
        ]
        return fields

    @property
    def docs_count(self):
        return sum(1 for _, f in self.get_documents() if f)

    @property
    def docs_total(self):
        return len(self.get_documents())
