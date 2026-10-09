from django import template

register = template.Library()


@register.filter
def dictkey(container, key):
    """Доступ по динамическому ключу к dict/QueryDict в шаблоне (container[key])."""
    if container is None:
        return None
    try:
        return container.get(key)
    except AttributeError:
        return None
