from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from cases.models import Case
from clients.models import Trustor

User = get_user_model()


class CalendarEvent(models.Model):
    EVENT_TYPES = [
        ('meeting', 'Встреча/Совещание'),
        ('deadline', 'Срок/Дедлайн'),
        ('reminder', 'Напоминание'),
        ('personal', 'Личное событие'),
        ('court_hearing', 'Судебное заседание'),
        ('client_meeting', 'Встреча с доверителем'),
        ('document_deadline', 'Срок подачи документов'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('critical', 'Критический'),
    ]
    
    # Основные поля
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, verbose_name="Тип события")
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    start_time = models.DateTimeField(verbose_name="Время начала")
    end_time = models.DateTimeField(verbose_name="Время окончания")
    location = models.CharField(max_length=200, blank=True, verbose_name="Место")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name="Приоритет")
    
    # Настройки уведомлений
    enable_notifications = models.BooleanField(default=True, verbose_name="Включить уведомления")
    notify_1_day = models.BooleanField(default=True, verbose_name="За 1 день")
    notify_12_hours = models.BooleanField(default=True, verbose_name="За 12 часов")
    notify_3_hours = models.BooleanField(default=True, verbose_name="За 3 часа")
    notify_1_hour = models.BooleanField(default=True, verbose_name="За 1 час")
    notify_30_minutes = models.BooleanField(default=True, verbose_name="За 30 минут")
    notify_10_minutes = models.BooleanField(default=False, verbose_name="За 10 минут")
    notify_1_minute = models.BooleanField(default=False, verbose_name="За 1 минуту")
    
    # Связи с другими моделями
    case = models.ForeignKey(
        Case, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Дело"
    )
    trustor = models.ForeignKey(
        Trustor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Доверитель"
    )
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='owned_events',
        verbose_name="Владелец"
    )
    participants = models.ManyToManyField(
        User, 
        related_name='events',
        blank=True,
        verbose_name="Участники"
    )
    
    # Системные поля
    is_recurring = models.BooleanField(default=False, verbose_name="Повторяющееся событие")
    recurrence_rule = models.CharField(max_length=100, blank=True, verbose_name="Правило повторения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Событие календаря"
        verbose_name_plural = "События календаря"
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%d.%m.%Y %H:%M')}"
    
    @property
    def is_all_day(self):
        return (self.end_time - self.start_time).days >= 1
    
    @property
    def is_past(self):
        from django.utils import timezone
        return self.end_time < timezone.now()
    
    @property
    def is_ongoing(self):
        from django.utils import timezone
        return self.start_time <= timezone.now() <= self.end_time
    
    @property
    def duration(self):
        return self.end_time - self.start_time
    
    def get_notification_times(self):
        """Возвращает список времен для уведомлений"""
        from datetime import timedelta
        notification_times = []
        
        if self.notify_1_day:
            notification_times.append(self.start_time - timedelta(days=1))
        if self.notify_12_hours:
            notification_times.append(self.start_time - timedelta(hours=12))
        if self.notify_3_hours:
            notification_times.append(self.start_time - timedelta(hours=3))
        if self.notify_1_hour:
            notification_times.append(self.start_time - timedelta(hours=1))
        if self.notify_30_minutes:
            notification_times.append(self.start_time - timedelta(minutes=30))
        if self.notify_10_minutes:
            notification_times.append(self.start_time - timedelta(minutes=10))
        if self.notify_1_minute:
            notification_times.append(self.start_time - timedelta(minutes=1))
        
        return sorted(notification_times)
    
    
class EventNotification(models.Model):
    """Модель для отслеживания отправленных уведомлений"""
    event = models.ForeignKey(
        CalendarEvent,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    notification_type = models.CharField(max_length=20, verbose_name="Тип уведомления")
    scheduled_time = models.DateTimeField(verbose_name="Время уведомления")
    sent = models.BooleanField(default=False, verbose_name="Отправлено")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Время отправки")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Уведомление о событии"
        verbose_name_plural = "Уведомления о событиях"
        unique_together = ['event', 'user', 'notification_type']
    
    def __str__(self):
        return f"{self.event} - {self.user} - {self.notification_type}"
