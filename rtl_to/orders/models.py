import os
import uuid

from django.db import models
from django.utils import timezone

from app_auth.models import User, Client, Contractor
from rtl_to import settings

CURRENCIES = (
    ('RUB', 'RUB'),
    ('USD', 'USD'),
    ('EUR', 'EUR')
)

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
        ('carrier_select', 'Выбор перевозчика'),
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


class Order(models.Model):
    TYPES = [
        ('international', 'Международная'),
        ('internal', 'Внутрироссийская'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_number = models.CharField(max_length=50, blank=True, null=False, verbose_name='Номер заказчика')
    inner_number = models.CharField(max_length=50, blank=True, null=False, verbose_name='Внутренний номер')
    creation_date = models.DateField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    manager = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE,
                                verbose_name='Менеджер', related_name='my_orders_manager')
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.CASCADE, verbose_name='Заказчик', related_name='orders')
    contract = models.CharField(max_length=255, verbose_name='Договор', blank=True, null=True)
    client_employee = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE,
                                        verbose_name='Сотрудник заказчика', related_name='my_orders_client')
    type = models.CharField(choices=TYPES, max_length=50, db_index=True, default='internal',
                            verbose_name='Вид поручения')
    status = models.CharField(choices=ORDER_STATUS_LABELS, max_length=50, default=ORDER_STATUS_LABELS[0][0],
                              db_index=True, verbose_name='Статус поручения', null=True, blank=True)
    price = models.CharField(max_length=255, verbose_name='Ставка', blank=True, null=True)
    price_carrier = models.CharField(max_length=255, verbose_name='Закупочная цена поручения', blank=True, null=True)
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
    currency = models.CharField(max_length=3, choices=CURRENCIES, default='RUB', verbose_name='Валюта')
    value = models.FloatField(verbose_name='Заявленная стоимость', default=0, blank=True, null=True)

    def __str__(self):
        return f'Поручение №{self.client_number} от {self.creation_date.strftime("%d.%m.%Y") if self.creation_date else ""}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.contract = f'{self.client.contract} от {self.client.contract_sign_date.strftime("%d.%m.%Y")}'

        super(Order, self).save(force_insert, force_update, using, update_fields)

        if not self.inner_number:
            self.inner_number = '{}-{:0>5}'.format(
                self.client.num_prefix.upper() if self.client else 'РТЛТО',
                self.client.orders.count() + 1 if self.client else Order.objects.count() + 1
            )
        if not self.client_number:
            self.client_number = self.inner_number

        if not self.history.exists() or self.history.last().status != self.status:
            OrderHistory.objects.create(order=self, status=self.status)

    def recalc_prices(self, field_name='price'):
        prices = dict()
        transits = self.transits.all()
        for transit in transits:
            price_str = transit.__getattribute__(field_name)
            if price_str:
                for price_item_str in price_str.split('; '):
                    price, currency = price_item_str.split()
                    if currency not in prices:
                        prices[currency] = float()
                    prices[currency] += float(price)
            prices = {key: value for key, value in prices.items() if value != 0}
            self.__setattr__(field_name, '; '.join([f'{price} {currency}' for currency, price in prices.items()]))

    def recalc_dates(self):
        self.from_date_plan = min([i.from_date_plan for i in self.transits.all() if i.from_date_plan], default=None) or None
        self.from_date_fact = min([i.from_date_fact for i in self.transits.all() if i.from_date_fact], default=None) or None
        self.to_date_plan = max([i.to_date_plan for i in self.transits.all() if i.to_date_plan], default=None) or None
        self.to_date_fact = max([i.to_date_fact for i in self.transits.all() if i.to_date_fact], default=None) or None

    def get_public_docs(self):
        return self.docs.filter(public=True)

    class Meta:
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


class Transit(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sub_number = models.CharField(max_length=255, db_index=True, default='', verbose_name='Субномер', blank=True)
    api_id = models.CharField(max_length=255, blank=True, null=True)
    creation_date = models.DateField(auto_now_add=True, editable=True)
    last_update = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transits', verbose_name='Поручение')
    volume = models.FloatField(verbose_name='Объем', default=0, blank=True, null=True)
    weight = models.FloatField(verbose_name='Вес брутто', default=0, blank=True, null=True)
    weight_payed = models.FloatField(verbose_name='Оплачиваемый вес', default=0, blank=True, null=True)
    quantity = models.IntegerField(verbose_name='Количество мест', default=0, blank=True, null=True)
    from_addr = models.CharField(max_length=255, verbose_name='Адрес забора груза')
    from_org = models.CharField(max_length=255, verbose_name='Отправитель')
    from_inn = models.CharField(max_length=255, verbose_name='ИНН отправителя')
    from_legal_addr = models.CharField(max_length=255, verbose_name='Юр. адрес')
    from_contact_name = models.CharField(max_length=255, verbose_name='Контактное лицо')
    from_contact_phone = models.CharField(max_length=255, verbose_name='Телефон')
    from_contact_email = models.CharField(max_length=255, verbose_name='email')
    from_date_plan = models.DateField(verbose_name='Плановая дата забора груза', blank=True, null=True)
    from_date_fact = models.DateField(verbose_name='Фактическая дата забора груза', blank=True, null=True)
    to_addr = models.CharField(max_length=255, verbose_name='Адрес доставки')
    to_org = models.CharField(max_length=255, verbose_name='Получатель')
    to_inn = models.CharField(max_length=255, verbose_name='ИНН получателя')
    to_legal_addr = models.CharField(max_length=255, verbose_name='Юр. адрес')
    to_contact_name = models.CharField(max_length=255, verbose_name='Контактное лицо')
    to_contact_phone = models.CharField(max_length=255, verbose_name='Телефон')
    to_contact_email = models.CharField(max_length=255, verbose_name='email')
    to_date_plan = models.DateField(verbose_name='Плановая дата доставки', blank=True, null=True)
    to_date_fact = models.DateField(verbose_name='Фактическая дата доставки', blank=True, null=True)
    type = models.CharField(max_length=255, db_index=True, blank=True, null=True, verbose_name='Вид перевозки')
    price = models.CharField(max_length=255, verbose_name='Ставка', blank=True, null=True)
    price_carrier = models.CharField(max_length=255, verbose_name='Закупочная цена', blank=True, null=True)
    status = models.CharField(choices=TRANSIT_STATUS_LABELS, max_length=50, default=TRANSIT_STATUS_LABELS[0][0], db_index=True,
                              verbose_name='Статус перевозки', blank=True, null=True)
    extra_services = models.ManyToManyField(ExtraService, blank=True, verbose_name='Доп. услуги')

    def __str__(self):
        if self.order:
            return f'Перевозка №{self.order.client_number}/{self.sub_number}'
        return 'Новая перевозка'

    class Meta:
        verbose_name = 'перевозка'
        verbose_name_plural = 'перевозки'
        permissions = [
            ('view_all_transits', 'Can view all transits')
        ]

    def update_order_data(self):
        transits = self.order.transits.all()
        self.order.from_addr_forlist = '<br>'.join(list({i.from_addr for i in transits}))
        self.order.to_addr_forlist = '<br>'.join(list({i.to_addr for i in transits}))
        self.order.weight = sum([i.weight for i in transits])
        self.order.quantity = sum([i.quantity for i in transits])
        self.order.recalc_dates()
        self.order.recalc_prices()
        self.order.recalc_prices('price_carrier')
        self.order.save()

    def recalc_dates(self):
        self.from_date_plan = min([i.from_date_plan for i in self.segments.all() if i.from_date_plan], default=None) or None
        self.from_date_fact = min([i.from_date_fact for i in self.segments.all() if i.from_date_fact], default=None) or None
        self.to_date_plan = max([i.to_date_plan for i in self.segments.all() if i.to_date_plan], default=None) or None
        self.to_date_fact = max([i.to_date_fact for i in self.segments.all() if i.to_date_fact], default=None) or None

    def recalc_prices(self, field_name='price'):
        prices = dict()
        segments = self.segments.all()
        for segment in segments:
            if segment.currency not in prices:
                prices[segment.currency] = 0
            prices[segment.currency] += segment.__getattribute__(field_name)
        prices = {key: value for key, value in prices.items() if value != 0}
        self.__setattr__(field_name, '; '.join([f'{price} {currency}' for currency, price in prices.items()]))

    def colect_types(self):
        segments = self.segments.all()
        types = [i.get_type_display() for i in segments]
        self.type = '-'.join(types)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.sub_number:
            max_sub_number = max(
                [int(i.sub_number) for i in self.order.transits.order_by('sub_number') if i.sub_number.isnumeric()],
                default=0)
            self.sub_number = max_sub_number + 1 or 1

        super(Transit, self).save(force_insert, force_update, using, update_fields)
        self.update_order_data()

        if not self.history.exists() or self.history.last().status != self.status:
            TransitHistory.objects.create(transit=self, status=self.status)

    def delete(self, using=None, keep_parents=False):
        super(Transit, self).delete(using, keep_parents)
        self.update_order_data()


class ExtraCargoParams(models.Model):
    machine_name = models.CharField(max_length=100, unique=True)
    human_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.human_name

    class Meta:
        verbose_name = 'доп. параметр груза'
        verbose_name_plural = 'доп. параметры груза'


class Cargo(models.Model):
    PACKAGE_TYPES = (
        ('cardboard_box', 'Картонная коробка'),
        ('wooden_box', 'Деревянный ящик'),
        ('safe_package', 'Сейф-пакет'),
        ('package', 'Пакет'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transit = models.ForeignKey(Transit, on_delete=models.CASCADE, verbose_name='Перевозка', related_name='cargos')
    title = models.CharField(max_length=255, verbose_name='Наименование груза')
    package_type = models.CharField(max_length=255, choices=PACKAGE_TYPES, verbose_name='Тип упаковки',
                                    default='cardboard_box')
    length = models.FloatField(verbose_name='Длина', default=0)
    width = models.FloatField(verbose_name='Ширина', default=0)
    height = models.FloatField(verbose_name='Высота', default=0)
    weight = models.FloatField(verbose_name='Вес', default=0)
    quantity = models.IntegerField(verbose_name='Мест', default=1)
    volume_weight = models.FloatField(default=0, verbose_name='Объемный вес', blank=True, null=True)
    mark = models.CharField(max_length=255, blank=True, null=True, verbose_name='Маркировка')
    extra_params = models.ManyToManyField(ExtraCargoParams, blank=True, verbose_name='Доп. параметры')

    def update_transit_data(self):
        cargos = self.transit.cargos.all()
        self.transit.volume = sum([i.length * i.width * i.height * i.quantity for i in cargos]) / 1000000
        self.transit.weight = sum([i.weight * i.quantity for i in cargos])
        self.transit.weight_payed = sum([max(i.weight * i.quantity, i.volume_weight) for i in cargos])
        self.transit.quantity = sum([i.quantity for i in cargos])
        self.transit.save()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.volume_weight = self.length * self.width * self.height * self.quantity * 167 / 1000000
        super(Cargo, self).save(force_insert, force_update, using, update_fields)
        self.update_transit_data()

    def delete(self, using=None, keep_parents=False):
        super(Cargo, self).delete(using, keep_parents)
        self.update_transit_data()

    class Meta:
        verbose_name = 'груз'
        verbose_name_plural = 'грузы'


class TransitSegment(models.Model):

    TYPES = [
        ('auto', 'Авто'),
        ('plane', 'Авиа'),
        ('rail', 'Ж/Д'),
        ('ship', 'Море')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transit = models.ForeignKey(Transit, on_delete=models.CASCADE, verbose_name='Перевозка', related_name='segments')

    api_id = models.CharField(max_length=255, blank=True, null=True)
    creation_date = models.DateField(auto_now_add=True, editable=True)
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
    currency = models.CharField(max_length=3, choices=CURRENCIES, default='RUB', verbose_name='Валюта')
    carrier = models.ForeignKey(Contractor, on_delete=models.CASCADE, related_name='segments',
                                verbose_name='Перевозчик')
    contract = models.CharField(max_length=255, verbose_name='Договор', blank=True, null=True)
    tracking_number = models.CharField(max_length=255, verbose_name='Номер транспортного документа', blank=True,
                                       null=True)
    status = models.CharField(choices=SEGMENT_STATUS_LABELS, max_length=50, default=SEGMENT_STATUS_LABELS[0][0],
                              db_index=True, verbose_name='Статус перевозки')
    comment = models.CharField(max_length=255, blank=True, null=True, verbose_name='Примечания')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.contract = f'{self.carrier.contract} от {self.carrier.contract_sign_date.strftime("%d.%m.%Y")}'
        super(TransitSegment, self).save(force_insert, force_update, using, update_fields)
        self.transit.recalc_dates()
        self.transit.recalc_prices()
        self.transit.recalc_prices('price_carrier')
        self.transit.colect_types()
        self.transit.save()

    def delete(self, using=None, keep_parents=False):
        super(TransitSegment, self).delete(using, keep_parents)
        self.transit.recalc_dates()
        self.transit.recalc_prices()
        self.transit.recalc_prices('price_carrier')
        self.transit.colect_types()
        self.transit.save()


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
