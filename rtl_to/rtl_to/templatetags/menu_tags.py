import re

from django import template
from django.urls import reverse

import configs.groups_perms

register = template.Library()


@register.simple_tag(takes_context=True)
def url_active(context, viewname, **kwargs):
    request = context['request']
    current_path = request.path
    compare_path = reverse(viewname, kwargs=kwargs)
    if compare_path == current_path:
        return ' active'
    return ''


@register.simple_tag(takes_context=True)
def user_type(context, key):

    mapper = {
        'ORG_USER': 'Обычный пользователь',
        'ORG_ADMIN': 'Администратор клиента',
        'STAFF_USER': 'Сотрудник РТЛ-ТО'
    }

    for group_name in configs.groups_perms.groups.keys():
        if context[key].groups.filter(name=group_name).exists():
            return mapper.get(group_name, 'Undefined')
