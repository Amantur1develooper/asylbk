import requests
import logging
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TelegramService:
    """Сервис для работы с Telegram API"""
    
    def __init__(self):
        self.token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        self.base_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_message(self, chat_id, text, parse_mode='HTML'):
        """Отправка сообщения в Telegram"""
        if not self.token:
            logger.error("TELEGRAM_BOT_TOKEN не настроен")
            return False
        
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"Сообщение отправлено пользователю {chat_id}")
                return True
            else:
                logger.error(f"Ошибка отправки сообщения: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения: {str(e)}")
            return False
    
    def send_event_notification(self, event, user, notification_type):
        """Отправка уведомления о событии"""
        if not hasattr(user, 'telegram_account') or not user.telegram_account.is_active:
            return False
        
        telegram_account = user.telegram_account
        
        # Проверяем настройки уведомлений пользователя
        if not self._should_send_notification(telegram_account, notification_type):
            return False
        
        # Формируем текст сообщения
        message = self._format_notification_message(event, notification_type)
        
        # Отправляем сообщение
        return self.send_message(telegram_account.telegram_id, message)
    
    def _should_send_notification(self, telegram_account, notification_type):
        """Проверяет, нужно ли отправлять уведомление данного типа"""
        if not telegram_account.notifications_enabled:
            return False
        
        notification_mapping = {
            '1_day': telegram_account.notify_1_day,
            '12_hours': telegram_account.notify_12_hours,
            '3_hours': telegram_account.notify_3_hours,
            '2_hours': telegram_account.notify_2_hours,
            '1_hour': telegram_account.notify_1_hour,
            '30_minutes': telegram_account.notify_30_minutes,
            '10_minutes': telegram_account.notify_10_minutes,
            '1_minute': telegram_account.notify_1_minute,
        }
        
        return notification_mapping.get(notification_type, False)
    
    def _format_notification_message(self, event, notification_type):
        """Форматирует текст уведомления"""
        time_until = self._get_time_until_text(notification_type)
        
        message = f"🔔 <b>Напоминание</b>\n\n"
        message += f"<b>Событие:</b> {event.title}\n"
        message += f"<b>Время:</b> {event.start_time.strftime('%d.%m.%Y в %H:%M')}\n"
        
        if event.location:
            message += f"<b>Место:</b> {event.location}\n"
        
        if event.event_type:
            message += f"<b>Тип:</b> {event.get_event_type_display()}\n"
        
        if event.case:
            message += f"<b>Дело:</b> {event.case.title}\n"
        
        message += f"\nСобытие начнется {time_until}"
        
        return message
    
    def _get_time_until_text(self, notification_type):
        """Возвращает текст о времени до события"""
        time_mapping = {
            '1_day': 'через 1 день',
            '12_hours': 'через 12 часов',
            '3_hours': 'через 3 часа',
            '2_hours': 'через 2 часа',
            '1_hour': 'через 1 час',
            '30_minutes': 'через 30 минут',
            '10_minutes': 'через 10 минут',
            '1_minute': 'через 1 минуту',
        }
        return time_mapping.get(notification_type, 'скоро')