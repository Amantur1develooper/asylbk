from django.db import models
from django.contrib.auth import get_user_model
from cases.models import Case

User = get_user_model()

class LawyerRating(models.Model):
    lawyer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='ratings',
        verbose_name="Юрист/Адвокат"
    )
    period_start = models.DateField(verbose_name="Начало периода")
    period_end = models.DateField(verbose_name="Конец периода")
    
    # Показатели эффективности
    total_cases = models.PositiveIntegerField(default=0, verbose_name="Всего дел")
    completed_cases = models.PositiveIntegerField(default=0, verbose_name="Завершенные дела")
    average_progress = models.FloatField(default=0, verbose_name="Средний прогресс")
    success_rate = models.FloatField(default=0, verbose_name="Процент успешных дел")
    
    # Дополнительные метрики
    client_satisfaction = models.FloatField(default=0, verbose_name="Удовлетворенность клиентов")
    efficiency_score = models.FloatField(default=0, verbose_name="Оценка эффективности")
    revenue_generated = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Сгенерированный доход")
    
    total_score = models.FloatField(default=0, verbose_name="Общий балл")
    rank = models.PositiveIntegerField(default=0, verbose_name="Рейтинг")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Рейтинг юриста"
        verbose_name_plural = "Рейтинги юристов"
        ordering = ['period_start', 'rank']
        unique_together = ['lawyer', 'period_start', 'period_end']
    
    def __str__(self):
        return f"{self.lawyer} - {self.period_start} to {self.period_end} - Рейтинг: {self.rank}"
    
    def calculate_score(self):
        # Расчет общего балла на основе различных метрик
        # Можно настроить веса для различных показателей
        progress_weight = 0.3
        success_weight = 0.3
        satisfaction_weight = 0.2
        revenue_weight = 0.2
        
        self.total_score = (
            self.average_progress * progress_weight +
            self.success_rate * success_weight +
            self.client_satisfaction * satisfaction_weight +
            min(self.revenue_generated / 100000, 1.0) * revenue_weight  # Нормализация дохода
        ) * 100
        
        return self.total_score
    
    def save(self, *args, **kwargs):
        self.calculate_score()
        super().save(*args, **kwargs)

class CaseComplexity(models.Model):
    COMPLEXITY_LEVELS = [
        (1, 'Очень низкая'),
        (2, 'Низкая'),
        (3, 'Средняя'),
        (4, 'Высокая'),
        (5, 'Очень высокая'),
    ]
    
    case = models.OneToOneField(
        Case, 
        on_delete=models.CASCADE,
        verbose_name="Дело"
    )
    complexity_level = models.PositiveSmallIntegerField(
        choices=COMPLEXITY_LEVELS, 
        default=3,
        verbose_name="Уровень сложности"
    )
    complexity_factors = models.TextField(verbose_name="Факторы сложности")
    estimated_hours = models.PositiveIntegerField(default=0, verbose_name="Оценочное время (часы)")
    actual_hours = models.PositiveIntegerField(default=0, verbose_name="Фактическое время (часы)")
    
    rated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Оценено"
    )
    rated_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата оценки")
    
    class Meta:
        verbose_name = "Сложность дела"
        verbose_name_plural = "Сложности дел"
    
    def __str__(self):
        return f"{self.case} - Сложность: {self.get_complexity_level_display()}"
    
    @property
    def efficiency_ratio(self):
        if self.estimated_hours > 0:
            return self.estimated_hours / self.actual_hours if self.actual_hours > 0 else 0
        return 0