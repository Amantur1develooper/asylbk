from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import TelegramAccount, User, PracticeType, TraineeProfile

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'position', 'is_staff')
    list_filter = ('role', 'position', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'position', 'phone', 'passport_series', 'passport_number', 
                      'passport_issued_by', 'passport_issue_date', 'registration_address',
                      'hire_date', 'contract_file')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'position', 'phone')
        }),
    )

@admin.register(PracticeType)
class PracticeTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(TraineeProfile)
class TraineeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'practice_type', 'curator')
    list_filter = ('practice_type',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user', 'curator')

admin.site.register(User, CustomUserAdmin)


@admin.register(TelegramAccount)
class TelegramAccountAdmin(admin.ModelAdmin):
    list_display = (
        'user_link', 'user_role', 'telegram_identity', 'telegram_id',
        'is_active', 'notifications_enabled', 'created_at',
    )
    list_display_links = ('user_link',)
    list_editable = ('is_active', 'notifications_enabled')
    list_filter = ('is_active', 'notifications_enabled', 'user__role')
    search_fields = (
        'user__username', 'user__first_name', 'user__last_name',
        'username', 'first_name', 'last_name', 'telegram_id',
    )
    autocomplete_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Привязка к сотруднику', {
            'fields': ('user',),
            'description': 'К какому сотруднику системы привязан этот Telegram-аккаунт.',
        }),
        ('Данные из Telegram', {
            'fields': ('telegram_id', 'username', 'first_name', 'last_name'),
            'description': 'ID заполняется автоматически при привязке бота — вручную его лучше не менять.',
        }),
        ('Статус', {
            'fields': ('is_active', 'notifications_enabled'),
            'description': (
                '"Аккаунт активен" — бот выключает его сам, если пользователь заблокировал бота. '
                '"Уведомления включены" — общий рубильник; ниже можно тонко настроить, за сколько '
                'до события присылать напоминание.'
            ),
        }),
        ('За сколько присылать напоминания', {
            'fields': (
                'notify_1_week', 'notify_1_day', 'notify_12_hours', 'notify_3_hours',
                'notify_2_hours', 'notify_1_hour', 'notify_30_minutes',
                'notify_10_minutes', 'notify_1_minute',
            ),
            'classes': ('collapse',),
        }),
        ('Служебное', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Сотрудник', ordering='user__last_name')
    def user_link(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description='Роль', ordering='user__role')
    def user_role(self, obj):
        return obj.user.get_role_display()

    @admin.display(description='Telegram')
    def telegram_identity(self, obj):
        handle = f'@{obj.username}' if obj.username else '—'
        full_name = obj.get_full_name()
        return f'{handle} ({full_name})' if full_name != 'Неизвестно' else handle