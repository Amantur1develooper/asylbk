from django import forms
from .models import FinancialTransaction, IncomeCategory, ExpenseCategory
from cases.models import Case, CaseStage
from clients.models import Trustor
from django.contrib.auth import get_user_model

User = get_user_model()

class FinancialTransactionForm(forms.ModelForm):
    class Meta:
        model = FinancialTransaction
        fields = [
            'transaction_type', 'amount', 'date', 'description',
            'category', 'expense_category', 'case', 'stage', 'client', 'employee'
        ]
        widgets = {
            'transaction_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_transaction_type',
                'onchange': 'toggleCategoryFields()'
            }),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select', 'id': 'id_category'}),
            'expense_category': forms.Select(attrs={'class': 'form-select', 'id': 'id_expense_category'}),
            'case': forms.Select(attrs={'class': 'form-select'}),
            'stage': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Ограничиваем выбор категорий соответствующими типами
        self.fields['category'].queryset = IncomeCategory.objects.all()
        self.fields['expense_category'].queryset = ExpenseCategory.objects.all()
        
        # Ограничиваем выбор дел и этапов
        self.fields['case'].queryset = Case.objects.all()
        self.fields['stage'].queryset = CaseStage.objects.all()
        
        # Ограничиваем выбор клиентов
        self.fields['client'].queryset = Trustor.objects.all()
        
        # Ограничиваем выбор сотрудников
        self.fields['employee'].queryset = User.objects.filter(
            role__in=['lawyer', 'advocate', 'manager', 'accountant']
        )
        
        # Устанавливаем необязательными поля, которые зависят от типа операции
        self.fields['category'].required = False
        self.fields['expense_category'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        category = cleaned_data.get('category')
        expense_category = cleaned_data.get('expense_category')
        
        # Проверяем, что для типа операции выбрана соответствующая категория
        if transaction_type == 'income' and not category:
            self.add_error('category', 'Для дохода необходимо выбрать категорию')
        elif transaction_type == 'expense' and not expense_category:
            self.add_error('expense_category', 'Для расхода необходимо выбрать категорию')
        
        return cleaned_data