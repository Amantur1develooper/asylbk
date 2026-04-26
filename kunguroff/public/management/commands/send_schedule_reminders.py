"""
Команда: python manage.py send_schedule_reminders

Запускать каждую минуту через cron (для точных уведомлений):
    * * * * * /venv/bin/python /path/manage.py send_schedule_reminders >> /var/log/schedule_reminders.log 2>&1

Диагностика (не отправляет, только показывает):
    python manage.py send_schedule_reminders --debug
"""

import logging
import requests
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from schedule.models import ScheduleEntry, ScheduleNotificationLog

logger = logging.getLogger(__name__)

# Пороги уведомлений в минутах до события
THRESHOLDS = [120, 60, 30, 10]

# Допуск ±1 минута — крон запускается каждую минуту, поэтому 1 минута достаточно
WINDOW = 1


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
        ok = r.ok and r.json().get('ok')
        if not ok:
            logger.warning('TG %s: %s', r.status_code, r.text[:200])
        return ok
    except Exception as exc:
        logger.exception('TG error: %s', exc)
        return False


def _format_reminder(entry: ScheduleEntry, minutes_before: int) -> str:
    labels = {
        120: 'через 2 часа',
        60:  'через 1 час',
        30:  'через 30 минут',
        10:  'через 10 минут',
    }
    when = labels.get(minutes_before, f'через {minutes_before} мин')

    lines = [f'⏰ <b>Напоминание — {when}!</b>', '']

    if entry.client_name:      lines.append(f'👤 <b>Клиент:</b> {entry.client_name}')
    if entry.opposing_party:   lines.append(f'⚖️ <b>Вторая сторона:</b> {entry.opposing_party}')
    if entry.court:            lines.append(f'🏛 <b>Место / суд:</b> {entry.court}')
    if entry.case_description: lines.append(f'📁 <b>Дело:</b> {entry.case_description}')
    if entry.responsible_staff:lines.append(f'👨‍💼 <b>Ответственный:</b> {entry.responsible_staff}')
    if entry.notes:            lines.append(f'📝 <b>Примечание:</b> {entry.notes}')

    lines += ['', f'📅 <b>Дата:</b> {entry.date.strftime("%d.%m.%Y")}']
    if entry.time:
        lines.append(f'🕐 <b>Время:</b> {entry.time}')

    return '\n'.join(lines)


class Command(BaseCommand):
    help = 'Отправляет Telegram-уведомления о событиях за 2ч, 1ч, 30мин, 10мин (запускать каждую минуту)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--debug', action='store_true',
            help='Показать все события и статусы без отправки',
        )

    def handle(self, *args, **options):
        debug = options['debug']
        now   = timezone.localtime()

        if debug:
            self.stdout.write(f'[{now.strftime("%d.%m.%Y %H:%M:%S")}] РЕЖИМ ДИАГНОСТИКИ')
            self.stdout.write(self.style.WARNING('⚠ Сообщения не отправляются'))
            self._debug_all(now)
            return

        total_sent = 0

        from django.db.models import Q

        for minutes in THRESHOLDS:
            target_min = now + timedelta(minutes=minutes - WINDOW)
            target_max = now + timedelta(minutes=minutes + WINDOW)

            # Учитываем переход через полночь
            date_filter = Q(date=target_min.date())
            if target_max.date() != target_min.date():
                date_filter |= Q(date=target_max.date())

            entries = (
                ScheduleEntry.objects
                .filter(date_filter, notify_users__isnull=False)
                .prefetch_related('notify_users__telegram_account')
                .distinct()
            )

            for entry in entries:
                if not entry.time:
                    continue

                # Парсим время записи
                try:
                    t = datetime.strptime(str(entry.time).strip()[:5], '%H:%M').time()
                except ValueError:
                    continue

                entry_dt = timezone.make_aware(
                    datetime.combine(entry.date, t),
                    timezone.get_current_timezone(),
                )

                # Проверяем попадает ли событие в окно этого порога
                if not (target_min <= entry_dt <= target_max):
                    continue

                for user in entry.notify_users.all():
                    # Уже отправляли для этого порога?
                    if ScheduleNotificationLog.objects.filter(
                        entry=entry, user=user, minutes_before=minutes
                    ).exists():
                        continue

                    try:
                        tg = user.telegram_account
                    except Exception:
                        continue

                    if not tg.is_active or not tg.notifications_enabled:
                        continue

                    # Персональные настройки уведомлений
                    pref_map = {
                        120: tg.notify_3_hours,
                        60:  tg.notify_1_hour,
                        30:  tg.notify_30_minutes,
                        10:  tg.notify_10_minutes,
                    }
                    if not pref_map.get(minutes, True):
                        # Отмечаем как "намеренно пропущено" чтобы не проверять снова
                        ScheduleNotificationLog.objects.get_or_create(
                            entry=entry, user=user, minutes_before=minutes
                        )
                        continue

                    text = _format_reminder(entry, minutes)
                    ok   = _send_tg(tg.telegram_id, text)

                    ScheduleNotificationLog.objects.get_or_create(
                        entry=entry, user=user, minutes_before=minutes
                    )

                    if ok:
                        total_sent += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'[{now.strftime("%H:%M:%S")}] ✓ [{minutes}м] '
                            f'{user.get_full_name() or user.username} ← '
                            f'{entry.date} {entry.time} {entry.client_name}'
                        ))
                    else:
                        self.stdout.write(self.style.ERROR(
                            f'[{now.strftime("%H:%M:%S")}] ✗ [{minutes}м] '
                            f'{user.get_full_name() or user.username} — ошибка TG'
                        ))

        if total_sent:
            self.stdout.write(self.style.SUCCESS(
                f'[{now.strftime("%H:%M:%S")}] Отправлено: {total_sent}'
            ))

    def _debug_all(self, now):
        """Показывает все записи сегодня + завтра с деталями."""
        from datetime import date, timedelta as td
        today    = now.date()
        tomorrow = today + td(days=1)

        entries = (
            ScheduleEntry.objects
            .filter(date__in=[today, tomorrow])
            .prefetch_related('notify_users__telegram_account', 'notification_logs')
            .order_by('date', 'time')
        )

        if not entries.exists():
            self.stdout.write('Нет записей на сегодня/завтра.')
            return

        self.stdout.write(f'\nЗаписей на {today} и {tomorrow}: {entries.count()}')
        for entry in entries:
            users     = list(entry.notify_users.all())
            sent_logs = list(
                entry.notification_logs.values_list('minutes_before', flat=True)
            )

            minutes_until = '?'
            if entry.time:
                try:
                    t  = datetime.strptime(str(entry.time).strip()[:5], '%H:%M').time()
                    dt = timezone.make_aware(
                        datetime.combine(entry.date, t),
                        timezone.get_current_timezone(),
                    )
                    diff = int((dt - now).total_seconds() / 60)
                    minutes_until = f'{diff} мин'
                except ValueError:
                    pass

            self.stdout.write(
                f'\n  [{entry.date} {entry.time}] {entry.client_name or "—"} | '
                f'через {minutes_until}'
            )
            if not users:
                self.stdout.write(
                    self.style.WARNING('    ⚠ Не выбраны "Уведомить" пользователи!')
                )
            for user in users:
                has_tg = hasattr(user, 'telegram_account')
                tg_ok  = (
                    has_tg
                    and user.telegram_account.is_active
                    and user.telegram_account.notifications_enabled
                )
                already = [
                    f'{m}м' for m in sorted(sent_logs)
                    if ScheduleNotificationLog.objects.filter(
                        entry=entry, user=user, minutes_before=m
                    ).exists()
                ]
                self.stdout.write(
                    f'    👤 {user.get_full_name() or user.username} | '
                    f'TG: {"✓" if tg_ok else "✗ НЕТУ/ВЫКЛ"} | '
                    f'уже отправлено: {", ".join(already) or "—"}'
                )

        self.stdout.write(f'\nТекущее время: {now.strftime("%d.%m.%Y %H:%M:%S")}')
        self.stdout.write(f'Часовой пояс: {timezone.get_current_timezone_name()}')
        self.stdout.write('\nОкна поиска (WINDOW=±1 мин):')
        for minutes in THRESHOLDS:
            t_min = now + timedelta(minutes=minutes - WINDOW)
            t_max = now + timedelta(minutes=minutes + WINDOW)
            self.stdout.write(
                f'  Порог {minutes:3d}м → '
                f'события с {t_min.strftime("%H:%M:%S")} до {t_max.strftime("%H:%M:%S")}'
            )
