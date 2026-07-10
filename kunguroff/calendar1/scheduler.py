import atexit
import logging
import os
import tempfile

from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.core.management import call_command

logger = logging.getLogger(__name__)

_scheduler = None
_lock_file = None


def _run_send_telegram_notifications():
    try:
        call_command('send_telegram_notifications')
    except Exception:
        logger.exception('Ошибка при отправке Telegram-напоминаний из планировщика')


def _acquire_singleton_lock() -> bool:
    """Гарантирует, что фоновый планировщик запустится только в одном процессе.

    Если приложение работает под несколькими worker-процессами (например, gunicorn
    с --workers > 1), каждый из них выполняет AppConfig.ready() и без этой блокировки
    поднял бы собственный планировщик — в результате одно и то же напоминание
    отправлялось бы в Telegram по разу от каждого воркера. flock снимается ОС
    автоматически при завершении процесса, так что при перезапуске лок подхватит
    следующий доступный процесс.
    """
    global _lock_file
    try:
        import fcntl
    except ImportError:
        # На платформах без fcntl (например, Windows) просто разрешаем запуск —
        # локальная разработка там не подразумевает несколько worker-процессов.
        return True

    lock_path = os.path.join(tempfile.gettempdir(), 'kunguroff_reminder_scheduler.lock')
    f = open(lock_path, 'w')
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.close()
        return False

    _lock_file = f  # держим файл открытым, чтобы лок не снялся раньше времени
    return True


def start():
    """Запускает фоновый планировщик, который каждую минуту рассылает
    Telegram-напоминания о событиях календаря (см. calendar1.models.CalendarEvent).
    """
    global _scheduler
    if _scheduler is not None:
        return

    if not _acquire_singleton_lock():
        logger.info('Планировщик напоминаний уже запущен в другом процессе — пропускаем.')
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
