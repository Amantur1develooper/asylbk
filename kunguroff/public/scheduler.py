import atexit
import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.core.management import call_command

from core.scheduler_utils import acquire_singleton_lock

logger = logging.getLogger(__name__)

_scheduler = None


def _run_fetch_toktom_news():
    try:
        call_command('fetch_toktom_news')
    except Exception:
        logger.exception('Ошибка при автоматическом обновлении новостей законодательства (toktom.kg)')


def start():
    """Запускает фоновый планировщик, который раз в сутки подтягивает свежие
    новости законодательства (постановления/токтомы) с online.toktom.kg —
    см. public.management.commands.fetch_toktom_news — и публикует их в разделе
    «Новости» на сайте.
    """
    global _scheduler
    if _scheduler is not None:
        return

    if not acquire_singleton_lock('news_scheduler'):
        logger.info('Планировщик новостей уже запущен в другом процессе — пропускаем.')
        return

    _scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    _scheduler.add_job(
        _run_fetch_toktom_news,
        trigger='cron',
        hour=9,
        minute=0,
        id='fetch_toktom_news',
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        next_run_time=datetime.now(),  # подтягиваем новости сразу при старте сервера,
                                        # дальше — каждый день в 09:00
    )
    _scheduler.start()
    atexit.register(lambda: _scheduler.shutdown(wait=False))
