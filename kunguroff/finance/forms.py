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

from django import forms
from django.utils import timezone
from decimal import Decimal

class CaseFinanceForm(forms.ModelForm):
    class Meta:
        model = CaseFinance
        fields = [
            "agreement_number",
            "agreement_date",
            "payment_due_date",
            "contract_amount",
            "paid_amount",
            "company_share_percent",
            "lawyers_share_percent",
        ]
        widgets = {
            "agreement_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "№ соглашения"}),

            # ✅ ВАЖНО: format='%Y-%m-%d'
            "agreement_date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"class": "form-control", "type": "date"}
            ),
            "payment_due_date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"class": "form-control", "type": "date"}
            ),

            "contract_amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "paid_amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "company_share_percent": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "lawyers_share_percent": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk and not self.is_bound:
            self.initial.setdefault("agreement_date", timezone.localdate())
            self.initial.setdefault("company_share_percent", Decimal("30.00"))
            self.initial.setdefault("lawyers_share_percent", Decimal("70.00"))

        # ✅ чтобы при редактировании корректно показывало дату в input[type=date]
        if self.instance and self.instance.pk:
            if self.instance.agreement_date:
                self.initial["agreement_date"] = self.instance.agreement_date.strftime("%Y-%m-%d")
            if getattr(self.instance, "payment_due_date", None):
                self.initial["payment_due_date"] = self.instance.payment_due_date.strftime("%Y-%m-%d")
                
                
# class CaseFinanceForm(forms.ModelForm):
#     class Meta:
#         model = CaseFinance
#         fields = [
#             "agreement_number",
#             "agreement_date",
#             "contract_amount",
#             'payment_due_date',
#             "paid_amount",
#             "company_share_percent",
#             "lawyers_share_percent",
#         ]
#         widgets = {
#                         'payment_due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             "agreement_number": forms.TextInput(
#                 attrs={"class": "form-control", "placeholder": "№ соглашения"}
#             ),
#             "agreement_date": forms.DateInput(
#                 attrs={"class": "form-control", "type": "date"}
#             ),
#             "contract_amount": forms.NumberInput(
#                 attrs={"class": "form-control", "step": "0.01", "min": "0"}
#             ),
#             "paid_amount": forms.NumberInput(
#                 attrs={"class": "form-control", "step": "0.01", "min": "0"}
#             ),
#             "company_share_percent": forms.NumberInput(
#                 attrs={"class": "form-control", "step": "0.01"}
#             ),
#             "lawyers_share_percent": forms.NumberInput(
#                 attrs={"class": "form-control", "step": "0.01"}
#             ),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         # Для нового объекта задаём дефолты (чтобы не было пусто)
#         if not self.instance.pk and not self.is_bound:
#             self.initial.setdefault("agreement_date", timezone.now().date())
#             self.initial.setdefault("company_share_percent", Decimal("30.00"))
#             self.initial.setdefault("lawyers_share_percent", Decimal("70.00"))



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
            'agreement_number',
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
            'agreement_number': forms.TextInput(attrs={  # ✅ НОВОЕ
                'class': 'form-control',
                'placeholder': 'Напр. №12/2026'
            }),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'case': forms.Select(attrs={'class': 'form-select js-s2-case'}),
            'client': forms.Select(attrs={'class': 'form-select js-s2-client'}),
            'employee': forms.Select(attrs={'class': 'form-select js-s2-employee'}),
            'category': forms.Select(attrs={'class': 'form-select js-s2-income-cat'}),
            'expense_category': forms.Select(attrs={'class': 'form-select js-s2-expense-cat'}),
            'stage': forms.Select(attrs={'class': 'form-select'}),
        }
    def clean(self):
        cleaned = super().clean()
        t = cleaned.get('transaction_type')
        agreement = (cleaned.get('agreement_number') or '').strip()
        case = cleaned.get('case')

        # (по желанию) требовать номер соглашения только для прихода по делу
        if t == 'income' and case and not agreement:
            self.add_error('agreement_number', 'Укажите номер соглашения для прихода по делу.')

        return cleaned
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
