from django.db import models
from django.contrib.auth import get_user_model
from cases.models import Case, CaseStage
from clients.models import Trustor 

User = get_user_model()

class IncomeCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    class Meta:
        verbose_name = "Категория дохода"
        verbose_name_plural = "Категории доходов"
    
    def __str__(self):
        return self.name

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    class Meta:
        verbose_name = "Категория расхода"
        verbose_name_plural = "Категории расходов"
    
    def __str__(self):
        return self.name

class FinancialTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Приход'),
        ('expense', 'Расход'),
    ]
    
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, verbose_name="Тип операции")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    date = models.DateField(verbose_name="Дата операции")
    description = models.TextField(verbose_name="Описание")
    
    # Связи с другими моделями
    category = models.ForeignKey(
        'finance.IncomeCategory', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Категория"
    )
    expense_category = models.ForeignKey(
        'finance.ExpenseCategory', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Категория расхода"
    )
    case = models.ForeignKey(
        Case, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Дело"
    )
    stage = models.ForeignKey(
        CaseStage, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Этап дела"
    )
    client = models.ForeignKey(
        Trustor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Клиент"
    )
    employee = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Сотрудник"
    )
    
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_transactions',
        verbose_name="Кем создана"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Финансовая операция"
        verbose_name_plural = "Финансовые операции"
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} - {self.date}"
    
    def save(self, *args, **kwargs):
        # Автоматическое определение категории на основе типа операции
        if self.transaction_type == 'income' and not self.category:
            self.category = IncomeCategory.objects.get_or_create(name='Прочие доходы')[0]
        elif self.transaction_type == 'expense' and not self.expense_category:
            self.expense_category = ExpenseCategory.objects.get_or_create(name='Прочие расходы')[0]
        
        super().save(*args, **kwargs)