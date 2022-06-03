import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


def inn_validator(value):

    if len(str(value)) != 10:
        raise ValidationError(
            _('ИНН должен состоять из 10 цифр'),
            params={'value': value},
        )


class Organisation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inn = models.BigIntegerField(db_index=True, verbose_name=_('ИНН'), validators=[inn_validator])
    kpp = models.BigIntegerField(db_index=True, verbose_name=_('КПП'), blank=True, null=True)
    short_name = models.CharField(max_length=255, verbose_name=_('Краткое наименование'))
    legal_address = models.CharField(max_length=255, verbose_name=_('Юр. адрес'))
    fact_address = models.CharField(max_length=255, verbose_name=_('Факт. адрес'))

    def __str__(self):
        return self.short_name

    class Meta:
        abstract = True
        verbose_name = 'организация'
        verbose_name_plural = 'организации'


class Client(Organisation):
    num_prefix = models.CharField(max_length=5, verbose_name=_('Префикс номера поручения'))
    contract = models.CharField(max_length=255, verbose_name='№ договора')
    contract_sign_date = models.DateField(verbose_name='Дата заключения договора')
    contract_expiration_date = models.DateField(verbose_name='Дата окончания действия договора')

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'
        permissions = [
            ('view_all_clients', 'Can view all clients')
        ]


class Counterparty(Organisation):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='counterparties')

    class Meta:
        verbose_name = 'контрагент клиента'
        verbose_name_plural = 'контрагенты клиента'


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

    class Meta:
        verbose_name = 'контакт'
        verbose_name_plural = 'контакты'


class Contractor(Organisation):
    contract = models.CharField(max_length=255, verbose_name='№ договора')
    contract_sign_date = models.DateField(verbose_name='Дата заключения договора')
    contract_expiration_date = models.DateField(verbose_name='Дата окончания действия договора')

    class Meta:
        verbose_name = 'подрядчик'
        verbose_name_plural = 'подрядчики'


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
