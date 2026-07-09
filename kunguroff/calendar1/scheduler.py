import atexit
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.core.management import call_command

logger = logging.getLogger(__name__)

_scheduler = None


def _run_send_telegram_notifications():
    try:
        call_command('send_telegram_notifications')
    except Exception:
        logger.exception('Ошибка при отправке Telegram-напоминаний из планировщика')


def start():
    """Запускает фоновый планировщик, который каждую минуту рассылает
    Telegram-напоминания о событиях календаря (см. calendar1.models.CalendarEvent).
    """
    global _scheduler
    if _scheduler is not None:
        return

    _scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    _scheduler.add_job(
        _run_send_telegram_notifications,
        trigger='interval',
        minutes=1,
        id='send_telegram_notifications',
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    _scheduler.start()
    atexit.register(lambda: _scheduler.shutdown(wait=False))
