from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def url_target_blank(text):
    return text.replace('<a', '<a target="_blank"')
