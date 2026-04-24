from django.db import models
from django.conf import settings


class ScheduleEntry(models.Model):
    date = models.DateField(verbose_name="Дата")
    time = models.CharField(max_length=50, blank=True, verbose_name="Время")
    client_name = models.CharField(max_length=300, blank=True, verbose_name="ФИО клиента / партнёра")
    opposing_party = models.CharField(max_length=300, blank=True, verbose_name="ФИО второй стороны")
    court = models.CharField(max_length=300, blank=True, verbose_name="Судебная инстанция / орган")
    responsible_staff = models.CharField(max_length=200, blank=True, verbose_name="Ответственный сотрудник")
    case_description = models.CharField(max_length=200, blank=True, verbose_name="Краткое описание дела")
    notes = models.TextField(blank=True, verbose_name="Примечание")
    notify_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='schedule_entries',
        verbose_name="Уведомить в Telegram",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Запись графика"
        verbose_name_plural = "График дел"
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.date} {self.time} — {self.client_name}"


class ScheduleNotificationLog(models.Model):
    """Фиксирует отправленные напоминания, чтобы не дублировать."""
    THRESHOLDS = [120, 60, 30, 10]

    entry = models.ForeignKey(
        ScheduleEntry, on_delete=models.CASCADE,
        related_name='notification_logs',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
    )
    minutes_before = models.IntegerField(verbose_name="За сколько минут")
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['entry', 'user', 'minutes_before']
        verbose_name = "Лог уведомления"
