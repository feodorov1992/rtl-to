import datetime
import uuid

from django.db import models
from django.utils.encoding import is_protected_type

from orders.models import Order, TransitSegment, Transit
from itertools import chain


class Config:
    MODEL_CLASS = None
    QUERYSET_PATH = None
    NECESSARY_FIELDS = None
    PROTECTED_FIELDS = None
    EXCLUDED_FIELDS = None
    RELATED_FIELDS = None

    def __setattr__(self, key, value):
        pass


class OrderConfig(Config):
    MODEL_CLASS = Order
    QUERYSET_PATH = []
    NECESSARY_FIELDS = ['id', 'created_at', 'last_update', 'client_number']
    PROTECTED_FIELDS = ['inner_number', 'price_carrier']
    EXCLUDED_FIELDS = ['from_addr_forlist', 'to_addr_forlist']
    RELATED_FIELDS = {
        'client': {
            'path': ['client'],
            'verbose_name': 'Заказчик',
        },
        'client__name': {
            'path': ['client', 'short_name'],
            'verbose_name': 'Юр. наименование заказчика'
        },
        'client__inn': {
            'path': ['client', 'inn'],
            'verbose_name': 'ИНН заказчика'
        },
    }


class TransitConfig(Config):
    MODEL_CLASS = Transit
    QUERYSET_PATH = ['transits']
    NECESSARY_FIELDS = ['id', 'created_at', 'last_update', 'sub_number']
    PROTECTED_FIELDS = ['price_carrier']
    EXCLUDED_FIELDS = ['api_id', 'from_org', 'from_inn', 'from_legal_addr', 'from_contact_name', 'from_contact_phone',
                       'from_contact_email', 'to_org', 'to_inn', 'to_legal_addr', 'to_contact_name', 'to_contact_phone',
                       'to_contact_email']
    RELATED_FIELDS = {
        'sender': {
            'path': ['sender'],
            'verbose_name': 'Отправитель'
        },
        'sender__name': {
            'path': ['sender', 'short_name'],
            'verbose_name': 'Юр. наименование отправителя',
            'if_not': 'from_org'
        },
        'sender__legal_address': {
            'path': ['sender', 'legal_address'],
            'verbose_name': 'Юр. адрес отправителя',
            'if_not': 'from_legal_addr'
        },
        'sender__inn': {
            'path': ['sender', 'inn'],
            'verbose_name': 'ИНН отправителя',
            'if_not': 'from_inn'
        },
        'receiver': {
            'path': ['receiver'],
            'verbose_name': 'Получатель'
        },
        'receiver__name': {
            'path': ['receiver', 'short_name'],
            'verbose_name': 'Юр. наименование получателя',
            'if_not': 'to_org'
        },
        'receiver__legal_address': {
            'path': ['receiver', 'legal_address'],
            'verbose_name': 'Юр. адрес получателя',
            'if_not': 'to_legal_addr'
        },
        'receiver__inn': {
            'path': ['receiver', 'inn'],
            'verbose_name': 'ИНН получателя',
            'if_not': 'to_inn'
        },
    }


class SegmentConfig(Config):
    MODEL_CLASS = TransitSegment
    QUERYSET_PATH = ['transits', 'segments']
    NECESSARY_FIELDS = ['id', 'created_at', 'last_update']
    PROTECTED_FIELDS = ['price_carrier']
    EXCLUDED_FIELDS = ['api_id']
    RELATED_FIELDS = {
        'carrier': {
            'path': ['carrier'],
            'verbose_name': 'Перевозчик',
            'if_not': ''
        },
        'carrier__name': {
            'path': ['carrier', 'short_name'],
            'verbose_name': 'Юр. наименование перевозчика',
            'if_not': ''
        },
        'carrier__inn': {
            'path': ['carrier', 'inn'],
            'verbose_name': 'ИНН перевозчика',
            'if_not': ''
        },
    }


router = {
        'order': OrderConfig,
        'transit': TransitConfig,
        'segment': SegmentConfig
    }


def get_config(model_label: str):

    if model_label not in router:
        raise AttributeError(f'Allowed model_label values are: {", ".join(router.keys())}')

    return router.get(model_label)


class FieldsMapper:

    def __init__(self):
        self.__raw_report = None

    @staticmethod
    def __simple_fields_collector(config, exclude, name_prefix):
        model = config.MODEL_CLASS
        for field in model._meta.get_fields():
            if field.name not in exclude and not field.is_relation:
                name = '__'.join([name_prefix, field.name])
                verbose = field.verbose_name
                yield Field(name, verbose, choices=field.choices)

    @staticmethod
    def __related_fields_collector(config, exclude, name_prefix):
        for field in config.RELATED_FIELDS:
            if field not in exclude:
                name = '__'.join([name_prefix, field])
                verbose = config.RELATED_FIELDS[field]['verbose_name']
                path = config.RELATED_FIELDS[field]['path']
                if_no_val = config.RELATED_FIELDS[field].get('if_not')
                yield Field(name, verbose, rel_path=path, if_no_val=if_no_val)

    def __collect_model_fields(self, model_label, exclude_protected: bool = False, exclude_necessary: bool = False):
        config = router[model_label]
        exclude = config.EXCLUDED_FIELDS.copy()

        if exclude_necessary:
            exclude += config.NECESSARY_FIELDS
        if exclude_protected:
            exclude += config.PROTECTED_FIELDS
        return chain(self.__simple_fields_collector(config, exclude, model_label),
                     self.__related_fields_collector(config, exclude, model_label))

    def get_fields_list(self, model_label, exclude_protected: bool = False, exclude_necessary: bool = False):
        return [
            (i.name, i.verbose_name) for i in
            self.__collect_model_fields(model_label, exclude_protected, exclude_necessary)
        ]

    def collect_object_data(self, obj, model_label, fields_list: list = None):
        result = list()
        if fields_list is None:
            fields_list = []
        else:
            fields_list = [i.split('__', maxsplit=1)[-1] for i in fields_list]
        for field in self.__collect_model_fields(model_label):
            if field.local_name in fields_list + router[model_label].NECESSARY_FIELDS:
                result.append(field.serialized(obj))
        return result

    def collect_fields_data(
            self,
            order_fields: list = None,
            order_filters: dict = None,
            transit_fields: list = None,
            transit_filters: dict = None,
            segment_fields: list = None,
            segment_filters: dict = None
    ):
        result = list()
        order_queryset = Order.objects.filter(**order_filters) if order_filters else Order.objects.all()
        if segment_fields:
            for order in order_queryset:
                order_tail = self.collect_object_data(order, 'order', order_fields)
                transit_queryset = order.transits.filter(
                    **transit_filters) if transit_filters else order.transits.all()
                for transit in transit_queryset:
                    transit_tail = order_tail + self.collect_object_data(transit, 'transit', transit_fields)
                    segment_queryset = transit.segments.filter(
                        **segment_filters) if segment_filters else transit.segments.all()
                    for segment in segment_queryset:
                        result.append(transit_tail + self.collect_object_data(segment, 'segment', segment_fields))

        elif transit_fields:
            for order in order_queryset:
                order_tail = self.collect_object_data(order, 'order', order_fields)
                transit_queryset = order.transits.filter(
                    **transit_filters) if transit_filters is not None else order.transits.all()
                for transit in transit_queryset:
                    result.append(order_tail + self.collect_object_data(transit, 'transit', transit_fields))
        else:
            for order in order_queryset:
                result.append(self.collect_object_data(order, 'order', order_fields))

        self.__raw_report = result

    def web_output(self):
        fields_counter = {
            'order': 0,
            'transit': 0,
            'segment': 0
        }
        data = list()
        header = list()
        if self.__raw_report:
            header = [i.verbose_name for i in self.__raw_report[0]]
            for key in fields_counter:
                fields_counter[key] = len([i for i in self.__raw_report[0] if i.name.startswith(key)])
            for row in self.__raw_report:
                data_row = list()
                for field in row:
                    if isinstance(field.value, bool):
                        data_row.append('Да' if field.value else 'Нет')
                    else:
                        data_row.append(field.value)
                data.append(data_row)
        return data, header, fields_counter

    def csv_output(self):
        data = list()
        header = list()
        if self.__raw_report:
            for field in self.__raw_report[0]:
                model_label, _ = field.name.split('__', maxsplit=1)
                model_verbose_name = router[model_label].MODEL_CLASS._meta.verbose_name
                header.append(f'{field.verbose_name} ({model_verbose_name})')
            for row in self.__raw_report:
                data_row = list()
                for field in row:
                    if isinstance(field.value, datetime.datetime):
                        data_row.append(field.value.strftime('%d.%m.%Y %H:%M:%S'))
                    elif isinstance(field.value, datetime.date):
                        data_row.append(field.value.strftime('%d.%m.%Y'))
                    elif isinstance(field.value, uuid.UUID):
                        data_row.append(str(field.value))
                    else:
                        data_row.append(field.value)
                data.append(data_row)
        return data, header


class Field:

    def __init__(self, field_name, verbose_name, rel_path: list = None, if_no_val: str = None, choices: list = None):
        self.name = field_name
        self.local_name = self.name.split('__', maxsplit=1)[-1]
        self.verbose_name = verbose_name
        self.rel_path = rel_path
        self.if_no_val = if_no_val
        self.choices = {i[0]: i[1] for i in choices} if choices else {}

    def get_value(self, obj):
        if self.rel_path:
            res = obj
            for chunk in self.rel_path:
                if res is not None:
                    res = res.__getattribute__(chunk)
                else:
                    if self.if_no_val is not None:
                        return obj.__getattribute__(self.if_no_val)
                    return
            return res
        elif self.choices:
            return self.choices[obj.__getattribute__(self.local_name)]
        else:
            return obj.__getattribute__(self.local_name)

    def serialized(self, obj):
        return SerializedField(self.name, self.verbose_name, self.get_value(obj))


class SerializedField:

    def __init__(self, name, verbose_name, value):
        self.name = name
        self.verbose_name = verbose_name
        self.value = value if value is not None else ''
