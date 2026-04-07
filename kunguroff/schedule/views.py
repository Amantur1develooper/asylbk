from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.utils import timezone
from django.db.models import Q
from datetime import date, timedelta
import calendar

from .models import ScheduleEntry
from .forms import ScheduleEntryForm


def _month_context(year, month):
    """Хелпер: возвращает данные для навигации по месяцам."""
    today = date.today()
    prev_month = date(year, month, 1) - timedelta(days=1)
    next_month_day = (date(year, month, 1) + timedelta(days=32)).replace(day=1)
    month_names = [
        '', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ]
    return {
        'today': today,
        'year': year,
        'month': month,
        'month_name': month_names[month],
        'prev_year': prev_month.year,
        'prev_month': prev_month.month,
        'next_year': next_month_day.year,
        'next_month': next_month_day.month,
    }


class ScheduleListView(View):
    """Главная страница — список событий за выбранный месяц."""
    template_name = 'schedule/list.html'

    def get(self, request):
        today = date.today()
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
        search = request.GET.get('q', '').strip()

        entries = ScheduleEntry.objects.filter(date__year=year, date__month=month)
        if search:
            entries = entries.filter(
                Q(client_name__icontains=search) |
                Q(court__icontains=search) |
                Q(responsible_staff__icontains=search) |
                Q(case_description__icontains=search) |
                Q(notes__icontains=search)
            )

        # Группируем по дате для удобного отображения
        from collections import defaultdict
        grouped = defaultdict(list)
        for entry in entries:
            grouped[entry.date].append(entry)

        # Создаём список дней месяца
        _, days_in_month = calendar.monthrange(year, month)
        days = []
        for d in range(1, days_in_month + 1):
            day_date = date(year, month, d)
            days.append({
                'date': day_date,
                'weekday': day_date.strftime('%A'),
                'is_weekend': day_date.weekday() >= 5,
                'is_today': day_date == today,
                'entries': grouped.get(day_date, []),
            })

        ctx = _month_context(year, month)
        ctx.update({
            'days': days,
            'search': search,
            'total_entries': entries.count(),
        })
        return render(request, self.template_name, ctx)


class ScheduleCreateView(View):
    template_name = 'schedule/form.html'

    def get(self, request):
        initial = {}
        if request.GET.get('date'):
            initial['date'] = request.GET['date']
        form = ScheduleEntryForm(initial=initial)
        return render(request, self.template_name, {'form': form, 'action': 'Добавить событие'})

    def post(self, request):
        form = ScheduleEntryForm(request.POST)
        if form.is_valid():
            entry = form.save()
            return redirect(f'/grafik/?year={entry.date.year}&month={entry.date.month}#day-{entry.date}')
        return render(request, self.template_name, {'form': form, 'action': 'Добавить событие'})


class ScheduleUpdateView(View):
    template_name = 'schedule/form.html'

    def get(self, request, pk):
        entry = get_object_or_404(ScheduleEntry, pk=pk)
        form = ScheduleEntryForm(instance=entry)
        return render(request, self.template_name, {'form': form, 'entry': entry, 'action': 'Редактировать событие'})

    def post(self, request, pk):
        entry = get_object_or_404(ScheduleEntry, pk=pk)
        form = ScheduleEntryForm(request.POST, instance=entry)
        if form.is_valid():
            entry = form.save()
            return redirect(f'/grafik/?year={entry.date.year}&month={entry.date.month}#day-{entry.date}')
        return render(request, self.template_name, {'form': form, 'entry': entry, 'action': 'Редактировать событие'})


class ScheduleDeleteView(View):
    template_name = 'schedule/confirm_delete.html'

    def get(self, request, pk):
        entry = get_object_or_404(ScheduleEntry, pk=pk)
        return render(request, self.template_name, {'entry': entry})

    def post(self, request, pk):
        entry = get_object_or_404(ScheduleEntry, pk=pk)
        year, month = entry.date.year, entry.date.month
        entry.delete()
        return redirect(f'/grafik/?year={year}&month={month}')
