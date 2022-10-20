from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def url_active(context, viewname, **kwargs):
    request = context['request']
    current_path = request.path
    compare_path = reverse(viewname, kwargs=kwargs)
    if compare_path == current_path:
        return ' active'
    return ''
