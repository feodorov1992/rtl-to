from django.contrib.auth.models import Group, Permission


groups = {
    'ORG_USER': [
        'view_client',
        'view_user',
        'view_order',
        'add_order',
    ],

    'ORG_ADMIN': [
        'view_client',
        'change_client',
        'view_user',
        'add_user',
        'change_user',
        'delete_user',
        'view_order',
        'add_order',
    ],

    'STAFF_USER': [
        'view_client',
        'add_client',
        'change_client',
        'view_all_clients',
        'view_user',
        'add_user',
        'change_user',
        'delete_user',
        'view_all_users',
        'view_order',
        'add_order',
        'change_order',
        'delete_order',
        'view_all_orders',
    ],
}


def init_group(group_name):
    perms_list = groups[group_name]
    group = Group(name=group_name)
    group.save()
    perms = Permission.objects.filter(codename__in=perms_list).values_list('id', flat=True)
    group.permissions.add(*perms)
    return group


def get_or_init(group_name):
    if Group.objects.filter(name=group_name).exists():
        return Group.objects.get(name=group_name)
    else:
        return init_group(group_name)
