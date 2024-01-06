import uuid

from django.db import models
from django.template.defaultfilters import floatformat
from django.utils import timezone

from app_auth.models import CurrencyRate
from orders.models import Order, TAXES, CURRENCIES, Transit
from print_forms.models import DocOriginal, TransDocsData


class OrderPrice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    last_update = models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')
    order = models.OneToOneField(Order, verbose_name='Входящее поручение', on_delete=models.CASCADE)
    price_date = models.DateField(verbose_name='Дата ставки')
    multi_currency_string = models.CharField(max_length=255, verbose_name='Сумма', blank=True, null=True)
    rub_equivalent = models.FloatField(verbose_name='Рублевый эквивалент', blank=True, null=True)

    def get_rate_date(self):
        today = timezone.now().date()
        if self.price_date > today:
            return today
        return self.price_date

    def update_pricing(self, save=True):
        rate = CurrencyRate.objects.get_or_create(date=self.get_rate_date())[0]
        sums = self.positions.values_list('currency').annotate(sum_value=models.Sum('value'))
        self.multi_currency_string = '; '.join([f'{floatformat(value, -2)} {currency}' for currency, value in sums])
        self.rub_equivalent = round(sum([value * rate.__getattribute__(currency) for currency, value in sums]), 2)
        if save:
            self.save()

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.positions.exists():
            self.update_pricing(False)
        super(OrderPrice, self).save(force_insert, force_update, using, update_fields)


class BillPosition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    last_update = models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')
    transit = models.ForeignKey(Transit, verbose_name='Перевозка', on_delete=models.CASCADE, related_name='positions')
    order_price = models.ForeignKey(OrderPrice, verbose_name='Суммирующая ставка', on_delete=models.CASCADE,
                                    related_name='positions')
    value = models.FloatField(verbose_name='Сумма')
    currency = models.CharField(max_length=3, choices=CURRENCIES, verbose_name='Валюта')
    taxes = models.IntegerField(verbose_name='НДС', blank=True, null=True, default=20, choices=TAXES)
    bill_number = models.CharField(max_length=100, verbose_name='Номер счета', blank=True, null=True)
    run_start = models.TextField(blank=True, null=True, verbose_name='Начало маршрута')
    run_end = models.TextField(blank=True, null=True, verbose_name='Конец маршрута')
    docs_list = models.TextField(blank=True, null=True, verbose_name='Номера транспортных документов')
    from_date_fact = models.DateField(verbose_name='Фактическая дата забора груза', blank=True, null=True)
    to_date_fact = models.DateField(verbose_name='Фактическая дата доставки', blank=True, null=True)
    quantity = models.IntegerField(verbose_name='Количество мест', default=0, blank=True, null=True)
    weight_payed = models.FloatField(verbose_name='Оплачиваемый вес', default=0, blank=True, null=True)
    value_wo_taxes = models.FloatField(verbose_name='Сумма без НДС', blank=True, null=True)
    taxes_value = models.FloatField(verbose_name='Сумма НДС', blank=True, null=True)

    @staticmethod
    def bill_run_item(obj, cp_field_name, addr_field_name):
        cp = obj.__getattribute__(cp_field_name)
        if cp is None:
            return obj.__getattribute__(addr_field_name)
        result = list()
        result.append(cp.short_name)
        if cp.inn:
            result.append(f'ИНН {cp.inn}')
        result.append(f'{cp.legal_address} / {obj.__getattribute__(addr_field_name)}')
        return ', '.join(result)

    @staticmethod
    def doc_as_string(doc_type, doc_type_verbose, doc_number, doc_date):
        if doc_type == 'auto':
            return f'{doc_type_verbose} №{doc_number} от {doc_date.strftime("%d.%m.%Y")}'
        return f'{doc_type_verbose} №{doc_number}'

    def get_docs(self):
        segment_pks = self.segments.values_list('pk', flat=True)
        origs = DocOriginal.objects.filter(segment_id__in=segment_pks)
        result = list()
        if origs.exists():
            for orig in origs:
                result.append(
                    self.doc_as_string(orig.doc_type, orig.get_doc_type_display(), orig.doc_number, orig.doc_date)
                )
        else:
            for blank in TransDocsData.objects.filter(segment_id__in=segment_pks):
                doc_number = blank.doc_num_trans if blank.doc_num_trans else blank.doc_number
                doc_date = blank.doc_date_trans if blank.doc_date_trans else blank.doc_date
                result.append(self.doc_as_string(blank.doc_type, blank.get_doc_type_display(), doc_number, doc_date))
        return ', '.join(result)

    def update_from_segments(self):
        if self.segments.exists():
            self.run_start = self.bill_run_item(self.segments.first(), 'sender', 'from_addr')
            self.from_date_fact = self.segments.first().from_date_fact
            self.run_end = self.bill_run_item(self.segments.last(), 'receiver', 'to_addr')
            self.to_date_fact = self.segments.last().to_date_fact
            self.docs_list = self.get_docs()
            cargo_params = self.segments.aggregate(quantity=models.Max('quantity'),
                                                   weight_payed=models.Max('weight_payed'))
            self.quantity = cargo_params.get('quantity')
            self.weight_payed = cargo_params.get('weight_payed')
            self.save()

    def recalc_taxes(self):
        if self.taxes is None:
            self.taxes_value = None
            self.value_wo_taxes = self.value
        else:
            self.taxes_value = round(self.value / (100 + self.taxes) * self.taxes, 2)
            self.value_wo_taxes = round(self.value - self.taxes_value, 2)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.recalc_taxes()
        super(BillPosition, self).save(force_insert, force_update, using, update_fields)
