from django.apps import AppConfig

class PublicConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "public"

    def ready(self):
        from . import signals  # noqa

        from core.scheduler_utils import should_start_scheduler
        if should_start_scheduler():
            from . import scheduler
            scheduler.start()
