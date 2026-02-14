from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    
     path("ajax/cases/", views.ajax_cases, name="ajax_cases"),
    path("ajax/clients/", views.ajax_clients, name="ajax_clients"),
    path("ajax/employees/", views.ajax_employees, name="ajax_employees"),
    path("ajax/income-categories/", views.ajax_income_categories, name="ajax_income_categories"),
    path("ajax/expense-categories/", views.ajax_expense_categories, name="ajax_expense_categories"),

    path('', views.FinanceDashboardView.as_view(), name='dashboard'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/create/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('transactions/<int:pk>/update/', views.TransactionUpdateView.as_view(), name='transaction_update'),
    path('transactions/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),
  path('transactions/export/', views.TransactionExportView.as_view(), name='transaction_export'),
path('ajax/case-stages/', views.ajax_case_stages, name='ajax_case_stages'),

   # Финансовые операции
# 🔹 наша новая страница "Финансы дела"
    path(
        "cases/<int:case_id>/finance/",
        views.CaseFinanceUpdateView.as_view(),
        name="case_finance",
    ),
    # Финансы по делам (30/70 и распределение)
    path('cases/<int:case_id>/finance/', views.CaseFinanceUpdateView.as_view(), name='case_finance_update'),
    path('cases/export/', views.CaseFinanceExportView.as_view(), name='case_finance_export'),

  ]