# public/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from public.models import ConsultationRequest
from public.telegram_notify import notify_consultation_request
import threading

@receiver(post_save, sender=ConsultationRequest)
def notify_on_create(sender, instance, created, **kwargs):
    if created:
        # чтобы не тормозить ответ пользователю — в отдельном потоке
        threading.Thread(
            target=notify_consultation_request, 
            args=(instance.id,), 
            daemon=True
        ).start()
