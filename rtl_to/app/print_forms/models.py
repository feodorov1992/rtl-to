import os
import uuid

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from orders.models import TransitSegment, ExtOrder, Transit, Document
from print_forms.tasks import transport_added_for_manager, transport_added_for_client

DOC_TYPES = (
    ('auto', 'ТН'),
    ('cmr', 'CMR'),
    ('plane', 'AWB'),
    ('rail', 'СМГС'),
    ('ship', 'Коносамент'),
    ('combined', 'ТН'),
    ('courier', 'ТН')
)


def path_by_order(instance, filename, month=None, year=None):
    if not month:
        month = instance.transit.order.order_date.month
    if not year:
        year = instance.transit.order.order_date.year
    return os.path.join(
        'files',
        'orders',
        str(year),
        '{:0>2}'.format(month),
        instance.transit.order.id.hex,
        filename
    )


class DocOriginal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=True, blank=True, verbose_name='Время создания')
    last_update = models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')
    segment = models.ForeignKey(TransitSegment, on_delete=models.CASCADE, verbose_name='Плечо перевозки',
                                related_name='originals')
    transit = models.ForeignKey(Transit, on_delete=models.CASCADE, blank=True, null=True,
                                verbose_name='Перевозка', related_name='originals')

    doc_type = models.CharField(max_length=50, verbose_name='Тип накладной', choices=DOC_TYPES)
    doc_number = models.CharField(max_length=100, verbose_name='Номер')
    doc_date = models.DateField(verbose_name='Дата документа')
    quantity = models.IntegerField(verbose_name='Количество мест', default=0)
    weight_brut = models.FloatField(verbose_name='Вес брутто, кг', default=0)
    weight_payed = models.FloatField(verbose_name='Оплачиваемый вес, кг', default=0)
    load_date = models.DateField(verbose_name='Дата погрузки')
    td_file = models.FileField(upload_to=path_by_order, verbose_name='Скан накладной')

    def __str__(self):
        return f'{self.get_doc_type_display()} №{self.doc_number}'

    @staticmethod
    def save_scan_to_order(order, file, doc_title):
        if order.docs.filter(title=doc_title).exists():
            doc = order.docs.get(title=doc_title)
        else:
            doc = Document(order=order)
        doc.file = file
        doc.title = doc_title
        doc.public = True
        doc.save()

    @staticmethod
    def del_scan_from_order(order, doc_title):
        order.docs.filter(title=doc_title).delete()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(DocOriginal, self).save(force_insert, force_update, using, update_fields)
        self.segment.update_from_docs()
        self.transit.collect('segments', 'weight_brut', 'quantity')
        self.save_scan_to_order(self.transit.order, self.td_file, str(self))
        self.transit.docs_list_update()
        self.segment.ext_order.docs_list_update()

    def delete(self, using=None, keep_parents=False):
        self.del_scan_from_order(self.transit.order, str(self))
        super(DocOriginal, self).delete(using, keep_parents)
        self.segment.update_from_docs()
        self.transit.collect('segments', 'weight_brut', 'quantity')
        self.transit.docs_list_update()
        self.segment.ext_order.docs_list_update()

    def get_file_name(self):
        return os.path.basename(self.td_file.path)

    class Meta:
        verbose_name = 'скан'
        verbose_name_plural = 'сканы'
        unique_together = 'transit', 'doc_type', 'doc_number'


class ShippingReceiptOriginal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=True, blank=True, verbose_name='Время создания')
    last_update = models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')
    segment = models.ForeignKey(TransitSegment, on_delete=models.CASCADE, verbose_name='Плечо перевозки',
                                related_name='receipts')
    transit = models.ForeignKey(Transit, on_delete=models.CASCADE, blank=True, null=True,
                                verbose_name='Перевозка', related_name='receipts')

    doc_number = models.CharField(max_length=100, verbose_name='Номер', unique=True)
    doc_date = models.DateField(verbose_name='Дата документа')
    load_date = models.DateField(verbose_name='Дата погрузки')
    sr_file = models.FileField(upload_to=path_by_order, verbose_name='Скан ЭР')

    def __str__(self):
        return f'ЭР №{self.doc_number}'

    @staticmethod
    def save_scan_to_order(order, file, doc_title):
        if order.docs.filter(title=doc_title).exists():
            doc = order.docs.get(title=doc_title)
        else:
            doc = Document(order=order)
        doc.file = file
        doc.title = doc_title
        doc.save()

    @staticmethod
    def del_scan_from_order(order, doc_title):
        order.docs.filter(title=doc_title).delete()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(ShippingReceiptOriginal, self).save(force_insert, force_update, using, update_fields)
        self.segment.update_from_docs()
        self.save_scan_to_order(self.transit.order, self.sr_file, str(self))

    def delete(self, using=None, keep_parents=False):
        self.segment.update_from_docs()
        self.del_scan_from_order(self.transit.order, str(self))
        super(ShippingReceiptOriginal, self).delete(using, keep_parents)


class RandomDocScan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=True, blank=True, verbose_name='Время создания')
    last_update = models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')
    segment = models.ForeignKey(TransitSegment, on_delete=models.CASCADE, verbose_name='Плечо перевозки',
                                related_name='randoms')
    transit = models.ForeignKey(Transit, on_delete=models.CASCADE, blank=True, null=True,
                                verbose_name='Перевозка', related_name='randoms')

    doc_name = models.CharField(max_length=50, verbose_name='Тип документа')
    doc_number = models.CharField(max_length=100, verbose_name='Номер документа')
    doc_date = models.DateField(verbose_name='Дата документа')
    rd_file = models.FileField(upload_to=path_by_order, verbose_name='Скан документа')

    def __str__(self):
        return f'{self.doc_name} №{self.doc_number}'

    @staticmethod
    def save_scan_to_order(order, file, doc_title):
        if order.docs.filter(title=doc_title).exists():
            doc = order.docs.get(title=doc_title)
        else:
            doc = Document(order=order)
        doc.file = file
        doc.title = doc_title
        doc.save()

    @staticmethod
    def del_scan_from_order(order, doc_title):
        order.docs.filter(title=doc_title).delete()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(RandomDocScan, self).save(force_insert, force_update, using, update_fields)
        self.save_scan_to_order(self.transit.order, self.rd_file, str(self))

    def delete(self, using=None, keep_parents=False):
        self.del_scan_from_order(self.transit.order, str(self))
        super(RandomDocScan, self).delete(using, keep_parents)

    def get_file_name(self):
        return os.path.basename(self.rd_file.path)

    class Meta:
        unique_together = 'transit', 'doc_name', 'doc_number'


class TransDocsData(models.Model):
    OWN_TYPES = (
        ('own', 'Собственность'),
        ('family', 'Совместная собственность супругов'),
        ('rent', 'Аренда'),
        ('leasing', 'Лизинг'),
        ('free', 'Безвозмездное пользование')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=True, blank=True, verbose_name='Время создания')
    last_update = models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')
    segment = models.ForeignKey(TransitSegment, on_delete=models.CASCADE, verbose_name='Плечо перевозки',
                                related_name='waybills')
    ext_order = models.ForeignKey(ExtOrder, on_delete=models.CASCADE, blank=True, null=True,
                                  verbose_name='Исх. поручение', related_name='waybills')
    doc_number = models.CharField(max_length=100, verbose_name='Номер ЭР', unique=True)
    doc_type = models.CharField(max_length=10, verbose_name='Тип основного транспортного документа', choices=DOC_TYPES)
    doc_num_trans = models.CharField(max_length=255, verbose_name='Номер основного транспортного документа')
    doc_date = models.DateField(verbose_name='Дата отгрузки')
    doc_date_trans = models.DateField(verbose_name='Дата основного транспортного документа')
    file_name = models.CharField(max_length=100, verbose_name='Имя файла')
    quantity = models.IntegerField(verbose_name='Количество мест', default=0)
    weight_brut = models.FloatField(verbose_name='Вес брутто, кг', default=0)
    value = models.FloatField(verbose_name='Стоимость', default=0)
    driver_last_name = models.CharField(max_length=50, verbose_name='Фамилия', blank=True, null=True)
    driver_first_name = models.CharField(max_length=50, verbose_name='Имя', blank=True, null=True)
    driver_second_name = models.CharField(max_length=50, verbose_name='Отчество', blank=True, null=True)
    driver_license = models.CharField(max_length=50, verbose_name='Номер в.у.', blank=True, null=True)
    driver_entity = models.CharField(max_length=50, verbose_name='Гражданство', blank=True, null=True)
    driver_phone = models.CharField(max_length=50, verbose_name='Тел.', blank=True, null=True)
    driver_passport_number = models.CharField(max_length=50, verbose_name='Серия и номер паспорта',
                                              blank=True, null=True)
    driver_passport_issued_at = models.DateField(verbose_name='Когда выдан', blank=True, null=True)
    driver_passport_issuer = models.CharField(max_length=255, verbose_name='Кем выдан', blank=True, null=True)
    auto_model = models.CharField(max_length=100, verbose_name='Марка авто', blank=True, null=True)
    auto_number = models.CharField(max_length=50, verbose_name='Гос. номер', blank=True, null=True)
    auto_ownership = models.CharField(max_length=20, choices=OWN_TYPES, blank=True, null=True,
                                      verbose_name='Тип владения')
    auto_tonnage = models.IntegerField(verbose_name='Тоннаж', blank=True, null=True)
    doc_original = models.OneToOneField(DocOriginal, verbose_name='Оригинал документа', blank=True, null=True,
                                        related_name='waybill', on_delete=models.SET_NULL)
    race_number = models.CharField(max_length=255, blank=True, null=True, verbose_name='Номер отправления (рейса)')

    def driver_indicated(self):
        return self.driver_last_name and self.driver_first_name and self.driver_license

    def auto_indicated(self):
        return self.auto_model and self.auto_number

    def ownership_num(self):
        for t, _type in enumerate(self.OWN_TYPES):
            if _type[0] == self.auto_ownership:
                return str(t + 1)
        return str()

    def short_name(self):
        if self.driver_last_name is not None:
            result = [self.driver_last_name]
            for arg in self.driver_first_name, self.driver_second_name:
                if isinstance(arg, str):
                    result.append(f'{arg[0].capitalize()}.')
            if result:
                return ' '.join(result)
        return ''

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        if self.ext_order is None:
            self.ext_order = self.segment.ext_order

        if not self.doc_number:
            if self.ext_order.number == self.ext_order.order.inner_number:
                delimiter = '-'
            else:
                delimiter = '.'
            self.doc_number = f'{self.ext_order.number}{delimiter}{self.ext_order.waybills.filter(segment__type="auto").count() + 1}'
        self.file_name = self.doc_number.replace('/', '_').replace('-', '_') + '.pdf'

        if self.segment.type == 'auto':
            if not self.doc_num_trans:
                self.doc_num_trans = self.doc_number
            if self.doc_type not in ['auto', 'cmr']:
                self.doc_type = 'auto'
        if not self.doc_num_trans:
            self.doc_num_trans = self.doc_number
            self.doc_type = dict(DOC_TYPES).get(self.segment.type)

        super(TransDocsData, self).save(force_insert, force_update, using, update_fields)
        self.ext_order.docs_list_update()
        self.ext_order.transit.docs_list_update()

    def delete(self, using=None, keep_parents=False):
        super(TransDocsData, self).delete(using, keep_parents)
        self.ext_order.docs_list_update()
        self.ext_order.transit.docs_list_update()

    class Meta:
        verbose_name = 'отгрузка'
        verbose_name_plural = 'отгрузки'


@receiver(post_save, sender=TransDocsData)
def order_added(sender, created, instance, **kwargs):
    if created:
        transport_added_for_manager.delay(instance.pk)
        transport_added_for_client.delay(instance.pk)
