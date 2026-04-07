from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from calendar1.models import CalendarEvent, EventNotification
from telegram.services import TelegramService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Отправка Telegram уведомлений о предстоящих событиях'
    
    def handle(self, *args, **options):
        self.stdout.write('Запуск отправки Telegram уведомлений...')
        
        telegram_service = TelegramService()
        now = timezone.now()
        
        # Находим события, для которых нужно отправить уведомления
        events = CalendarEvent.objects.filter(
            enable_notifications=True,
            start_time__gt=now,  # Только будущие события
            start_time__lte=now + timedelta(days=1)  # Только в ближайшие 24 часа
        )
        
        # Маппинг типа уведомления -> поле модели и задержка
        notification_types = [
            ('1_day',       'notify_1_day',       timedelta(days=1)),
            ('12_hours',    'notify_12_hours',     timedelta(hours=12)),
            ('3_hours',     'notify_3_hours',      timedelta(hours=3)),
            ('1_hour',      'notify_1_hour',       timedelta(hours=1)),
            ('30_minutes',  'notify_30_minutes',   timedelta(minutes=30)),
            ('10_minutes',  'notify_10_minutes',   timedelta(minutes=10)),
            ('1_minute',    'notify_1_minute',     timedelta(minutes=1)),
        ]

        sent_count = 0

        for event in events:
            for notification_type, notify_field, time_delta in notification_types:

                # Проверяем, включён ли данный тип уведомления для этого события
                if not getattr(event, notify_field, False):
                    continue

                notification_time = event.start_time - time_delta

                # Проверяем, нужно ли отправить уведомление сейчас (окно ±1 мин)
                if not (notification_time - timedelta(minutes=1) <= now <= notification_time + timedelta(minutes=1)):
                    continue

                # Получаем всех пользователей для уведомления (владелец + участники)
                users_to_notify = list(event.participants.all())
                if event.owner not in users_to_notify:
                    users_to_notify.append(event.owner)

                for user in users_to_notify:
                    # get_or_create только по уникальным полям (event, user, notification_type)
                    # scheduled_time передаём в defaults, чтобы не был ключом поиска
                    notification, created = EventNotification.objects.get_or_create(
                        event=event,
                        user=user,
                        notification_type=notification_type,
                        defaults={
                            'scheduled_time': notification_time,
                            'sent': False,
                        }
                    )

                    # Если уведомление уже отправлено — пропускаем (защита от двойной отправки)
                    if notification.sent:
                        continue

                    # Отправляем уведомление
                    success = telegram_service.send_event_notification(
                        event, user, notification_type
                    )

                    if success:
                        notification.sent = True
                        notification.sent_at = now
                        notification.save(update_fields=['sent', 'sent_at'])
                        sent_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Отправлено уведомление пользователю {user.username} "
                                f"о событии '{event.title}'"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Ошибка отправки уведомления пользователю {user.username}"
                            )
                        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Уведомления отправлены. Всего отправлено: {sent_count}'
            )
        )