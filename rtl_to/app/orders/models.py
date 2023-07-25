import datetime
import logging
import os
import uuid

import requests
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from dadata import Dadata
from app_auth.models import User, Client, Contractor, Contact, Counterparty, Auditor, ClientContract, ContractorContract
from app_auth.models import inn_validator
from django.conf import settings
from orders.tasks import from_date_plan_manager_notification, from_date_fact_manager_notification, \
    to_date_plan_manager_notification, to_date_fact_manager_notification, order_created_for_manager, \
    order_created_for_client, from_date_plan_client_notification, from_date_plan_sender_notification, \
    from_date_fact_client_notification, to_date_plan_client_notification, to_date_plan_receiver_notification, \
    to_date_fact_client_notification, document_added_for_manager, document_added_for_client

logger = logging.getLogger(__name__)

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
    ('pickup', 'Ожидание забора груза'),
    ('in_progress', 'В пути'),
    ('temporary_storage', 'Груз на СВХ (ТО)'),
    ('transit_storage', 'Груз на транзитном складе'),
    ('completed', 'Доставлено'),
    ('rejected', 'Аннулировано')
]

EXT_ORDER_STATUS_LABELS = [
    ('new', 'Новое'),
    ('pre_process', 'Принято в работу'),
    ('rejected', 'Аннулировано'),
    ('in_progress', 'На исполнении'),
    ('delivered', 'Выполнено'),
    ('bargain', 'Согласование ставок'),
    ('awaiting_docs', 'Ожидание оригиналов документов'),
    ('completed', 'Завершено'),
]

SEGMENT_STATUS_LABELS = [
    ('waiting', 'В ожидании'),
    ('in_progress', 'В пути'),
    ('completed', 'Выполнено'),
    ('rejected', 'Аннулировано')
]


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
            logging.error(rates.get('error'))
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


class RecalcMixin:
    """
    Миксин для осуществления взаимодействия моделей между собой
    (автоматические пересчеты значений полей, установка дат, статусов и т.п.)
    """

    def update_related(self, parent_field, *fields, related_name: str = None):
        """
        Метод для запуска пересчетов. Вызывается в форме
        :param parent_field: наименование поля ForeignKey, ссылающегося на вышестоящий объект
        :param fields: перчень названий обновленных при сохранении формы полей
        :param related_name: имя, по которому объект-родитель собирает нижестоящие объекты
        (в том числе, из которого вызван данный метод)
        :return: None
        """
        if not related_name:
            related_name = self.__class__.__name__.lower() + 's'

        related = self.__getattribute__(parent_field.lower())
        related.collect(related_name, *fields)

    def collect(self, related_name, *fields):
        """
        Основной метод, описывающий процесс сбора данных, обновления полей и сохранение объектов.
        Если данный метод не переназначить, возникнет исключение
        :param related_name: имя, по которому объект-родитель собирает нижестоящие объекты
        (в том числе, из которого вызван данный метод)
        :param fields: обновленные поля нижестоящих объектов
        :return: None
        """
        raise NotImplementedError(f'No logics for {self.__class__.__name__} implemented')

    def get_status_list(self):
        """
        Метод, описывающий логику генерации списка доступных для объекта статусов, в зависимости от текущего состояния.
        Если данный метод не переназначить, возникнет исключение
        :return: None
        """
        raise NotImplementedError

    @staticmethod
    def get_sub_queryset(queryset, sub_model_rel_name, filters: dict = None):
        """
        Сборщик набора объектов еще одним уровнем ниже текущего
        :param queryset: набор объектов, ниже которого опускаемся
        :param sub_model_rel_name: наименование наборов объектов (самых нижних)
        :param filters: применяемые фильтры
        :return: None
        """
        querysets = list()
        try:
            result = queryset.first().__getattribute__(sub_model_rel_name).none()
        except AttributeError as e:
            logger.error(e)
            return querysets

        for item in queryset:
            querysets.append(item.__getattribute__(sub_model_rel_name).all())
        result = result.union(*querysets)
        if filters:
            return result.filter(**filters)
        return result

    @staticmethod
    def check_non_empty(query_list):
        for i in query_list:
            if not i:
                return False
        return True

    @staticmethod
    def list_from_queryset(
            queryset, field_name, remove_duplicates: bool = False, callables: bool = False,
            check_all_exist: bool = False, filter_empty: bool = True
    ):
        """
        Генератор списка значений указанного поля для queryset
        :param queryset: источник данных
        :param field_name: наименование поля
        :param remove_duplicates: True, если нужно удалить идущие подряд (!!!) дубликаты
        :param callables: True, если поле является методом
        :param check_all_exist: True, если нужно вывести пустой результат при наличии пустых значений
        :param filter_empty: True, если нужно удалить пустые значения
        :return: Обработанный список значений указанного поля
        """
        if callables:
            result = [i.__getattribute__(field_name)() for i in queryset if hasattr(i, field_name)]
        else:
            result = [i.__getattribute__(field_name) for i in queryset if hasattr(i, field_name)]

        if filter_empty:
            result = [i for i in result if i]

        if check_all_exist and not all(result):
            return list()

        if remove_duplicates:
            new_result = list()
            for t, item in enumerate(result):
                if t == 0 or (t > 0 and item != result[t - 1]):
                    new_result.append(item)
            return new_result
        return result

    def equal_to_min(self, queryset, source_field_name: str, check_all_exist: bool = False):
        """
        Находит наименьшее значение указанного поля
        :param queryset: источник данных
        :param source_field_name: наименование поля
        :param check_all_exist: True, если нужно вывести пустой результат при наличии пустых значений
        :return: Минимальное значение поля или None
        """
        query_list = self.list_from_queryset(queryset, source_field_name, check_all_exist=check_all_exist,
                                             filter_empty=not check_all_exist)
        if query_list:
            return min(query_list, default=None)

    def equal_to_max(self, queryset, source_field_name: str, check_all_exist: bool = False):
        """
        Находит наибольшее значение указанного поля
        :param queryset: источник данных
        :param source_field_name: наименование поля
        :param check_all_exist: True, если нужно вывести пустой результат при наличии пустых значений
        :return: Максимальное значение поля или None
        """
        query_list = self.list_from_queryset(queryset, source_field_name, check_all_exist=check_all_exist,
                                             filter_empty=not check_all_exist)
        if query_list:
            return max(query_list, default=None)

    def sum_values(self, queryset, source_field_name: str, decimal_round: int = 2):
        """
        Рассчитывает сумму значений указанного поля
        :param queryset: источник данных
        :param source_field_name: наименование поля
        :param decimal_round: количество знаков после запятой для округления float
        :return: Сумма значений поля
        """
        result = sum(self.list_from_queryset(queryset, source_field_name))
        if isinstance(result, float):
            result = round(result, decimal_round)
        return result

    def join_values(
            self, queryset, delimiter, source_field_name: str, remove_duplicates: bool = False, callables: bool = False
    ):
        """
        Генератор строки, содержащий значения указанного поля через определенный разделитель
        :param queryset: источник данных
        :param delimiter: разделитель
        :param source_field_name: наименование поля
        :param remove_duplicates: True, если нужно удалить идущие подряд (!!!) дубликаты
        :param callables: True, если поле является методом
        :return: Искомая строка
        """
        return delimiter.join(self.list_from_queryset(queryset, source_field_name, remove_duplicates, callables))

    @staticmethod
    def sum_multicurrency_values(queryset, source_value_field_name, source_currency_field_name: str):
        """
        Генератор строки, содержащей "сумму" денег в различных валютах
        :param queryset: источник данных
        :param source_value_field_name: наименование поля стоимости
        :param source_currency_field_name: наименование поля валюты
        :return: Искомая строка
        """

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

    @staticmethod
    def clean_address(address: str) -> (str, str, str):
        if not isinstance(address, str):
            return None, None, None
        try:
            dadata_data = Dadata(settings.DADATA_TOKEN, settings.DADATA_SECRET)
            result = dadata_data.clean('address', address.replace(',', ''))
            logger.info(result)
        except Exception as e:
            logger.error(e)
            return None, None, None
        if result.get('country') != 'Россия':
            return address, result.get('country'), None
        clean_parts = list()
        if result.get('postal_code'):
            clean_parts.append(result.get('postal_code'))
        clean_parts.append(result.get('result'))
        clean_address = ', '.join(clean_parts)
        city = result.get('city_with_type') if result.get('city_with_type') else result.get('region_with_type')
        street = result.get('street_with_type')
        return clean_address, city, street

    def short_address(self, from_fn='from_addr', to_fn='to_addr'):
        from_addr = self.__getattribute__(from_fn)
        to_addr = self.__getattribute__(to_fn)
        if from_addr is not None and ('а/п' in from_addr.lower() or 'аэропорт' in from_addr.lower()):
            from_cleaned, from_city, from_street = from_addr, from_addr, None
        else:
            from_cleaned, from_city, from_street = self.clean_address(from_addr)
        if to_addr is not None and ('а/п' in to_addr.lower() or 'аэропорт' in to_addr.lower()):
            to_cleaned, to_city, to_street = to_addr, to_addr, None
        else:
            to_cleaned, to_city, to_street = self.clean_address(to_addr)
        if from_city == to_city and all([i is not None for i in (from_city, from_street, to_city, to_street)]):
            from_short = f'{from_city}, {from_street}'
            to_short = f'{to_city}, {to_street}'
        else:
            from_short = from_city
            to_short = to_city
        if from_cleaned is not None:
            self.__setattr__(from_fn, from_cleaned)
            logger.info(f'{from_fn} cleaned. Result: {from_cleaned}')
        if to_cleaned is not None:
            self.__setattr__(to_fn, to_cleaned)
            logger.info(f'{to_fn} cleaned. Result: {to_cleaned}')

        if from_short is not None:
            self.__setattr__(f'{from_fn}_short', from_short)
        else:
            self.__setattr__(f'{from_fn}_short', from_addr)
        logger.info(f'{str(self)}: {from_fn}_short updated: {self.__getattribute__(f"{from_fn}_short")}')

        if to_short is not None:
            self.__setattr__(f'{to_fn}_short', to_short)
        else:
            self.__setattr__(f'{to_fn}_short', to_addr)
        logger.info(f'{str(self)}: {to_fn}_short updated: {self.__getattribute__(f"{to_fn}_short")}')


class Order(models.Model, RecalcMixin):
    """
    Входящее поручение
    """
    TYPES = [
        ('international', 'Международная перевозка'),
        ('internal', 'Внутрироссийская перевозка'),
        ('combined', 'Сборный груз'),
        ('courier', 'Курьерская перевозка'),
    ]

    INSURANCE_COEFFS = (
        (1, '100%'),
        (1.1, '110%')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    last_update = models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')

    client_number = models.CharField(max_length=50, blank=True, null=False, verbose_name='Номер поручения')
    inner_number = models.CharField(max_length=50, blank=True, null=False, verbose_name='Внутренний номер')
    order_date = models.DateField(default=timezone.now, verbose_name='Дата поручения')
    manager = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                verbose_name='Менеджер', related_name='my_orders_manager')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Заказчик', related_name='orders')
    auditors = models.ManyToManyField(Auditor, verbose_name='Аудиторы', related_name='orders', blank=True)
    contract = models.ForeignKey(ClientContract, on_delete=models.PROTECT, verbose_name='Договор', null=True)
    client_employee = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                        verbose_name='Сотрудник заказчика', related_name='my_orders_client')
    type = models.CharField(choices=TYPES, max_length=50, db_index=True, default='internal',
                            verbose_name='Вид поручения')
    status = models.CharField(choices=ORDER_STATUS_LABELS, max_length=50, default=ORDER_STATUS_LABELS[0][0],
                              db_index=True, verbose_name='Статус поручения', null=True, blank=True)
    price = models.CharField(max_length=255, verbose_name='Ставка', blank=True, null=True)
    price_carrier = models.CharField(max_length=255, verbose_name='Закупочная цена поручения', blank=True, null=True)
    taxes = models.IntegerField(verbose_name='НДС', blank=True, null=True, default=20, choices=TAXES)
    from_addr_forlist = models.TextField(verbose_name='Адрес забора груза', editable=False)
    to_addr_forlist = models.TextField(verbose_name='Адрес доставки', editable=False)
    active_segments = models.TextField(verbose_name='Активные плечи', editable=False, blank=True, null=True)
    comment = models.TextField(verbose_name='Примечания', null=True, blank=True)
    weight = models.FloatField(verbose_name='Вес брутто', null=True, blank=True)
    quantity = models.IntegerField(verbose_name='Количество мест', null=True, blank=True)
    from_date_plan = models.DateField(verbose_name='Плановая дата забора груза', blank=True, null=True)
    from_date_fact = models.DateField(verbose_name='Фактическая дата забора груза', blank=True, null=True)
    to_date_plan = models.DateField(verbose_name='Плановая дата доставки', blank=True, null=True)
    to_date_fact = models.DateField(verbose_name='Фактическая дата доставки', blank=True, null=True)
    insurance = models.BooleanField(default=False, verbose_name='Страхование')
    value = models.FloatField(verbose_name='Заявленная стоимость', default=0, blank=True)
    sum_insured_coeff = models.FloatField(verbose_name='Коэффициент страховой суммы', choices=INSURANCE_COEFFS,
                                          default=1)
    insurance_currency = models.CharField(max_length=3, choices=CURRENCIES, default='RUB',
                                          verbose_name='Валюта страхования')
    insurance_premium_coeff = models.FloatField(verbose_name='Коэффициент страховой премии', default=0.00055)
    insurance_policy_number = models.CharField(max_length=255, verbose_name='№ полиса', blank=True, null=True)
    currency_rate = models.FloatField(verbose_name='Курс страховой валюты', default=0, blank=True, null=True)
    cargo_name = models.CharField(max_length=150, verbose_name='Общее наименование груза')
    cargo_origin = models.CharField(max_length=150, verbose_name='Страна происхождения груза', default='Россия')
    created_by = models.ForeignKey(User, verbose_name='Создатель поручения', on_delete=models.SET_NULL,
                                   blank=True, null=True)

    def filename(self):
        """
        Генерирует наименование файла поручения
        :return: наименование файла поручения
        """
        return self.client_number.replace('/', '_').replace('-', '_') + '.pdf'

    def __str__(self):
        return f'Поручение №{self.client_number} от {self.order_date.strftime("%d.%m.%Y")}'

    def get_status_list(self):
        """
        Генератор списка доступных для объекта статусов, в зависимости от текущего состояния.
        :return: список статуса для использовании в choices поля формы
        """
        allowed = [self.status]  # Позволяем оставить текущий статус

        if self.status == 'new':
            allowed.append('pre_process')
        if self.status == 'pre_process':
            allowed.append('in_progress')
        if self.status == 'in_progress':
            allowed.append('delivered')
        if self.status == 'delivered':
            allowed += ['bargain', 'completed']
        if self.status == 'bargain':
            allowed.append('completed')

        allowed.append('rejected')  # Позволяем аннулировать

        return list(filter(lambda x: x[0] in allowed, ORDER_STATUS_LABELS))

    @staticmethod
    def update_status(sub_items_statuses):
        """
        Определяет статус для автоматического перехода, в зависимости от статусов объектов пониже
        :param sub_items_statuses: перечень статусов нижестоящих объектов
        :return: Искомый статус или None
        """
        mass_check = ('pickup', 'in_progress', 'temporary_storage', 'transit_storage', 'completed')
        if len(sub_items_statuses) == 1 and 'carrier_select' in sub_items_statuses:
            return 'pre_process'
        elif len(sub_items_statuses) == 1 and 'completed' in sub_items_statuses:
            return 'delivered'
        elif all([i in mass_check for i in sub_items_statuses]):
            return 'in_progress'

    def collect(self, related_name, *fields):
        """
        Основной метод, описывающий процесс сбора данных, обновления полей и сохранение объектов.
        :param related_name: имя, по которому объект-родитель собирает нижестоящие объекты
        (в том числе, из которого вызван данный метод)
        :param fields: обновленные поля нижестоящих объектов
        :return: None
        """
        queryset = self.__getattribute__(related_name).all().order_by('created_at')

        if 'weight' in fields or 'DELETE' in fields:
            # Вес в поручении равен сумме весов в перевозках
            self.weight = self.sum_values(queryset, 'weight')
        if 'quantity' in fields or 'DELETE' in fields:
            # Кол-во мест в поручении равен сумме весов в перевозках
            self.quantity = self.sum_values(queryset, 'quantity')
        if 'from_date_plan' in fields or 'DELETE' in fields:
            # Плановая дата отправки в поручении равна самой ранней плановой дате отправки в перевозках
            self.from_date_plan = self.equal_to_min(queryset, 'from_date_plan')
        if 'from_date_fact' in fields or 'DELETE' in fields:
            # Фактическая дата отправки в поручении равна самой ранней фактической дате отправки в перевозках
            self.from_date_fact = self.equal_to_max(queryset, 'from_date_fact', True)
        if 'to_date_plan' in fields or 'DELETE' in fields:
            # Плановая дата доставки в поручении равна самой ранней плановой дате доставки в перевозках
            self.to_date_plan = self.equal_to_min(queryset, 'to_date_plan')
        if 'to_date_fact' in fields or 'DELETE' in fields:
            # Фактическая дата доставки в поручении равна самой ранней фактической дате доставки в перевозках
            self.to_date_fact = self.equal_to_max(queryset, 'to_date_fact', True)

        if 'status' in fields or 'DELETE' in fields:
            # Обновляем статус
            new_status = self.update_status(self.list_from_queryset(queryset, 'status', True))
            if new_status:
                self.status = new_status

        if 'currency' in fields:
            # обнуляем курс валют, чтобы он автоматически рассчитался при сохранении
            self.currency_rate = None

        if any([i in fields for i in ('currency', 'value', 'order_date', 'DELETE')]):
            # Заявленная стоимость грузов в поручении равна сумме заявленных стоимостей грузов в перевозках
            self.value = self.sum_values(queryset, 'value')
            if self.insurance and queryset.exists():
                # Обновляем данные по страхованию в перевозках
                self.update_transits_insurance(queryset, self.value, queryset.first().currency, self.order_date)
        if any([i in fields for i in ('price', 'price_currency', 'DELETE')]):
            # Ставка поручения равна сумме ставок в перевозках
            self.price = self.sum_multicurrency_values(self.transits.all(), 'price', 'price_currency')  #
        if 'price_carrier' in fields or 'DELETE' in fields:
            # Закупочная стоимость поручения равна сумме закупочных стоимостей в перевозках
            self.price_carrier = self.sum_multicurrency_values(self.ext_orders.all(), 'price_carrier', 'currency')
        if 'from_addr' in fields or 'DELETE' in fields:
            # Генерим <ul> для отображения в списке поручений
            self.from_addr_forlist = self.make_address_for_list(queryset, 'from_addr', 'from_addr_short')
        if 'to_addr' in fields or 'DELETE' in fields:
            # Генерим <ul> для отображения в списке поручений
            self.to_addr_forlist = self.make_address_for_list(queryset, 'to_addr', 'to_addr_short')  #
        if any([i in fields for i in ('status', 'from_addr', 'to_addr', 'DELETE')]):
            self.collect_active_segments()
        self.save()

    def enumerate_transits(self):
        """
        Присваивает человекочитаемые номера перевозок
        :return: None
        """
        transits = self.transits.all().order_by('created_at')
        if transits.count() == 1:
            transits.update(number=self.inner_number)
        else:
            for t, transit in enumerate(transits):
                transit.number = f'{self.inner_number}-{t + 1}'
                transit.save()

    def update_transits_insurance(self, queryset, value, currency, rate_date):
        """
        Обновляет данные по страхованию в перевозках
        :param queryset: набор объектов Перевозок
        :param value: заявленная стоимость груза
        :param currency: валюта страхования
        :param rate_date: дата курса валюты
        :return: Суммарная страховая премия
        """
        if currency == self.insurance_currency:
            rate = 1
        elif self.currency_rate:
            rate = self.currency_rate
        else:
            rate = get_currency_rate(currency, self.insurance_currency, rate_date)
        self.currency_rate = rate
        sum_insured = value * self.sum_insured_coeff * rate
        insurance_premium = round(sum_insured * self.insurance_premium_coeff, 2)
        for transit in queryset:
            transit.sum_insured = transit.value * self.sum_insured_coeff * rate
            transit.insurance_premium = transit.sum_insured * self.insurance_premium_coeff
            transit.save()
        return insurance_premium

    def need_to_change_numbers(self, prefix: str = None):
        """
        Проверяет необходимость генерации номеров поручения
        :param prefix: Префикс номера поручения
        :return: True, если менять надо
        """
        if not self.client_number or not self.inner_number:
            return True

        if not prefix:
            return self.inner_number != self.client_number
        else:
            if self.client_number.startswith(prefix):
                return self.inner_number != self.client_number
            else:
                return self.inner_number != f'{prefix}-{self.client_number}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """
        Обеспечивает сохранение объекта с запуском необходимых действий
        """
        if not self.order_date:
            self.order_date = self.created_at

        prefix = self.client.num_prefix.upper() if self.client and self.client.num_prefix else None

        # Автоназначения номера поручения
        if not self.client_number:
            self.client_number = '{}-{:0>5}'.format(
                prefix if prefix else 'РТЛТО',
                self.client.orders.count() if self.client else Order.objects.count() + 1
            )
            self.inner_number = self.client_number
        elif self.need_to_change_numbers(prefix):
            if prefix and not self.client_number.startswith(prefix):
                self.inner_number = f'{prefix}-{self.client_number}'
            else:
                self.inner_number = self.client_number

        super(Order, self).save(force_insert, force_update, using, update_fields)

        # Добавление статуса в историю статусов
        if not self.history.exists() or self.history.last().status != self.status:
            OrderHistory.objects.create(order=self, status=self.status)

    @staticmethod
    def make_address_for_list(queryset, field_name='from_addr', field_name_short='from_addr_short'):
        """
        Генератор <ul> для выведения в списке поручений
        :param queryset: источник данных
        :param field_name: наименование поля полного адреса
        :param field_name_short: наименование поля краткого адреса
        :return:
        """
        diff_addr = list({(i.__getattribute__(field_name), i.__getattribute__(field_name_short)) for i in queryset})
        forlist = list()
        for full, short in diff_addr:
            if short is not None:
                forlist.append(short)
            else:
                forlist.append(full)
        if len(forlist) > 1:
            return '<ul>\n\t<li>{}\t</li>\n</ul>'.format('</li>\n\t<li>'.join(forlist))
        else:
            return ''.join(forlist)

    def collect_active_segments(self):
        """
        Сборщик списка <ul> активных плеч
        :return:
        """
        active_segments = self.segments.filter(status='in_progress')
        active_segments = [str(i) for i in active_segments]
        if len(active_segments) > 1:
            self.active_segments = '<ul>\n\t<li>{}\t</li>\n</ul>'.format('</li>\n\t<li>'.join(active_segments))
        else:
            self.active_segments = ''.join(active_segments)

    def get_public_docs(self):
        """
        Сборщик документов, доступных сотрудникам заказчиков и аудиторов
        :return: queryset документов по поручению
        """
        return self.docs.filter(public=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'входящее поручение'
        verbose_name_plural = 'входящие поручения'
        permissions = [
            ('view_all_orders', 'Can view all orders')
        ]


@receiver(post_save, sender=Order)
def order_added(sender, created, instance, **kwargs):
    if created:
        if instance.created_by.user_type.startswith('client'):
            order_created_for_manager.delay(instance.pk)
        elif instance.created_by.user_type == 'manager':
            order_created_for_client.delay(instance.pk)


class ExtraService(models.Model):
    """
    Справочник доп. услуг
    """
    machine_name = models.CharField(max_length=100, unique=True)
    human_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.human_name

    class Meta:
        verbose_name = 'доп. услуга'
        verbose_name_plural = 'доп. услуги'


class Transit(models.Model, RecalcMixin):
    """
    Перевозка
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=True, blank=True, verbose_name='Время создания')
    last_update = models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')
    number = models.CharField(max_length=255, db_index=True, default='', verbose_name='Полный номер', blank=True)
    api_id = models.CharField(max_length=255, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transits', verbose_name='Поручение')
    volume = models.FloatField(verbose_name='Объем', default=0, blank=True, null=True)
    weight = models.FloatField(verbose_name='Вес брутто', default=0, blank=True, null=True)
    weight_payed = models.FloatField(verbose_name='Оплачиваемый вес', default=0, blank=True, null=True)
    quantity = models.IntegerField(verbose_name='Количество мест', default=0, blank=True, null=True)
    from_addr = models.CharField(max_length=255, verbose_name='Адрес забора груза')
    from_addr_short = models.CharField(max_length=255, verbose_name='Пункт забора груза', blank=True, null=True)
    from_org = models.CharField(max_length=255, verbose_name='Отправитель', blank=True, null=True)
    from_inn = models.CharField(max_length=15, validators=[inn_validator], verbose_name='ИНН отправителя', blank=True,
                                null=True)
    from_legal_addr = models.CharField(max_length=255, verbose_name='Юр. адрес', blank=True, null=True)

    sender = models.ForeignKey(Counterparty, verbose_name='Отправитель', on_delete=models.PROTECT, null=True,
                               related_name='sent_transits')
    take_from = models.CharField(max_length=255, verbose_name='Забрать груз у третьего лица', blank=True, null=True)
    from_contacts = models.ManyToManyField(Contact, verbose_name='Контактные лица', related_name='cnt_sent_transits')

    from_contact_name = models.CharField(max_length=255, verbose_name='Контактное лицо', blank=True, null=True)
    from_contact_phone = models.CharField(max_length=255, verbose_name='Телефон', blank=True, null=True)
    from_contact_email = models.CharField(max_length=255, verbose_name='email', blank=True, null=True)
    from_date_plan = models.DateField(verbose_name='Плановая дата забора груза', blank=True, null=True)
    from_date_fact = models.DateField(verbose_name='Фактическая дата забора груза', blank=True, null=True)
    from_date_wanted = models.DateField(verbose_name='Дата готовности груза', blank=True, null=True)
    to_addr = models.CharField(max_length=255, verbose_name='Адрес доставки')
    to_addr_short = models.CharField(max_length=255, verbose_name='Пункт доставки', blank=True, null=True)
    to_org = models.CharField(max_length=255, verbose_name='Получатель', blank=True, null=True)
    to_inn = models.CharField(max_length=15, validators=[inn_validator], verbose_name='ИНН получателя', blank=True,
                              null=True)
    to_legal_addr = models.CharField(max_length=255, verbose_name='Юр. адрес', blank=True, null=True)

    receiver = models.ForeignKey(Counterparty, verbose_name='Получатель', on_delete=models.PROTECT, null=True,
                                 related_name='received_transits')
    give_to = models.CharField(max_length=255, verbose_name='Передать груз третьему лицу', blank=True, null=True)
    to_contacts = models.ManyToManyField(Contact, verbose_name='Контактные лица', related_name='cnt_received_transits')

    to_contact_name = models.CharField(max_length=255, verbose_name='Контактное лицо', blank=True, null=True)
    to_contact_phone = models.CharField(max_length=255, verbose_name='Телефон', blank=True, null=True)
    to_contact_email = models.CharField(max_length=255, verbose_name='email', blank=True, null=True)
    to_date_plan = models.DateField(verbose_name='Плановая дата доставки', blank=True, null=True)
    to_date_fact = models.DateField(verbose_name='Фактическая дата доставки', blank=True, null=True)
    to_date_wanted = models.DateField(verbose_name='Желаемая дата доставки', blank=True, null=True)
    type = models.CharField(max_length=255, db_index=True, blank=True, null=True, verbose_name='Вид перевозки')
    price = models.FloatField(verbose_name='Ставка', default=0)
    price_currency = models.CharField(max_length=3, choices=CURRENCIES, default='RUB', verbose_name='Валюта ставки')
    price_carrier = models.CharField(max_length=255, verbose_name='Закупочная цена', blank=True, null=True)
    status = models.CharField(choices=TRANSIT_STATUS_LABELS, max_length=50, default=TRANSIT_STATUS_LABELS[0][0],
                              db_index=True, verbose_name='Статус перевозки')
    extra_services = models.ManyToManyField(ExtraService, blank=True, verbose_name='Доп. услуги')
    currency = models.CharField(max_length=3, choices=CURRENCIES, default='RUB', verbose_name='Валюта')
    value = models.FloatField(verbose_name='Заявленная стоимость', default=0, blank=True, null=True)

    sum_insured = models.FloatField(verbose_name='Страховая сумма', default=0, blank=True, null=True)
    insurance_premium = models.FloatField(verbose_name='Страховая премия', default=0, blank=True, null=True)
    bill_number = models.CharField(max_length=100, verbose_name='Номер счета', blank=True, null=True)

    def __str__(self):
        if self.order:
            return f'Перевозка №{self.number}'
        return 'Новая перевозка'

    def price_wo_taxes(self):
        """
        Рассчитывает ставку без учета НДС (для документов)
        :return: ставка без НДС
        """
        if self.order.taxes is not None and self.price is not None:
            return round(self.price * (100 - self.order.taxes) / 100, 2)
        else:
            return round(self.price if self.price else 0, 2)

    def taxes_sum(self):
        """
        Рассчитывает сумму НДС (для документов)
        :return: сумма НДС или "Не применимо"
        """
        if self.order.taxes is not None and self.price is not None:
            return round(self.price * self.order.taxes / 100, 2)
        else:
            return 'Не применимо'

    def enumerate_ext_orders(self):
        """
        Назначает номера связанным исходящим поручениям
        :return: None
        """
        ext_orders = self.ext_orders.filter(contractor__isnull=False).order_by('created_at')
        if ext_orders.count() == 1:
            ext_orders.update(number=self.number)
        else:
            if self.number == self.order.inner_number:
                delimiter = '-'
            else:
                delimiter = '.'
            for t, ext_order in enumerate(ext_orders):
                ext_order.number = f'{self.number}{delimiter}{t + 1}'
                ext_order.save()

    def get_status_list(self):
        """
        Генерирует список допустимых статусов
        :return: список статусов
        """
        allowed = [self.status]

        if self.status == 'new':
            allowed.append('carrier_select')
        if self.status == 'carrier_select':
            allowed.append('pickup')
        if self.status == 'pickup':
            allowed += ['in_progress', 'temporary_storage', 'transit_storage']
        if self.status in ['in_progress', 'temporary_storage', 'transit_storage']:
            allowed.append('completed')

        allowed.append('rejected')

        return list(filter(lambda x: x[0] in allowed, TRANSIT_STATUS_LABELS))

    @staticmethod
    def update_status(sub_items_statuses):
        """
        Устанавливает статус перевозки в зависимости от статусов плеч
        :param sub_items_statuses: список статусов плеч
        :return: статус
        """
        mass_check = ('waiting', 'completed')
        mass_check = [i in sub_items_statuses for i in mass_check]
        if len(sub_items_statuses) == 1 and 'waiting' in sub_items_statuses:
            return 'pickup'
        elif len(sub_items_statuses) == 1 and 'completed' in sub_items_statuses:
            return 'completed'
        elif len(sub_items_statuses) > 1 and all([i in mass_check for i in sub_items_statuses]):  # !!!!!
            return 'transit_storage'
        elif 'in_progress' in sub_items_statuses:
            return 'in_progress'

    def filename(self):
        """
        Генерирует наименование файла ЭР
        :return: наименование файла
        """
        return self.number.replace('/', '_').replace('-', '_') + '.pdf'

    class Meta:
        verbose_name = 'перевозка'
        verbose_name_plural = 'перевозки'
        ordering = ['created_at']
        permissions = [
            ('view_all_transits', 'Can view all transits')
        ]

    def collect(self, related_name, *fields):
        """
        Использование метода collect класса RecalcMixin для перевозки
        """
        pass_to_order = list()
        notifications = list()

        queryset = self.__getattribute__(related_name).all()

        if related_name == 'cargos':
            if any([i in fields for i in ('weight', 'quantity', 'DELETE')]):
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
            if 'from_date_plan' in fields or 'DELETE' in fields:
                prev_value = self.from_date_plan
                self.from_date_plan = self.equal_to_min(queryset, 'from_date_plan')
                pass_to_order.append('from_date_plan')
                if prev_value != self.from_date_plan and self.from_date_plan is not None:
                    notifications.append(from_date_plan_manager_notification)
                    notifications.append(from_date_plan_client_notification)
                    notifications.append(from_date_plan_sender_notification)
            if 'from_date_fact' in fields or 'DELETE' in fields:
                prev_value = self.from_date_fact
                self.from_date_fact = self.equal_to_min(queryset, 'from_date_fact')
                pass_to_order.append('from_date_fact')
                if prev_value != self.from_date_fact and self.from_date_fact is not None:
                    notifications.append(from_date_fact_manager_notification)
                    notifications.append(from_date_fact_client_notification)
            if 'to_date_plan' in fields or 'DELETE' in fields:
                prev_value = self.to_date_plan
                self.to_date_plan = self.equal_to_max(queryset, 'to_date_plan', True)
                pass_to_order.append('to_date_plan')
                if prev_value != self.to_date_plan and self.to_date_plan is not None:
                    notifications.append(to_date_plan_manager_notification)
                    notifications.append(to_date_plan_client_notification)
                    notifications.append(to_date_plan_receiver_notification)
            if 'to_date_fact' in fields or 'DELETE' in fields:
                prev_value = self.to_date_fact
                self.to_date_fact = self.equal_to_max(queryset, 'to_date_fact', True)
                pass_to_order.append('to_date_fact')
                if prev_value != self.to_date_fact and self.to_date_fact is not None:
                    notifications.append(to_date_fact_manager_notification)
                    notifications.append(to_date_fact_client_notification)
            if 'status' in fields or 'DELETE' in fields:
                new_status = self.update_status(self.list_from_queryset(queryset, 'status', True))
                if new_status:
                    self.status = new_status
                    pass_to_order.append('status')
            if 'weight_payed' in fields or 'DELETE' in fields:
                self.weight_payed = self.equal_to_max(queryset, 'weight_payed')
        if related_name == 'ext_orders':
            if any([i in fields for i in ('price_carrier', 'currency', 'DELETE')]):
                self.price_carrier = self.sum_multicurrency_values(queryset, 'price_carrier', 'currency')
                pass_to_order.append('price_carrier')
        self.save()

        if pass_to_order:
            self.update_related('order', *pass_to_order)

        for notification in notifications:
            notification.delay(self.pk)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

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
        ('wooden_box', 'Деревянный ящик'),
        ('cardboard_box', 'Картонная коробка'),
        ('no_package', 'Без упаковки'),
        ('envelope', 'Конверт'),
        ('container', 'Контейнер'),
        ('package', 'Пакет'),
        ('pallet', 'Паллет'),
        ('bag', 'Мешок'),
        ('barrel', 'Бочка'),
        ('bucket', 'Ведро'),
        ('roll', 'Рулон'),
        ('pile', 'Навалом'),
        ('pack', 'Пачка'),
        ('big_bag', 'Биг бэг'),
        ('euroocube', 'Еврокуб'),
        ('coil', 'Катушка'),
        ('bale', 'Кипа'),
        ('safe_package', 'Сейф-пакет'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=True, blank=True, verbose_name='Создано')
    transit = models.ForeignKey(Transit, on_delete=models.CASCADE, verbose_name='Перевозка', related_name='cargos')
    title = models.CharField(max_length=255, verbose_name='Наименование груза', blank=True, null=True)
    package_type = models.CharField(max_length=255, choices=PACKAGE_TYPES, verbose_name='Тип упаковки',
                                    default=PACKAGE_TYPES[0][0])
    length = models.FloatField(verbose_name='Длина')
    width = models.FloatField(verbose_name='Ширина')
    height = models.FloatField(verbose_name='Высота')
    weight = models.FloatField(verbose_name='Вес, кг')
    quantity = models.IntegerField(verbose_name='Кол-во мест')
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


def path_by_order(instance, filename, month=None, year=None):
    if not month:
        month = instance.order.order_date.month
    if not year:
        year = instance.order.order_date.year
    return os.path.join(
        'files',
        'orders',
        str(year),
        '{:0>2}'.format(month),
        instance.order.id.hex,
        filename
    )


class Document(models.Model):
    title = models.CharField(max_length=255, verbose_name='Пояснение')
    file = models.FileField(upload_to=path_by_order, verbose_name='Файл')
    order = models.ForeignKey(Order, related_name='docs', on_delete=models.CASCADE, verbose_name='Поручение')
    public = models.BooleanField(default=False, verbose_name='Видно клиенту')

    def __str__(self):
        return f'{self.order}: {self.title} ({self.file.name})'

    def clean_in_fs(self):
        """
        Удаляет файл при удалении объекта из БД
        :return: None
        """
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


@receiver(post_save, sender=Document)
def order_added(sender, created, instance, **kwargs):
    if created:
        document_added_for_manager.delay(instance.pk)
    if instance.public:
        document_added_for_client.delay(instance.pk)


class ExtOrder(models.Model, RecalcMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=True, blank=True, verbose_name='Время создания')
    last_update = models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')

    number = models.CharField(max_length=255, verbose_name='Номер поручения')
    date = models.DateField(verbose_name='Дата поручения', default=timezone.now)
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE, related_name='ext_orders',
                                   verbose_name='Перевозчик', blank=True, null=True)
    contract = models.ForeignKey(ContractorContract, on_delete=models.PROTECT, verbose_name='Договор',
                                 blank=True, null=True)
    price_carrier = models.FloatField(verbose_name='Закупочная цена', default=0)
    taxes = models.IntegerField(verbose_name='НДС', blank=True, null=True, default=20, choices=TAXES)
    currency = models.CharField(max_length=3, choices=CURRENCIES, default='RUB', verbose_name='Валюта')

    transit = models.ForeignKey(Transit, on_delete=models.CASCADE, related_name='ext_orders')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='ext_orders')

    sender = models.ForeignKey(Counterparty, verbose_name='Отправитель', on_delete=models.PROTECT,
                               related_name='sent_ext_orders')
    take_from = models.CharField(max_length=255, verbose_name='Забрать груз у третьего лица', blank=True, null=True)
    from_contacts = models.ManyToManyField(Contact, verbose_name='Контактные лица', related_name='cnt_sent_ext_orders')
    from_addr = models.CharField(max_length=255, verbose_name='Адрес забора груза')
    from_addr_short = models.CharField(max_length=255, verbose_name='Пункт забора груза', blank=True, null=True)
    from_date_wanted = models.DateField(verbose_name='Дата готовности груза', blank=True, null=True)
    from_date_plan = models.DateField(verbose_name='Плановая дата забора груза', blank=True, null=True)
    from_date_fact = models.DateField(verbose_name='Фактическая дата забора груза', blank=True, null=True)

    receiver = models.ForeignKey(Counterparty, verbose_name='Получатель', on_delete=models.PROTECT,
                                 related_name='received_ext_orders')
    give_to = models.CharField(max_length=255, verbose_name='Передать груз третьему лицу', blank=True, null=True)
    to_contacts = models.ManyToManyField(Contact, verbose_name='Контактные лица', related_name='cnt_received_ext_orders')
    to_addr = models.CharField(max_length=255, verbose_name='Адрес доставки')
    to_addr_short = models.CharField(max_length=255, verbose_name='Пункт доставки', blank=True, null=True)
    to_date_wanted = models.DateField(verbose_name='Желаемая дата доставки', blank=True, null=True)
    to_date_plan = models.DateField(verbose_name='Плановая дата доставки', blank=True, null=True)
    to_date_fact = models.DateField(verbose_name='Фактическая дата доставки', blank=True, null=True)
    status = models.CharField(choices=EXT_ORDER_STATUS_LABELS, max_length=50, default=EXT_ORDER_STATUS_LABELS[0][0],
                              db_index=True, verbose_name='Статус поручения')
    other = models.TextField(verbose_name='Иное', blank=True, null=True)
    manager = models.ForeignKey(User, verbose_name='Менеджер', on_delete=models.SET_NULL, blank=True, null=True,
                                related_name='ext_orders')
    contractor_employee = models.ForeignKey(User, verbose_name='Сотрудник Перевозчика', on_delete=models.SET_NULL,
                                            blank=True, null=True, related_name='executing_orders')
    act_num = models.CharField(verbose_name='Акт №', max_length=255, blank=True, null=True)
    act_date = models.DateField(verbose_name='Дата акта', blank=True, null=True)
    bill_num = models.CharField(verbose_name='Счет №', max_length=255, blank=True, null=True)
    bill_date = models.DateField(verbose_name='Дата счета', blank=True, null=True)
    necessary_docs = models.CharField(verbose_name='Требуемые документы (для бланка ПЭ)', max_length=255,
                                      blank=True, null=True)

    def filename(self):
        """
        Генерирует наименование файла ЭР
        :return: наименование файла ЭР
        """
        return self.number.replace('/', '_').replace('-', '_') + '.pdf'

    def act_filename(self):
        """
        Генерирует наименование файла акта
        :return: наименование файла акта
        """
        return self.act_num.replace('/', '_').replace('-', '_') + '.pdf'

    def bill_filename(self):
        """
        Генерирует наименование файла счета
        :return: наименование файла счета
        """
        return self.bill_num.replace('/', '_').replace('-', '_') + '.pdf'

    def transport(self):
        """
        Генерирует строку из типов перевозки в связанных плечах
        :return: что-то вроде "Авто-Авиа-Авто"
        """
        return '-'.join([i.get_type_display() for i in self.segments.all()])

    def collect(self, related_name=None, *fields):
        """
        Использование метода collect класса RecalcMixin для исходящего поручения
        """
        pass_to_transit_from_segments = list()

        queryset = self.__getattribute__(related_name).all()

        if 'type' in fields or 'DELETE' in fields:
            pass_to_transit_from_segments.append('type')
        if 'from_date_plan' in fields or 'DELETE' in fields:
            self.from_date_plan = self.equal_to_min(queryset, 'from_date_plan')
            pass_to_transit_from_segments.append('from_date_plan')
        if 'from_date_fact' in fields or 'DELETE' in fields:
            self.from_date_fact = self.equal_to_min(queryset, 'from_date_fact')
            pass_to_transit_from_segments.append('from_date_fact')
        if 'to_date_plan' in fields or 'DELETE' in fields:
            self.to_date_plan = self.equal_to_max(queryset, 'to_date_plan', True)
            pass_to_transit_from_segments.append('to_date_plan')
        if 'to_date_fact' in fields or 'DELETE' in fields:
            self.to_date_fact = self.equal_to_max(queryset, 'to_date_fact', True)
            pass_to_transit_from_segments.append('to_date_fact')
        if 'weight_payed' in fields or 'DELETE' in fields:
            pass_to_transit_from_segments.append('weight_payed')
        if 'status' in fields or 'DELETE' in fields:
            new_status = self.update_status(self.list_from_queryset(queryset, 'status', True))
            if new_status:
                self.status = new_status
                pass_to_transit_from_segments.append('status')
        self.save()

        if pass_to_transit_from_segments:
            self.update_related('transit', *pass_to_transit_from_segments, related_name='segments')

    @staticmethod
    def update_status(sub_items_statuses):
        """
        Устанавливает статус исх. поручения в зависимости от статусов плеч
        :param sub_items_statuses: список статусов плеч
        :return: статус
        """
        mass_check = ('waiting', 'completed')
        mass_check = [i in sub_items_statuses for i in mass_check]
        if len(sub_items_statuses) == 1 and 'waiting' in sub_items_statuses:
            return 'pre_process'
        elif len(sub_items_statuses) == 1 and 'completed' in sub_items_statuses:
            return 'delivered'
        elif 'in_progress' in sub_items_statuses or all(mass_check):
            return 'in_progress'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not hasattr(self, 'order'):
            self.order = self.transit.order
        super(ExtOrder, self).save(force_insert, force_update, using, update_fields)

    def get_status_list(self):
        """
        Генерирует список допустимых статусов
        :return: список статусов
        """
        allowed = [self.status]

        if self.status == 'new':
            allowed.append('pre_process')
        if self.status == 'pre_process':
            allowed.append('in_progress')
        if self.status == 'in_progress':
            allowed.append('delivered')
        if self.status == 'delivered':
            allowed += ['bargain', 'awaiting_docs']
        if self.status == 'bargain':
            allowed.append('awaiting_docs')
        if self.status == 'awaiting_docs':
            allowed.append('completed')

        allowed.append('rejected')

        return list(filter(lambda x: x[0] in allowed, EXT_ORDER_STATUS_LABELS))

    class Meta:
        verbose_name = 'Исходящее поручение'
        verbose_name_plural = 'Исходящие поручения'
        permissions = [
            ('view_all_ext_orders', 'Can view all external orders')
        ]
        ordering = ['created_at']


class TransitSegment(models.Model, RecalcMixin):
    TYPES = [
        ('auto', 'Авто'),
        ('plane', 'Авиа'),
        ('rail', 'Ж/Д'),
        ('ship', 'Море'),
        ('combined', 'Сборный груз'),
        ('courier', 'Курьер')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=True, blank=True, verbose_name='Время создания')
    last_update = models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')

    transit = models.ForeignKey(Transit, on_delete=models.CASCADE, verbose_name='Перевозка', related_name='segments')
    ordering_num = models.IntegerField(verbose_name='Порядковый номер', blank=True, null=True)
    ext_order = models.ForeignKey(ExtOrder, on_delete=models.CASCADE, blank=True, null=True, related_name='segments',
                                  verbose_name='Исходящее поручение')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='segments', null=True, blank=True)

    api_id = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.IntegerField(verbose_name='Количество мест', default=0)
    weight_brut = models.FloatField(verbose_name='Вес брутто, кг', default=0)
    weight_payed = models.FloatField(verbose_name='Оплачиваемый вес, кг', default=0)
    sender = models.ForeignKey(Counterparty, verbose_name='Отправитель', on_delete=models.PROTECT,
                               related_name='sent_segments', blank=True, null=True)
    from_addr = models.CharField(max_length=255, verbose_name='Адрес забора груза', blank=True, null=True)
    from_addr_short = models.CharField(max_length=255, verbose_name='Пункт забора груза', blank=True, null=True)
    from_date_plan = models.DateField(verbose_name='Плановая дата забора груза', blank=True, null=True)
    from_date_fact = models.DateField(verbose_name='Фактическая дата забора груза', blank=True, null=True)
    receiver = models.ForeignKey(Counterparty, verbose_name='Получатель', on_delete=models.PROTECT,
                                 related_name='received_segments', blank=True, null=True)
    to_addr = models.CharField(max_length=255, verbose_name='Адрес доставки', blank=True, null=True)
    to_addr_short = models.CharField(max_length=255, verbose_name='Пункт доставки', blank=True, null=True)
    to_date_plan = models.DateField(verbose_name='Плановая дата доставки', blank=True, null=True)
    to_date_fact = models.DateField(verbose_name='Фактическая дата доставки', blank=True, null=True)
    type = models.CharField(choices=TYPES, max_length=50, db_index=True, verbose_name='Вид перевозки')
    price = models.FloatField(verbose_name='Ставка', default=0, blank=True, null=True) #
    price_carrier = models.FloatField(verbose_name='Закупочная цена', default=0, blank=True, null=True) #
    taxes = models.IntegerField(verbose_name='НДС', blank=True, null=True, default=20, choices=TAXES) #
    currency = models.CharField(max_length=3, choices=CURRENCIES, default='RUB', verbose_name='Валюта', blank=True, null=True) #
    carrier = models.ForeignKey(Contractor, on_delete=models.CASCADE, related_name='segments',
                                verbose_name='Перевозчик', blank=True, null=True)
    contract = models.CharField(max_length=255, verbose_name='Договор', blank=True, null=True)
    tracking_number = models.CharField(max_length=255, verbose_name='Номер транспортного документа', blank=True, #
                                       null=True)
    tracking_date = models.DateField(blank=True, null=True, verbose_name='Дата транспортного документа') #
    status = models.CharField(choices=SEGMENT_STATUS_LABELS, max_length=50, default=SEGMENT_STATUS_LABELS[0][0],
                              db_index=True, verbose_name='Статус перевозки')
    # comment = models.CharField(max_length=255, blank=True, null=True, verbose_name='Примечания')
    sub_carrier = models.CharField(max_length=255, blank=True, null=True, verbose_name='Субподрядчик')

    def get_status_list(self):
        """
        Генерирует список допустимых статусов
        :return: список статусов
        """
        allowed = [self.status]

        if self.status == 'waiting':
            allowed.append('in_progress')
        if self.status == 'in_progress':
            allowed.append('completed')

        allowed.append('rejected')

        return list(filter(lambda x: x[0] in allowed, SEGMENT_STATUS_LABELS))

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        self.transit = self.ext_order.transit
        self.order = self.ext_order.order

        super(TransitSegment, self).save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        super(TransitSegment, self).delete(using, keep_parents)
        self.update_related('transit', 'DELETE', related_name='segments')

    def update_from_docs(self):
        """
        Пересчитывает параметры плеча по приложенным сканам документов
        :return: None
        """
        if self.originals.exists():
            self.from_date_fact = max([doc.load_date for doc in self.originals.all()])
            self.quantity = sum([doc.quantity for doc in self.originals.all()])
            self.weight_brut = sum([doc.weight_brut for doc in self.originals.all()])
            self.weight_payed = sum([doc.weight_payed for doc in self.originals.all()])
            self.save()

    def __str__(self):
        if self.from_addr_short:
            from_addr = self.from_addr_short
        else:
            from_addr = self.from_addr
        if self.to_addr_short:
            to_addr = self.to_addr_short
        else:
            to_addr = self.to_addr
        return f'{from_addr} - {to_addr}'

    class Meta:
        ordering = ['ext_order', 'ordering_num']
        verbose_name = 'плечо перевозки'
        verbose_name_plural = 'плечи перевозки'
