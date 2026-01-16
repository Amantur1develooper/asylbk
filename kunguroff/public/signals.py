# public/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
import threading

from public.models import ConsultationRequest
from public.telegram_notify import notify_consultation_request

@receiver(post_save, sender=ConsultationRequest)
def notify_on_create(sender, instance: ConsultationRequest, created, **kwargs):
    if not created:
        return

    req_id = instance.pk

    def _run():
        try:
            notify_consultation_request(req_id)
        except Exception as e:
            import logging
            logging.getLogger(__name__).exception("TG notify failed: %s", e)

    # запускаем только ПОСЛЕ коммита транзакции (надёжно)
    transaction.on_commit(lambda: threading.Thread(target=_run, daemon=True).start())
