from django import template
from django.urls import reverse

from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def static(context, path):
    return f'{settings.BASE_DIR}/assets/{path}'


@register.simple_tag(takes_context=True)
def media(context, path):
    return f'{settings.BASE_DIR}/media/{path}'
