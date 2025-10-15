from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Позволяет обращаться к словарю по ключу в шаблоне"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
