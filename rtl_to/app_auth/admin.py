from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from app_auth.models import User, Organisation


@admin.register(User)
class AdminUser(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'last_name', 'first_name', 'second_name', 'email', 'password')}),
        (_('Affiliation'), {'fields': ('org', 'is_org_admin')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    ordering = ('last_name',)
    list_display = ('email', 'last_name', 'first_name', 'second_name', 'org', 'is_org_admin')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'is_org_admin')
    search_fields = ('username', 'first_name', 'last_name', 'email')


@admin.register(Organisation)
class OrganisationAdmin(ModelAdmin):
    pass
