from django import template
from django.urls import reverse

from rtl_to import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def static(context, path):
    if settings.ALLOWED_HOSTS:
        domain = settings.ALLOWED_HOSTS[0]
    else:
        domain = '127.0.0.1:8000'
    return f'http://{domain}/{settings.STATIC_URL}{path}'


@register.simple_tag(takes_context=True)
def media(context, path):
    if settings.ALLOWED_HOSTS:
        domain = settings.ALLOWED_HOSTS[0]
    else:
        domain = '127.0.0.1:8000'
    return f'http://{domain}/{settings.MEDIA_URL}{path}'
