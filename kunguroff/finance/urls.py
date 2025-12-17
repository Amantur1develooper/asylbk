from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.FinanceDashboardView.as_view(), name='dashboard'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/create/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('transactions/<int:pk>/update/', views.TransactionUpdateView.as_view(), name='transaction_update'),
    path('transactions/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),
  path('transactions/export/', views.TransactionExportView.as_view(), name='transaction_export'),


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