from django.db import migrations


SURVEY_SLUG = 'otzyv-ot-klienta'


def create_survey(apps, schema_editor):
    Survey = apps.get_model('surveys', 'Survey')
    SurveyQuestion = apps.get_model('surveys', 'SurveyQuestion')

    if Survey.objects.filter(slug=SURVEY_SLUG).exists():
        return

    survey = Survey.objects.create(
        title='Отзыв от клиента',
        slug=SURVEY_SLUG,
        description='Мы будем рады вашим отзывам и идеям. Они помогут нам стать ещё лучше.',
        thank_you_text='Спасибо! Ваш отзыв очень важен для нас.',
        is_published=True,
    )

    questions = [
        dict(text='Ваше обращение', field_type='long_text', is_required=True, order=1),
        dict(text='Предложения по улучшению', field_type='long_text', is_required=False, order=2),
        dict(text='Имя', field_type='short_text', is_required=False, order=3),
        dict(text='Оцените качество обслуживания', field_type='rating', is_required=False, order=4),
    ]
    for q in questions:
        SurveyQuestion.objects.create(survey=survey, **q)


def remove_survey(apps, schema_editor):
    Survey = apps.get_model('surveys', 'Survey')
    Survey.objects.filter(slug=SURVEY_SLUG).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_survey, remove_survey),
    ]
