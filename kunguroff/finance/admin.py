from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import IncomeCategory, ExpenseCategory, FinancialTransaction

@admin.register(IncomeCategory)
class IncomeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(FinancialTransaction)
class FinancialTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'amount', 'date', 'category', 'expense_category', 'case', 'created_by')
    list_filter = ('transaction_type', 'date', 'category', 'expense_category')
    search_fields = ('description', 'case__title', 'client__last_name')
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('transaction_type', 'amount', 'date', 'description')
        }),
        ('Категории', {
            'fields': ('category', 'expense_category')
        }),
        ('Связи', {
            'fields': ('case', 'stage', 'client', 'employee')
        }),
        ('Системная информация', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)