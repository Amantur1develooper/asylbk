"""
Команда: python manage.py send_schedule_reminders

Запускать каждые 10 минут через cron:
    */10 * * * * /venv/bin/python /path/manage.py send_schedule_reminders >> /var/log/schedule_reminders.log 2>&1

Отправляет Telegram-уведомления о запланированных событиях:
  - за 2 часа (120 мин)
  - за 1 час  (60 мин)
  - за 30 минут
  - за 10 минут
"""

import logging
import requests
from datetime import datetime, timedelta, time as dtime

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from schedule.models import ScheduleEntry, ScheduleNotificationLog

logger = logging.getLogger(__name__)

# Пороги уведомлений в минутах
THRESHOLDS = [120, 60, 30, 10]

# Допуск — окно ±5 минут вокруг каждого порога
WINDOW = 5


def _token():
    return getattr(settings, 'TELEGRAM_BOT_TOKEN', '') or ''


def _send_tg(chat_id: int, text: str) -> bool:
    token = _token()
    if not token:
        return False
    try:
        r = requests.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            data={
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True,
            },
            timeout=8,
        )
        return r.ok and r.json().get('ok')
    except Exception as exc:
        logger.exception('TG error: %s', exc)
        return False


def _format_reminder(entry: ScheduleEntry, minutes_before: int) -> str:
    if minutes_before == 120:
        when = 'через 2 часа'
    elif minutes_before == 60:
        when = 'через 1 час'
    elif minutes_before == 30:
        when = 'через 30 минут'
    else:
        when = 'через 10 минут'

    lines = [
        f'⏰ <b>Напоминание — {when}!</b>',
        '',
    ]

    if entry.client_name:
        lines.append(f'👤 <b>Клиент:</b> {entry.client_name}')
    if entry.opposing_party:
        lines.append(f'⚖️ <b>Вторая сторона:</b> {entry.opposing_party}')
    if entry.court:
        lines.append(f'🏛 <b>Место / суд:</b> {entry.court}')
    if entry.case_description:
        lines.append(f'📁 <b>Дело:</b> {entry.case_description}')
    if entry.responsible_staff:
        lines.append(f'👨‍💼 <b>Ответственный:</b> {entry.responsible_staff}')
    if entry.notes:
        lines.append(f'📝 <b>Примечание:</b> {entry.notes}')

    lines.append('')
    lines.append(f'📅 <b>Дата:</b> {entry.date.strftime("%d.%m.%Y")}')
    if entry.time:
        lines.append(f'🕐 <b>Время:</b> {entry.time}')

    return '\n'.join(lines)


class Command(BaseCommand):
    help = 'Отправляет Telegram-уведомления о событиях за 2ч, 1ч, 30мин, 10мин'

    def handle(self, *args, **options):
        now = timezone.localtime()
        self.stdout.write(f'[{now.strftime("%d.%m.%Y %H:%M")}] Проверка напоминаний...')

        total_sent = 0

        for minutes in THRESHOLDS:
            # Целевое время события = now + minutes (с допуском ±WINDOW)
            target_min = now + timedelta(minutes=minutes - WINDOW)
            target_max = now + timedelta(minutes=minutes + WINDOW)

            # Ищем записи, у которых есть notify_users и время попадает в окно
            entries = (
                ScheduleEntry.objects
                .filter(
                    date=target_min.date(),
                    notify_users__isnull=False,
                )
                .prefetch_related('notify_users__telegram_account', 'notification_logs')
                .distinct()
            )

            # Также проверяем записи на следующий день, если окно перешло полночь
            if target_max.date() != target_min.date():
                from django.db.models import Q
                entries = ScheduleEntry.objects.filter(
                    Q(date=target_min.date()) | Q(date=target_max.date()),
                    notify_users__isnull=False,
                ).prefetch_related('notify_users__telegram_account', 'notification_logs').distinct()

            for entry in entries:
                # Парсим время записи
                if not entry.time:
                    continue

                try:
                    t = datetime.strptime(str(entry.time).strip()[:5], '%H:%M').time()
                except ValueError:
                    continue

                entry_dt = timezone.make_aware(
                    datetime.combine(entry.date, t)
                )

                # Проверяем попадание в окно
                if not (target_min <= entry_dt <= target_max):
                    continue

                # Для каждого пользователя
                for user in entry.notify_users.all():
                    # Уже отправляли?
                    already = ScheduleNotificationLog.objects.filter(
                        entry=entry, user=user, minutes_before=minutes
                    ).exists()
                    if already:
                        continue

                    # Получаем Telegram-аккаунт
                    try:
                        tg = user.telegram_account
                    except Exception:
                        continue

                    if not tg.is_active or not tg.notifications_enabled:
                        continue

                    # Проверяем персональные настройки пользователя
                    pref_map = {
                        120: tg.notify_3_hours,   # используем 3h как "2h" (ближайшее)
                        60:  tg.notify_1_hour,
                        30:  tg.notify_30_minutes,
                        10:  tg.notify_10_minutes,
                    }
                    if not pref_map.get(minutes, True):
                        # Пользователь отключил этот тип уведомлений
                        ScheduleNotificationLog.objects.get_or_create(
                            entry=entry, user=user, minutes_before=minutes
                        )
                        continue

                    text = _format_reminder(entry, minutes)
                    ok = _send_tg(tg.telegram_id, text)

                    if ok:
                        ScheduleNotificationLog.objects.get_or_create(
                            entry=entry, user=user, minutes_before=minutes
                        )
                        total_sent += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ [{minutes}м] {user.get_full_name() or user.username} ← '
                                f'{entry.date} {entry.time} {entry.client_name}'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f'  ✗ [{minutes}м] {user.get_full_name() or user.username} — ошибка TG'
                            )
                        )

        self.stdout.write(self.style.SUCCESS(f'Готово. Отправлено: {total_sent}'))
