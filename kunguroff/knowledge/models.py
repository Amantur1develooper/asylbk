from django.db import models
from django.conf import settings


class Category(models.Model):
    COLOR_CHOICES = [
        ('primary',   'Синий'),
        ('success',   'Зелёный'),
        ('danger',    'Красный'),
        ('warning',   'Жёлтый'),
        ('info',      'Голубой'),
        ('secondary', 'Серый'),
        ('dark',      'Тёмный'),
    ]

    name  = models.CharField(max_length=100, unique=True, verbose_name='Название')
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='primary', verbose_name='Цвет')
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name        = 'Категория'
        verbose_name_plural = 'Категории'
        ordering            = ['order', 'name']

    def __str__(self):
        return self.name


class KnowledgePost(models.Model):
    title      = models.CharField(max_length=255, verbose_name='Заголовок')
    body       = models.TextField(blank=True, verbose_name='Текст')
    category   = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='posts',
        verbose_name='Категория',
    )
    author     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='knowledge_posts',
        verbose_name='Автор',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    updated_at = models.DateTimeField(auto_now=True,     verbose_name='Изменено')
    is_pinned  = models.BooleanField(default=False, verbose_name='Закреплён')

    class Meta:
        verbose_name        = 'Запись базы знаний'
        verbose_name_plural = 'Записи базы знаний'
        ordering            = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title


class KnowledgeFile(models.Model):
    post        = models.ForeignKey(
        KnowledgePost,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='Запись',
    )
    file        = models.FileField(upload_to='knowledge/', verbose_name='Файл')
    name        = models.CharField(max_length=255, blank=True, verbose_name='Название файла')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Файл'
        verbose_name_plural = 'Файлы'

    def __str__(self):
        return self.name or self.file.name

    def save(self, *args, **kwargs):
        import os
        if not self.name and self.file:
            self.name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)

    def ext(self):
        import os
        return os.path.splitext(self.file.name)[1].lower().lstrip('.')

    def icon(self):
        icons = {
            'pdf':  'bi-file-earmark-pdf text-danger',
            'doc':  'bi-file-earmark-word text-primary',
            'docx': 'bi-file-earmark-word text-primary',
            'xls':  'bi-file-earmark-excel text-success',
            'xlsx': 'bi-file-earmark-excel text-success',
            'ppt':  'bi-file-earmark-ppt text-warning',
            'pptx': 'bi-file-earmark-ppt text-warning',
            'jpg':  'bi-file-earmark-image text-info',
            'jpeg': 'bi-file-earmark-image text-info',
            'png':  'bi-file-earmark-image text-info',
            'zip':  'bi-file-earmark-zip text-secondary',
            'rar':  'bi-file-earmark-zip text-secondary',
        }
        return icons.get(self.ext(), 'bi-file-earmark text-muted')
