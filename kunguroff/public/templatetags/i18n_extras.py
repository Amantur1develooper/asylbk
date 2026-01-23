from django import template
from django.urls import translate_url as dj_translate_url

register = template.Library()

@register.simple_tag(takes_context=True)
def translate_url(context, lang_code):
    request = context["request"]
    return dj_translate_url(request.get_full_path(), lang_code)
