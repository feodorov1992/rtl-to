import os
import uuid

from django.db import models

from orders.models import TransitSegment, ExtOrder, Transit, Document


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
    DOC_TYPES = (
        ('auto', 'ТН'),
        ('plane', 'AWB'),
        ('rail', 'СМГС'),
        ('ship', 'Коносамент')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    segment = models.ForeignKey(TransitSegment, on_delete=models.CASCADE, verbose_name='Плечо перевозки',
                                related_name='originals')
    transit = models.ForeignKey(Transit, on_delete=models.CASCADE, blank=True, null=True,
                                verbose_name='Перевозка', related_name='originals')

    doc_type = models.CharField(max_length=50, verbose_name='Тип документа', choices=DOC_TYPES)
    doc_number = models.CharField(max_length=100, verbose_name='Номер', unique=True)
    doc_date = models.DateField(verbose_name='Дата документа')
    quantity = models.IntegerField(verbose_name='Количество мест', default=0)
    weight_brut = models.FloatField(verbose_name='Вес брутто, кг', default=0)
    weight_payed = models.FloatField(verbose_name='Оплачиваемый вес, кг', default=0)
    load_date = models.DateField(verbose_name='Дата погрузки')
    file = models.FileField(upload_to=path_by_order, verbose_name='Скан документа')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(DocOriginal, self).save(force_insert, force_update, using, update_fields)
        self.segment.update_from_docs()
        order = self.segment.transit.order
        doc_title = f'{self.get_doc_type_display()} №{self.doc_number}'
        if order.docs.filter(title=doc_title).exists():
            doc = order.docs.get(title=doc_title)
        else:
            doc = Document(order=order)
        doc.file = self.file
        doc.title = doc_title
        doc.save()

    def delete(self, using=None, keep_parents=False):
        self.segment.update_from_docs()
        order = self.segment.transit.order
        doc_title = f'{self.get_doc_type_display()} №{self.doc_number}'
        if order.docs.filter(title=doc_title).exists():
            order.docs.get(title=doc_title).delete()
        super(DocOriginal, self).delete(using, keep_parents)


class WaybillData(models.Model):
    OWN_TYPES = (
        ('own', 'Собственность'),
        ('family', 'Совместная собственность супругов'),
        ('rent', 'Аренда'),
        ('leasing', 'Лизинг'),
        ('free', 'Безвозмездное пользование')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    segment = models.ForeignKey(TransitSegment, on_delete=models.CASCADE, verbose_name='Плечо перевозки',
                                related_name='waybills')
    ext_order = models.ForeignKey(ExtOrder, on_delete=models.CASCADE, blank=True, null=True,
                                  verbose_name='Исх. поручение', related_name='waybills')
    waybill_number = models.CharField(max_length=100, verbose_name='Номер ТН', unique=True)
    waybill_date = models.DateField(verbose_name='Дата накладной')
    file_name = models.CharField(max_length=100, verbose_name='Имя файла')
    quantity = models.IntegerField(verbose_name='Количество мест', default=0)
    weight_brut = models.FloatField(verbose_name='Вес брутто, кг', default=0)
    driver_last_name = models.CharField(max_length=50, verbose_name='Фамилия', blank=True, null=True)
    driver_first_name = models.CharField(max_length=50, verbose_name='Имя', blank=True, null=True)
    driver_second_name = models.CharField(max_length=50, verbose_name='Отчество', blank=True, null=True)
    driver_license = models.CharField(max_length=50, verbose_name='Номер в.у.', blank=True, null=True)
    driver_entity = models.CharField(max_length=50, verbose_name='Национальность', blank=True, null=True)
    auto_model = models.CharField(max_length=100, verbose_name='Марка авто', blank=True, null=True)
    auto_number = models.CharField(max_length=20, verbose_name='Гос. номер', blank=True, null=True)
    ownership = models.CharField(max_length=20, choices=OWN_TYPES, blank=True, null=True, verbose_name='Тип владения')
    original = models.OneToOneField(DocOriginal, verbose_name='Оригинал документа', blank=True, null=True,
                                    related_name='waybill', on_delete=models.SET_NULL)

    def ownership_num(self):
        for t, _type in enumerate(self.OWN_TYPES):
            if _type[0] == self.ownership:
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
        self.file_name = self.waybill_number.replace('/', '_').replace('-', '_') + '.pdf'
        if self.ext_order is None:
            self.ext_order = self.segment.ext_order
        super(WaybillData, self).save(force_insert, force_update, using, update_fields)

