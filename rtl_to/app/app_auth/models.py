import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


def inn_validator(value: str):
    """
    Валидатор ИНН
    :param value: проверяемое значение
    :return: None или ошибка
    """
    allowed_inn_lengths = [10, 12]
    if not value.isnumeric() or len(value) not in allowed_inn_lengths:
        raise ValidationError(
            _('ИНН должен состоять из 10 цифр!'),
            params={'value': value},
        )


class Organisation(models.Model):
    """
    Абстрактная модель организации
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inn = models.CharField(db_index=True, verbose_name=_('ИНН'), validators=[inn_validator], blank=True, null=True, max_length=12)
    kpp = models.CharField(db_index=True, verbose_name=_('КПП'), blank=True, null=True, max_length=12)
    ogrn = models.CharField(db_index=True, verbose_name=_('ОГРН'), blank=True, null=True, max_length=15)
    short_name = models.CharField(max_length=255, verbose_name=_('Краткое наименование'))
    full_name = models.CharField(max_length=255, verbose_name=_('Полное наименование'))
    legal_address = models.CharField(max_length=255, verbose_name=_('Юр. адрес'))
    fact_address = models.CharField(max_length=255, verbose_name=_('Факт. адрес'))
    email = models.CharField(max_length=50, verbose_name=_('Почта для рассылки'), blank=True, null=True)

    def __str__(self):
        return self.short_name

    class Meta:
        abstract = True
        verbose_name = 'организация'
        verbose_name_plural = 'организации'


class Contract(models.Model):
    """
    Абстрактная модель договора
    """
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    number = models.CharField(max_length=255, verbose_name='№ договора')
    sign_date = models.DateField(verbose_name='Дата заключения договора')
    expiration_date = models.DateField(verbose_name='Дата окончания действия договора')

    def __str__(self):
        return f'{self.number} от {self.sign_date.strftime("%d.%m.%Y")}'

    class Meta:
        abstract = True
        verbose_name = 'договор'
        verbose_name_plural = 'договоры'


class Client(Organisation):
    """
    Организация-заказчик
    """
    num_prefix = models.CharField(max_length=5, verbose_name=_('Префикс номера поручения'), blank=True, null=True)

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'
        permissions = [
            ('view_all_clients', 'Can view all clients')
        ]


class ClientContract(Contract):
    """
    Договор с заказчиком
    """
    client = models.ForeignKey(Client, related_name='contracts', on_delete=models.CASCADE, verbose_name='Заказчик')

    class Meta:
        verbose_name = 'договор с клиентом'
        verbose_name_plural = 'договоры с клиентами'


class Auditor(Organisation):
    """
    Аудитор
    """
    controlled_clients = models.ManyToManyField(Client, verbose_name='Поднадзорные организации', related_name='auditors')

    class Meta:
        verbose_name = 'аудитор'
        verbose_name_plural = 'аудиторы'


class Contractor(Organisation):
    """
    Подрядчик
    """
    head = models.CharField(max_length=255, verbose_name='Руководитель', blank=True, null=True)
    accountant = models.CharField(max_length=255, verbose_name='Бухгалтер', blank=True, null=True)

    class Meta:
        verbose_name = 'подрядчик'
        verbose_name_plural = 'подрядчики'


class ContractorContract(Contract):
    """
    Договор с подрядчиком
    """
    bank = models.CharField(max_length=255, blank=True, null=True, verbose_name='Банк')
    bik = models.CharField(max_length=255, blank=True, null=True, verbose_name='БИК банка')
    pay_acc = models.CharField(max_length=255, blank=True, null=True, verbose_name='р/с')
    corr_acc = models.CharField(max_length=255, blank=True, null=True, verbose_name='к/с')
    contractor = models.ForeignKey(Contractor, related_name='contracts', on_delete=models.CASCADE,
                                   verbose_name='Подрядчик')

    class Meta:
        verbose_name = 'договор с подрядчиком'
        verbose_name_plural = 'договоры с подрядчиками'


class Counterparty(Organisation):
    """
    Контрагент (отправитель/получатель)
    """
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, related_name='counterparties', null=True, blank=True)
    contractor = models.ForeignKey(Contractor, on_delete=models.SET_NULL, related_name='counterparties', null=True,
                                   blank=True)
    admin = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name = 'контрагент клиента'
        verbose_name_plural = 'контрагенты клиента'


class Contact(models.Model):
    """
    Контактное лицо
    """
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
    """
    Пользователь приложения
    """
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
    """
    Шаблон отчета
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name='Имя отчета')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports', verbose_name='Пользователь')

    _order_fields = models.TextField(verbose_name='Поля входящего поручения')
    _transit_fields = models.TextField(verbose_name='Поля перевозки')
    _ext_order_fields = models.TextField(verbose_name='Поля исходящего поручения')
    _segment_fields = models.TextField(verbose_name='Поля плеча перевозки')

    def __str__(self):
        return self.name

    def get_order_fields_list(self):
        """
        getter набора полей входящего поручения
        :return: список полей входящего поручения
        """
        return list(self._order_fields.split(','))

    def set_order_fields_list(self, value: list):
        """
        setter набора полей входящего поручения
        :param value: список полей входящего поручения
        """
        self._order_fields = ','.join(value)

    def get_transit_fields_list(self):
        """
        getter набора полей перевозки
        :return: список полей перевозки
        """
        return list(self._transit_fields.split(','))

    def set_transit_fields_list(self, value):
        """
        setter набора полей перевозки
        :return: список полей перевозки
        """
        self._transit_fields = ','.join(value)

    def get_ext_order_fields_list(self):
        """
        getter набора полей исходящего поручения
        :return: список полей исходящего поручения
        """
        return list(self._ext_order_fields.split(','))

    def set_ext_order_fields_list(self, value):
        """
        setter набора полей исходящего поручения
        :return: список полей исходящего поручения
        """
        self._ext_order_fields = ','.join(value)

    def get_segment_fields_list(self):
        """
        getter набора полей плеча
        :return: список полей плеча
        """
        return list(self._segment_fields.split(','))

    def set_segment_fields_list(self, value):
        """
        setter набора полей плеча
        :return: список полей плеча
        """
        self._segment_fields = ','.join(value)

    order_fields = property(get_order_fields_list, set_order_fields_list)
    transit_fields = property(get_transit_fields_list, set_transit_fields_list)
    ext_order_fields = property(get_ext_order_fields_list, set_ext_order_fields_list)
    segment_fields = property(get_segment_fields_list, set_segment_fields_list)

