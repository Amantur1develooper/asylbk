from django.views.generic import ListView, TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from core.permissions import ManagerRequiredMixin
from cases.models import Case
from users.models import User
from .models import LawyerRating, CaseComplexity

class RatingsDashboardView(ManagerRequiredMixin, TemplateView):
    template_name = 'ratings/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Период для анализа (последние 3 месяца)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=90)
        
        # Получаем всех юристов и адвокатов
        lawyers = User.objects.filter(role__in=['lawyer', 'advocate'])
        
        # Собираем статистику по каждому юристу
        lawyer_stats = []
        for lawyer in lawyers:
            cases = Case.objects.filter(
                responsible_lawyer=lawyer,
                created_at__date__range=[start_date, end_date]
            )
            
            total_cases = cases.count()
            completed_cases = cases.filter(status='completed').count()
            
            if total_cases > 0:
                average_progress = cases.aggregate(avg=Avg('progress'))['avg'] or 0
                success_rate = (completed_cases / total_cases) * 100
            else:
                average_progress = 0
                success_rate = 0
            
            # Получаем доход, сгенерированный юристом (из модуля финансов)
            revenue_generated = 0
            try:
                from finance.models import FinancialTransaction
                revenue_generated = FinancialTransaction.objects.filter(
                    case__responsible_lawyer=lawyer,
                    transaction_type='income',
                    date__range=[start_date, end_date]
                ).aggregate(total=Sum('amount'))['total'] or 0
            except:
                pass
            
            lawyer_stats.append({
                'lawyer': lawyer,
                'total_cases': total_cases,
                'completed_cases': completed_cases,
                'average_progress': average_progress,
                'success_rate': success_rate,
                'revenue_generated': revenue_generated,
                'score': (average_progress * 0.4 + success_rate * 0.4 + min(revenue_generated / 100000, 100) * 0.2)
            })
        
        # Сортируем по рейтингу
        lawyer_stats.sort(key=lambda x: x['score'], reverse=True)
        
        # Добавляем рейтинг
        for i, stats in enumerate(lawyer_stats):
            stats['rank'] = i + 1
        
        context.update({
            'lawyer_stats': lawyer_stats,
            'start_date': start_date,
            'end_date': end_date,
        })
        
        return context

class LawyerRankingView(ManagerRequiredMixin, ListView):
    template_name = 'ratings/lawyer_ranking.html'
    context_object_name = 'ratings'
    
    def get_queryset(self):
        # Получаем последние рейтинги
        latest_period = LawyerRating.objects.values('period_start').order_by('-period_start').first()
        
        if latest_period:
            return LawyerRating.objects.filter(
                period_start=latest_period['period_start']
            ).order_by('rank')
        
        return LawyerRating.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем доступные периоды для фильтрации
        periods = LawyerRating.objects.values('period_start', 'period_end').distinct().order_by('-period_start')
        
        context['periods'] = periods
        return context

class CaseAnalysisView(ManagerRequiredMixin, TemplateView):
    template_name = 'ratings/case_analysis.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Статистика по категориям дел
        case_stats = Case.objects.values('category__name').annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            avg_progress=Avg('progress'),
            avg_duration=Avg('updated_at' - 'created_at')
        ).order_by('-total')
        
        # Статистика по сложности дел
        complexity_stats = CaseComplexity.objects.values('complexity_level').annotate(
            count=Count('id'),
            avg_estimated=Avg('estimated_hours'),
            avg_actual=Avg('actual_hours'),
            avg_efficiency=Avg('actual_hours') / Avg('estimated_hours')
        ).order_by('complexity_level')
        
        context.update({
            'case_stats': case_stats,
            'complexity_stats': complexity_stats,
        })
        
        return context

class PerformanceReportView(ManagerRequiredMixin, TemplateView):
    template_name = 'ratings/performance_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Параметры отчета
        report_type = self.request.GET.get('type', 'monthly')
        year = int(self.request.GET.get('year', timezone.now().year))
        
        reports = []
        
        if report_type == 'monthly':
            # Генерируем monthly report
            for month in range(1, 13):
                start_date = datetime(year, month, 1).date()
                if month == 12:
                    end_date = datetime(year, month, 31).date()
                else:
                    end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
                
                # Статистика за месяц
                cases = Case.objects.filter(
                    created_at__date__range=[start_date, end_date]
                )
                
                total_cases = cases.count()
                completed_cases = cases.filter(status='completed').count()
                avg_progress = cases.aggregate(avg=Avg('progress'))['avg'] or 0
                
                reports.append({
                    'period': start_date.strftime('%B %Y'),
                    'total_cases': total_cases,
                    'completed_cases': completed_cases,
                    'completion_rate': (completed_cases / total_cases * 100) if total_cases > 0 else 0,
                    'avg_progress': avg_progress,
                })
        
        context.update({
            'reports': reports,
            'report_type': report_type,
            'year': year,
        })
        
        return context