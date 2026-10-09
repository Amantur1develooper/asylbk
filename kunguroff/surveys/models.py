from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Survey(models.Model):
    """Опросник — набор вопросов с публичной страницей для заполнения."""

    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Адрес (slug)', max_length=200, unique=True, blank=True,
                             help_text='Часть публичной ссылки. Если оставить пустым — сформируется из названия.')
    description = models.TextField('Описание / приветственный текст', blank=True)
    thank_you_text = models.TextField(
        'Текст после отправки', blank=True,
        default='Спасибо! Ваш ответ сохранён.',
    )
    is_published = models.BooleanField('Опубликован (доступен по ссылке)', default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Создал',
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата изменения', auto_now=True)

    class Meta:
        verbose_name = 'Опросник'
        verbose_name_plural = 'Опросники'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title) or 'oprosnik'
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('surveys:detail', kwargs={'slug': self.slug})


class SurveyQuestion(models.Model):
    """Одно поле опросника — своя формулировка и свой тип."""

    FIELD_TYPES = [
        ('short_text', 'Короткий текст (одна строка)'),
        ('long_text', 'Длинный текст (абзац)'),
        ('email', 'Email'),
        ('phone', 'Телефон'),
        ('date', 'Дата'),
        ('rating', 'Шкала-оценка (1–5)'),
        ('choice', 'Один вариант из списка'),
        ('checkbox', 'Несколько вариантов из списка'),
    ]

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions', verbose_name='Опросник')
    text = models.CharField('Текст вопроса', max_length=300)
    field_type = models.CharField('Тип поля', max_length=20, choices=FIELD_TYPES, default='short_text')
    is_required = models.BooleanField('Обязательное', default=False)
    help_text = models.CharField('Пояснение под вопросом', max_length=300, blank=True)
    options = models.TextField(
        'Варианты ответа', blank=True,
        help_text='Только для «Один вариант» / «Несколько вариантов» — каждый вариант с новой строки.',
    )
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['survey', 'order', 'id']

    def __str__(self):
        return f'{self.survey} — {self.text}'

    @property
    def options_list(self):
        return [line.strip() for line in self.options.splitlines() if line.strip()]

    @property
    def field_name(self):
        """Имя поля в HTML-форме — уникальное для этого вопроса."""
        return f'question_{self.pk}'


class SurveyResponse(models.Model):
    """Один заполненный опросник (одно прохождение)."""

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses', verbose_name='Опросник')
    submitted_at = models.DateTimeField('Дата заполнения', auto_now_add=True)
    ip_address = models.GenericIPAddressField('IP-адрес', null=True, blank=True)

    class Meta:
        verbose_name = 'Ответ на опросник'
        verbose_name_plural = 'Ответы на опросники'
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.survey} — {self.submitted_at:%d.%m.%Y %H:%M}'


class SurveyAnswer(models.Model):
    """Ответ на один конкретный вопрос в рамках одного прохождения."""

    response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name='answers', verbose_name='Прохождение')
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE, related_name='answers', verbose_name='Вопрос')
    value = models.TextField(
        'Значение', blank=True,
        help_text='Текст, выбранное значение шкалы/варианта, или варианты через запятую для чекбоксов.',
    )

    class Meta:
        verbose_name = 'Ответ на вопрос'
        verbose_name_plural = 'Ответы на вопросы'
        unique_together = [('response', 'question')]
        ordering = ['question__order', 'id']

    def __str__(self):
        return f'{self.question.text}: {self.value[:50]}'
