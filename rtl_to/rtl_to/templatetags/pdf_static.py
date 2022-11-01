from django import template
from django.urls import reverse

from rtl_to import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def static(context, path):
    if settings.ALLOWED_HOSTS:
        return f'http://{settings.ALLOWED_HOSTS[0]}/{settings.STATIC_URL}{path}'
    else:
        return f'http://127.0.0.1:8000/{settings.STATIC_URL}{path}'


@register.simple_tag(takes_context=True)
def media(context, path):
    if settings.ALLOWED_HOSTS:
        return f'http://{settings.ALLOWED_HOSTS[0]}/{settings.MEDIA_URL}{path}'
    else:
        return f'http://127.0.0.1:8000/{settings.MEDIA_URL}{path}'
