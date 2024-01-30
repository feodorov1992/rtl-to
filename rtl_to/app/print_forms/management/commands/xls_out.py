import uuid

import xlwt
import datetime
from django.contrib.postgres.aggregates import StringAgg
from django.core.management.base import BaseCommand
from django.db import connection, models
from django.db.models import F, FileField
from django.db.models.fields.related import ForeignKey
from django.utils import timezone
from django.apps import apps


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.__all_models = {model.__name__: model for model in apps.get_models()}

    def add_arguments(self, parser):
        parser.add_argument("models", nargs="*", type=str,
                            help=f'Models for output', choices=self.__all_models.keys())
        parser.add_argument("-o", "--output", type=str, default='/tmp/output.xls',
                            help='Output file path strictly in XLS format. Default is /tmp/output.xls')

    @staticmethod
    def fields_verbose_names(model):
        return [field.verbose_name for field in model._meta.fields if not isinstance(field, FileField)]

    @staticmethod
    def fields_names(model):
        return [field.name for field in model._meta.fields if not isinstance(field, FileField)]

    @staticmethod
    def fk_field_names(model):
        result = list()
        for field in model._meta.fields:
            if isinstance(field, ForeignKey):
                result.append(field.name)
        return result

    @staticmethod
    def m2m_field_names(model):
        return {field.name: field.verbose_name for field in model._meta.many_to_many}

    @staticmethod
    def model_verbose_name(model):
        return model._meta.verbose_name_plural.capitalize()

    @staticmethod
    def write_header(sheet, field_names):
        style = xlwt.XFStyle()
        style.font.bold = True
        for column, item in enumerate(field_names):
            sheet.write(0, column, str(item), style)

    @staticmethod
    def get_queryset(model, select_related, m2m_fields):
        queryset = model.objects.all()
        if select_related:
            queryset = queryset.select_related(*select_related)
        if m2m_fields:
            queryset = queryset.prefetch_related(*m2m_fields)
        return queryset

    @staticmethod
    def get_value(obj, field_name, m2m_fields):

        fields = {field.name: field for field in obj.__class__._meta.fields}
        if field_name in m2m_fields:
            return ', '.join([str(i) for i in obj.__getattribute__(field_name).all()])
        elif field_name in fields and fields.get(field_name).choices:
            return obj.__getattribute__(f'get_{field_name}_display')()

        value = obj.__getattribute__(field_name)

        if value is None:
            value = ''
        elif isinstance(value, uuid.UUID) or isinstance(value, models.Model):
            value = str(value)
        return value

    @staticmethod
    def get_style(value):
        if isinstance(value, datetime.datetime):
            return 'DD/MM/YYYY hh:mm:ss'
        elif isinstance(value, datetime.date):
            return 'DD/MM/YYYY'
        elif isinstance(value, float):
            return '#,##0.00'
        return 'General'

    def write_body(self, sheet, model, m2m_fields=None):
        field_names = self.fields_names(model)
        if m2m_fields and isinstance(m2m_fields, list):
            field_names += m2m_fields
        queryset = self.get_queryset(model, self.fk_field_names(model), m2m_fields)
        style = xlwt.XFStyle()
        for i, obj in enumerate(queryset):
            for column, field in enumerate(field_names):
                value = self.get_value(obj, field, m2m_fields)
                style.num_format_str = self.get_style(value)
                sheet.write(i + 1, column, value, style)

    def handle(self, *args, **options):
        excel = xlwt.Workbook(encoding='cp1251')
        check_postgres = connection.vendor == 'postgresql'
        for model_name in options.get('models', []):
            model = self.__all_models.get(model_name)
            sheet = excel.add_sheet(self.model_verbose_name(model))
            verbose_names = self.fields_verbose_names(model)
            m2m_fields = None
            if check_postgres:
                m2m_data = self.m2m_field_names(model)
                m2m_fields = list(m2m_data.keys())
                verbose_names = verbose_names + list(m2m_data.values())
            self.write_header(sheet, verbose_names)
            self.write_body(sheet, model, m2m_fields)

        excel.save(options.get('output'))

