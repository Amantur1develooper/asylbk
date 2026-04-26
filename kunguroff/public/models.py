from django.db import models
from django.utils import timezone
from django.urls import reverse

class SiteSettings(models.Model):
    company_name = models.CharField("Название", max_length=255, default="Kunguroff & Partners")
    slogan = models.CharField("Слоган", max_length=255, default="Stand for your rights")
    address = models.CharField("Адрес", max_length=255, blank=True)
    phone = models.CharField("Телефон", max_length=64, blank=True)
    email = models.EmailField("Email", blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=64, blank=True)
    telegram = models.CharField("Telegram", max_length=64, blank=True)
    work_hours = models.CharField("График работы", max_length=255, blank=True)

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Настройки сайта"


class Practice(models.Model):
    title = models.CharField("Название практики", max_length=120)
    icon = models.CharField("Иконка (FontAwesome class)", max_length=80, blank=True, help_text="Напр: fa-solid fa-scale-balanced")
    description = models.TextField("Описание", blank=True)
    order = models.PositiveIntegerField("Сортировка", default=0)

    class Meta:
        verbose_name = "Практика"
        verbose_name_plural = "Практики"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class Staff(models.Model):
    full_name = models.CharField("ФИО", max_length=150)
    position = models.CharField("Должность", max_length=120, blank=True)
    bio = models.TextField("Описание", blank=True)
    photo = models.ImageField("Фото", upload_to="public/staff/", blank=True, null=True)
    phone = models.CharField("Телефон", max_length=64, blank=True)
    email = models.EmailField("Email", blank=True)
    is_partner = models.BooleanField("Партнёр", default=False)
    order = models.PositiveIntegerField("Сортировка", default=0)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ["-is_partner", "order", "id"]

    def __str__(self):
        return self.full_name


class PublicCase(models.Model):
    title = models.CharField("Название кейса", max_length=200)
    slug = models.SlugField("Slug", unique=True)
    category = models.CharField("Категория", max_length=120, blank=True)
    excerpt = models.TextField("Коротко (для карточки)", blank=True)
    content = models.TextField("Описание кейса", blank=True)
    cover = models.ImageField("Обложка", upload_to="public/cases/", blank=True, null=True)
    is_published = models.BooleanField("Опубликован", default=True)
    published_at = models.DateTimeField("Дата публикации", default=timezone.now)

    class Meta:
        verbose_name = "Кейс"
        verbose_name_plural = "Кейсы"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("public:case_detail", kwargs={"slug": self.slug})


class NewsPost(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("Slug", unique=True)
    excerpt = models.TextField("Коротко (для карточки)", blank=True)
    content = models.TextField("Текст", blank=True)
    cover = models.ImageField("Обложка", upload_to="public/news/", blank=True, null=True)
    is_published = models.BooleanField("Опубликовано", default=True)
    published_at = models.DateTimeField("Дата публикации", default=timezone.now)

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("public:news_detail", kwargs={"slug": self.slug})


class Vacancy(models.Model):
    EMPLOYMENT_CHOICES = [
        ('full',     'Полная занятость'),
        ('part',     'Частичная занятость'),
        ('intern',   'Стажировка'),
        ('remote',   'Удалённо'),
        ('contract', 'Договор / Проект'),
    ]

    title       = models.CharField("Должность", max_length=200)
    department  = models.CharField("Отдел / Направление", max_length=120, blank=True)
    employment  = models.CharField("Тип занятости", max_length=20, choices=EMPLOYMENT_CHOICES, default='full')
    salary      = models.CharField("Зарплата", max_length=100, blank=True, help_text="Напр: от 30 000 сом или по договорённости")
    description = models.TextField("Описание вакансии")
    requirements= models.TextField("Требования", blank=True)
    conditions  = models.TextField("Условия", blank=True)
    is_active   = models.BooleanField("Активна", default=True)
    created_at  = models.DateTimeField("Создано", auto_now_add=True)
    updated_at  = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class OutsourceCase(models.Model):
    PRACTICE_CHOICES = [
        ('civil',          'Гражданское право'),
        ('criminal',       'Уголовное право'),
        ('family',         'Семейное право'),
        ('labor',          'Трудовое право'),
        ('administrative', 'Административное'),
        ('tax',            'Налоговое право'),
        ('corporate',      'Корпоративное'),
        ('other',          'Другое'),
    ]

    title          = models.CharField("Название дела", max_length=255)
    practice_area  = models.CharField("Отрасль", max_length=30, choices=PRACTICE_CHOICES, default='civil')
    description    = models.TextField("Описание дела")
    requirements   = models.TextField("Требования к исполнителю", blank=True)
    price          = models.CharField("Цена", max_length=120, blank=True,
                                      help_text="Напр: 15 000 сом, или оставьте пустым для «Договорная»")
    is_negotiable  = models.BooleanField("Цена договорная", default=False)
    deadline       = models.DateField("Срок подачи заявок", null=True, blank=True)
    is_active      = models.BooleanField("Активно", default=True)
    created_at     = models.DateTimeField("Создано", auto_now_add=True)
    updated_at     = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name        = "Аутсорс дело"
        verbose_name_plural = "Аутсорс дела"
        ordering            = ["-created_at"]

    def __str__(self):
        return self.title

    def price_display(self):
        if self.is_negotiable or not self.price:
            return "Договорная"
        return self.price


class ConsultationRequest(models.Model):
    STATUS_CHOICES = [
        ("new", "Новая"),
        ("in_work", "В работе"),
        ("done", "Закрыта"),
    ]
    name = models.CharField("Имя", max_length=120)
    phone = models.CharField("Телефон", max_length=64)
    email = models.EmailField("Email", blank=True)
    topic = models.CharField("Тема", max_length=200, blank=True)
    message = models.TextField("Сообщение", blank=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Заявка на консультацию"
        verbose_name_plural = "Заявки на консультацию"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.phone}"
