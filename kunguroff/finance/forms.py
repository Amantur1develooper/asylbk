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
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
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