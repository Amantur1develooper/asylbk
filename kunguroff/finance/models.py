from django.db import models
from django.contrib.auth import get_user_model
from cases.models import Case, CaseStage
from clients.models import Trustor 
from django.core.validators import MinValueValidator
from django.db.models import Sum
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
User = get_user_model()
# finance/models.py
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model
from clients.models import Trustor 

User = get_user_model()

# --- твои старые модели IncomeCategory / ExpenseCategory / FinancialTransaction остаются как есть ---

class CaseFinance(models.Model):
    """
    Финансовая карточка дела (договор). Один к одному с делом.
    Здесь храним сумму договора 100%, оплачено, проценты 30/70.
    """
    case = models.OneToOneField(
        Case,
        on_delete=models.CASCADE,
        related_name='finance',
        verbose_name='Дело'
    )

    agreement_number = models.CharField(
        'Номер соглашения',
        max_length=100,
        blank=True
    )
    agreement_date = models.DateField(
        'Дата соглашения',
        null=True,
        blank=True
    )

    contract_amount = models.DecimalField(
        'Сумма договора (100%)',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    paid_amount = models.DecimalField(
        'Оплачено по договору',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0)]
    )

    # 30% / 70% — по умолчанию
    company_share_percent = models.DecimalField(
        'Процент компании',
        max_digits=5,
        decimal_places=2,
        default=Decimal('30.00'),
        validators=[MinValueValidator(0)]
    )
    lawyers_share_percent = models.DecimalField(
        'Процент юристов/адвокатов',
        max_digits=5,
        decimal_places=2,
        default=Decimal('70.00'),
        validators=[MinValueValidator(0)]
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Финансы дела'
        verbose_name_plural = 'Финансы дел'

    def __str__(self):
        return f'Финансы по делу #{self.case_id} — {self.case.title}'

    @property
    def company_share_amount(self):
        """
        30% от суммы договора (или другой %, если поменяли company_share_percent).
        """
        if not self.contract_amount:
            return Decimal('0.00')
        return (self.contract_amount * self.company_share_percent / Decimal('100')).quantize(Decimal('0.01'))

    @property
    def lawyers_pool_amount(self):
        """
        70% от суммы договора — общий «котёл» для юристов/адвокатов.
        """
        if not self.contract_amount:
            return Decimal('0.00')
        return (self.contract_amount * self.lawyers_share_percent / Decimal('100')).quantize(Decimal('0.01'))

    @property
    def paid_ratio(self):
        """
        Доля оплаченности договора (для частичных оплат).
        """
        if not self.contract_amount or self.contract_amount == 0:
            return Decimal('0')
        return (self.paid_amount / self.contract_amount).quantize(Decimal('0.0001'))

    def recalc_shares(self):
        """
        Пересчитать суммы по CaseFinanceShare (когда меняется сумма, оплачено или проценты).
        """
        pool = self.lawyers_pool_amount
        ratio = self.paid_ratio

        for share in self.shares.all():
            share.recalc_amounts(pool_amount=pool, paid_ratio=ratio, save=True)

class CaseFinanceShare(models.Model):
    """
    Доля конкретного сотрудника из 70% (lawyers_pool_amount).
    percent_of_pool — это % от этих 70 (суммарно должен быть 100).
    """
    case_finance = models.ForeignKey(
        CaseFinance,
        on_delete=models.CASCADE,
        related_name='shares',
        verbose_name='Финансы дела'
    )
    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Сотрудник (юрист/адвокат)'
    )

    percent_of_pool = models.DecimalField(
        'Доля от 70% (в %)',
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    # Расчётные поля (для отчётов / Excel)
    amount_full = models.DecimalField(
        'Сумма при полной оплате договора',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    amount_current = models.DecimalField(
        'Сумма с учётом текущей оплаты',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    is_manual = models.BooleanField(
        'Ручная корректировка',
        default=False,
        help_text='Если включено — доля выставлена вручную бухгалтером/директором.'
    )

    class Meta:
        verbose_name = 'Доля сотрудника в 70%'
        verbose_name_plural = 'Доли сотрудников в 70%'
        unique_together = ('case_finance', 'employee')

    def __str__(self):
        return f'{self.employee} — {self.percent_of_pool}% от 70% по делу #{self.case_finance.case_id}'

    def recalc_amounts(self, pool_amount=None, paid_ratio=None, save=True):
        """
        Пересчитать amount_full и amount_current.
        pool_amount — общий котёл 70% (Decimal)
        paid_ratio — доля оплаченности договора (0..1)
        """
        if pool_amount is None:
            pool_amount = self.case_finance.lawyers_pool_amount
        if paid_ratio is None:
            paid_ratio = self.case_finance.paid_ratio

        self.amount_full = (pool_amount * self.percent_of_pool / Decimal('100')).quantize(Decimal('0.01'))
        self.amount_current = (self.amount_full * paid_ratio).quantize(Decimal('0.01'))

        if save:
            self.save()
# class CaseFinanceShare(models.Model):
#     """
#     Доля конкретного сотрудника из 70% (lawyers_pool_amount).

#     percent_of_pool — это % от этих 70 (должна суммарно быть 100).
#     Например:
#       - два юриста по 50.00 => каждый получает 50% от 70% (т.е. 35% от договора).
#     """
#     case_finance = models.ForeignKey(
#         CaseFinance,
#         on_delete=models.CASCADE,
#         related_name='shares',
#         verbose_name='Финансы дела'
#     )
#     employee = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         verbose_name='Сотрудник (юрист/адвокат)'
#     )

#     percent_of_pool = models.DecimalField(
#         'Доля от 70% (в %)',
#         max_digits=5,
#         decimal_places=2,
#         validators=[MinValueValidator(0)]
#     )

#     # Расчётные поля (можно держать для отчётов / Excel)
#     amount_full = models.DecimalField(
#         'Сумма при полной оплате договора',
#         max_digits=12,
#         decimal_places=2,
#         default=0
#     )
#     amount_current = models.DecimalField(
#         'Сумма к выплате с учётом текущей оплаты',
#         max_digits=12,
#         decimal_places=2,
#         default=0
#     )

#     is_manual = models.BooleanField(
#         'Ручная корректировка',
#         default=False,
#         help_text='Если включено — доля выставлена вручную бухгалтером/директором.'
#     )

#     class Meta:
#         verbose_name = 'Доля сотрудника в 70%'
#         verbose_name_plural = 'Доли сотрудников в 70%'
#         unique_together = ('case_finance', 'employee')

#     def __str__(self):
#         return f'{self.employee} — {self.percent_of_pool}% от 70% по делу #{self.case_finance.case_id}'

#     def recalc_amounts(self, pool_amount=None, paid_ratio=None, save=True):
#         """
#         Пересчитать amount_full и amount_current.
#         pool_amount — общий котёл 70% (Decimal)
#         paid_ratio — доля оплаченности договора (0..1)
#         """
#         from decimal import Decimal

#         if pool_amount is None:
#             pool_amount = self.case_finance.lawyers_pool_amount
#         if paid_ratio is None:
#             paid_ratio = self.case_finance.paid_ratio

#         # сколько этому сотруднику при полной оплате договора
#         self.amount_full = (pool_amount * self.percent_of_pool / Decimal('100')).quantize(Decimal('0.01'))
#         # сколько ему сейчас, с учётом фактически оплаченной суммы
#         self.amount_current = (self.amount_full * paid_ratio).quantize(Decimal('0.01'))

#         if save:
#             self.save()

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
            self.category, _ = IncomeCategory.objects.get_or_create(name='Прочие доходы')
        elif self.transaction_type == 'expense' and not self.expense_category:
            self.expense_category, _ = ExpenseCategory.objects.get_or_create(name='Прочие расходы')

        super().save(*args, **kwargs)

        # После сохранения обновляем "сколько отдал от договора" (paid_amount) по делу — по всем приходам
        if self.case_id and self.transaction_type == 'income':
            total_income = FinancialTransaction.objects.filter(
                case_id=self.case_id,
                transaction_type='income'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            try:
                finance = self.case.finance
            except CaseFinance.DoesNotExist:
                finance = CaseFinance.objects.create(
                    case=self.case,
                    contract_amount=getattr(self.case, 'contract_amount', Decimal('0.00')) or Decimal('0.00'),
                    paid_amount=Decimal('0.00')
                )
            finance.paid_amount = total_income
            finance.recalc_shares()
            finance.save(update_fields=['paid_amount', 'updated_at'])

    def delete(self, *args, **kwargs):
        case_id = self.case_id
        transaction_type = self.transaction_type
        super().delete(*args, **kwargs)

        if case_id and transaction_type == 'income':
            total_income = FinancialTransaction.objects.filter(
                case_id=case_id,
                transaction_type='income'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            try:
                finance = CaseFinance.objects.get(case_id=case_id)
            except CaseFinance.DoesNotExist:
                return
            finance.paid_amount = total_income
            finance.recalc_shares()
            finance.save(update_fields=['paid_amount', 'updated_at'])
            
            
# class FinancialTransaction(models.Model):
#     TRANSACTION_TYPES = [
#         ('income', 'Приход'),
#         ('expense', 'Расход'),
#     ]
    
#     transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, verbose_name="Тип операции")
#     amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
#     date = models.DateField(verbose_name="Дата операции")
#     description = models.TextField(verbose_name="Описание")
    
#     # Связи с другими моделями
#     category = models.ForeignKey(
#         'finance.IncomeCategory', 
#         on_delete=models.SET_NULL, 
#         null=True, 
#         blank=True,
#         verbose_name="Категория"
#     )
#     expense_category = models.ForeignKey(
#         'finance.ExpenseCategory', 
#         on_delete=models.SET_NULL, 
#         null=True, 
#         blank=True,
#         verbose_name="Категория расхода"
#     )
#     case = models.ForeignKey(
#         Case, 
#         on_delete=models.SET_NULL, 
#         null=True, 
#         blank=True,
#         verbose_name="Дело"
#     )
#     stage = models.ForeignKey(
#         CaseStage, 
#         on_delete=models.SET_NULL, 
#         null=True, 
#         blank=True,
#         verbose_name="Этап дела"
#     )
#     client = models.ForeignKey(
#         Trustor, 
#         on_delete=models.SET_NULL, 
#         null=True, 
#         blank=True,
#         verbose_name="Клиент"
#     )
#     employee = models.ForeignKey(
#         User, 
#         on_delete=models.SET_NULL, 
#         null=True, 
#         blank=True,
#         verbose_name="Сотрудник"
#     )
    
#     created_by = models.ForeignKey(
#         User, 
#         on_delete=models.CASCADE, 
#         related_name='created_transactions',
#         verbose_name="Кем создана"
#     )
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
#     updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
#     class Meta:
#         verbose_name = "Финансовая операция"
#         verbose_name_plural = "Финансовые операции"
#         ordering = ['-date', '-created_at']
    
#     def __str__(self):
#         return f"{self.get_transaction_type_display()} - {self.amount} - {self.date}"
    
#     def save(self, *args, **kwargs):
#         # Автоматическое определение категории на основе типа операции
#         if self.transaction_type == 'income' and not self.category:
#             self.category = IncomeCategory.objects.get_or_create(name='Прочие доходы')[0]
#         elif self.transaction_type == 'expense' and not self.expense_category:
#             self.expense_category = ExpenseCategory.objects.get_or_create(name='Прочие расходы')[0]
        
#         super().save(*args, **kwargs)


from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Case)
def create_case_finance_on_case_create(sender, instance: Case, created, **kwargs):
    """
    При создании дела автоматически создаём финансовую карточку.
    Сумма договора берётся из поля дела (если заполнено).
    """
    if not created:
        return
    # Если уже есть финансовая карточка — ничего не делаем
    if hasattr(instance, 'finance'):
        return

    CaseFinance.objects.create(
        case=instance,
        contract_amount=getattr(instance, 'contract_amount', Decimal('0.00')) or Decimal('0.00'),
        paid_amount=Decimal('0.00'),
    )
    
    

@receiver(m2m_changed, sender=Case.responsible_lawyer.through)
def sync_case_finance_shares(sender, instance: Case, action, reverse, pk_set, **kwargs):
    """
    Синхронизируем доли юристов (70%) с полем responsible_lawyer дела.
    По умолчанию 70% делятся поровну между всеми ответственными юристами.
    """
    if action not in ('post_add', 'post_remove', 'post_clear'):
        return

    # Получаем или создаём финансовую карточку
    try:
        finance = instance.finance
    except CaseFinance.DoesNotExist:
        finance = CaseFinance.objects.create(
            case=instance,
            contract_amount=getattr(instance, 'contract_amount', Decimal('0.00')) or Decimal('0.00'),
            paid_amount=Decimal('0.00'),
        )

    # Удаляем только авто-сгенерированные доли (is_manual=False)
    finance.shares.filter(is_manual=False).delete()

    lawyers = instance.responsible_lawyer.all()
    count = lawyers.count()
    if count == 0:
        return

    base = (Decimal('100.00') / count).quantize(Decimal('0.01'))
    remainder = Decimal('100.00') - base * count

    for idx, lawyer in enumerate(lawyers):
        percent = base + remainder if idx == 0 else base
        CaseFinanceShare.objects.create(
            case_finance=finance,
            employee=lawyer,
            percent_of_pool=percent,
            is_manual=False,
        )

    finance.recalc_shares()