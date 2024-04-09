from django.contrib.auth.models import Group, Permission


groups = {
    'client_simple': [
        'view_client',
        'view_user',
        'view_order',
        'add_order',
    ],

    'client_advanced': [
        'view_client',
        'view_user',
        'view_order',
        'add_order',

        'add_user',
        'change_user',
        'delete_user',
    ],

    'auditor_simple': [
        'view_auditor',
        'view_user',
        'view_order',
    ],

    'auditor_advanced': [
        'view_auditor',
        'view_user',
        'view_order',

        'add_user',
        'change_user',
        'delete_user',
    ],

    'contractor_simple': [
        'view_contractor',
        'view_user',
        'view_order',
    ],

    'contractor_advanced': [
        'view_contractor',
        'view_user',
        'view_order',

        'add_user',
        'change_user',
        'delete_user',
    ],

    'manager': [
        'view_client',
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
        'view_contractor',
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
