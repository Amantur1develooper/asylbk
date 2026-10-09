import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Survey, SurveyResponse, SurveyAnswer


def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def survey_detail(request, slug):
    survey = get_object_or_404(Survey, slug=slug, is_published=True)
    questions = list(survey.questions.all())

    if request.method == 'POST':
        errors = {}
        answers = {}

        for question in questions:
            if question.field_type == 'checkbox':
                values = request.POST.getlist(question.field_name)
                value = ', '.join(values)
                is_empty = not values
            else:
                value = request.POST.get(question.field_name, '').strip()
                is_empty = not value

            if question.is_required and is_empty:
                errors[question.field_name] = 'Это поле обязательно для заполнения.'

            answers[question.pk] = value

        if not errors:
            response = SurveyResponse.objects.create(survey=survey, ip_address=_client_ip(request))
            SurveyAnswer.objects.bulk_create([
                SurveyAnswer(response=response, question_id=question_id, value=value)
                for question_id, value in answers.items()
            ])
            return redirect('surveys:thanks', slug=survey.slug)

        messages.error(request, 'Пожалуйста, заполните обязательные поля.')
        return render(request, 'surveys/detail.html', {
            'survey': survey,
            'questions': questions,
            'errors': errors,
            'posted': request.POST,
        })

    return render(request, 'surveys/detail.html', {
        'survey': survey,
        'questions': questions,
        'errors': {},
        'posted': None,
    })


def survey_thanks(request, slug):
    survey = get_object_or_404(Survey, slug=slug, is_published=True)
    return render(request, 'surveys/thanks.html', {'survey': survey})


# ── Внутренняя статистика (для сотрудников) ─────────────────────────────────

@login_required
def survey_manage_list(request):
    surveys = Survey.objects.annotate(responses_count=Count('responses')).order_by('-created_at')
    return render(request, 'surveys/manage_list.html', {'surveys': surveys})


def _survey_table(survey):
    """Вопросы по порядку + список прохождений, где каждая строка — словарь
    question_id -> значение (для вывода таблицей, как в Google Forms)."""
    questions = list(survey.questions.all())
    responses = (
        survey.responses
        .order_by('-submitted_at')
        .prefetch_related('answers')
    )
    rows = []
    for response in responses:
        values_by_question = {a.question_id: a.value for a in response.answers.all()}
        rows.append({
            'response': response,
            'values': [values_by_question.get(q.pk, '') for q in questions],
        })
    return questions, rows


@login_required
def survey_manage_detail(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    questions, rows = _survey_table(survey)

    # Средняя оценка по каждому вопросу-шкале
    rating_stats = []
    for q in questions:
        if q.field_type != 'rating':
            continue
        values = [
            int(v) for v in q.answers.exclude(value='').values_list('value', flat=True)
            if v.isdigit()
        ]
        rating_stats.append({
            'question': q,
            'count': len(values),
            'average': round(sum(values) / len(values), 2) if values else None,
        })

    return render(request, 'surveys/manage_detail.html', {
        'survey': survey,
        'questions': questions,
        'rows': rows,
        'rating_stats': rating_stats,
        'responses_count': len(rows),
    })


@login_required
def survey_manage_export(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    questions, rows = _survey_table(survey)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{survey.slug}_responses.csv"'
    writer = csv.writer(response)
    writer.writerow(['Дата заполнения', 'IP'] + [q.text for q in questions])
    for row in rows:
        writer.writerow(
            [row['response'].submitted_at.strftime('%d.%m.%Y %H:%M'), row['response'].ip_address or '']
            + row['values']
        )
    return response
