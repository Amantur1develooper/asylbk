"""Общая проверка, уместно ли поднимать фоновый APScheduler в этом процессе.

Используется в AppConfig.ready() приложений, которым нужен периодический
фоновый планировщик (calendar1 — Telegram-напоминания, public — новости
законодательства с toktom.kg и т.д.), чтобы не плодить копии одной и той же
проверки.
"""
import os
import sys
import tempfile


def should_start_scheduler() -> bool:
    """
    True, если сейчас уместно запускать фоновый планировщик:
    - под gunicorn/uwsgi/asgi (запуск не через manage.py) — всегда True;
    - под `manage.py runserver` — только в дочернем процессе автоперезагрузки
      (RUN_MAIN=true), иначе планировщик задвоится;
    - под остальными management-командами (migrate, shell, test и т.д.) — False.
    """
    argv = sys.argv
    is_manage = bool(argv) and argv[0].endswith('manage.py')
    if not is_manage:
        return True
    if 'runserver' not in argv:
        return False
    return os.environ.get('RUN_MAIN') == 'true'


# Держим открытые файловые дескрипторы блокировок здесь, иначе они будут
# закрыты сборщиком мусора и лок снимется раньше времени.
_held_locks = {}


def acquire_singleton_lock(name: str) -> bool:
    """Гарантирует, что конкретный фоновый планировщик запустится только в одном
    процессе на машине — даже если приложение работает под несколькими
    worker-процессами (например, gunicorn с --workers > 1). Без этого каждый
    воркер поднял бы свою копию планировщика, и одно и то же действие
    (отправка напоминания, обновление новостей) выполнялось бы по разу от
    каждого воркера.

    `name` — уникальное имя ЭТОГО планировщика (разные планировщики не должны
    делить один лок-файл, иначе застолбит его только первый из них).

    flock снимается ОС автоматически при завершении процесса, так что при
    перезапуске лок подхватит следующий доступный процесс.
    """
    try:
        import fcntl
    except ImportError:
        # На платформах без fcntl (например, Windows) просто разрешаем запуск —
        # локальная разработка там не подразумевает несколько worker-процессов.
        return True

    lock_path = os.path.join(tempfile.gettempdir(), f'kunguroff_{name}.lock')
    f = open(lock_path, 'w')
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.close()
        return False

    _held_locks[name] = f
    return True
