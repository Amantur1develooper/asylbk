import sys

from django.apps import AppConfig


class Calendar1Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calendar1'

    def ready(self):
        import os

        argv = sys.argv
        is_manage = bool(argv) and argv[0].endswith('manage.py')
        if is_manage:
            # Не запускаем планировщик для служебных команд (migrate, shell, test и т.д.)
            if 'runserver' not in argv:
                return
            # С автоперезагрузкой runserver запускает дочерний процесс с RUN_MAIN=true —
            # планировщик стартует только там, чтобы не задваиваться.
            if os.environ.get('RUN_MAIN') != 'true':
                return

        from . import scheduler
        scheduler.start()
