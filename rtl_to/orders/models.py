import os
import uuid

import requests
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from app_auth.models import User, Client, Contractor
from rtl_to import settings
from django.utils.translation import gettext_lazy as _

CURRENCIES = (
    ('RUB', 'RUB'),
    ('USD', 'USD'),
    ('EUR', 'EUR'),
    ('GBP', 'GBP')
)

TAXES = [
    (None, 'Без НДС'),
    (0, '0%'),
    (20, '20%')
]

ORDER_STATUS_LABELS = [
    ('new', 'Новое'),
    ('pre_process', 'Принято в работу'),
    ('rejected', 'Аннулировано'),
    ('in_progress', 'На исполнении'),
    ('delivered', 'Выполнено'),
    ('bargain', 'Согласование ставок'),
    ('completed', 'Завершено'),
]

TRANSIT_STATUS_LABELS = [
    ('new', 'Новая'),
    ('carrier_select', 'Первичная обработка'),
    ('pickup', 'Забор груза'),
    ('in_progress', 'В пути'),
    ('temporary_storage', 'Груз на СВХ (ТО)'),
    ('transit_storage', 'Груз на транзитном складе'),
    ('completed', 'Доставлено'),
    ('rejected', 'Аннулировано')
]

SEGMENT_STATUS_LABELS = [
    ('waiting', 'В ожидании'),
    ('in_progress', 'В пути'),
    ('completed', 'Выполнено'),
    ('rejected', 'Аннулировано')
]


def get_currency_rate(from_curr: str, to_curr: str):
    url = 'https://www.cbr-xml-daily.ru/daily_json.js'
    rates = requests.get(url).json()

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
    if not value.isnumeric() or len(value) != 10:
        raise ValidationError(
            _('ИНН должен состоять из 10 цифр!'),
            params={'value': value},
        )


class RecalcMixin:

    def update_related(self, parent_field, *fields, related_name: str = None):
        if not related_name:
            related_name = self.__class__.__name__.lower() + 's'

        related = self.__getattribute__(parent_field.lower())
        related.collect(related_name, *fields)

    def collect(self, related_name, *fields):
        raise NotImplementedError

    @staticmethod
    def get_sub_queryset(queryset, sub_model_rel_name, filters: dict = None):
        result = queryset.first().__getattribute__(sub_model_rel_name).none()
        querysets = list()
        for item in queryset:
            querysets.append(item.__getattribute__(sub_model_rel_name).all())
        result = result.union(*querysets)
        if filters:
            return result.filter(**filters)
        return result

    @staticmethod
    def list_from_queryset(queryset, field_name, remove_duplicates: bool = False, callables: bool = False):
        if callables:
            result = [i.__getattribute__(field_name)() for i in queryset if i.__getattribute__(field_name)()]
        else:
            result = [i.__getattribute__(field_name) for i in queryset if i.__getattribute__(field_name)]

        if remove_duplicates:
            new_result = list()
            for t, item in enumerate(result):
                if t == 0 or (t > 0 and item != result[t - 1]):
                    new_result.append(item)
            return new_result
        return result

    def equal_to_min(self, queryset, source_field_name: str):
        return min(self.list_from_queryset(queryset, source_field_name), default=None)

    def equal_to_max(self, queryset, source_field_name: str):
        return max(self.list_from_queryset(queryset, source_field_name), default=None)

    def sum_values(self, queryset, source_field_name: str):
        return sum(self.list_from_queryset(queryset, source_field_name))

    def join_values(
            self, queryset, delimiter, source_field_name: str, remove_duplicates: bool = False, callables: bool = False
    ):
        return delimiter.join(self.list_from_queryset(queryset, source_field_name, remove_duplicates, callables))

    @staticmethod
    def sum_multicurrency_values(queryset, source_value_field_name, source_currency_field_name: str):

        result = dict()
        for obj in queryset:
            value = obj.__getattribute__(source_value_field_name)
            currency = obj.__getattribute__(source_currency_field_name)
            if currency not in result:
                result[currency] = 0
            result[currency] += value
        result = {key: value for key, value in result.items() if value != 0}
        return '; '.join(['{:,} {}'.format(price, currency).replace(',', ' ').replace('.', ',')
                          for currency, price in result.items()])


class Order(models.Model, RecalcMixin):
    TYPES = [
        ('international', 'Международная'),
        ('internal', 'Внутрироссийская'),
    ]

    INSURANCE_COEFFS = (
        (1, '100%'),
        (1.1, '110%')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_number = models.CharField(max_length=50, blank=True, null=False, verbose_name='Номер заказчика')
    inner_number = models.CharField(max_length=50, blank=True, null=False, verbose_name='Внутренний номер')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    last_update = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    order_date = models.DateField(blank=True, null=True, verbose_name='Дата поручения')
    manager = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                verbose_name='Менеджер', related_name='my_orders_manager')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Заказчик', related_name='orders')
    contract = models.CharField(max_length=255, verbose_name='Договор', blank=True, null=True)
    client_employee = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                        verbose_name='Сотрудник заказчика', related_name='my_orders_client')
    type = models.CharField(choices=TYPES, max_length=50, db_index=True, default='internal',
                            verbose_name='Вид поручения')
    status = models.CharField(choices=ORDER_STATUS_LABELS, max_length=50, default=ORDER_STATUS_LABELS[0][0],
                              db_index=True, verbose_name='Статус поручения', null=True, blank=True)
    price = models.CharField(max_length=255, verbose_name='Ставка', blank=True, null=True)
    price_carrier = models.CharField(max_length=255, verbose_name='Закупочная цена поручения', blank=True, null=True)
    taxes = models.IntegerField(verbose_name='НДС', blank=True, null=True, default=20, choices=TAXES)
    from_addr_forlist = models.CharField(max_length=255, verbose_name='Адрес забора груза', editable=False)
    to_addr_forlist = models.CharField(max_length=255, verbose_name='Адрес доставки', editable=False)
    comment = models.TextField(verbose_name='Примечания', null=True, blank=True)
    weight = models.FloatField(verbose_name='Вес брутто', null=True, blank=True)
    quantity = models.IntegerField(verbose_name='Количество мест', null=True, blank=True)
    from_date_plan = models.DateField(verbose_name='Плановая дата забора груза', blank=True, null=True)
    from_date_fact = models.DateField(verbose_name='Фактическая дата забора груза', blank=True, null=True)
    to_date_plan = models.DateField(verbose_name='Плановая дата доставки', blank=True, null=True)
    to_date_fact = models.DateField(verbose_name='Фактическая дата доставки', blank=True, null=True)
    insurance = models.BooleanField(default=False, verbose_name='Страхование')
    value = models.CharField(verbose_name='Заявленная стоимость', max_length=255, blank=True, null=True)
    sum_insured_coeff = models.FloatField(verbose_name='Коэффициент страховой суммы', choices=INSURANCE_COEFFS,
                                          default=INSURANCE_COEFFS[0][0], blank=True)
    insurance_currency = models.CharField(max_length=3, choices=CURRENCIES, default='RUB',
                                          verbose_name='Валюта страхования', blank=True)
    currency_rate = models.FloatField(verbose_name='Курс страховой валюты', default=0, blank=True, null=True)

    def __str__(self):
        return f'Поручение №{self.client_number} от {self.order_date.strftime("%d.%m.%Y")}'

    def collect(self, related_name, *fields):
        queryset = self.__getattribute__(related_name).all().order_by('created_at')

        if 'weight' in fields or 'DELETE' in fields:
            self.weight = self.sum_values(queryset, 'weight')
        if 'quantity' in fields or 'DELETE' in fields:
            self.quantity = self.sum_values(queryset, 'quantity')
        if 'from_date_plan' in fields or 'DELETE' in fields:
            self.from_date_plan = self.equal_to_min(queryset, 'from_date_plan')
        if 'from_date_fact' in fields or 'DELETE' in fields:
            self.from_date_fact = self.equal_to_min(queryset, 'from_date_fact')
        if 'to_date_plan' in fields or 'DELETE' in fields:
            self.to_date_plan = self.equal_to_max(queryset, 'to_date_plan')
        if 'to_date_fact' in fields or 'DELETE' in fields:
            self.to_date_fact = self.equal_to_max(queryset, 'to_date_fact')
        if 'value' in fields or 'DELETE' in fields:
            self.value = self.sum_values(queryset, 'value')
            if self.insurance:
                self.update_transits_insurance(queryset, self.value, queryset.first().currency)
        if 'price' in fields or 'DELETE' in fields:
            self.price = self.sum_multicurrency_values(self.get_sub_queryset(queryset, 'segments'), 'price', 'currency')
        if 'price_carrier' in fields or 'DELETE' in fields:
            self.price_carrier = self.sum_multicurrency_values(self.get_sub_queryset(queryset, 'segments'),
                                                               'price_carrier', 'currency')
        if 'from_addr' in fields or 'DELETE' in fields:
            self.from_addr_forlist = self.make_address_for_list(queryset, 'from_addr')
        if 'to_addr' in fields or 'DELETE' in fields:
            self.to_addr_forlist = self.make_address_for_list(queryset, 'to_addr')

        self.save()

    def update_transits_insurance(self, queryset, value, currency):

        if currency == self.insurance_currency:
            rate = 1
        elif self.currency_rate:
            rate = self.currency_rate
        else:
            rate = get_currency_rate(currency, self.insurance_currency)
        self.currency_rate = rate
        sum_insured = value * self.sum_insured_coeff * rate
        insurance_premium = round(sum_insured * 0.00055, 2)
        for transit in queryset:
            transit.sum_insured = transit.value * self.sum_insured_coeff
            transit.insurance_premium = round(insurance_premium / self.transits.count(), 2)
            transit.save()
        return insurance_premium

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.contract = f'{self.client.contract} от {self.client.contract_sign_date.strftime("%d.%m.%Y")}'
        if not self.order_date:
            self.order_date = self.created_at

        super(Order, self).save(force_insert, force_update, using, update_fields)

        if not self.inner_number and not self.client_number:
            self.inner_number = '{}-{:0>5}'.format(
                self.client.num_prefix.upper() if self.client else 'РТЛТО',
                self.client.orders.count() + 1 if self.client else Order.objects.count() + 1
            )
            self.client_number = self.inner_number
        elif self.inner_number and not self.client_number:
            self.client_number = self.inner_number
        elif not self.inner_number and self.client_number:
            self.inner_number = self.client_number

        if not self.history.exists() or self.history.last().status != self.status:
            OrderHistory.objects.create(order=self, status=self.status)

    @staticmethod
    def make_address_for_list(queryset, field_name='from_addr'):
        diff_addr = list({i.__getattribute__(field_name) for i in queryset})
        if len(diff_addr) > 1:
            return '<ul>\n\t<li>{}\t</li>\n</ul>'.format('</li>\n\t<li>'.join(diff_addr))
        else:
            return ''.join(diff_addr)

    def get_public_docs(self):
        return self.docs.filter(public=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'поручение'
        verbose_name_plural = 'поручения'
        permissions = [
            ('view_all_orders', 'Can view all orders')
        ]


class ExtraService(models.Model):
    machine_name = models.CharField(max_length=100, unique=True)
    human_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.human_name

    class Meta:
        verbose_name = 'доп. услуга'
        verbose_name_plural = 'доп. услуги'


class Transit(models.Model, RecalcMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sub_number = models.CharField(max_length=255, db_index=True, default='', verbose_name='Субномер', blank=True)
    api_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=True, blank=True)
    last_update = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transits', verbose_name='Поручение')
    volume = models.FloatField(verbose_name='Объем', default=0, blank=True, null=True)
    weight = models.FloatField(verbose_name='Вес брутто', default=0, blank=True, null=True)
    # weight_payed = models.FloatField(verbose_name='Оплачиваемый вес', default=0, blank=True, null=True)
    quantity = models.IntegerField(verbose_name='Количество мест', default=0, blank=True, null=True)
    from_addr = models.CharField(max_length=255, verbose_name='Адрес забора груза')
    from_org = models.CharField(max_length=255, verbose_name='Отправитель')
    from_inn = models.CharField(max_length=15, validators=[inn_validator], verbose_name='ИНН отправителя', blank=True,
                                null=True)
    from_legal_addr = models.CharField(max_length=255, verbose_name='Юр. адрес')
    from_contact_name = models.CharField(max_length=255, verbose_name='Контактное лицо')
    from_contact_phone = models.CharField(max_length=255, verbose_name='Телефон')
    from_contact_email = models.CharField(max_length=255, verbose_name='email')
    from_date_plan = models.DateField(verbose_name='Плановая дата забора груза', blank=True, null=True)
    from_date_fact = models.DateField(verbose_name='Фактическая дата забора груза', blank=True, null=True)
    to_addr = models.CharField(max_length=255, verbose_name='Адрес доставки')
    to_org = models.CharField(max_length=255, verbose_name='Получатель')
    to_inn = models.CharField(max_length=15, validators=[inn_validator], verbose_name='ИНН получателя', blank=True,
                              null=True)
    to_legal_addr = models.CharField(max_length=255, verbose_name='Юр. адрес')
    to_contact_name = models.CharField(max_length=255, verbose_name='Контактное лицо')
    to_contact_phone = models.CharField(max_length=255, verbose_name='Телефон')
    to_contact_email = models.CharField(max_length=255, verbose_name='email')
    to_date_plan = models.DateField(verbose_name='Плановая дата доставки', blank=True, null=True)
    to_date_fact = models.DateField(verbose_name='Фактическая дата доставки', blank=True, null=True)
    type = models.CharField(max_length=255, db_index=True, blank=True, null=True, verbose_name='Вид перевозки')
    price = models.CharField(max_length=255, verbose_name='Ставка', blank=True, null=True)
    price_carrier = models.CharField(max_length=255, verbose_name='Закупочная цена', blank=True, null=True)
    status = models.CharField(choices=TRANSIT_STATUS_LABELS, max_length=50, default=TRANSIT_STATUS_LABELS[0][0],
                              db_index=True,
                              verbose_name='Статус перевозки', blank=True, null=True)
    extra_services = models.ManyToManyField(ExtraService, blank=True, verbose_name='Доп. услуги')
    currency = models.CharField(max_length=3, choices=CURRENCIES, default='RUB', verbose_name='Валюта')
    value = models.FloatField(verbose_name='Заявленная стоимость', default=0, blank=True, null=True)

    sum_insured = models.FloatField(verbose_name='Страховая сумма', default=0, blank=True, null=True)
    insurance_premium = models.FloatField(verbose_name='Страховая премия', default=0, blank=True, null=True)

    def __str__(self):
        if self.order:
            return f'Перевозка №{self.order.client_number}/{self.sub_number}'
        return 'Новая перевозка'

    class Meta:
        verbose_name = 'перевозка'
        verbose_name_plural = 'перевозки'
        ordering = ['created_at']
        permissions = [
            ('view_all_transits', 'Can view all transits')
        ]

    def collect(self, related_name, *fields):

        pass_to_order = list()

        queryset = self.__getattribute__(related_name).all()
        print('\nDEBUG Transit.collect')
        print('related_name:', related_name)
        print('fields:', fields)
        print('queryset:', queryset)

        if related_name == 'cargos':
            if 'weight' in fields or 'DELETE' in fields:
                self.weight = sum([i.weight * i.quantity for i in queryset])
                pass_to_order.append('weight')
            if any([i in fields for i in ('length', 'width', 'height', 'quantity', 'DELETE')]):
                self.volume = sum([i.length * i.width * i.height * i.quantity for i in queryset]) / 1000000
            if 'quantity' in fields or 'DELETE' in fields:
                self.quantity = self.sum_values(queryset, 'quantity')
                pass_to_order.append('quantity')
        if related_name == 'segments':
            if 'type' in fields or 'DELETE' in fields:
                self.type = self.join_values(queryset, '-', 'get_type_display', True, True)
            if 'price' in fields or 'DELETE' in fields:
                self.price = self.sum_multicurrency_values(queryset, 'price', 'currency')
                pass_to_order.append('price')
            if 'price_carrier' in fields or 'DELETE' in fields:
                self.price_carrier = self.sum_multicurrency_values(queryset, 'price_carrier', 'currency')
                pass_to_order.append('price_carrier')
            if 'from_date_plan' in fields or 'DELETE' in fields:
                self.from_date_plan = self.equal_to_min(queryset, 'from_date_plan')
                pass_to_order.append('from_date_plan')
            if 'from_date_fact' in fields or 'DELETE' in fields:
                self.from_date_fact = self.equal_to_min(queryset, 'from_date_fact')
                pass_to_order.append('from_date_fact')
            if 'to_date_plan' in fields or 'DELETE' in fields:
                self.to_date_plan = self.equal_to_max(queryset, 'to_date_plan')
                pass_to_order.append('to_date_plan')
            if 'to_date_fact' in fields or 'DELETE' in fields:
                self.to_date_fact = self.equal_to_max(queryset, 'to_date_fact')
                pass_to_order.append('to_date_fact')
        print('pass_to_order:', pass_to_order)
        print('END DEBUG\n')
        self.save()

        if pass_to_order:
            self.update_related('order', *pass_to_order)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.sub_number:
            max_sub_number = max(
                [int(i.sub_number) for i in self.order.transits.order_by('sub_number') if i.sub_number.isnumeric()],
                default=0)
            self.sub_number = max_sub_number + 1 or 1

        super(Transit, self).save(force_insert, force_update, using, update_fields)

        if not self.history.exists() or self.history.last().status != self.status:
            TransitHistory.objects.create(transit=self, status=self.status)

    def delete(self, using=None, keep_parents=False):
        super(Transit, self).delete(using, keep_parents)
        self.update_related('order', 'DELETE')


class ExtraCargoParams(models.Model):
    machine_name = models.CharField(max_length=100, unique=True)
    human_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.human_name

    class Meta:
        verbose_name = 'доп. параметр груза'
        verbose_name_plural = 'доп. параметры груза'


class Cargo(models.Model, RecalcMixin):
    PACKAGE_TYPES = (
        ('no_package', 'Без упаковки'),
        ('wooden_box', 'Деревянный ящик'),
        ('cardboard_box', 'Картонная коробка'),
        ('pallet', 'Паллет'),
        ('envelope', 'Конверт'),
        ('pile', 'Навалом'),
        ('pack', 'Пачка'),
        ('bag', 'Мешок'),
        ('bucket', 'Ведро'),
        ('big_bag', 'Биг бэг'),
        ('barrel', 'Бочка'),
        ('roll', 'Рулон'),
        ('euroocube', 'Еврокуб'),
        ('coil', 'Катушка'),
        ('bale', 'Кипа'),
        ('safe_package', 'Сейф-пакет'),
        ('package', 'Пакет'),
        ('container', 'Контейнер'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=True, blank=True)
    transit = models.ForeignKey(Transit, on_delete=models.CASCADE, verbose_name='Перевозка', related_name='cargos')
    title = models.CharField(max_length=255, verbose_name='Наименование груза')
    package_type = models.CharField(max_length=255, choices=PACKAGE_TYPES, verbose_name='Тип упаковки',
                                    default=PACKAGE_TYPES[0][0])
    length = models.FloatField(verbose_name='Длина', default=0)
    width = models.FloatField(verbose_name='Ширина', default=0)
    height = models.FloatField(verbose_name='Высота', default=0)
    weight = models.FloatField(verbose_name='Вес, кг', default=0)
    quantity = models.IntegerField(verbose_name='Кол-во мест', default=1)
    # volume_weight = models.FloatField(default=0, verbose_name='Объемный вес, кг', blank=True, null=True)
    mark = models.CharField(max_length=255, blank=True, null=True, verbose_name='Маркировка')
    extra_params = models.ManyToManyField(ExtraCargoParams, blank=True, verbose_name='Доп. параметры')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Cargo, self).save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        super(Cargo, self).delete(using, keep_parents)
        self.update_related('transit', 'DELETE')

    class Meta:
        ordering = ['created_at']
        verbose_name = 'груз'
        verbose_name_plural = 'грузы'


class TransitSegment(models.Model, RecalcMixin):
    TYPES = [
        ('auto', 'Авто'),
        ('plane', 'Авиа'),
        ('rail', 'Ж/Д'),
        ('ship', 'Море')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transit = models.ForeignKey(Transit, on_delete=models.CASCADE, verbose_name='Перевозка', related_name='segments')

    api_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=True, blank=True)
    last_update = models.DateTimeField(auto_now=True)
    quantity = models.IntegerField(verbose_name='Количество мест', default=0)
    weight_payed = models.FloatField(verbose_name='Оплачиваемый вес', default=0)
    from_addr = models.CharField(max_length=255, verbose_name='Адрес забора груза')
    from_date_plan = models.DateField(verbose_name='Плановая дата забора груза', blank=True, null=True)
    from_date_fact = models.DateField(verbose_name='Фактическая дата забора груза', blank=True, null=True)
    to_addr = models.CharField(max_length=255, verbose_name='Адрес доставки')
    to_date_plan = models.DateField(verbose_name='Плановая дата доставки', blank=True, null=True)
    to_date_fact = models.DateField(verbose_name='Фактическая дата доставки', blank=True, null=True)
    type = models.CharField(choices=TYPES, max_length=50, db_index=True, verbose_name='Вид перевозки')
    price = models.FloatField(verbose_name='Ставка', default=0)
    price_carrier = models.FloatField(verbose_name='Закупочная цена', default=0)
    taxes = models.IntegerField(verbose_name='НДС', blank=True, null=True, default=20, choices=TAXES)
    currency = models.CharField(max_length=3, choices=CURRENCIES, default='RUB', verbose_name='Валюта')
    carrier = models.ForeignKey(Contractor, on_delete=models.CASCADE, related_name='segments',
                                verbose_name='Перевозчик')
    contract = models.CharField(max_length=255, verbose_name='Договор', blank=True, null=True)
    tracking_number = models.CharField(max_length=255, verbose_name='Номер транспортного документа', blank=True,
                                       null=True)
    tracking_date = models.DateField(blank=True, null=True, verbose_name='Дата транспортного документа')
    status = models.CharField(choices=SEGMENT_STATUS_LABELS, max_length=50, default=SEGMENT_STATUS_LABELS[0][0],
                              db_index=True, verbose_name='Статус перевозки')
    comment = models.CharField(max_length=255, blank=True, null=True, verbose_name='Примечания')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.contract = f'{self.carrier.contract} от {self.carrier.contract_sign_date.strftime("%d.%m.%Y")}'
        super(TransitSegment, self).save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        super(TransitSegment, self).delete(using, keep_parents)
        self.update_related('transit', 'DELETE', related_name='segments')

    class Meta:
        ordering = ['created_at']
        verbose_name = 'плечо перевозки'
        verbose_name_plural = 'плечи перевозки'


class OrderHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history', verbose_name='Поручение')
    status = models.CharField(choices=ORDER_STATUS_LABELS, max_length=50, default=ORDER_STATUS_LABELS[0][0],
                              verbose_name='Статус')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Время')

    def __str__(self):
        return f'{self.order} - {self.get_status_display()}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(OrderHistory, self).save(force_insert, force_update, using, update_fields)
        if self.order.status != self.order.history.last().status:
            self.order.status = self.order.history.last().status
            self.order.save()

    def delete(self, using=None, keep_parents=False):
        super(OrderHistory, self).delete(using, keep_parents)
        if self.order.status != self.order.history.last().status:
            self.order.status = self.order.history.last().status
            self.order.save()

    class Meta:
        ordering = ['created_at']
        verbose_name = 'элемент истории поручения'
        verbose_name_plural = 'элементы истории поручения'


class TransitHistory(models.Model):
    transit = models.ForeignKey(Transit, on_delete=models.CASCADE, related_name='history', verbose_name='Перевозка')
    status = models.CharField(choices=TRANSIT_STATUS_LABELS, max_length=50, default=TRANSIT_STATUS_LABELS[0][0],
                              verbose_name='Статус')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Время')

    def __str__(self):
        return f'{self.transit} - {self.get_status_display()}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(TransitHistory, self).save(force_insert, force_update, using, update_fields)
        if self.transit.status != self.transit.history.last().status:
            self.transit.status = self.transit.history.last().status
            self.transit.save()

    def delete(self, using=None, keep_parents=False):
        super(TransitHistory, self).delete(using, keep_parents)
        if self.transit.status != self.transit.history.last().status:
            self.transit.status = self.transit.history.last().status
            self.transit.save()

    class Meta:
        ordering = ['created_at']
        verbose_name = 'элемент истории перевозки'
        verbose_name_plural = 'элементы истории перевозки'


def path_by_order(instance, filename):
    return os.path.join('files', 'orders', instance.order.id.hex, filename)


class Document(models.Model):
    title = models.CharField(max_length=255, verbose_name='Пояснение')
    file = models.FileField(upload_to=path_by_order, verbose_name='Файл')
    order = models.ForeignKey(Order, related_name='docs', on_delete=models.CASCADE, verbose_name='Поручение')
    public = models.BooleanField(default=False, verbose_name='Видно клиенту')

    def __str__(self):
        return f'{self.order}: {self.title} ({self.file.name})'

    def clean_in_fs(self):
        used_files = [os.path.split(i.file.name)[-1] for i in self.order.docs.all()]
        file_path = os.path.abspath(os.path.join(settings.MEDIA_ROOT, os.path.split(self.file.name)[0]))
        for file_name in os.listdir(file_path):
            if file_name not in used_files:
                os.remove(os.path.join(file_path, file_name))

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Document, self).save(force_insert, force_update, using, update_fields)
        self.clean_in_fs()

    def delete(self, using=None, keep_parents=False):
        super(Document, self).delete(using, keep_parents)
        self.clean_in_fs()

    class Meta:
        verbose_name = 'документ'
        verbose_name_plural = 'документы'
