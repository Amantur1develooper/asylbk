"""
Команда: python manage.py send_payment_notifications

Рассылает менеджерам в Telegram личные уведомления о финансах дел:
  - Просрочено (дата прошла, остаток > 0)
  - Срок сегодня
  - Срок через 1 день
  - Срок через 3 дня
  - Срок через 7 дней

Запускать через cron каждый день утром, например в 09:00.
"""

import requests
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from finance.models import CaseFinance
from users.models import User, TelegramAccount

logger = logging.getLogger(__name__)


def _token() -> str:
    return getattr(settings, 'TELEGRAM_BOT_TOKEN', '') or ''


def _send(chat_id: int, text: str) -> bool:
    token = _token()
    if not token:
        logger.error('TELEGRAM_BOT_TOKEN не задан')
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
        if r.ok and r.json().get('ok'):
            return True
        logger.warning('TG error %s: %s', r.status_code, r.text[:200])
        return False
    except Exception as e:
        logger.exception('TG exception: %s', e)
        return False


def _format_message(finance: CaseFinance, days: int) -> str:
    case = finance.case
    today = timezone.localdate()

    # Иконка и заголовок по статусу
    if days < 0:
        header = f'🚨 <b>ПРОСРОЧЕНА ОПЛАТА!</b> (просрочено на {abs(days)} дн.)'
    elif days == 0:
        header = '🔴 <b>Срок оплаты — СЕГОДНЯ!</b>'
    elif days == 1:
        header = '🟠 <b>Срок оплаты — ЗАВТРА</b>'
    elif days <= 3:
        header = f'🟡 <b>Срок оплаты через {days} дня</b>'
    else:
        header = f'🔵 <b>Срок оплаты через {days} дней</b>'

    # Клиент(ы) из участников дела
    participants = case.participants.select_related('trustor').filter(
        main_participant=True
    )
    if participants.exists():
        client_name = ', '.join(
            p.trustor.get_full_name() for p in participants
        )
    else:
        client_name = '—'

    due_str = finance.payment_due_date.strftime('%d.%m.%Y')
    remaining = finance.remaining_amount
    contract = finance.contract_amount
    paid = finance.paid_amount

    lines = [
        header,
        '',
        f'📁 <b>Дело:</b> {case.title}',
        f'👤 <b>Клиент:</b> {client_name}',
        f'📅 <b>Срок погашения:</b> {due_str}',
        '',
        f'💰 <b>Сумма договора:</b> {contract:,.0f} сом',
        f'✅ <b>Оплачено:</b> {paid:,.0f} сом',
        f'❗ <b>Остаток к оплате:</b> {remaining:,.0f} сом',
    ]

    # Ответственные юристы
    lawyers = case.responsible_lawyer.all()
    if lawyers.exists():
        names = ', '.join(
            u.get_full_name() or u.username for u in lawyers
        )
        lines.append(f'⚖️ <b>Юрист(ы):</b> {names}')

    return '\n'.join(lines)


class Command(BaseCommand):
    help = 'Отправка менеджерам уведомлений об оплатах по финансам дел'

    def handle(self, *args, **options):
        today = timezone.localdate()
        self.stdout.write(f'Запуск уведомлений об оплатах [{today}]...')

        # Пороговые дни для уведомлений
        notify_days = {0, 1, 3, 7}

        # Финансы с датой погашения и ненулевым остатком
        finances = (
            CaseFinance.objects
            .select_related('case')
            .prefetch_related('case__responsible_lawyer', 'case__participants__trustor')
            .filter(payment_due_date__isnull=False)
            .exclude(contract_amount=0)
        )

        # Отбираем нужные записи
        targets = []
        for finance in finances:
            if finance.remaining_amount <= 0:
                continue  # уже полностью оплачено — пропускаем
            days = (finance.payment_due_date - today).days
            if days < 0 or days in notify_days:
                targets.append((finance, days))

        if not targets:
            self.stdout.write(self.style.SUCCESS('Нет подходящих записей для уведомления.'))
            return

        # Находим менеджеров с активным Telegram
        managers_tg = (
            TelegramAccount.objects
            .select_related('user')
            .filter(
                is_active=True,
                notifications_enabled=True,
                user__is_active=True,
                user__role__in=['manager', 'director', 'deputy_director'],
            )
        )

        if not managers_tg.exists():
            self.stdout.write(self.style.WARNING('Нет менеджеров с привязанным Telegram.'))
            return

        sent_total = 0
        for finance, days in targets:
            text = _format_message(finance, days)

            for tg_acc in managers_tg:
                ok = _send(tg_acc.telegram_id, text)
                if ok:
                    sent_total += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ [{tg_acc.user.username}] Дело: {finance.case.title} '
                            f'(осталось {days} дн.)'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  ✗ [{tg_acc.user.username}] Ошибка отправки'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(f'\nГотово. Отправлено: {sent_total} уведомлений.')
        )
