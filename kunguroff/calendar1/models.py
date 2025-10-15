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
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]
    
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES, verbose_name="Тип события")
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    start_time = models.DateTimeField(verbose_name="Время начала")
    end_time = models.DateTimeField(verbose_name="Время окончания")
    location = models.CharField(max_length=200, blank=True, verbose_name="Место")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name="Приоритет")
    
    # Связи с другими моделями
    case = models.ForeignKey(
        Case, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Дело"
    )
    client = models.ForeignKey(
        Trustor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Клиент"
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