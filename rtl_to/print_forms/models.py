from django.db import models

from orders.models import TransitSegment


class WaybillData(models.Model):
    OWN_TYPES = (
        ('own', 'Собственность'),
        ('family', 'Совместная собственность супругов'),
        ('rent', 'Аренда'),
        ('leasing', 'Лизинг'),
        ('free', 'Безвозмездное пользование')
    )

    segment = models.ForeignKey(TransitSegment, on_delete=models.CASCADE, verbose_name='Плечо перевозки',
                                related_name='waybills')
    waybill_number = models.CharField(max_length=100, verbose_name='Номер транспортной накладной', unique=True)
    driver_last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    driver_first_name = models.CharField(max_length=50, verbose_name='Имя')
    driver_second_name = models.CharField(max_length=50, verbose_name='Отчество')
    driver_license = models.CharField(max_length=50, verbose_name='Номер в.у.')
    driver_entity = models.CharField(max_length=50, verbose_name='Национальность', default='РФ')
    auto_model = models.CharField(max_length=100, verbose_name='Марка авто')
    auto_number = models.CharField(max_length=20, verbose_name='Гос. номер')
    ownership = models.CharField(max_length=20, choices=OWN_TYPES, default='own', verbose_name='Тип владения')

    def ownership_num(self):
        for t, _type in enumerate(self.OWN_TYPES):
            if _type[0] == self.ownership:
                return str(t + 1)
            return str()

    def short_name(self):
        result = [self.driver_last_name]
        for arg in self.driver_first_name, self.driver_second_name:
            if isinstance(arg, str):
                result.append(f'{arg[0].capitalize()}.')
        return ' '.join(result)

