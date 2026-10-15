from django.db import migrations

SURVEY_SLUG = 'otzyv-ot-klienta'

# Вопросы, которых больше не должно быть в анкете.
# ВНИМАНИЕ: вместе с вопросом удаляются и собранные по нему ответы (CASCADE).
REMOVED = [
    'Ваше обращение',
    'Оцените качество обслуживания',
]

# Переименования — сохраняют уже собранные ответы (это тот же по смыслу вопрос).
RENAMED = {
    'Имя': 'ФИО',
    'Предложения по улучшению': 'Предложения по улучшению / комментарии',
}

# Итоговый состав анкеты: текст -> (тип, обязательный, порядок)
FINAL = {
    'ФИО': ('short_text', False, 1),
    'Качество организации': ('rating', True, 2),
    'Соответствие тренинга вашим ожиданиям': ('rating', True, 3),
    'Компетенция тренера': ('rating', True, 4),
    'Предложения по улучшению / комментарии': ('long_text', False, 5),
}


def apply_changes(apps, schema_editor):
    Survey = apps.get_model('surveys', 'Survey')
    SurveyQuestion = apps.get_model('surveys', 'SurveyQuestion')

    survey = Survey.objects.filter(slug=SURVEY_SLUG).first()
    if not survey:
        return

    SurveyQuestion.objects.filter(survey=survey, text__in=REMOVED).delete()

    for old_text, new_text in RENAMED.items():
        SurveyQuestion.objects.filter(survey=survey, text=old_text).update(text=new_text)

    for text, (field_type, is_required, order) in FINAL.items():
        SurveyQuestion.objects.update_or_create(
            survey=survey,
            text=text,
            defaults={'field_type': field_type, 'is_required': is_required, 'order': order},
        )


def revert_changes(apps, schema_editor):
    """Откат возвращает прежний состав вопросов, но не удалённые ответы."""
    Survey = apps.get_model('surveys', 'Survey')
    SurveyQuestion = apps.get_model('surveys', 'SurveyQuestion')

    survey = Survey.objects.filter(slug=SURVEY_SLUG).first()
    if not survey:
        return

    SurveyQuestion.objects.filter(survey=survey, text__in=[
        'Качество организации',
        'Соответствие тренинга вашим ожиданиям',
        'Компетенция тренера',
    ]).delete()

    for new_text, old_text in {v: k for k, v in RENAMED.items()}.items():
        SurveyQuestion.objects.filter(survey=survey, text=new_text).update(text=old_text)

    SurveyQuestion.objects.update_or_create(
        survey=survey, text='Ваше обращение',
        defaults={'field_type': 'long_text', 'is_required': True, 'order': 1},
    )
    SurveyQuestion.objects.filter(survey=survey, text='Предложения по улучшению').update(order=2)
    SurveyQuestion.objects.filter(survey=survey, text='Имя').update(order=3)
    SurveyQuestion.objects.update_or_create(
        survey=survey, text='Оцените качество обслуживания',
        defaults={'field_type': 'rating', 'is_required': False, 'order': 4},
    )


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0002_seed_feedback_survey'),
    ]

    operations = [
        migrations.RunPython(apply_changes, revert_changes),
    ]
