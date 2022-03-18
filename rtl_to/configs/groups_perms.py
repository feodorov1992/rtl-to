from django.contrib.auth.models import Group, Permission

ORG_USER = [
    'view_organisation',
    'view_user',
]

ORG_ADMIN = [
    'change_organisation',
    'add_user',
    'change_user',
    'delete_user',
]

STAFF_USER = [
    'add_organisation',
]


def init_group(group_name, perms_list):
    group = Group(name=group_name)
    group.save()
    perms = Permission.objects.filter(codename__in=perms_list).values_list('id', flat=True)
    group.permissions.add(*perms)
    return group


def get_or_init(group_name, perms_list):
    if Group.objects.filter(name=group_name).exists():
        return Group.objects.get(name=group_name)
    else:
        return init_group(group_name, perms_list)
