from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Subscriber(models.Model):
    CLIENT_TYPE = [
        ('individual', 'Физическое лицо'),
        ('legal',      'Юридическое лицо'),
    ]

    client_type    = models.CharField('Тип клиента', max_length=20, choices=CLIENT_TYPE, default='individual')
    full_name      = models.CharField('ФИО / Название организации', max_length=255)
    contact_person = models.CharField('Контактное лицо', max_length=200, blank=True,
                                      help_text='Для юр. лиц — ФИО представителя')
    inn            = models.CharField('ИНН', max_length=20, blank=True)
    phone          = models.CharField('Телефон', max_length=64, blank=True)
    email          = models.EmailField('Email', blank=True)
    address        = models.CharField('Адрес', max_length=300, blank=True)
    notes          = models.TextField('Примечания', blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Абонент'
        verbose_name_plural = 'Абоненты'
        ordering            = ['full_name']

    def __str__(self):
        return self.full_name

    @property
    def active_subscription(self):
        return self.subscriptions.filter(status='active').first()


class Subscription(models.Model):
    STATUS = [
        ('active', 'Активна'),
        ('paused', 'На паузе'),
        ('ended',  'Завершена'),
    ]

    subscriber      = models.ForeignKey(Subscriber, on_delete=models.CASCADE,
                                        related_name='subscriptions', verbose_name='Абонент')
    contract_number = models.CharField('Номер договора', max_length=100, blank=True)
    start_date      = models.DateField('Дата начала')
    end_date        = models.DateField('Дата окончания', null=True, blank=True)
    monthly_fee     = models.DecimalField('Ежемесячная сумма', max_digits=12, decimal_places=2, default=0)
    status          = models.CharField('Статус', max_length=20, choices=STATUS, default='active')
    responsible     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                        verbose_name='Ответственный юрист')
    notes           = models.TextField('Примечания', blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Абонентский договор'
        verbose_name_plural = 'Абонентские договоры'
        ordering            = ['-start_date']

    def __str__(self):
        return f'{self.subscriber} — {self.contract_number or "б/н"}'

    @property
    def total_paid(self):
        from django.db.models import Sum
        return self.payments.aggregate(s=Sum('amount'))['s'] or 0

    @property
    def is_overdue(self):
        if self.status != 'active':
            return False
        today = timezone.localdate()
        current_period = f'{today.year}-{today.month:02d}'
        return not self.payments.filter(period=current_period).exists()


class SubscriptionPayment(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE,
                                     related_name='payments', verbose_name='Договор')
    amount       = models.DecimalField('Сумма', max_digits=12, decimal_places=2)
    date         = models.DateField('Дата оплаты', default=timezone.localdate)
    period       = models.CharField('Период (YYYY-MM)', max_length=7,
                                    help_text='Напр: 2026-05 — за какой месяц')
    note         = models.TextField('Примечание', blank=True)
    created_by   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                     verbose_name='Кем записано')
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Платёж'
        verbose_name_plural = 'Платежи'
        ordering            = ['-date']

    def __str__(self):
        return f'{self.amount} сом ({self.period})'


class SubscriptionService(models.Model):
    SERVICE_TYPES = [
        ('consultation',    'Консультация'),
        ('document',        'Подготовка документа'),
        ('representation',  'Представительство'),
        ('negotiation',     'Переговоры'),
        ('claim',           'Претензионная работа'),
        ('other',           'Иное'),
    ]

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE,
                                     related_name='services', verbose_name='Договор')
    date         = models.DateField('Дата оказания', default=timezone.localdate)
    service_type = models.CharField('Вид услуги', max_length=30, choices=SERVICE_TYPES, default='consultation')
    description  = models.TextField('Описание / результат')
    lawyer       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     verbose_name='Исполнитель')
    hours        = models.DecimalField('Часы', max_digits=5, decimal_places=1, null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Оказанная услуга'
        verbose_name_plural = 'Оказанные услуги'
        ordering            = ['-date']

    def __str__(self):
        return f'{self.get_service_type_display()} — {self.date}'


class SubscriptionDocument(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE,
                                     related_name='documents', verbose_name='Договор')
    service      = models.ForeignKey(SubscriptionService, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='documents',
                                     verbose_name='Услуга (необязательно)')
    name         = models.CharField('Название документа', max_length=255)
    file         = models.FileField('Файл', upload_to='retainer/documents/')
    uploaded_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                     verbose_name='Загрузил')
    uploaded_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Документ'
        verbose_name_plural = 'Документы'
        ordering            = ['-uploaded_at']

    def __str__(self):
        return self.name

    @property
    def ext(self):
        import os
        return os.path.splitext(self.file.name)[1].lower()

    @property
    def icon(self):
        e = self.ext
        if e == '.pdf':
            return 'bi-file-earmark-pdf text-danger'
        if e in ('.doc', '.docx'):
            return 'bi-file-earmark-word text-primary'
        if e in ('.xls', '.xlsx'):
            return 'bi-file-earmark-excel text-success'
        if e in ('.jpg', '.jpeg', '.png', '.gif', '.webp'):
            return 'bi-file-earmark-image text-info'
        return 'bi-file-earmark text-secondary'
