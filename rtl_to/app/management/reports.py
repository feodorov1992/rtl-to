import datetime
import uuid

from django.apps import apps
from django.db import models


class ReportGenerator:
    """
    Генератор отчетов менеджера
    """

    __DEFAULT_MODEL_LABEL = 'segment'

    __PREFIXES_ROUTER = {
        'order': 'Order',
        'transit': 'Transit',
        'ext_order': 'ExtOrder',
        'segment': 'TransitSegment'
    }

    __FIELDS = (
        ('order__client_number', 'Номер поручения'),
        ('order__inner_number', 'Внутренний номер'),
        ('order__order_date', 'Дата поручения'),
        ('order__manager', 'Менеджер'),
        ('order__client', 'Заказчик'),
        ('order__contract', 'Договор'),
        ('order__client_employee', 'Сотрудник заказчика'),
        ('order__get_type_display', 'Вид поручения'),
        ('order__get_status_display', 'Статус поручения'),
        ('order__from_date_plan', 'Дата начала перевозок (план)'),
        ('order__from_date_fact', 'Дата начала перевозок (факт)'),
        ('order__to_date_plan', 'Дата завершения перевозок (план)'),
        ('order__to_date_fact', 'Дата завершения перевозок (факт)'),
        ('order__price', 'Ставка заказчика'),
        ('order__price_carrier', 'Суммарная ставка перевозчиков'),
        ('order__get_taxes_display', 'НДС'),
        ('order__re_submission', 'Перевыставление'),
        ('order__insurance', 'Страхование требуется'),
        ('order__value', 'Заявленная стоимость груза'),
        ('order__sum_insured_coeff', '% страховой суммы'),
        ('order__insurance_currency', 'Валюта страхования'),
        ('order__insurance_premium_coeff', 'Коэффициент страховой премии'),
        ('order__insurance_policy_number', '№ полиса'),
        ('order__cargo_name', 'Общее наименование груза'),
        ('order__cargo_origin', 'Страна происхождения груза'),
        ('transit__number', 'Номер маршрута'),
        ('transit__volume', 'Объем груза, м3'),
        ('transit__weight', 'Вес брутто, кг'),
        ('transit__quantity', 'Количество мест'),
        ('transit__from_addr', 'Адрес забора груза'),
        ('transit__sender', 'Отправитель'),
        ('transit__sender__inn', 'ИНН Отправителя'),
        ('transit__sender__legal_address', 'Юр. Адрес Отправителя'),
        ('transit__take_from', 'Забрать груз у третьего лица'),
        ('transit__from_date_wanted', 'Дата готовности груза'),
        ('transit__from_date_plan', 'Плановая дата забора груза'),
        ('transit__from_date_fact', 'Фактическая дата забора груза'),
        ('transit__to_addr', 'Адрес доставки'),
        ('transit__receiver', 'Получатель'),
        ('transit__receiver__inn', 'ИНН Получателя'),
        ('transit__receiver__legal_address', 'Юр. Адрес Получателя'),
        ('transit__give_to', 'Передать груз третьему лицу'),
        ('transit__to_date_wanted', 'Желаемая дата доставки'),
        ('transit__to_date_plan', 'Плановая дата доставки'),
        ('transit__to_date_fact', 'Фактическая дата доставки'),
        ('transit__type', 'Вид перевозки'),
        ('transit__price', 'Ставка заказчика'),
        ('transit__price_currency', 'Валюта ставки'),
        ('transit__price_carrier', 'Закупочная цена маршрута'),
        ('transit__get_status_display', 'Статус перевозки'),
        ('transit__value', 'Заявленная стоимость груза'),
        ('transit__sum_insured', 'Страховая сумма'),
        ('transit__insurance_premium', 'Страховая премия'),
        ('transit__currency', 'Валюта стоимости груза'),
        ('transit__bill_number', 'Номер счета'),
        ('ext_order__number', 'Номер исходящего поручения'),
        ('ext_order__date', 'Дата исходящего поручения'),
        ('ext_order__contractor', 'Перевозчик'),
        ('ext_order__contract', 'Договор'),
        ('ext_order__approx_price', 'Приблизительная ставка'),
        ('ext_order__price_carrier', 'Ставка перевозчика'),
        ('ext_order__get_taxes_display', 'НДС'),
        ('ext_order__currency', 'Валюта'),
        ('ext_order__sender', 'Отправитель'),
        ('ext_order__sender__inn', 'ИНН Отправителя'),
        ('ext_order__sender__legal_address', 'Юр. Адрес Отправителя'),
        ('ext_order__take_from', 'Забрать груз у третьего лица'),
        ('ext_order__from_addr', 'Адрес забора груза'),
        ('ext_order__from_date_wanted', 'Дата готовности груза'),
        ('ext_order__from_date_plan', 'Плановая дата забора груза'),
        ('ext_order__from_date_fact', 'Фактическая дата забора груза'),
        ('ext_order__receiver', 'Получатель'),
        ('ext_order__receiver__inn', 'ИНН Получателя'),
        ('ext_order__receiver__legal_address', 'Юр. Адрес Получателя'),
        ('ext_order__give_to', 'Передать груз третьему лицу'),
        ('ext_order__to_addr', 'Адрес доставки'),
        ('ext_order__to_date_wanted', 'Желаемая дата доставки'),
        ('ext_order__to_date_plan', 'Плановая дата доставки'),
        ('ext_order__to_date_fact', 'Фактическая дата доставки'),
        ('ext_order__get_status_display', 'Статус поручения'),
        ('ext_order__manager', 'Менеджер'),
        ('ext_order__contractor_employee', 'Сотрудник Перевозчика'),
        ('segment__sender', 'Отправитель'),
        ('segment__sender__inn', 'ИНН Отправителя'),
        ('segment__sender__legal_address', 'Юр. Адрес Отправителя'),
        ('segment__from_addr', 'Адрес забора груза'),
        ('segment__from_date_plan', 'Плановая дата забора груза'),
        ('segment__from_date_fact', 'Фактическая дата забора груза'),
        ('segment__receiver', 'Получатель'),
        ('segment__receiver__inn', 'ИНН Получателя'),
        ('segment__receiver__legal_address', 'Юр. Адрес Получателя'),
        ('segment__to_addr', 'Адрес доставки'),
        ('segment__to_date_plan', 'Плановая дата доставки'),
        ('segment__to_date_fact', 'Фактическая дата доставки'),
        ('segment__quantity', 'Количество мест'),
        ('segment__weight_brut', 'Вес брутто, кг'),
        ('segment__weight_payed', 'Оплачиваемый вес, кг'),
        ('segment__get_type_display', 'Тип плеча'),
        ('segment__get_status_display', 'Статус плеча')
    )

    def __init__(self, fields: list, **filters):
        self.mapper = dict(self.__FIELDS)
        self.requested_fields = fields
        self.model_label = self.get_model_label()
        self.model = self.get_model()
        self.requested_fields = self.get_fields_list(self.requested_fields)
        self.filters = self.get_filters(filters)

    @property
    def __prefix_weights(self):
        result = dict()
        for t, i in enumerate(self.__PREFIXES_ROUTER):
            result[i] = t
        return result

    def get_model_label(self):
        used_models = list(set([i.split('__')[0] for i in self.requested_fields]))
        used_models.sort(key=lambda x: self.__prefix_weights.get(x))
        if used_models:
            return used_models[-1]
        return self.__DEFAULT_MODEL_LABEL

    def get_model(self):
        return apps.get_model('orders', self.__PREFIXES_ROUTER[self.model_label])

    def get_fields_list(self, fields):
        result = list()
        for field in fields:
            if field in self.mapper:
                if field.startswith(self.model_label):
                    result.append((field.split('__')[1:], self.mapper[field]))
                else:
                    result.append((field.split('__'), self.mapper[field]))
        return result

    def get_filters(self, filters: dict):
        result = dict()
        for old_key, value in filters.items():
            old_key_prefix = old_key.split('__')[0]
            if old_key_prefix == self.model_label:
                new_key = '__'.join(old_key.split('__')[1:])
            elif self.__prefix_weights[old_key_prefix] > self.__prefix_weights[self.model_label]:
                continue
            else:
                new_key = old_key
            result[new_key] = value
        return result

    def fields_list(self) -> dict:
        """
        Разбивка списка полей отчета по принодлежности к моделям
        :return: словарь с набором полей для каждой модели
        """
        result = dict()
        for field_name, label in self.__FIELDS:
            model_label = field_name.split('__')[0]
            if model_label not in result:
                result[model_label] = tuple()
            result[model_label] = (*result[model_label], (field_name, label))
        return result

    @staticmethod
    def get_field(obj: models.Model, field_list: str):
        """
        Готовит к выводу значение поля объекта
        :param obj: объект, в котором ищется поле
        :param field_list: наименование искомого поля
        :return: значение поля (с защитой)
        """
        value = obj
        for f in field_list:
            if hasattr(value, f):
                value = value.__getattribute__(f)
                if callable(value):
                    value = value()
            else:
                return ''

        if isinstance(value, datetime.datetime):
            return value.replace(tzinfo=None)
        elif isinstance(value, uuid.UUID):
            return str(value)
        elif isinstance(value, models.Model):
            return str(value)
        elif isinstance(value, bool):
            if value:
                return 'Да'
            return 'Нет'
        elif value is None:
            return ''
        else:
            return value

    def collect_fields(self, obj: models.Model, fields: list) -> list:
        """
        Сборщик набора значений полей объекта
        :param obj: объект поиска
        :param fields: набор наименование полей
        :return: набор значений полей
        """
        return [self.get_field(obj, field[0]) for field in fields]

    def serialize(self):
        """
        Сборщик данных для отчета из набора объектов искомых моделей
        :return: готовый к выводу в отчет набор данных
        """
        result = list()
        queryset = self.model.objects.filter(**self.filters)
        for obj in queryset:
            serialized = self.collect_fields(obj, self.requested_fields)
            if serialized not in result:
                result.append(serialized)
        return result

    def fields_verbose(self):
        """
        Сборщик человекочитаемых наименований выбранных полей
        :return: набор наименований полей
        """
        return [i[-1] for i in self.requested_fields]
