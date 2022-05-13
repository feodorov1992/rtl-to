from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from app_auth.models import User, Client, Counterparty, Contact, Contractor


@admin.register(User)
class AdminUser(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'last_name', 'first_name', 'second_name', 'email', 'password')}),
        (_('Affiliation'), {'fields': ('client',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    ordering = ('last_name',)
    list_display = ('email', 'last_name', 'first_name', 'second_name', 'client')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')


@admin.register(Client)
class ClientAdmin(ModelAdmin):
    pass


@admin.register(Counterparty)
class CounterpartyAdmin(ModelAdmin):
    pass


@admin.register(Contact)
class ContactAdmin(ModelAdmin):
    pass


@admin.register(Contractor)
class ContractorAdmin(ModelAdmin):
    pass
