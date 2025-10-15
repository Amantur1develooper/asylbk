from django.shortcuts import render

# Create your views here.
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from core.permissions import AccountantRequiredMixin
from finance.forms import FinancialTransactionForm
from .models import FinancialTransaction, IncomeCategory, ExpenseCategory
from django.core.paginator import Paginator

class FinanceDashboardView(AccountantRequiredMixin, TemplateView):
    template_name = 'finance/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Обработка параметров фильтрации
        period = self.request.GET.get('period', 'month')
        transaction_type = self.request.GET.get('transaction_type', '')
        category_id = self.request.GET.get('category', '')
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        
        # Определение периода
        today = timezone.now().date()
        
        if period == 'week':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif period == 'month':
            start_date = today.replace(day=1)
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        elif period == 'quarter':
            current_quarter = (today.month - 1) // 3 + 1
            start_date = datetime(today.year, 3 * current_quarter - 2, 1).date()
            end_date = (datetime(today.year, 3 * current_quarter + 1, 1) - timedelta(days=1)).date()
        elif period == 'year':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        elif period == 'custom' and date_from and date_to:
            start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        else:
            # По умолчанию - текущий месяц
            start_date = today.replace(day=1)
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        # Базовый запрос с фильтрацией по дате
        transactions = FinancialTransaction.objects.filter(date__range=[start_date, end_date])
        
        # Применяем дополнительные фильтры
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)
        
        if category_id:
            # Фильтруем по категории дохода или расхода
            transactions = transactions.filter(
                Q(category_id=category_id) | Q(expense_category_id=category_id)
            )
        
        # Вычисляем общие показатели
        total_income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Вычисляем рост по сравнению с предыдущим месяцем
        prev_month_start = (start_date - timedelta(days=1)).replace(day=1)
        prev_month_end = start_date - timedelta(days=1)
        
        prev_month_transactions = FinancialTransaction.objects.filter(
            date__range=[prev_month_start, prev_month_end]
        )
        prev_month_income = prev_month_transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        
        if prev_month_income > 0:
            growth_rate = round(((total_income - prev_month_income) / prev_month_income) * 100, 1)
        else:
            growth_rate = 0
        
        # Получаем данные для графиков
        income_by_category = transactions.filter(transaction_type='income').values(
            'category__name'
        ).annotate(total=Sum('amount')).order_by('-total')
        
        expense_by_category = transactions.filter(transaction_type='expense').values(
            'expense_category__name'
        ).annotate(total=Sum('amount')).order_by('-total')
        
        # Получаем все категории для фильтра
        income_categories = IncomeCategory.objects.all()
        expense_categories = ExpenseCategory.objects.all()
        categories = list(income_categories) + list(expense_categories)
        # Пагинация
        paginator = Paginator(transactions.order_by('-date'), 20)  # 20 элементов на страницу
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
       
        context.update({
            'page_obj': page_obj,
            'is_paginated': paginator.num_pages > 1,
            'total_income': total_income,
            'total_expense': total_expense,
            'profit': total_income - total_expense,
            'transactions': transactions.order_by('-date'),
            'income_by_category': income_by_category,
            'expense_by_category': expense_by_category,
            'categories': categories,
            'growth_rate': growth_rate,
            'start_date': start_date,
            'end_date': end_date,
            'period': period,
            'transaction_type': transaction_type,
            'category_id': category_id,
            'date_from': date_from,
            'date_to': date_to,
        })
        
        return context
    
    
# class FinanceDashboardView(AccountantRequiredMixin, TemplateView):
#     template_name = 'finance/dashboard.html'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
        
#         # Фильтры по дате
#         date_filter = self.request.GET.get('period', 'month')
#         today = timezone.now().date()
        
#         if date_filter == 'week':
#             start_date = today - timedelta(days=today.weekday())
#             end_date = start_date + timedelta(days=6)
#         elif date_filter == 'month':
#             start_date = today.replace(day=1)
#             end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
#         elif date_filter == 'quarter':
#             current_quarter = (today.month - 1) // 3 + 1
#             start_date = datetime(today.year, 3 * current_quarter - 2, 1).date()
#             end_date = (datetime(today.year, 3 * current_quarter + 1, 1) - timedelta(days=1)).date()
#         else:  # year
#             start_date = today.replace(month=1, day=1)
#             end_date = today.replace(month=12, day=31)
        
#         # Получаем данные по доходам и расходам
#         transactions = FinancialTransaction.objects.filter(date__range=[start_date, end_date])
        
#         total_income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
#         total_expense = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
#         profit = total_income - total_expense
        
#         # Доходы по категориям
#         income_by_category = transactions.filter(transaction_type='income').values(
#             'category__name'
#         ).annotate(total=Sum('amount')).order_by('-total')
        
#         # Расходы по категориям
#         expense_by_category = transactions.filter(transaction_type='expense').values(
#             'expense_category__name'
#         ).annotate(total=Sum('amount')).order_by('-total')
        
#         context.update({
#             'total_income': total_income,
#             'total_expense': total_expense,
#             'profit': profit,
#             'transactions':transactions,
#             'income_by_category': income_by_category,
#             'expense_by_category': expense_by_category,
#             'start_date': start_date,
#             'end_date': end_date,
#             'period': date_filter,
#         })
        
#         return context
import pandas as pd
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
import pandas as pd
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q, Sum
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from datetime import datetime

class TransactionExportView(AccountantRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Применяем те же фильтры, что и в TransactionListView
        queryset = FinancialTransaction.objects.all()
        
        # Сохраняем параметры фильтрации для отчета
        filter_params = {}
        
        # Фильтрация по типу операции
        transaction_type = self.request.GET.get('type')
        if transaction_type in ['income', 'expense']:
            queryset = queryset.filter(transaction_type=transaction_type)
            filter_params['Тип операции'] = 'Приход' if transaction_type == 'income' else 'Расход'
        
        # Фильтрация по дате
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
            filter_params['Дата с'] = date_from
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
            filter_params['Дата по'] = date_to
        
        # Фильтрация по категории
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(Q(category_id=category) | Q(expense_category_id=category))
            try:
                # Пытаемся найти категорию
                cat = IncomeCategory.objects.filter(id=category).first()
                if not cat:
                    cat = ExpenseCategory.objects.filter(id=category).first()
                if cat:
                    filter_params['Категория'] = cat.name
            except:
                pass
        
        # Фильтрация по делу
        case = self.request.GET.get('case')
        if case:
            queryset = queryset.filter(case_id=case)
            filter_params['Дело'] = f"ID: {case}"
        
        # Вычисляем итоги
        total_income = queryset.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = queryset.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        net_income = total_income - total_expense
        
        # Создаем HTTP-ответ с Excel-файлом
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = f"financial_report_{timezone.now().strftime('%Y-%m-%d_%H-%M')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Создаем книгу Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Финансовый отчет"
        
        # Стили
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        border = Border(left=Side(style='thin'), 
                       right=Side(style='thin'), 
                       top=Side(style='thin'), 
                       bottom=Side(style='thin'))
        total_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
        income_font = Font(color="00B050", bold=True)  # Зеленый для доходов
        expense_font = Font(color="FF0000", bold=True)  # Красный для расходов
        
        # Заголовок отчета
        ws.merge_cells('A1:J1')
        title_cell = ws['A1']
        title_cell.value = "Отчет по финансовым операциям"
        title_cell.font = Font(size=16, bold=True)
        title_cell.alignment = Alignment(horizontal='center')
        
        # Параметры фильтрации
        row_num = 3
        if filter_params:
            ws.merge_cells(f'A{row_num}:J{row_num}')
            filter_cell = ws[f'A{row_num}']
            filter_cell.value = "Параметры фильтрации:"
            filter_cell.font = Font(bold=True)
            row_num += 1
            
            for key, value in filter_params.items():
                ws.merge_cells(f'A{row_num}:B{row_num}')
                param_cell = ws[f'A{row_num}']
                param_cell.value = f"{key}: {value}"
                param_cell.font = Font(bold=True)
                row_num += 1
        
        # Пропускаем строку
        row_num += 1
        
        # Заголовки таблицы
        headers = ['Дата', 'Тип операции', 'Сумма', 'Описание', 'Категория', 'Дело', 'Клиент', 'Сотрудник', 'Создано', 'Кем создано']
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.border = border
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Данные
        row_num += 1
        start_data_row = row_num
        
        for transaction in queryset.order_by('-date', '-created_at'):
            ws.cell(row=row_num, column=1).value = transaction.date.strftime('%d.%m.%Y')
            ws.cell(row=row_num, column=2).value = transaction.get_transaction_type_display()
            
            amount_cell = ws.cell(row=row_num, column=3)
            amount_cell.value = float(transaction.amount)
            if transaction.transaction_type == 'income':
                amount_cell.font = income_font
            else:
                amount_cell.font = expense_font
            
            ws.cell(row=row_num, column=4).value = transaction.description
            ws.cell(row=row_num, column=5).value = transaction.category.name if transaction.transaction_type == 'income' and transaction.category else transaction.expense_category.name if transaction.expense_category else '-'
            ws.cell(row=row_num, column=6).value = f"#{transaction.case.id} - {transaction.case.title}" if transaction.case else '-'
            ws.cell(row=row_num, column=7).value = str(transaction.client) if transaction.client else '-'
            ws.cell(row=row_num, column=8).value = str(transaction.employee) if transaction.employee else '-'
            ws.cell(row=row_num, column=9).value = transaction.created_at.strftime('%d.%m.%Y %H:%M')
            ws.cell(row=row_num, column=10).value = str(transaction.created_by)
            
            # Применяем границы ко всем ячейкам строки
            for col_num in range(1, 11):
                ws.cell(row=row_num, column=col_num).border = border
            
            row_num += 1
        
        # Итоги
        end_data_row = row_num - 1
        
        # Пропускаем строку
        row_num += 1
        
        # Итог по доходам
        ws.merge_cells(f'A{row_num}:B{row_num}')
        total_income_label = ws.cell(row=row_num, column=1)
        total_income_label.value = "Общий доход:"
        total_income_label.font = Font(bold=True)
        total_income_label.fill = total_fill
        total_income_label.border = border
        
        total_income_value = ws.cell(row=row_num, column=3)
        total_income_value.value = float(total_income)
        total_income_value.font = income_font
        total_income_value.fill = total_fill
        total_income_value.border = border
        
        # Формула для суммирования доходов
        income_col_letter = get_column_letter(3)
        total_income_value.value = f"=SUMIF(B{start_data_row}:B{end_data_row}, \"Приход\", {income_col_letter}{start_data_row}:{income_col_letter}{end_data_row})"
        
        # Итог по расходам
        row_num += 1
        ws.merge_cells(f'A{row_num}:B{row_num}')
        total_expense_label = ws.cell(row=row_num, column=1)
        total_expense_label.value = "Общий расход:"
        total_expense_label.font = Font(bold=True)
        total_expense_label.fill = total_fill
        total_expense_label.border = border
        
        total_expense_value = ws.cell(row=row_num, column=3)
        total_expense_value.font = expense_font
        total_expense_value.fill = total_fill
        total_expense_value.border = border
        
        # Формула для суммирования расходов
        total_expense_value.value = f"=SUMIF(B{start_data_row}:B{end_data_row}, \"Расход\", {income_col_letter}{start_data_row}:{income_col_letter}{end_data_row})"
        
        # Чистая прибыль
        row_num += 1
        ws.merge_cells(f'A{row_num}:B{row_num}')
        net_income_label = ws.cell(row=row_num, column=1)
        net_income_label.value = "Чистая прибыль:"
        net_income_label.font = Font(bold=True)
        net_income_label.fill = total_fill
        net_income_label.border = border
        
        net_income_value = ws.cell(row=row_num, column=3)
        net_income_value.font = Font(bold=True)
        net_income_value.fill = total_fill
        net_income_value.border = border
        
        # Формула для расчета чистой прибыли
        prev_income_row = row_num - 2
        prev_expense_row = row_num - 1
        net_income_value.value = f"={income_col_letter}{prev_income_row}-{income_col_letter}{prev_expense_row}"
        
        # Количество операций
        row_num += 2
        ws.merge_cells(f'A{row_num}:B{row_num}')
        count_label = ws.cell(row=row_num, column=1)
        count_label.value = "Количество операций:"
        count_label.font = Font(bold=True)
        
        count_value = ws.cell(row=row_num, column=3)
        count_value.value = queryset.count()
        count_value.font = Font(bold=True)
        
        # Настраиваем ширину столбцов
        column_widths = {
            'A': 12,  # Дата
            'B': 12,  # Тип операции
            'C': 12,  # Сумма
            'D': 40,  # Описание
            'E': 20,  # Категория
            'F': 25,  # Дело
            'G': 20,  # Клиент
            'H': 20,  # Сотрудник
            'I': 16,  # Создано
            'J': 20,  # Кем создано
        }
        
        for col_letter, width in column_widths.items():
            ws.column_dimensions[col_letter].width = width
        
        # Форматируем столбец с суммой как денежный
        for row in range(start_data_row, end_data_row + 1):
            cell = ws.cell(row=row, column=3)
            cell.number_format = '#,##0.00" сом"'
        
        # Форматируем итоговые значения
        for row in [start_data_row + queryset.count() + 2, start_data_row + queryset.count() + 3, start_data_row + queryset.count() + 4]:
            cell = ws.cell(row=row, column=3)
            cell.number_format = '#,##0.00" сом"'
        
        # Сохраняем книгу
        wb.save(response)
        
        return response
    
class TransactionListView(AccountantRequiredMixin, ListView):
    model = FinancialTransaction
    template_name = 'finance/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по типу операции
        transaction_type = self.request.GET.get('type')
        if transaction_type in ['income', 'expense']:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        # Фильтрация по дате
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        # Фильтрация по категории
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(Q(category_id=category) | Q(expense_category_id=category))
        
        # Фильтрация по делу
        case = self.request.GET.get('case')
        if case:
            queryset = queryset.filter(case_id=case)
        
        return queryset.order_by('-date', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем отфильтрованный queryset
        queryset = self.get_queryset()
        
        # Вычисляем общую статистику
        total_income = queryset.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = queryset.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        net_income = total_income - total_expense
        
        context.update({
            'income_categories': IncomeCategory.objects.all(),
            'expense_categories': ExpenseCategory.objects.all(),
            'total_income': total_income,
            'total_expense': total_expense,
            'net_income': net_income,
        })
        
        return context   
# class TransactionListView(AccountantRequiredMixin, ListView):
#     model = FinancialTransaction
#     template_name = 'finance/transaction_list.html'
#     context_object_name = 'transactions'
#     paginate_by = 20
    
#     def get_queryset(self):
#         queryset = super().get_queryset()
        
#         # Фильтрация по типу операции
#         transaction_type = self.request.GET.get('type')
#         if transaction_type in ['income', 'expense']:
#             queryset = queryset.filter(transaction_type=transaction_type)
        
#         # Фильтрация по дате
#         date_from = self.request.GET.get('date_from')
#         date_to = self.request.GET.get('date_to')
#         if date_from:
#             queryset = queryset.filter(date__gte=date_from)
#         if date_to:
#             queryset = queryset.filter(date__lte=date_to)
        
#         # Фильтрация по категории
#         category = self.request.GET.get('category')
#         if category:
#             queryset = queryset.filter(Q(category_id=category) | Q(expense_category_id=category))
        
#         # Фильтрация по делу
#         case = self.request.GET.get('case')
#         if case:
#             queryset = queryset.filter(case_id=case)
        
#         return queryset.order_by('-date', '-created_at')
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['income_categories'] = IncomeCategory.objects.all()
#         context['expense_categories'] = ExpenseCategory.objects.all()
#         return context

class TransactionCreateView(AccountantRequiredMixin, CreateView):
    model = FinancialTransaction
    form_class = FinancialTransactionForm
    template_name = 'finance/transaction_form.html'
    success_url = reverse_lazy('finance:transaction_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class TransactionUpdateView(AccountantRequiredMixin, UpdateView):
    model = FinancialTransaction
    template_name = 'finance/transaction_form.html'
    fields = [
        'transaction_type', 'amount', 'date', 'description',
        'category', 'expense_category', 'case', 'stage', 'client', 'employee'
    ]
    
    def get_success_url(self):
        return reverse_lazy('finance:transaction_list')

class TransactionDeleteView(AccountantRequiredMixin, DeleteView):
    model = FinancialTransaction
    template_name = 'finance/transaction_confirm_delete.html'
    success_url = reverse_lazy('finance:transaction_list')