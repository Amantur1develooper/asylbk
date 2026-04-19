"""
Команда: python manage.py fetch_toktom_news

Парсит новости с https://online.toktom.kg/News/1?page=0&size=20,
сохраняет новые статьи в модель NewsPost и отправляет уведомление
в Telegram всем пользователям с активным Telegram-аккаунтом.

Запускать через cron каждый день в 10:00:
    0 10 * * * /path/to/venv/bin/python /path/to/manage.py fetch_toktom_news >> /var/log/toktom_news.log 2>&1
"""

import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from public.models import NewsPost
from users.models import TelegramAccount

logger = logging.getLogger(__name__)

BASE_URL     = "https://online.toktom.kg"
LIST_URL     = f"{BASE_URL}/News/1?page=0&size=20"
SITE_URL     = getattr(settings, "SITE_PUBLIC_URL", "https://kunguroff.kg")
SLUG_PREFIX  = "toktom-"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9",
}


# ─── Helpers ────────────────────────────────────────────────────────────────

def _get(url: str, timeout: int = 15) -> BeautifulSoup | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        return BeautifulSoup(r.text, "html.parser")
    except Exception as exc:
        logger.warning("Не удалось загрузить %s: %s", url, exc)
        return None


def _parse_date(text: str) -> datetime | None:
    """Парсит дату вида 17.04.2026 → aware datetime."""
    text = text.strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(text, fmt)
            return timezone.make_aware(dt)
        except ValueError:
            continue
    return None


def _fetch_article_content(path: str) -> tuple[str, str]:
    """
    Загружает страницу статьи, возвращает (excerpt, content).
    excerpt — первый абзац текста (без заголовка).
    content — весь текст.
    """
    soup = _get(BASE_URL + path)
    if not soup:
        return "", ""

    topic = soup.find(class_="cms-topic") or soup.find(class_="cms-news-topic")
    if not topic:
        return "", ""

    paragraphs = topic.find_all("p")
    text_parts = []
    for p in paragraphs:
        t = p.get_text(separator="\n").strip()
        if t:
            text_parts.append(t)

    if not text_parts:
        return "", ""

    # Первый абзац может быть жирным заголовком — пропускаем его, если он короткий
    start = 0
    if len(text_parts) > 1 and len(text_parts[0]) < 200 and text_parts[0].isupper() is False:
        # Первый абзац часто дублирует заголовок — берём его как excerpt
        excerpt = text_parts[0][:500]
        start = 0  # всё равно включаем в content
    else:
        excerpt = text_parts[0][:500]

    content = "\n\n".join(text_parts)
    return excerpt, content


def _send_tg(chat_id: int, text: str) -> bool:
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    if not token:
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            },
            timeout=8,
        )
        if r.ok and r.json().get("ok"):
            return True
        logger.warning("TG %s: %s", r.status_code, r.text[:200])
        return False
    except Exception as exc:
        logger.exception("TG exception: %s", exc)
        return False


def _notify_all(news: NewsPost) -> int:
    """Отправляет уведомление о новой новости всем активным TG-аккаунтам."""
    site_link = f"{SITE_URL}/news/{news.slug}/"
    text = (
        f"📰 <b>Новость — Toktom.kg</b>\n\n"
        f"<b>{news.title}</b>\n\n"
        f"<a href='{site_link}'>Читать на сайте Kunguroff &amp; Partners →</a>"
    )

    accounts = TelegramAccount.objects.filter(
        is_active=True,
        notifications_enabled=True,
        user__is_active=True,
    )

    sent = 0
    for acc in accounts:
        if _send_tg(acc.telegram_id, text):
            sent += 1
        else:
            # Бот заблокирован пользователем — отключаем
            pass
    return sent


# ─── Command ────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = "Забирает новости с online.toktom.kg и сохраняет новые в БД, рассылает в Telegram"

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-notify",
            action="store_true",
            help="Не отправлять Telegram-уведомления",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Только показать новые новости, не сохранять",
        )

    def handle(self, *args, **options):
        no_notify = options["no_notify"]
        dry_run   = options["dry_run"]

        self.stdout.write(f"[fetch_toktom_news] Загружаем список: {LIST_URL}")
        soup = _get(LIST_URL)
        if not soup:
            self.stderr.write(self.style.ERROR("Не удалось загрузить страницу новостей."))
            return

        items = soup.select(".news-item")
        self.stdout.write(f"Найдено элементов на странице: {len(items)}")

        new_count = 0
        for item in items:
            # Ссылка и заголовок
            a_tag = item.find("a")
            if not a_tag:
                continue

            title = a_tag.get_text(strip=True)
            path  = a_tag.get("href", "")           # /NewsTopic/7562
            if not path or not title:
                continue

            # ID статьи → slug
            article_id = path.rstrip("/").rsplit("/", 1)[-1]
            slug       = f"{SLUG_PREFIX}{article_id}"

            # Уже есть в БД?
            if NewsPost.objects.filter(slug=slug).exists():
                self.stdout.write(f"  Уже есть: {slug}")
                continue

            # Дата
            date_tag  = item.find(class_="news-item-date")
            pub_date  = _parse_date(date_tag.get_text()) if date_tag else None
            pub_date  = pub_date or timezone.now()

            if dry_run:
                self.stdout.write(self.style.WARNING(f"  [DRY-RUN] Новая: {title} ({slug})"))
                new_count += 1
                continue

            # Загружаем контент статьи
            self.stdout.write(f"  Загружаем: {path}")
            excerpt, content = _fetch_article_content(path)

            # Сохраняем
            news = NewsPost.objects.create(
                title        = title,
                slug         = slug,
                excerpt      = excerpt or title,
                content      = content,
                is_published = True,
                published_at = pub_date,
            )
            self.stdout.write(self.style.SUCCESS(f"  ✓ Сохранено: {news.title}"))
            new_count += 1

            # Telegram
            if not no_notify:
                sent = _notify_all(news)
                self.stdout.write(f"    → Уведомлений отправлено: {sent}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nГотово. Новых новостей: {new_count}"
                + (" (dry-run, не сохранено)" if dry_run else "")
            )
        )
