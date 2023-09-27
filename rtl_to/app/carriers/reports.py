from management.reports import ReportGenerator


class CarrierReportGenerator(ReportGenerator):

    prefixes_router = {
        'ext_order': 'ExtOrder',
        'segment': 'TransitSegment'
    }

    fields = (
        ('ext_order__number', 'Номер поручения'),
        ('ext_order__date', 'Дата поручения'),
        ('ext_order__gov_contr_num', '№ ИГК'),
        ('ext_order__contract', 'Договор'),
        ('ext_order__price_carrier', 'Ставка'),
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
        ('ext_order__docs_list', 'Номера транспортных документов'),
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

    possible_custom_filters = [
        'ext_order__from_date__gte', 'from_date__gte', 'ext_order__from_date__lte', 'from_date__lte',
        'ext_order__to_date__gte', 'to_date__gte', 'ext_order__to_date__lte', 'to_date__lte'
    ]
