from django.db import models


class ScheduleEntry(models.Model):
    date = models.DateField(verbose_name="Дата")
    time = models.CharField(max_length=50, blank=True, verbose_name="Время")
    client_name = models.CharField(max_length=300, blank=True, verbose_name="ФИО клиента / партнёра")
    opposing_party = models.CharField(max_length=300, blank=True, verbose_name="ФИО второй стороны")
    court = models.CharField(max_length=300, blank=True, verbose_name="Судебная инстанция / орган")
    responsible_staff = models.CharField(max_length=200, blank=True, verbose_name="Ответственный сотрудник")
    case_description = models.CharField(max_length=200, blank=True, verbose_name="Краткое описание дела")
    notes = models.TextField(blank=True, verbose_name="Примечание")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Запись графика"
        verbose_name_plural = "График дел"
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.date} {self.time} — {self.client_name}"
