from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import SiteSettings, Practice, Staff, PublicCase, NewsPost, ConsultationRequest

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("company_name", "phone", "email")

@admin.register(Practice)
class PracticeAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    list_editable = ("order",)

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("full_name", "position", "is_partner", "order")
    list_editable = ("is_partner", "order")
    search_fields = ("full_name", "position")

@admin.register(PublicCase)
class PublicCaseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "published_at")
    list_filter = ("is_published", "category")
    search_fields = ("title", "excerpt")
    prepopulated_fields = {"slug": ("title",)}

@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "published_at")
    list_filter = ("is_published",)
    search_fields = ("title", "excerpt")
    prepopulated_fields = {"slug": ("title",)}

@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "phone", "topic")
