from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Trustor


@admin.register(Trustor)
class TrustorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'phone', 'email', 'primary_contact')
    list_filter = ('primary_contact',)
    search_fields = ('last_name', 'first_name', 'phone', 'email')
    fieldsets = (
        (None, {
            'fields': (('first_name', 'last_name', 'middle_name'),)
        }),
        ('Контактная информация', {
            'fields': (('phone', 'email'),)
        }),
        ('Паспортные данные', {
            'fields': (
                ('passport_series', 'passport_number'),
                'passport_issued_by',
                'passport_issue_date',
                'registration_address',
                'residence_address'
            )
        }),
        ('Дополнительная информация', {
            'fields': ('inn', 'notes', 'primary_contact')
        }),
    )