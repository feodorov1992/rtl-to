import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


def inn_validator(value: str):
    allowed_inn_lengths = [10, 12]
    if not value.isnumeric() or len(value) not in allowed_inn_lengths:
        raise ValidationError(
            _('ИНН должен состоять из 10 цифр!'),
            params={'value': value},
        )


class Organisation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inn = models.CharField(db_index=True, verbose_name=_('ИНН'), validators=[inn_validator], blank=True, null=True, max_length=12)
    kpp = models.CharField(db_index=True, verbose_name=_('КПП'), blank=True, null=True, max_length=12)
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


class Auditor(Organisation):
    controlled_clients = models.ManyToManyField(Client, verbose_name='Поднадзорные организации', related_name='auditors')

    class Meta:
        verbose_name = 'аудитор'
        verbose_name_plural = 'аудиторы'


class Contractor(Organisation):
    contract = models.CharField(max_length=255, verbose_name='№ договора')
    contract_sign_date = models.DateField(verbose_name='Дата заключения договора')
    contract_expiration_date = models.DateField(verbose_name='Дата окончания действия договора')

    class Meta:
        verbose_name = 'подрядчик'
        verbose_name_plural = 'подрядчики'


class Counterparty(Organisation):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='counterparties', blank=True, null=True)
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE, related_name='counterparties', blank=True, null=True)

    class Meta:
        verbose_name = 'контрагент клиента'
        verbose_name_plural = 'контрагенты клиента'


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    last_name = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('фамилия'))
    first_name = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('имя'))
    second_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('отчество'))
    email = models.EmailField(blank=True, null=True, verbose_name=_('email'))
    phone = models.CharField(max_length=30, blank=False, null=False, verbose_name=_('Тел.'))
    cp = models.ManyToManyField(Counterparty, verbose_name='Контрагенты', related_name='contacts')

    def __str__(self):
        if not self.second_name:
            return f'{self.first_name} {self.last_name}'
        else:
            return f'{self.last_name} {self.first_name} {self.second_name}'

    class Meta:
        verbose_name = 'контакт'
        verbose_name_plural = 'контакты'


class User(AbstractUser):

    TYPES = [
        ('manager', 'Менеджер'),
        ('client_simple', 'Заказчик (обычный)'),
        ('client_advanced', 'Заказчик (расширенный)'),
        ('auditor_simple', 'Аудитор (обычный)'),
        ('auditor_advanced', 'Аудитор (расширенный)'),
        ('contractor_simple', 'Подрядчик (обычный)'),
        ('contractor_advanced', 'Подрядчик (расширенный)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    last_name = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('фамилия'))
    first_name = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('имя'))
    second_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('отчество'))
    email = models.EmailField(blank=False, null=False, verbose_name=_('email'), unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name=_('заказчик'), related_name='users',
                               null=True, blank=True)
    auditor = models.ForeignKey(Auditor, on_delete=models.CASCADE, verbose_name=_('контроллирующий орган'),
                                related_name='agents', null=True, blank=True)
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE, verbose_name=_('подрядчик'), related_name='users',
                                   null=True, blank=True)
    user_type = models.CharField(max_length=25, choices=TYPES, verbose_name=_('тип пользователя'),
                                 default='manager')

    def __str__(self):
        if not self.second_name:
            return f'{self.last_name} {self.first_name}'
        else:
            return f'{self.last_name} {self.first_name} {self.second_name}'

    def save(self, *args, **kwargs):
        fields_to_check = ['client', 'auditor', 'contractor']
        if '_' in self.user_type:
            key, _ = self.user_type.split('_')
            fields_to_check = [i for i in fields_to_check if i != key]
        for field_name in fields_to_check:
            self.__setattr__(field_name, None)

        super(User, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        permissions = [
            ('view_all_users', 'Can view all users')
        ]


class ReportParams(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name='Имя отчета')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports', verbose_name='Пользователь')

    _order_fields = models.TextField(verbose_name='Поля поручения')
    _transit_fields = models.TextField(verbose_name='Поля перевозки')
    _segment_fields = models.TextField(verbose_name='Поля плеча перевозки')

    merge_segments = models.BooleanField(verbose_name='Группировать по перевозчику', default=False)

    def __str__(self):
        return self.name

    def get_order_fields_list(self):
        return list(self._order_fields.split(','))

    def set_order_fields_list(self, value):
        self._order_fields = ','.join(value)

    def get_transit_fields_list(self):
        return list(self._transit_fields.split(','))

    def set_transit_fields_list(self, value):
        self._transit_fields = ','.join(value)

    def get_segment_fields_list(self):
        return list(self._segment_fields.split(','))

    def set_segment_fields_list(self, value):
        self._segment_fields = ','.join(value)

    order_fields = property(get_order_fields_list, set_order_fields_list)
    transit_fields = property(get_transit_fields_list, set_transit_fields_list)
    segment_fields = property(get_segment_fields_list, set_segment_fields_list)

