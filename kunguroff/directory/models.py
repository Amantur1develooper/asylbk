from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Region(models.Model):
    """Область / город республиканского значения."""
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Organization(models.Model):
    ORG_TYPES = [
        ('court',          'Судебная система'),
        ('prosecutor',     'Прокуратура'),
        ('investigative',  'Следственная служба'),
        ('police',         'МВД / Полиция'),
        ('notary',         'Нотариат'),
        ('bailiff',        'Служба судебных исполнителей'),
        ('justice',        'Министерство юстиции'),
        ('other',          'Другое'),
    ]

    org_type = models.CharField(
        max_length=30, choices=ORG_TYPES,
        verbose_name='Тип организации'
    )
    name = models.CharField(max_length=300, verbose_name='Название')
    region = models.ForeignKey(
        Region, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='organizations', verbose_name='Область / регион'
    )
    district = models.CharField(
        max_length=200, blank=True,
        verbose_name='Район / город'
    )
    address = models.TextField(blank=True, verbose_name='Адрес')
    phone = models.CharField(max_length=200, blank=True, verbose_name='Телефон(ы)')
    email = models.EmailField(blank=True, verbose_name='Email')
    head_name = models.CharField(max_length=255, blank=True, verbose_name='ФИО руководителя')
    head_position = models.CharField(max_length=200, blank=True, verbose_name='Должность руководителя')
    website = models.URLField(blank=True, verbose_name='Сайт')
    notes = models.TextField(blank=True, verbose_name='Примечания')

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='dir_created', verbose_name='Добавил'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'
        ordering = ['org_type', 'region__name', 'name']

    def __str__(self):
        return self.name

    def get_org_type_icon(self):
        icons = {
            'court':         '⚖️',
            'prosecutor':    '🏛️',
            'investigative': '🔍',
            'police':        '👮',
            'notary':        '📜',
            'bailiff':       '📋',
            'justice':       '🏢',
            'other':         '📌',
        }
        return icons.get(self.org_type, '📌')
