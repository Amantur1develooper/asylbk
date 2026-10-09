from django.contrib import messages
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
