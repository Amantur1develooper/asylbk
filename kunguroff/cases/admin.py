from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CaseCategory, CaseStage, StageField, Case, CaseDocument
from .models import CaseParticipant, CaseParticipantRole

class CaseParticipantInline(admin.TabularInline):
    model = CaseParticipant
    extra = 1
    raw_id_fields = ('trustor',)
class StageFieldInline(admin.TabularInline):
    model = StageField
    extra = 1

@admin.register(CaseCategory)
class CaseCategoryAdmin(admin.ModelAdmin):
    list_display = ('get_name_display', 'description')
    list_filter = ('name',)

@admin.register(CaseStage)
class CaseStageAdmin(admin.ModelAdmin):
    list_display = ('category', 'name', 'order', 'description')
    list_filter = ('category',)
    ordering = ('category', 'order')
    inlines = [StageFieldInline]

@admin.register(StageField)
class StageFieldAdmin(admin.ModelAdmin):
    list_display = ('stage', 'name', 'field_type', 'is_required', 'order')
    list_filter = ('stage__category', 'field_type', 'is_required')
    ordering = ('stage', 'order')

class CaseDocumentInline(admin.TabularInline):
    model = CaseDocument
    extra = 0
    readonly_fields = ('created_by', 'created_at')
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'progress', 'created_at')
    list_filter = ('category', 'status', 'responsible_lawyer', 'created_at')
    search_fields = ('title', 'client__last_name', 'client__first_name')
    readonly_fields = ('progress', 'created_at', 'updated_at')
    filter_horizontal = ['responsible_lawyer']  # Для удобного выбора
    inlines = [CaseParticipantInline, CaseDocumentInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'category')
        }),
        ('Ответственные', {
            'fields': ('responsible_lawyer', 'manager')
        }),
        ('Статус', {
            'fields': ('status', 'current_stage', 'progress')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CaseDocument)
class CaseDocumentAdmin(admin.ModelAdmin):
    list_display = ('case', 'stage', 'field', 'created_by', 'created_at')
    list_filter = ('stage__category', 'field__field_type', 'created_at')
    search_fields = ('case__title', 'field__name')
    readonly_fields = ('created_by', 'created_at')
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        

@admin.register(CaseParticipantRole)
class CaseParticipantRoleAdmin(admin.ModelAdmin):
    list_display = ('category', 'role_name', 'role_code', 'order')
    list_filter = ('category',)
    ordering = ('category', 'order')


@admin.register(CaseParticipant)
class CaseParticipantAdmin(admin.ModelAdmin):
    list_display = ('case', 'trustor', 'role', 'main_participant')
    list_filter = ('case__category', 'role', 'main_participant')
    search_fields = ('case__title', 'trustor__last_name', 'trustor__first_name')
    raw_id_fields = ('case', 'trustor')


