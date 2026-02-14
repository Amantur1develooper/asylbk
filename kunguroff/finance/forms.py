# from datetime import timezone
# import datetime
from django.utils import timezone
from django import forms
from .models import FinancialTransaction, IncomeCategory, ExpenseCategory
from cases.models import Case, CaseStage
from clients.models import Trustor
from django.contrib.auth import get_user_model
# finance/forms.py
from decimal import Decimal
from django import forms
from django.utils import timezone
from django.forms import inlineformset_factory

from .models import CaseFinance, CaseFinanceShare
User = get_user_model()
# finance/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import CaseFinance, CaseFinanceShare


# class CaseFinanceForm(forms.ModelForm):
#     class Meta:
#         model = CaseFinance
#         fields = [
#             'agreement_number',
#             'agreement_date',
#             'contract_amount',
#             'paid_amount',
#             'company_share_percent',
#             'lawyers_share_percent',
#         ]


class CaseFinanceForm(forms.ModelForm):
    class Meta:
        model = CaseFinance
        fields = [
            "agreement_number",
            "agreement_date",
            "contract_amount",
            "paid_amount",
            "company_share_percent",
            "lawyers_share_percent",
        ]
        widgets = {
            "agreement_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "№ соглашения"}
            ),
            "agreement_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "contract_amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "paid_amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "company_share_percent": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "lawyers_share_percent": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Для нового объекта задаём дефолты (чтобы не было пусто)
        if not self.instance.pk and not self.is_bound:
            self.initial.setdefault("agreement_date", timezone.now().date())
            self.initial.setdefault("company_share_percent", Decimal("30.00"))
            self.initial.setdefault("lawyers_share_percent", Decimal("70.00"))

# class CaseFinanceForm(forms.ModelForm):
#     class Meta:
#         model = CaseFinance
#         fields = [
#             'agreement_number',
#             'agreement_date',
#             'contract_amount',
#             'paid_amount',
#             'company_share_percent',
#             'lawyers_share_percent',
#         ]
#         widgets = {
#             'agreement_number': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Номер соглашения',
#             }),
#             'agreement_date': forms.DateInput(attrs={
#                 'type': 'date',
#                 'class': 'form-control',
#             }),
#             'contract_amount': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'step': '0.01',
#                 'placeholder': 'Сумма договора 100%',
#             }),
#             'paid_amount': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'step': '0.01',
#             }),
#             'company_share_percent': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'step': '0.01',
#             }),
#             'lawyers_share_percent': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'step': '0.01',
#             }),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         instance = kwargs.get('instance')

#         # Авто-подстановка дефолтного номера/даты соглашения,
#         # если ещё ничего не введено
#         if instance and instance.pk:
#             case = instance.case
#             # Номер соглашения по умолчанию: CASE-{id}/{год}
#             if not instance.agreement_number:
#                 default_number = f"CASE-{case.id}/{timezone.now().year}"
#                 self.initial.setdefault('agreement_number', default_number)

#             # Дата соглашения по умолчанию: дата создания дела
#             if not instance.agreement_date and case.created_at:
#                 self.initial.setdefault('agreement_date', case.created_at.date())

# class CaseFinanceForm(forms.ModelForm):
#     class Meta:
#         model = CaseFinance
#         fields = [
#             'agreement_number',
#             'agreement_date',
#             'contract_amount',
#             'paid_amount',
#             'company_share_percent',
#             'lawyers_share_percent',
#         ]
#         widgets = {
#             'agreement_number': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Номер соглашения',}),
#             'agreement_date': forms.DateInput(attrs={
#                 'type': 'date',
#                 'class': 'form-control',
#             }),
#             # 'agreement_number': forms.TextInput(attrs={'class': 'form-control'}),
#             # 'agreement_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'contract_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
#             'paid_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
#             'company_share_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
#             'lawyers_share_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
#         }


# class CaseFinanceShareForm(forms.ModelForm):
#     class Meta:
#         model = CaseFinanceShare
#         fields = ['employee', 'percent_of_pool', 'is_manual']

class CaseFinanceShareForm(forms.ModelForm):
    class Meta:
        model = CaseFinanceShare
        fields = ['employee', 'percent_of_pool', 'is_manual']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'percent_of_pool': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_manual': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# CaseFinanceShareFormSet = inlineformset_factory(
#     CaseFinance,
#     CaseFinanceShare,
#     form=CaseFinanceShareForm,
#     extra=0,
#     can_delete=True
# )


from django import forms
from django.forms import inlineformset_factory

from .models import FinancialTransaction, CaseFinance, CaseFinanceShare

# finance/forms.py
from django import forms
from django.utils import timezone
from cases.models import Case
from .models import FinancialTransaction

# finance/forms.py
from django import forms
from django.utils import timezone

from cases.models import Case
from users.models import User
from clients.models import Trustor
from .models import FinancialTransaction, IncomeCategory, ExpenseCategory


class FinancialTransactionForm(forms.ModelForm):
    class Meta:
        model = FinancialTransaction
        fields = [
            'transaction_type',
            'amount',
            'date',
            'description',
            'category',
            'expense_category',
            'case',
            'stage',
            'client',
            'employee',
        ]
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),

            # select2 ajax (пустые селекты)
            'case': forms.Select(attrs={'class': 'form-select js-s2-case'}),
            'client': forms.Select(attrs={'class': 'form-select js-s2-client'}),
            'employee': forms.Select(attrs={'class': 'form-select js-s2-employee'}),
            'category': forms.Select(attrs={'class': 'form-select js-s2-income-cat'}),
            'expense_category': forms.Select(attrs={'class': 'form-select js-s2-expense-cat'}),

            'stage': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk and not (self.data.get('date') or self.initial.get('date')):
            self.initial['date'] = timezone.localdate()

        # ВАЖНО: чтобы не рендерить 1000+ options — держим queryset пустым,
        # но добавляем выбранное значение (из instance или POST), чтобы форма валидировалась/показывалась.
        self._limit_queryset('case', Case)
        self._limit_queryset('client', Trustor)
        self._limit_queryset('employee', User)
        self._limit_queryset('category', IncomeCategory)
        self._limit_queryset('expense_category', ExpenseCategory)

        # stage как у тебя: зависит от case
        self.fields['stage'].required = False
        self.fields['stage'].queryset = self.fields['stage'].queryset.none()
        case_id = self.data.get('case') or getattr(self.instance, 'case_id', None)
        if case_id:
            case = Case.objects.select_related('category').filter(pk=case_id).first()
            if case and case.category_id:
                self.fields['stage'].queryset = case.category.stages.all().order_by('order')

    def _limit_queryset(self, field_name, model_cls):
        field = self.fields.get(field_name)
        if not field:
            return
        selected_id = self.data.get(field_name) or getattr(self.instance, f"{field_name}_id", None)
        if selected_id:
            field.queryset = model_cls.objects.filter(pk=selected_id)
        else:
            field.queryset = model_cls.objects.none()

# class FinancialTransactionForm(forms.ModelForm):
#     class Meta:
#         model = FinancialTransaction
#         fields = [
#             'transaction_type',
#             'amount',
#             'date',
#             'description',
#             'category',
#             'expense_category',
#             'case',
#             'stage',
#             'client',
#             'employee',
#         ]
#         widgets = {
#             'transaction_type': forms.Select(attrs={'class': 'form-select'}),
#             'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
#             'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
#             'category': forms.Select(attrs={'class': 'form-select'}),
#             'expense_category': forms.Select(attrs={'class': 'form-select'}),
#             'case': forms.Select(attrs={'class': 'form-select'}),
#             'stage': forms.Select(attrs={'class': 'form-select'}),
#             'client': forms.Select(attrs={'class': 'form-select'}),
#             'employee': forms.Select(attrs={'class': 'form-select'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         # дата по умолчанию
#         if not self.instance.pk and not (self.data.get('date') or self.initial.get('date')):
#             self.initial['date'] = timezone.localdate()

#         # эти поля выбираем по типу операции (проверим в clean)
#         self.fields['category'].required = False
#         self.fields['expense_category'].required = False

#         # stage показываем/наполняем только если выбрали дело
#         self.fields['stage'].required = False
#         self.fields['stage'].queryset = self.fields['stage'].queryset.none()

#         case_id = self.data.get('case') or self.initial.get('case') or getattr(self.instance, 'case_id', None)
#         if case_id:
#             case = Case.objects.select_related('category').filter(pk=case_id).first()
#             if case and case.category_id:
#                 self.fields['stage'].queryset = case.category.stages.all().order_by('order')

#         # красивые пустые значения
#         for name in ('category', 'expense_category', 'case', 'stage', 'client', 'employee'):
#             f = self.fields.get(name)
#             if f and hasattr(f, 'empty_label'):
#                 f.empty_label = '— выберите —'

#     def clean(self):
#         cleaned = super().clean()
#         t = cleaned.get('transaction_type')

#         if t == 'income':
#             if not cleaned.get('category'):
#                 self.add_error('category', 'Выберите категорию дохода.')
#             cleaned['expense_category'] = None

#         elif t == 'expense':
#             if not cleaned.get('expense_category'):
#                 self.add_error('expense_category', 'Выберите категорию расхода.')
#             cleaned['category'] = None

#         return cleaned

# class FinancialTransactionForm(forms.ModelForm):
#     class Meta:
#         model = FinancialTransaction
#         fields = [
#             'transaction_type',
#             'amount',
#             'date',
#             'description',
#             'category',
#             'expense_category',
#             'case',
#             'stage',
#             'client',
#             'employee',
#         ]
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
#         }
CaseFinanceShareFormSet = inlineformset_factory(
    CaseFinance,
    CaseFinanceShare,
    fields=["employee", "percent_of_pool", "is_manual"],
    extra=0,
    can_delete=True,
    widgets={
        "employee": forms.Select(attrs={"class": "form-select"}),
        "percent_of_pool": forms.NumberInput(
            attrs={"class": "form-control", "step": "0.01", "min": "0"}
        ),
        "is_manual": forms.CheckboxInput(attrs={"class": "form-check-input"}),
    },
)
# class FinancialTransactionForm(forms.ModelForm):
#     class Meta:
#         model = FinancialTransaction
#         fields = [
#             'transaction_type', 'amount', 'date', 'description',
#             'category', 'expense_category', 'case', 'stage', 'client', 'employee'
#         ]
#         widgets = {
#             'transaction_type': forms.Select(attrs={
#                 'class': 'form-select',
#                 'id': 'id_transaction_type',
#                 'onchange': 'toggleCategoryFields()'
#             }),
#             'amount': forms.NumberInput(attrs={'class': 'form-control'}),
#             'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#             'category': forms.Select(attrs={'class': 'form-select', 'id': 'id_category'}),
#             'expense_category': forms.Select(attrs={'class': 'form-select', 'id': 'id_expense_category'}),
#             'case': forms.Select(attrs={'class': 'form-select'}),
#             'stage': forms.Select(attrs={'class': 'form-select'}),
#             'client': forms.Select(attrs={'class': 'form-select'}),
#             'employee': forms.Select(attrs={'class': 'form-select'}),
#         }
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         # Ограничиваем выбор категорий соответствующими типами
#         self.fields['category'].queryset = IncomeCategory.objects.all()
#         self.fields['expense_category'].queryset = ExpenseCategory.objects.all()
        
#         # Ограничиваем выбор дел и этапов
#         self.fields['case'].queryset = Case.objects.all()
#         self.fields['stage'].queryset = CaseStage.objects.all()
        
#         # Ограничиваем выбор клиентов
#         self.fields['client'].queryset = Trustor.objects.all()
        
#         # Ограничиваем выбор сотрудников
#         self.fields['employee'].queryset = User.objects.filter(
#             role__in=['lawyer', 'advocate', 'manager', 'accountant']
#         )
        
#         # Устанавливаем необязательными поля, которые зависят от типа операции
#         self.fields['category'].required = False
#         self.fields['expense_category'].required = False
    
#     def clean(self):
#         cleaned_data = super().clean()
#         transaction_type = cleaned_data.get('transaction_type')
#         category = cleaned_data.get('category')
#         expense_category = cleaned_data.get('expense_category')
        
#         # Проверяем, что для типа операции выбрана соответствующая категория
#         if transaction_type == 'income' and not category:
#             self.add_error('category', 'Для дохода необходимо выбрать категорию')
#         elif transaction_type == 'expense' and not expense_category:
#             self.add_error('expense_category', 'Для расхода необходимо выбрать категорию')
        
#         return cleaned_data