"""
Сигналы для приложения cases.
При загрузке нового документа — отправляет файл в Telegram-канал архива.
"""

import os
import threading
import logging

import requests
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone

from cases.models import CaseDocument

logger = logging.getLogger(__name__)


def _send_document_to_channel(doc_id: int):
    """Отправляет документ в Telegram-канал архива."""
    channel_id = getattr(settings, 'TELEGRAM_ARCHIVE_CHANNEL_ID', None)
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)

    if not channel_id or not token:
        logger.warning('TELEGRAM_ARCHIVE_CHANNEL_ID или TELEGRAM_BOT_TOKEN не задан — архив не отправлен')
        return

    try:
        doc = CaseDocument.objects.select_related(
            'case', 'stage', 'field', 'created_by'
        ).get(pk=doc_id)
    except CaseDocument.DoesNotExist:
        return

    if not doc.file_value:
        return  # только файловые поля

    file_path = doc.file_value.path
    if not os.path.exists(file_path):
        logger.warning('Файл не найден на диске: %s', file_path)
        return

    case = doc.case
    stage = doc.stage
    field = doc.field
    uploaded_by = doc.created_by
    uploaded_at = timezone.localtime(doc.created_at).strftime('%d.%m.%Y %H:%M')

    # Получаем главного доверителя
    participant = case.participants.select_related('trustor').filter(
        main_participant=True
    ).first()
    client_name = participant.trustor.get_full_name() if participant else '—'

    caption = (
        f'📂 <b>Новый документ загружен</b>\n\n'
        f'📁 <b>Дело:</b> {case.title}\n'
        f'👤 <b>Клиент:</b> {client_name}\n'
        f'🗂 <b>Этап:</b> {stage.name}\n'
        f'📄 <b>Документ:</b> {field.name}\n'
        f'📅 <b>Дата загрузки:</b> {uploaded_at}\n'
        f'👨‍💼 <b>Загрузил:</b> {uploaded_by.get_full_name() or uploaded_by.username}'
    )

    file_name = os.path.basename(file_path)
    ext = os.path.splitext(file_name)[1].lower()

    # Выбираем метод отправки по типу файла
    image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    if ext in image_exts:
        method = 'sendPhoto'
        file_key = 'photo'
    else:
        method = 'sendDocument'
        file_key = 'document'

    try:
        with open(file_path, 'rb') as f:
            r = requests.post(
                f'https://api.telegram.org/bot{token}/{method}',
                data={
                    'chat_id': channel_id,
                    'caption': caption,
                    'parse_mode': 'HTML',
                },
                files={file_key: (file_name, f)},
                timeout=30,
            )
        if r.ok and r.json().get('ok'):
            logger.info('Документ отправлен в Telegram-архив: %s', file_name)
        else:
            logger.warning('TG archive error %s: %s', r.status_code, r.text[:200])
    except Exception as e:
        logger.exception('Ошибка отправки документа в TG-архив: %s', e)


@receiver(post_save, sender=CaseDocument)
def archive_document_on_upload(sender, instance, created, **kwargs):
    """При создании нового документа с файлом — отправляем в канал."""
    if not created:
        return
    if not instance.file_value:
        return

    doc_id = instance.pk

    def _run():
        _send_document_to_channel(doc_id)

    transaction.on_commit(
        lambda: threading.Thread(target=_run, daemon=True).start()
    )
