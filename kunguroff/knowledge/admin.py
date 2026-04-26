from django.contrib import admin
from .models import Category, KnowledgePost, KnowledgeFile


class KnowledgeFileInline(admin.TabularInline):
    model  = KnowledgeFile
    extra  = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'order']
    list_editable = ['order', 'color']


@admin.register(KnowledgePost)
class KnowledgePostAdmin(admin.ModelAdmin):
    list_display  = ['title', 'category', 'author', 'created_at', 'is_pinned']
    list_filter   = ['category', 'is_pinned']
    search_fields = ['title', 'body']
    inlines       = [KnowledgeFileInline]
