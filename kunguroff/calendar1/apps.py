from django.apps import AppConfig


class Calendar1Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calendar1'

    def ready(self):
        from core.scheduler_utils import should_start_scheduler
        if not should_start_scheduler():
            return

        from . import scheduler
        scheduler.start()
