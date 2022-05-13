import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class Organisation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inn = models.IntegerField(db_index=True)
    kpp = models.IntegerField(db_index=True)
    short_name = models.CharField(max_length=255, verbose_name=_('Краткое наименование'))
    legal_address = models.CharField(max_length=255)
    fact_address = models.CharField(max_length=255)

    def __str__(self):
        return self.short_name

    class Meta:
        abstract = True
        verbose_name = _('organisation')
        verbose_name_plural = _('organisations')


class Client(Organisation):
    num_prefix = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        verbose_name = _('client')
        verbose_name_plural = _('clients')
        permissions = [
            ('view_all_clients', 'Can view all clients')
        ]


class Counterparty(Organisation):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='counterparties')

    class Meta:
        verbose_name = _('client counterparty')
        verbose_name_plural = _('client counterparties')


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    last_name = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('фамилия'))
    first_name = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('имя'))
    second_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('отчество'))
    email = models.EmailField(blank=True, null=True, verbose_name=_('email'))
    phone = models.CharField(max_length=30, blank=False, null=False)
    cp = models.ForeignKey(Counterparty, on_delete=models.CASCADE)

    def __str__(self):
        if not self.second_name:
            return f'{self.first_name} {self.last_name}'
        else:
            return f'{self.last_name} {self.first_name} {self.second_name}'


class Contractor(Organisation):
    class Meta:
        verbose_name = _('contractor')
        verbose_name_plural = _('contractors')


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    last_name = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('фамилия'))
    first_name = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('имя'))
    second_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('отчество'))
    email = models.EmailField(blank=False, null=False, verbose_name=_('email'), unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name=_('организация'), related_name='users',
                               null=True, blank=True)

    def __str__(self):
        if not self.second_name:
            return f'{self.first_name} {self.last_name}'
        else:
            return f'{self.last_name} {self.first_name} {self.second_name}'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        permissions = [
            ('view_all_users', 'Can view all users')
        ]
