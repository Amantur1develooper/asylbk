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
admin.site.register(TelegramAccount)