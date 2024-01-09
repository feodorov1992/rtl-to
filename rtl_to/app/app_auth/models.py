import datetime
import logging
import uuid
from typing import Union, Tuple, List

import requests
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from app_auth.tasks import contract_depletion_for_manager


logger = logging.getLogger(__name__)


CURRENCIES = (
    ('RUB', 'RUB'),
    ('USD', 'USD'),
    ('EUR', 'EUR'),
    ('GBP', 'GBP')
)


def get_currency_rate(from_curr: str, to_curr: str, rate_date: datetime.datetime = timezone.now()) -> float:
    """
    Функция для запроса курса валют у сервиса cbr-xml-daily.ru
    :param from_curr: Валюта, курс которой мы ищем
    :param to_curr: Валюта, в которой считается искомый курс
    :param rate_date: Дата курса
    :return: Отношения курсов указанных валют или 0 в случае ошибки
    """
    url = 'https://www.cbr-xml-daily.ru/daily_json.js'
    rates = requests.get(url).json()

    while datetime.datetime.fromisoformat(rates.get('Date', timezone.now())).date() > rate_date:
        # Перебираем даты, пока не найдем нужную. Сразу запросить сервис позволяет с косяками
        if rates.get('error') is not None:
            logger.error(rates.get('error'))
            return 0
        rates = requests.get('https:' + rates['PreviousURL']).json()

    if to_curr != 'RUB':
        to_curr_rate = rates['Valute'][to_curr]['Value']
    else:
        to_curr_rate = 1

    if from_curr != 'RUB':
        from_curr_rate = rates['Valute'][from_curr]['Value']
    else:
        from_curr_rate = 1
    return from_curr_rate / to_curr_rate


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


class CurrencyRate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(editable=False, verbose_name='Дата курса', default=timezone.now)
    EUR = models.FloatField(editable=False, verbose_name='EUR')
    USD = models.FloatField(editable=False, verbose_name='USD')
    GBP = models.FloatField(editable=False, verbose_name='GBP')
    INR = models.FloatField(editable=False, verbose_name='INR')

    @staticmethod
    def rates_url(date: datetime.date):
        return 'https://www.cbr-xml-daily.ru/archive/{year:0>4}/{month:0>2}/{day:0>2}/daily_json.js'.format(
            year=date.year,
            month=date.month,
            day=date.day
        )

    @property
    def RUB(self):
        return 1

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        date = self.date
        rates = requests.get(self.rates_url(date)).json()

        while rates.get('error') is not None:
            date -= datetime.timedelta(days=1)
            rates = requests.get(self.rates_url(date)).json()

        self.EUR = rates['Valute']['EUR']['Value']
        self.USD = rates['Valute']['USD']['Value']
        self.GBP = rates['Valute']['GBP']['Value']
        self.INR = rates['Valute']['INR']['Value']

        super(CurrencyRate, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return 'Курс валют на {day:0>2}.{month:0>2}.{year:0>4}'.format(
            day=self.date.day, month=self.date.month, year=self.date.year
        )

    class Meta:
        verbose_name = 'курс валют'
        verbose_name_plural = 'курсы валют'
        ordering = ['date']


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
    name = models.CharField(max_length=255, verbose_name='Наименование договора', default='')
    number = models.CharField(max_length=255, verbose_name='№ договора')
    sign_date = models.DateField(verbose_name='Дата заключения договора')
    start_date = models.DateField(verbose_name='Дата начала действия договора')
    expiration_date = models.DateField(verbose_name='Дата окончания действия договора')
    currency = models.CharField(max_length=3, verbose_name='Валюта договора', default='RUB', choices=CURRENCIES)
    full_sum = models.FloatField(verbose_name='Сумма договора', default=0)
    initial_sum = models.FloatField(verbose_name='Начальный остаток', default=0)
    current_sum = models.FloatField(verbose_name='Текущий остаток', default=0)
    add_agreement_number = models.CharField(max_length=255, verbose_name='№ доп. соглашения', blank=True, null=True)
    add_agreement_date = models.DateField(verbose_name='Дата доп. соглашения', blank=True, null=True)

    def __str__(self):
        output = f'{self.name} №{self.number} от {self.sign_date.strftime("%d.%m.%Y")}'
        if self.add_agreement_number and self.add_agreement_date:
            output += f' ДС №{self.add_agreement_number} от {self.add_agreement_date.strftime("%d.%m.%Y")}'
        return output

    class Meta:
        abstract = True
        verbose_name = 'договор'
        verbose_name_plural = 'договоры'


class OrderLabelManager:
    __FORMS = {'default': {
        'nominative': ('поручение', 'поручения'),
        'genitive': ('поручения', 'поручений'),
        'dative': ('поручению', 'поручениям'),
        'accusative': ('поручение', 'поручения'),
        'instrumental': ('поручением', 'поручениями'),
        'prepositional': ('поручении', 'поручениях'),
        'abbr': ('ПЭ', 'ПЭ'),
    }}

    def __init__(self, label: str = None):
        if label is not None and label in self.__FORMS:
            self.__label = label
        else:
            self.__label = self.__init_label()
        self.__case = self.__init_case()
        self.__plurality = False

    def __init_label(self):
        return list(self.__FORMS.keys())[0]

    def __init_case(self):
        return list(self.__FORMS[self.__label].keys())[0]

    def is_default(self):
        return self.__label == self.__init_label()

    @classmethod
    def add_form(cls, label: str,
                 nominative: Union[Tuple[str, str], List[str]],
                 genitive: Union[Tuple[str, str], List[str]],
                 dative: Union[Tuple[str, str], List[str]],
                 accusative: Union[Tuple[str, str], List[str]],
                 instrumental: Union[Tuple[str, str], List[str]],
                 prepositional: Union[Tuple[str, str], List[str]],
                 abbr: Union[Tuple[str, str], List[str]]):
        args = locals().copy()
        args.pop('cls')
        args.pop('label')
        cls.__FORMS[label] = args

    @classmethod
    def choices(cls):
        result = list()
        for label, values in cls.__FORMS.items():
            result.append((label, values['abbr'][0]))
        return tuple(result)

    def __getattribute__(self, item):
        if '__' in item:
            return super(OrderLabelManager, self).__getattribute__(item)
        
        if item in self.__FORMS:
            self.__label = item
            self.__case = self.__init_case()
            self.__plurality = False
        elif item in self.__FORMS[self.__label]:
            self.__case = item
            self.__plurality = False
        elif item == 'plural':
            self.__plurality = True
        else:
            default_value = super(OrderLabelManager, self).__getattribute__(item)
            if callable(default_value):
                return default_value

        return self

    def __str__(self):
        return self.__FORMS[self.__label][self.__case][int(self.__plurality)]


OrderLabelManager.add_form('order', ('заказ', 'заказы'), ('заказа', 'заказов'), ('заказу', 'заказам'),
                           ('заказ', 'заказы'), ('заказом', 'заказами'), ('заказе', 'заказах'), ('Заказ', 'Заказы'))
OrderLabelManager.add_form('claim', ('заявка', 'заявки'), ('заявки', 'заявок'), ('заявке', 'заявкам'),
                           ('заявку', 'заявки'), ('заявкой', 'заявками'), ('заявке', 'заявках'), ('Заявка', 'Заявки'))

ORDER_LABEL_CHOICES = OrderLabelManager.choices()


class Client(Organisation):
    """
    Организация-заказчик
    """
    num_prefix = models.CharField(max_length=5, verbose_name=_('Префикс номера поручения'), blank=True, null=True)
    order_label = models.CharField(max_length=20, verbose_name='Название осн. вх. документа',
                                   choices=ORDER_LABEL_CHOICES, default=ORDER_LABEL_CHOICES[0][0])
    order_template = models.FileField(blank=True, null=True, verbose_name='Шаблон ПЭ')
    receipt_template = models.FileField(blank=True, null=True, verbose_name='Шаблон ЭР')

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
    order_label = models.CharField(max_length=20, verbose_name='Название осн. вх. документа',
                                   choices=ORDER_LABEL_CHOICES, default=ORDER_LABEL_CHOICES[0][0])
    order_template = models.FileField(blank=True, null=True, verbose_name='Шаблон ПЭ')
    receipt_template = models.FileField(blank=True, null=True, verbose_name='Шаблон ЭР')

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
    order_label = models.CharField(max_length=20, verbose_name='Название осн. вх. документа',
                                   choices=ORDER_LABEL_CHOICES, default=ORDER_LABEL_CHOICES[0][0])
    order_template = models.FileField(blank=True, null=True, verbose_name='Шаблон ПЭ')
    receipt_template = models.FileField(blank=True, null=True, verbose_name='Шаблон ЭР')

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
    order_label = models.CharField(max_length=20, verbose_name='Название осн. вх. документа',
                                   choices=ORDER_LABEL_CHOICES, default=ORDER_LABEL_CHOICES[0][0])
    order_template = models.FileField(blank=True, null=True, verbose_name='Шаблон ПЭ')
    receipt_template = models.FileField(blank=True, null=True, verbose_name='Шаблон ЭР')

    @staticmethod
    def get_currency_rate(currency, base_currency, date):
        if currency == base_currency:
            return 1
        rate, _ = CurrencyRate.objects.get_or_create(date=date)
        curr_rate = getattr(rate, currency)
        base_rate = getattr(rate, base_currency)
        return curr_rate / base_rate

    def sum_rated_values(self, queryset):
        result = 0
        for price_dict in queryset:
            date = price_dict['bill_date'] if price_dict['bill_date'] is not None else timezone.now().date()
            price_rate = self.get_currency_rate(price_dict['currency'], self.currency, date)
            insurance_rate = self.get_currency_rate(price_dict['insurance_currency'], self.currency, date)
            price = price_rate * price_dict['price'] + insurance_rate * price_dict['insurance']
            result += round(price, 2)
        return result

    def update_current_sum(self):
        freeze_for = self.extorder_set.filter(price_carrier=0) \
            .values('currency', 'bill_date', 'insurance_currency').annotate(
            price=Sum('approx_price'), insurance=Sum('insurance_value')
        )
        spend_for = self.extorder_set.exclude(price_carrier=0) \
            .values('currency', 'bill_date', 'insurance_currency').annotate(
            price=Sum('price_carrier'), insurance=Sum('insurance_value')
        )

        self.current_sum = self.initial_sum - self.sum_rated_values(freeze_for) - self.sum_rated_values(spend_for)
        if self.current_sum <= self.full_sum * 0.15:
            contract_depletion_for_manager.delay(self.pk)
        self.save()

    def check_sum(self, value, currency, date):
        if not date:
            date = timezone.now().date()
        rate, _ = CurrencyRate.objects.get_or_create(date=date)
        curr_rate = getattr(rate, currency)
        base_rate = getattr(rate, self.currency)
        rate = curr_rate / base_rate
        price = rate * value
        return price <= self.current_sum

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
            return f'{self.last_name} {self.first_name}'
        else:
            return f'{self.last_name} {self.first_name} {self.second_name}'

    def full_output(self):
        out_list = [str(self)]
        if self.phone:
            out_list.append(f'тел. {self.phone}')
        if self.email:
            out_list.append(f'email {self.email}')
        return ', '.join(out_list)

    class Meta:
        verbose_name = 'контакт'
        verbose_name_plural = 'контакты'
        ordering = ['last_name', 'first_name']


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
    boss = models.BooleanField(verbose_name='Руководящее лицо', default=False)

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
        ordering = ['last_name', 'first_name']


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
