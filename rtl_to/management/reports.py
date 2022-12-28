import datetime

from django.db import models

from orders.models import TransitSegment


class ReportGenerator:

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
        ('transit__take_from', 'Забрать груз у третьего лица'),
        ('transit__from_date_wanted', 'Дата готовности груза'),
        ('transit__from_date_plan', 'Плановая дата забора груза'),
        ('transit__from_date_fact', 'Фактическая дата забора груза'),
        ('transit__to_addr', 'Адрес доставки'),
        ('transit__receiver', 'Получатель'),
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
        ('transit__currency', 'Валюта страхования'),
        ('transit__bill_number', 'Номер счета'),
        ('ext_order__number', 'Номер исходящего поручения'),
        ('ext_order__date', 'Дата исходящего поручения'),
        ('ext_order__contractor', 'Перевозчик'),
        ('ext_order__contract', 'Договор'),
        ('ext_order__price_carrier', 'Ставка перевозчика'),
        ('ext_order__get_taxes_display', 'НДС'),
        ('ext_order__currency', 'Валюта'),
        ('ext_order__sender', 'Отправитель'),
        ('ext_order__take_from', 'Забрать груз у третьего лица'),
        ('ext_order__from_addr', 'Адрес забора груза'),
        ('ext_order__from_date_wanted', 'Дата готовности груза'),
        ('ext_order__from_date_plan', 'Плановая дата забора груза'),
        ('ext_order__from_date_fact', 'Фактическая дата забора груза'),
        ('ext_order__receiver', 'Получатель'),
        ('ext_order__give_to', 'Передать груз третьему лицу'),
        ('ext_order__to_addr', 'Адрес доставки'),
        ('ext_order__to_date_wanted', 'Желаемая дата доставки'),
        ('ext_order__to_date_plan', 'Плановая дата доставки'),
        ('ext_order__to_date_fact', 'Фактическая дата доставки'),
        ('ext_order__get_status_display', 'Статус поручения'),
        ('ext_order__manager', 'Менеджер'),
        ('ext_order__contractor_employee', 'Сотрудник Перевозчика'),
        ('segment__sender', 'Отправитель'),
        ('segment__from_addr', 'Адрес забора груза'),
        ('segment__from_date_plan', 'Плановая дата забора груза'),
        ('segment__from_date_fact', 'Фактическая дата забора груза'),
        ('segment__receiver', 'Получатель'),
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
        self.requested_fields = [i for i in fields if i in self.mapper]
        self.filters = filters

    def fields_list(self):
        result = dict()
        for field_name, label in self.__FIELDS:
            model_label = field_name.split('__')[0]
            if model_label not in result:
                result[model_label] = tuple()
            result[model_label] = (*result[model_label], (field_name, label))
        return result

    @staticmethod
    def get_field(obj, field):
        field_list = field.split('__')
        if field_list[0] == 'segment':
            field_list = field_list[1:]
        value = obj
        for f in field_list:
            if hasattr(value, f):
                value = value.__getattribute__(f)
                if callable(value):
                    value = value()
            else:
                return ''

        if isinstance(value, datetime.date):
            return value.strftime('%d.%m.%Y')
        elif isinstance(value, datetime.datetime):
            return value.strftime('%d.%m.%Y %H:%M:%S')
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

    def collect_fields(self, obj, fields):
        return [self.get_field(obj, field) for field in fields]

    def serialize(self):
        result = list()
        queryset = TransitSegment.objects.filter(**self.filters)
        for obj in queryset:
            serialized = self.collect_fields(obj, self.requested_fields)
            if serialized not in result:
                result.append(serialized)
        return result

    def fields_verbose(self):
        return [self.mapper[i] for i in self.requested_fields]
