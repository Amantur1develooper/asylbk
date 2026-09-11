"""
Автоматическое формирование соглашения об оказании юридических услуг по делу.

Как только по делу заполнены все необходимые данные (категория, сумма договора,
хотя бы один ответственный юрист и основной доверитель) — cases/signals.py вызывает
generate_agreement_docx() и сохраняет результат в Case.agreement_file.

Текст — типовой шаблон соглашения, составленный вручную (готового образца от
заказчика не было). Документ отдаётся в формате .docx, чтобы его можно было
скачать и доредактировать вручную перед подписанием.
"""
import io

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

COMPANY_NAME_DEFAULT = "Kunguroff & Partners"


def _site_settings():
    try:
        from public.models import SiteSettings
        return SiteSettings.objects.first()
    except Exception:
        return None


def _party_label(trustor):
    """ФИО/название доверителя для использования в тексте соглашения."""
    if trustor.entity_type == 'legal':
        return trustor.company_name
    parts = [trustor.last_name, trustor.first_name, trustor.middle_name]
    return " ".join(p for p in parts if p)


def _party_requisites(trustor):
    """Паспортные/регистрационные данные доверителя одной строкой."""
    if trustor.entity_type == 'legal':
        bits = []
        if trustor.legal_form:
            bits.append(trustor.legal_form)
        if trustor.reg_number:
            bits.append(f"рег. № {trustor.reg_number}")
        if trustor.inn:
            bits.append(f"ИНН {trustor.inn}")
        if trustor.director_name:
            bits.append(f"в лице {trustor.director_name}")
        return ", ".join(bits) or "—"
    bits = []
    if trustor.passport_series or trustor.passport_number:
        bits.append(f"паспорт {trustor.passport_series or ''} {trustor.passport_number or ''}".strip())
    if trustor.passport_issued_by:
        bits.append(f"выдан {trustor.passport_issued_by}")
    if trustor.passport_issue_date:
        bits.append(f"от {trustor.passport_issue_date.strftime('%d.%m.%Y')}")
    if trustor.registration_address:
        bits.append(f"зарегистрирован(а) по адресу: {trustor.registration_address}")
    return ", ".join(bits) or "—"


def _format_amount(amount):
    return f"{amount:,.2f}".replace(",", " ").replace(".", ",")


def _add_heading(doc, text, size=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER):
    p = doc.add_paragraph()
    p.alignment = align
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    return p


def _add_paragraph(doc, text, size=11, justify=True):
    p = doc.add_paragraph()
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    run.font.size = Pt(size)
    return p


def build_agreement_document(case) -> Document:
    """Собирает docx.Document с текстом соглашения по делу. Не сохраняет файл."""
    site = _site_settings()
    company_name = (site.company_name if site and site.company_name else COMPANY_NAME_DEFAULT)
    company_address = site.address if site and site.address else "___________________"
    company_phone = site.phone if site and site.phone else "___________________"

    lawyers = list(case.responsible_lawyer.all())
    lead_lawyer = lawyers[0] if lawyers else None
    lead_lawyer_name = (lead_lawyer.get_full_name() or lead_lawyer.username) if lead_lawyer else "___________________"

    trustor = case.main_trustor
    client_name = _party_label(trustor) if trustor else "___________________"
    client_requisites = _party_requisites(trustor) if trustor else "—"

    today = timezone.localdate()
    number = case.internal_number or f"ID-{case.pk}"

    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(11)

    _add_heading(doc, f"СОГЛАШЕНИЕ № {number}")
    _add_heading(doc, "об оказании юридических услуг", size=12, bold=False)
    doc.add_paragraph()

    date_line = doc.add_paragraph()
    date_line.add_run(f"г. Ош{' ' * 40}{today.strftime('%d.%m.%Y')} г.")
    doc.add_paragraph()

    _add_paragraph(
        doc,
        f"{company_name}, именуем__ в дальнейшем «Исполнитель», в лице юриста "
        f"{lead_lawyer_name}, действующего на основании внутреннего распорядка "
        f"Исполнителя, с одной стороны, и {client_name} ({client_requisites}), "
        f"именуем__ в дальнейшем «Доверитель», с другой стороны, совместно "
        f"именуемые «Стороны», а по отдельности — «Сторона», заключили настоящее "
        f"соглашение (далее — «Соглашение») о нижеследующем:"
    )
    doc.add_paragraph()

    _add_heading(doc, "1. Предмет соглашения", size=12, align=WD_ALIGN_PARAGRAPH.LEFT)
    _add_paragraph(
        doc,
        f"1.1. Исполнитель обязуется оказать Доверителю юридические услуги по делу "
        f"«{case.title}» (категория: {case.category.get_name_display()}), а Доверитель "
        f"обязуется оплатить эти услуги в порядке и на условиях, предусмотренных "
        f"настоящим Соглашением."
    )
    if case.description:
        _add_paragraph(doc, f"1.2. Описание дела: {case.description}")
    if case.court_name or case.case_number or case.judge_name:
        court_bits = []
        if case.court_name:
            court_bits.append(case.court_name)
        if case.case_number:
            court_bits.append(f"дело № {case.case_number}")
        if case.judge_name:
            court_bits.append(f"судья {case.judge_name}")
        _add_paragraph(doc, f"1.3. Судебная инстанция: {', '.join(court_bits)}.")
    doc.add_paragraph()

    _add_heading(doc, "2. Стоимость услуг и порядок расчётов", size=12, align=WD_ALIGN_PARAGRAPH.LEFT)
    _add_paragraph(
        doc,
        f"2.1. Стоимость услуг по настоящему Соглашению составляет "
        f"{_format_amount(case.contract_amount)} сом."
    )
    _add_paragraph(
        doc,
        "2.2. Оплата производится Доверителем наличным или безналичным способом "
        "в порядке, согласованном Сторонами дополнительно."
    )
    doc.add_paragraph()

    _add_heading(doc, "3. Права и обязанности Сторон", size=12, align=WD_ALIGN_PARAGRAPH.LEFT)
    _add_paragraph(doc, "3.1. Исполнитель обязуется:")
    _add_paragraph(doc, "— оказывать юридические услуги добросовестно и квалифицированно;")
    _add_paragraph(doc, "— информировать Доверителя о ходе исполнения поручения;")
    _add_paragraph(doc, "— соблюдать конфиденциальность сведений, ставших известными в связи с исполнением Соглашения.")
    _add_paragraph(doc, "3.2. Доверитель обязуется:")
    _add_paragraph(doc, "— своевременно предоставлять документы и сведения, необходимые для оказания услуг;")
    _add_paragraph(doc, "— оплатить услуги в размере и в сроки, установленные настоящим Соглашением.")
    doc.add_paragraph()

    _add_heading(doc, "4. Ответственность Сторон", size=12, align=WD_ALIGN_PARAGRAPH.LEFT)
    _add_paragraph(
        doc,
        "4.1. За неисполнение или ненадлежащее исполнение обязательств по настоящему "
        "Соглашению Стороны несут ответственность в соответствии с действующим "
        "законодательством Кыргызской Республики."
    )
    doc.add_paragraph()

    _add_heading(doc, "5. Срок действия соглашения", size=12, align=WD_ALIGN_PARAGRAPH.LEFT)
    _add_paragraph(
        doc,
        "5.1. Настоящее Соглашение вступает в силу с момента подписания Сторонами "
        "и действует до полного исполнения Сторонами своих обязательств."
    )
    doc.add_paragraph()

    _add_heading(doc, "6. Прочие условия", size=12, align=WD_ALIGN_PARAGRAPH.LEFT)
    _add_paragraph(
        doc,
        "6.1. Все изменения и дополнения к настоящему Соглашению действительны при "
        "условии, что они совершены в письменной форме и подписаны обеими Сторонами."
    )
    _add_paragraph(
        doc,
        "6.2. Настоящее Соглашение составлено в двух экземплярах, имеющих равную "
        "юридическую силу, по одному для каждой из Сторон."
    )
    doc.add_paragraph()
    doc.add_paragraph()

    _add_heading(doc, "7. Реквизиты и подписи Сторон", size=12, align=WD_ALIGN_PARAGRAPH.LEFT)
    doc.add_paragraph()

    table = doc.add_table(rows=1, cols=2)
    left, right = table.rows[0].cells
    left.paragraphs[0].add_run("Исполнитель:").bold = True
    left.add_paragraph(company_name)
    left.add_paragraph(company_address)
    left.add_paragraph(company_phone)
    left.add_paragraph()
    left.add_paragraph(f"_______________ / {lead_lawyer_name}")

    right.paragraphs[0].add_run("Доверитель:").bold = True
    right.add_paragraph(client_name)
    right.add_paragraph(client_requisites)
    right.add_paragraph()
    right.add_paragraph()
    right.add_paragraph(f"_______________ / {client_name}")

    return doc


def generate_agreement_docx(case) -> ContentFile:
    """Строит документ и возвращает его в виде ContentFile, готового к сохранению в FileField."""
    doc = build_agreement_document(case)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    filename = f"soglashenie_delo_{case.pk}.docx"
    return filename, ContentFile(buffer.read())


def regenerate_case_agreement(case) -> bool:
    """
    Пересобирает соглашение по делу и сохраняет в Case.agreement_file, если данных
    достаточно (case.agreement_ready). Обновляет запись напрямую через .update(),
    не вызывая Case.save() — иначе сигнал post_save зациклился бы сам на себя.
    Возвращает True, если файл был (пере)сформирован.
    """
    from cases.models import Case

    if not case.agreement_ready:
        return False

    filename, content = generate_agreement_docx(case)

    field = Case._meta.get_field('agreement_file')
    storage = field.storage

    # Убираем предыдущую версию файла, чтобы не копились версии с суффиксами.
    if case.agreement_file:
        try:
            if storage.exists(case.agreement_file.name):
                storage.delete(case.agreement_file.name)
        except Exception:
            pass

    saved_name = storage.save(f"{field.upload_to}{filename}", content)

    Case.objects.filter(pk=case.pk).update(
        agreement_file=saved_name,
        agreement_generated_at=timezone.now(),
    )
    return True
