import requests
from django.conf import settings
from django.utils import timezone
from django.utils.html import escape

from public.models import ConsultationRequest
from users.models import TelegramAccount  # если у вас другое приложение — поменяйте импорт


def _telegram_token() -> str:
    return getattr(settings, "TELEGRAM_BOT_TOKEN", "7647322168:AAHC-VSVSS7qxrDCfJD2kaMHbeC9z2-l9R4") or ""


def _notify_roles():
    roles = getattr(settings, "TELEGRAM_NOTIFY_ROLES", None)
    return roles if roles else ["admin", "manager", "director", "advocate", "lawyer"]


def _format_consultation(req: ConsultationRequest) -> str:
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
        f"🟦 <b>Статус:</b> {escape(req.status)}\n"
        f"🆔 <b>ID:</b> {req.id}"
    )


def _send_to_chat(chat_id: int, text: str) -> tuple[bool, str]:
    token = _telegram_token()
    if not token:
        return False, "NO_TOKEN"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
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
        if not r.ok:
            return False, f"HTTP_{r.status_code}"

        data = r.json()
        if not data.get("ok"):
            return False, data.get("description", "TG_ERROR")

        return True, "OK"
    except Exception:
        return False, "EXCEPTION"


def notify_consultation_request(req_id: int) -> int:
    """
    Рассылает заявку всем активным TelegramAccount у пользователей нужных ролей.
    Возвращает кол-во успешных отправок.
    """
    try:
        req = ConsultationRequest.objects.get(id=req_id)
    except ConsultationRequest.DoesNotExist:
        return 0

    text = _format_consultation(req)

    qs = (
        TelegramAccount.objects
        .select_related("user")
        .filter(
            is_active=True,
            notifications_enabled=True,
            user__is_active=True,
            user__role__in=_notify_roles(),
        )
    )

    ok_count = 0
    for acc in qs:
        ok, err = _send_to_chat(acc.telegram_id, text)
        if ok:
            ok_count += 1
        else:
            # если юзер заблокировал бота или чат недоступен — можно отключить аккаунт
            # Telegram часто возвращает 403/400
            if err in ("HTTP_403", "HTTP_400"):
                acc.is_active = False
                acc.save(update_fields=["is_active", "updated_at"])

    return ok_count
