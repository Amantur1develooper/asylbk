import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import Survey, SurveyQuestion, SurveyResponse, SurveyAnswer


class SurveyQuestionInline(admin.TabularInline):
    model = SurveyQuestion
    extra = 1
    fields = ('order', 'text', 'field_type', 'is_required', 'options', 'help_text')


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'questions_count', 'responses_count', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    inlines = [SurveyQuestionInline]

    fieldsets = (
        (None, {'fields': ('title', 'slug', 'description', 'is_published')}),
        ('После отправки', {'fields': ('thank_you_text',)}),
        ('Служебное', {'fields': ('created_by', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    @admin.display(description='Вопросов')
    def questions_count(self, obj):
        return obj.questions.count()

    @admin.display(description='Ответов')
    def responses_count(self, obj):
        return obj.responses.count()

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class SurveyAnswerInline(admin.TabularInline):
    model = SurveyAnswer
    extra = 0
    fields = ('question', 'value')
    readonly_fields = ('question', 'value')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('survey', 'submitted_at', 'short_summary', 'ip_address')
    list_filter = ('survey',)
    date_hierarchy = 'submitted_at'
    readonly_fields = ('survey', 'submitted_at', 'ip_address')
    inlines = [SurveyAnswerInline]
    actions = ['export_as_csv']

    def has_add_permission(self, request):
        return False

    @admin.display(description='Ответы')
    def short_summary(self, obj):
        parts = [f'{a.question.text}: {a.value}' for a in obj.answers.select_related('question')[:3]]
        return ' | '.join(parts) or '—'

    @admin.action(description='Экспортировать выбранные ответы в CSV')
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="survey_responses.csv"'
        writer = csv.writer(response)

        # Собираем объединённый список вопросов по всем выбранным опросам, сохраняя порядок
        questions = []
        seen = set()
        for survey_response in queryset.select_related('survey').prefetch_related('answers__question'):
            for answer in survey_response.answers.all():
                if answer.question_id not in seen:
                    seen.add(answer.question_id)
                    questions.append(answer.question)
        questions.sort(key=lambda q: (q.survey_id, q.order, q.id))

        writer.writerow(['Опросник', 'Дата заполнения', 'IP'] + [q.text for q in questions])

        for survey_response in queryset.select_related('survey').prefetch_related('answers__question'):
            values_by_question = {a.question_id: a.value for a in survey_response.answers.all()}
            row = [
                survey_response.survey.title,
                survey_response.submitted_at.strftime('%d.%m.%Y %H:%M'),
                survey_response.ip_address or '',
            ]
            row += [values_by_question.get(q.id, '') for q in questions]
            writer.writerow(row)

        return response
