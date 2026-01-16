import requests
from django.conf import settings
from django.utils.html import escape
from django.utils import timezone

def _chat_ids_from_settings():
    ids_ = getattr(settings, "TELEGRAM_CHAT_IDS", [])
    if isinstance(ids_, (str, int)):
        return [str(ids_)]
    return [str(x) for x in ids_ if str(x).strip()]

def send_telegram_message(text: str) -> bool:
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    if not token:
        return False

    chat_ids = _chat_ids_from_settings()
    if not chat_ids:
        return False

    ok_any = False
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    for chat_id in chat_ids:
        try:
            r = requests.post(
                url,
                data={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
                timeout=8,
            )
            if r.ok and r.json().get("ok"):
                ok_any = True
        except Exception:
            # чтобы заявка не ломалась из-за телеги
            pass

    return ok_any

def format_consultation(req) -> str:
    dt = timezone.localtime(req.created_at).strftime("%d.%m.%Y %H:%M")
    name = escape(req.name or "")
    phone = escape(req.phone or "")
    email = escape(req.email or "—")
    topic = escape(req.topic or "—")
    msg = escape(req.message or "—")

    return (
        "🆕 <b>Новая заявка на консультацию</b>\n\n"
        f"👤 <b>Имя:</b> {name}\n"
        f"📞 <b>Телефон:</b> {phone}\n"
        f"📧 <b>Email:</b> {email}\n"
        f"🏷 <b>Тема:</b> {topic}\n"
        f"💬 <b>Сообщение:</b> {msg}\n\n"
        f"⏱ <b>Время:</b> {dt}\n"
        f"🟦 <b>Статус:</b> {escape(req.status)}"
    )
