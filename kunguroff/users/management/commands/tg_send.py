# users/management/commands/tg_send.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from users.models import TelegramAccount
import requests

class Command(BaseCommand):
    help = "Отправить тестовое сообщение одному chat_id"

    def add_arguments(self, p):
        p.add_argument("--chat_id", type=int)

    def handle(self, *a, **o):
        token = getattr(settings,"TELEGRAM_BOT_TOKEN","")
        if not token:
            raise CommandError("TELEGRAM_BOT_TOKEN пустой")
        chat_id = o["chat_id"] or getattr(TelegramAccount.objects.filter(is_active=True,notifications_enabled=True).first(),"telegram_id",None)
        if not chat_id:
            raise CommandError("Нет активных TelegramAccount")
        r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                          data={"chat_id": int(chat_id), "text":"Тест ✅"}, timeout=8)
        if not r.ok or not r.json().get("ok"):
            raise CommandError(f"TG error {r.status_code}: {r.text[:200]}")
        self.stdout.write(self.style.SUCCESS("OK"))
