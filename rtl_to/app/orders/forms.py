import logging

from django.db import models
from django.forms import CheckboxSelectMultiple, Form, CharField, DateInput, DateTimeInput
from django.forms.models import inlineformset_factory, BaseInlineFormSet, ModelForm

import rtl_to.settings
from app_auth.models import User, ContractorContract
from orders.models import Order, Transit, Cargo, OrderHistory, TransitHistory, TransitSegment, Document, ExtOrder
from orders.tasks import address_changed_for_carrier, ext_order_assigned_carrier_notification

logger = logging.getLogger(__name__)


def form_save_logging(method):
    """
    Декоратор для осуществления детального логирования результатов сохранения форм
    :param method: декориремый метод формы
    :return:
    """
    def comapre_field(ref, fieldname):
        new = ref.cleaned_data.get(fieldname)
        old = ref.initial.get(fieldname)
        if isinstance(new, models.Model) and old is not None:
            old = new.__class__.objects.get(pk=old)
        return {'old': old, 'new': new}

    def wrapper(ref, commit=True):
        result = method(ref, commit)
        if ref.initial:
            changed_data_tracked = {i: comapre_field(ref, i) for i in ref.changed_data}
            log_msg = f'{ref._meta.model.__name__} (pk={result.pk}) updated: {changed_data_tracked}'
        else:
            changed_data_tracked = ref.cleaned_data
            log_msg = f'{ref._meta.model.__name__} (pk={result.pk}) created: {changed_data_tracked}'
        if changed_data_tracked:
            logger.info(log_msg)
        return result

    return wrapper


class OrderForm(ModelForm):
    """
    Форма входящего поручения
    """
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        """
        Генерация списка доступных статусов, назначение HTML классов полям формы
        :param args:
        :param kwargs:
        """
        super(OrderForm, self).__init__(*args, **kwargs)
        if 'status' in self.fields:
            self.fields['status'].widget.choices = self.instance.get_status_list()
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = f'order_{visible.name}'

    def as_my_style(self, template_name: str):
        """
        Тег шаблона для вывода формы в нужном виде
        :return: HTML-код формы в необходимом виде
        """
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name=template_name, context=context)

    def as_my_style_add(self):
        return self.as_my_style('management/basic_styles/order_as_my_style_add.html')

    def as_my_style_edit(self):
        return self.as_my_style('management/basic_styles/order_as_my_style_edit.html')

    def clean(self):
        cleaned_data = super(OrderForm, self).clean()
        contract = cleaned_data.get('contract')
        order_date = cleaned_data.get('order_date')
        if order_date > contract.expiration_date or order_date < contract.start_date:
            self.add_error('contract', 'Данное поручение не попадает в период действия договора')
        return cleaned_data

    @form_save_logging
    def save(self, commit=True):
        """
        Сохранение формы с запуском рассчетов
        :param commit: True, если результат необходимо сохранить в БД
        :param order_type: машиночитаемый тип поручения - международное или внутрироссийское
        :return: Сохраненный объект
        """
        result = super(OrderForm, self).save()
        if self.initial and 'insurance_currency' in self.changed_data:
            result.currency_rate = None
        if any([i in self.changed_data for i in
                ('insurance', 'sum_insured_coeff', 'insurance_currency', 'currency_rate')]):
            result.collect('transits', 'value')
        if 'client' in self.changed_data:
            # При назначении заказчика назначаем аудитора. Потенциально можно передать в модель поручения
            result.auditors.set(result.client.auditors.all())
        return result

    class Meta:
        model = Order
        exclude = [
            'value', 'auditors', 'inner_number', 'from_date_plan', 'from_date_fact', 'to_date_plan', 'to_date_fact',
            'price', 'price_carrier', 'type', 'weight_fact', 'quantity_fact', 'created_at', 'last_update'
        ]
        widgets = {
            'order_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }


class BaseTransitFormset(BaseInlineFormSet):
    """
    Базовый динамический набор форм перевозок
    """
    def get_queryset(self):
        """
        Формирует отсортированный по номеру набор данных
        :return: queryset
        """
        queryset = super().get_queryset()
        return queryset.order_by('number')

    def add_fields(self, form, index):
        """
        Добавляем в перевозку набор грузов
        :param form: форма из набора, к которой добавляется набор грузов
        :param index: порядковый номер формы
        :return: None
        """
        super(BaseTransitFormset, self).add_fields(form, index)
        form.nested = CargoFormset(
            data=form.data if form.is_bound else None,
            instance=form.instance,
            prefix='%s-%s' % (form.prefix, CargoFormset.get_default_prefix())
        )

    def clean(self):
        """
        Проверяет одинаковость валют стоимости грузов
        :return: None
        """
        if self.forms:
            ref_curr = self.forms[0].instance.__getattribute__('currency')
            for form in self.forms:
                curr = form.instance.__getattribute__('currency')
                if curr != ref_curr:
                    form.add_error(
                        'currency',
                        f'Валюты должны быть одинаковы для всех перевозок в поручении: {curr} не равно {ref_curr}'
                    )
        super(BaseTransitFormset, self).clean()

    def is_valid(self):
        """
        Проверяет корректность заполнения полей формы перевозки, а также всех форм грузов
        :return: bool
        """
        result = super(BaseTransitFormset, self).is_valid()
        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    for n in form.nested:
                        val = n.is_valid()
                        result = result and val
        return result

    def save(self, commit=True):
        """
        Сохранение набора форм с запуском необходимой автоматики
        :param commit:
        :return: результат сохранения
        """
        result = super(BaseTransitFormset, self).save(commit=commit)
        changed_data = list()
        for form in self.forms:
            check = form.changed_data if form.initial else form.cleaned_data
            for field in check:
                if field not in changed_data:
                    changed_data.append(field)
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)
        if changed_data and result:
            result[0].update_related('order', *changed_data)
        return result

    @property
    def empty_form(self):
        """
        Генерирует пустую форму для динамического добавления
        :return: Пустая форма
        """
        form = self.form(
            auto_id=self.auto_id,
            prefix=self.add_prefix('__tprefix__'),
            empty_permitted=True,
            use_required_attribute=False,
            **self.get_form_kwargs(None),
            renderer=self.renderer,
        )
        self.add_fields(form, None)
        if 'status' in form.fields:
            form.fields['status'].widget.choices = form.fields['status'].widget.choices[:1]
        for visible in form.visible_fields():
            visible.field.widget.attrs['class'] = f'transit_{visible.name}'
        return form


TransitFormset = inlineformset_factory(Order, Transit, formset=BaseTransitFormset, extra=0, exclude=[
    'sum_insured', 'insurance_premium', 'volume', 'weight', 'weight_payed', 'quantity', 'type', 'number',
    'price_carrier', 'from_date_plan', 'from_date_fact', 'to_date_plan', 'to_date_fact',
    'from_addr_short', 'to_addr_short', 'created_at', 'last_update'
])


class TransitForm(ModelForm):
    """
    Форма перевозки
    """
    required_css_class = 'required'
    form_template = 'management/basic_styles/transit_as_my_style.html'

    def as_my_style(self):
        """
        Тег шаблона для вывода формы в нужном виде
        :return: HTML-код формы в необходимом виде
        """
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name=self.form_template, context=context)

    def update_segments_and_ext_orders(self, result):

        expected_departure_changes = ('from_addr', 'from_addr_short', 'from_addr_eng', 'sender', 'from_contacts')
        if [i for i in expected_departure_changes if i in self.changed_data]:
            result.change_child('ext_orders', 'first', expected_departure_changes)
            result.change_child('segments', 'first', expected_departure_changes)

        expected_delivery_changes = ('to_addr', 'to_addr_short', 'to_addr_eng', 'receiver', 'to_contacts')
        if [i for i in expected_delivery_changes if i in self.changed_data]:
            result.change_child('ext_orders', 'last', expected_delivery_changes)
            result.change_child('segments', 'last', expected_delivery_changes)

    @form_save_logging
    def save(self, commit=True):
        """
        Сохранение формы с логированием результата
        :param commit:
        :return: результат сохранения
        """
        result = super(TransitForm, self).save(commit)
        if 'from_addr' in self.changed_data or 'to_addr' in self.changed_data:
            if (not self.initial.get('from_addr') or result.from_addr_short not in result.from_addr) or \
                    (not self.initial.get('to_addr') or result.to_addr_short not in result.to_addr):
                result.short_address()
                result.save()
            self.update_segments_and_ext_orders(result)
        return result

    class Meta:
        model = Transit
        exclude = ['status', 'created_at', 'last_update']


class InternationalTransitForm(TransitForm):
    """
    Форма перевозки
    """
    required_css_class = 'required'
    form_template = 'management/basic_styles/transit_as_my_style_international.html'

    @form_save_logging
    def save(self, commit=True):
        """
        Сохранение формы с логированием результата
        :param commit:
        :return: результат сохранения
        """
        result = super(TransitForm, self).save(commit)
        self.update_segments_and_ext_orders(result)
        return result


class CargoCalcForm(ModelForm):
    """
    Форма груза
    """
    required_css_class = 'required'

    def sizes_label(self):
        """
        Формирует общую подпись для полей габаритов
        :return: подпись
        """
        return self["length"].label_tag("Габариты (ДхШхВ), см")

    def as_my_style(self):
        """
        Тег шаблона для вывода формы в нужном виде
        :return: HTML-код формы в необходимом виде
        """
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='management/basic_styles/cargo_as_my_style.html', context=context)

    @form_save_logging
    def save(self, commit=True):
        """
        Сохранение формы с логированием результата
        :param commit:
        :return: результат сохранения
        """
        return super(CargoCalcForm, self).save(commit)

    class Meta:
        model = Cargo
        exclude = ['created_at', 'last_update', 'title']


CargoFormset = inlineformset_factory(Transit, Cargo, extra=0, exclude=['created_at', 'last_update'],
                                     form=CargoCalcForm,
                                     widgets={'extra_services': CheckboxSelectMultiple()}, )


class CalcForm(Form):
    """
    Потенциально неиспользуемый класс. Назначение не установлено.
    """
    from_addr = CharField(max_length=255, label='Адрес отправки')
    to_addr = CharField(max_length=255, label='Адрес доставки')


class BaseCargoFormset(BaseInlineFormSet):
    """
    Базовый динамический набор форм грузов
    """

    def __init__(self, *args, **kwargs):
        super(BaseCargoFormset, self).__init__(*args, **kwargs)
        for form in self.forms:
            for visible in form.visible_fields():
                visible.field.widget.attrs['class'] = f'cargo_{visible.name}'

    @property
    def empty_form(self):
        """
        Генерирует пустую форму для динамического добавления
        :return: Пустая форма
        """
        form = super().empty_form
        for visible in form.visible_fields():
            visible.field.widget.attrs['class'] = f'cargo_{visible.name}'
        return form

    def save(self, commit=True):
        """
        Сохранение набора форм с запуском необходимой автоматики
        :param commit:
        :return: результат сохранения
        """
        result = super(BaseCargoFormset, self).save(commit)
        changed_data = list()
        for form in self.forms:
            check = form.changed_data if form.initial else form.cleaned_data
            for field in check:
                if field not in changed_data:
                    changed_data.append(field)
        if changed_data and result:
            result[0].update_related('transit', *changed_data)
        return result


CargoCalcFormset = inlineformset_factory(Transit, Cargo, extra=1, form=CargoCalcForm, formset=BaseCargoFormset,
                                         exclude=['created_at', 'last_update', 'mark', 'transit'],
                                         widgets={'extra_services': CheckboxSelectMultiple()})


class OrderStatusForm(ModelForm):
    """
    Форма статуса
    """
    required_css_class = 'required'

    def as_my_style(self):
        """
        Тег шаблона для вывода формы в нужном виде
        :return: HTML-код формы в необходимом виде
        """
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='management/basic_styles/status_as_my_style.html', context=context)

    @form_save_logging
    def save(self, commit=True):
        """
        Сохранение формы с логированием результата
        :param commit:
        :return: результат сохранения
        """
        return super(OrderStatusForm, self).save(commit)

    class Meta:
        model = OrderHistory
        fields = '__all__'


class TransitStatusForm(ModelForm):
    """
    Форма статуса
    """
    required_css_class = 'required'

    def as_my_style(self):
        """
        Тег шаблона для вывода формы в нужном виде
        :return: HTML-код формы в необходимом виде
        """
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='management/basic_styles/status_as_my_style.html', context=context)

    @form_save_logging
    def save(self, commit=True):
        """
        Сохранение формы с логированием результата
        :param commit:
        :return: результат сохранения
        """
        return super(TransitStatusForm, self).save(commit)

    class Meta:
        model = TransitHistory
        fields = '__all__'


class TransitSegmentForm(ModelForm):
    """
    Форма плеча перевозки
    """
    required_css_class = 'required'

    def as_my_style(self):
        """
        Тег шаблона для вывода формы в нужном виде
        :return: HTML-код формы в необходимом виде
        """
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='management/basic_styles/segment_as_my_style.html', context=context)

    @form_save_logging
    def save(self, commit=True):
        """
        Сохранение формы с логированием результата
        :param commit:
        :return: результат сохранения
        """
        return super(TransitSegmentForm, self).save(commit)

    class Meta:
        model = TransitSegment
        exclude = ['created_at', 'last_update']


OrderStatusFormset = inlineformset_factory(
    Order, OrderHistory, extra=0, fields='__all__', form=OrderStatusForm,
    widgets={'created_at': DateTimeInput(attrs={'type': 'datetime-local'}, format="%Y-%m-%dT%H:%M:%S")}
)
TransitStatusFormset = inlineformset_factory(
    Transit, TransitHistory, extra=0, fields='__all__', form=TransitStatusForm,
    widgets={'created_at': DateTimeInput(attrs={'type': 'datetime-local'}, format="%Y-%m-%dT%H:%M:%S")}
)


class BaseTransitSegmentFormset(BaseInlineFormSet):
    """
    Базовый динамический набор форм плеч перевозки
    """
    FIELDS_TO_COPY = [
        'quantity',
        'from_addr',
        'to_addr',
        'from_addr_short',
        'to_addr_short',
        'from_addr_eng',
        'to_addr_eng',
        'weight',
        'take_from',
        'give_to'
    ]

    CROSS_EXCHANGE = [
        'from_addr',
        'to_addr',
        'from_addr_short',
        'to_addr_short',
        'from_addr_eng',
        'to_addr_eng',
        'sender',
        'receiver'
    ]

    ALWAYS_COLLECT = [
        'from_date_plan',
        'from_date_fact',
        'to_date_plan',
        'to_date_fact',
        'weight_brut',
        'quantity',
    ]

    def __init__(self, *args, initials=None, **kwargs):
        """
        Инициатор объекта с применением установленных изменений в стандартном HTML-коде
        :param initials: перечень начальных значений полей форм набора
        """
        super(BaseTransitSegmentFormset, self).__init__(*args, **kwargs)
        self.initials = initials
        for form in self.forms:
            if 'status' in form.fields:
                form.fields['status'].widget.choices = form.instance.get_status_list()

            for field_name in self.CROSS_EXCHANGE:
                form.fields[field_name].widget.attrs['class'] = 'segment_cross_exchange'
            for visible in form.visible_fields():
                if visible.field.widget.attrs.get('class') is not None:
                    visible.field.widget.attrs['class'] += f' segment_{visible.name}'
                else:
                    visible.field.widget.attrs['class'] = f'segment_{visible.name}'

    @property
    def empty_form(self):
        """
        Генерирует пустую форму для динамического добавления
        :return: Пустая форма
        """
        form = self.form(
            auto_id=self.auto_id,
            initial=self.initials,
            prefix=self.add_prefix('__prefix__'),
            empty_permitted=True,
            use_required_attribute=False,
            **self.get_form_kwargs(None),
            renderer=self.renderer,
        )
        self.add_fields(form, None)
        if 'status' in form.fields:
            form.fields['status'].widget.choices = form.fields['status'].widget.choices[:1]

        for field_name in self.CROSS_EXCHANGE:
            form.fields[field_name].widget.attrs['class'] = 'segment_cross_exchange'

        for visible in form.visible_fields():
            if visible.field.widget.attrs.get('class') is not None:
                visible.field.widget.attrs['class'] += f' segment_{visible.name}'
            else:
                visible.field.widget.attrs['class'] = f'segment_{visible.name}'

        return form

    def save(self, commit=True):
        """
        Сохранение набора форм с запуском необходимой автоматики
        :param commit:
        :return: результат сохранения
        """
        result = super(BaseTransitSegmentFormset, self).save(commit)
        changed_data = list()
        for form in self.forms:
            check = form.changed_data if form.initial else form.cleaned_data
            for field in list(check) + self.ALWAYS_COLLECT:
                if field not in changed_data:
                    changed_data.append(field)
        if changed_data and result:
            result[0].update_related('ext_order', *changed_data, related_name='segments')
        return result


ExtOrderSegmentFormset = inlineformset_factory(
    ExtOrder, TransitSegment, formset=BaseTransitSegmentFormset,
    extra=0, exclude=[
        'transit', 'price', 'price_carrier', 'taxes', 'currency', 'order', 'bill_position', 'created_at', 'last_update'
    ],
    form=TransitSegmentForm,
    widgets={
        'from_date_plan': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        'from_date_fact': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        'to_date_plan': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        'to_date_fact': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        'tracking_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
    }
)


class BaseExtOrderFormset(BaseInlineFormSet):
    """
    Базовый динамический набор форм исходящих поручений
    """
    CROSS_EXCHANGE = [
        'from_addr',
        'to_addr',
        'from_addr_short',
        'to_addr_short',
        'from_addr_eng',
        'to_addr_eng',
    ]

    def __init__(self, *args, segments_initials=None, initials=None, **kwargs):
        """
        Инициатор объекта с применением установленных изменений в стандартном HTML-коде
        :param initials: перечень начальных значений полей форм набора
        """
        super(BaseExtOrderFormset, self).__init__(*args, **kwargs)
        self.segments_initials = segments_initials
        self.initials = initials
        for form in self.forms:
            if 'status' in form.fields:
                form.fields['status'].widget.choices = form.instance.get_status_list()
            if 'manager' in form.fields:
                form.fields['manager'].queryset = User.objects.filter(user_type='manager', is_superuser=False)
            for field_name in self.CROSS_EXCHANGE:
                form.fields[field_name].widget.attrs['class'] = 'ext_order_cross_exchange'

            for visible in form.visible_fields():
                if visible.field.widget.attrs.get('class') is not None:
                    visible.field.widget.attrs['class'] += f' ext_order_{visible.name}'
                else:
                    visible.field.widget.attrs['class'] = f'ext_order_{visible.name}'

    def add_fields(self, form, index):
        """
        Добавляем в исходящее поручение набор плеч
        :param form: форма из набора, к которой добавляется набор плеч
        :param index: порядковый номер формы
        :return: None
        """
        super(BaseExtOrderFormset, self).add_fields(form, index)
        form.nested = ExtOrderSegmentFormset(
            data=form.data if form.is_bound else None,
            instance=form.instance,
            prefix='%s-%s' % (form.prefix, ExtOrderSegmentFormset.get_default_prefix()),
            initials=self.segments_initials
        )

    def is_valid(self):
        """
        Проверяет корректность заполнения полей формы перевозки, а также всех форм грузов
        :return: bool
        """
        result = super(BaseExtOrderFormset, self).is_valid()
        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    for n in form.nested:
                        val = n.is_valid()
                        result = result and val

        return result

    def save(self, commit=True):
        """
        Сохранение набора форм с запуском необходимой автоматики
        :param commit:
        :return: результат сохранения
        """
        result = super(BaseExtOrderFormset, self).save(commit=commit)
        changed_data = list()
        for form in self.forms:
            check = form.changed_data if form.initial else form.cleaned_data
            for field in check:
                if field not in changed_data:
                    changed_data.append(field)
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)

        if changed_data and result:
            result[0].update_related('transit', *changed_data, related_name='ext_orders')
        return result

    @property
    def empty_form(self):
        """
        Генерирует пустую форму для динамического добавления
        :return: Пустая форма
        """
        form = self.form(
            auto_id=self.auto_id,
            prefix=self.add_prefix('__eoprefix__'),
            empty_permitted=True,
            use_required_attribute=False,
            **self.get_form_kwargs(None),
            renderer=self.renderer,
            initial=self.initials
        )
        self.add_fields(form, None)
        if 'status' in form.fields:
            form.fields['status'].widget.choices = form.fields['status'].widget.choices[:1]

        for field_name in self.CROSS_EXCHANGE:
            form.fields[field_name].widget.attrs['class'] = 'ext_order_cross_exchange'

        for visible in form.visible_fields():
            if visible.field.widget.attrs.get('class') is not None:
                visible.field.widget.attrs['class'] += f' ext_order_{visible.name}'
            else:
                visible.field.widget.attrs['class'] = f'ext_order_{visible.name}'

        return form


class ExtOrderForm(ModelForm):
    required_css_class = 'required'

    def as_my_style(self):
        """
        Тег шаблона для вывода формы в нужном виде
        :return: HTML-код формы в необходимом виде
        """
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='management/basic_styles/ext_order_as_my_style.html', context=context)

    def clean(self):
        cleaned_data = super(ExtOrderForm, self).clean()
        contract = cleaned_data.get('contract')
        if contract is not None:
            price_carrier = cleaned_data.get('price_carrier')
            approx_price = cleaned_data.get('approx_price')
            currency = cleaned_data.get('currency')
            bill_date = cleaned_data.get('bill_date')
            order_date = cleaned_data.get('date')

            if not price_carrier:
                check_price = approx_price
            else:
                check_price = price_carrier
            if not contract.check_sum(check_price, currency, bill_date):
                self.add_error('contract', 'Остаток договора недостаточен для данного поручения!')

            if not bill_date:
                check_date = order_date
            else:
                check_date = bill_date
            if check_date > contract.expiration_date or check_date < contract.start_date:
                self.add_error('contract', 'Данное поручение не попадает в период действия договора')
        return cleaned_data

    @form_save_logging
    def save(self, commit=True):
        """
        Сохранение формы с логированием результата
        :param commit:
        :return: результат сохранения
        """
        result = super(ExtOrderForm, self).save(commit)
        contract_affecting_fields = ('currency', 'price_carrier', 'approx_price', 'bill_date', 'contract')
        if any([i in self.changed_data for i in contract_affecting_fields]) and result.contract is not None:
            result.contract.update_current_sum()
        if 'contract' in self.changed_data:
            old_contract_pk = self.initial.get('contract')
            if old_contract_pk and old_contract_pk != result.contract.pk:
                old_contract = ContractorContract.objects.get(pk=old_contract_pk)
                old_contract.update_current_sum()
        if 'contractor' in self.changed_data:
            ext_order_assigned_carrier_notification.delay(result.pk)
        elif ('from_addr' in self.changed_data or 'to_addr' in self.changed_data) and self.instance.pk:
            address_changed_for_carrier.delay(result.pk)
        return result

    class Meta:
        model = ExtOrder
        fields = '__all__'


ExtOrderFormset = inlineformset_factory(Transit, ExtOrder, formset=BaseExtOrderFormset, form=ExtOrderForm,
                                        extra=0, exclude=['order', 'number', 'status', 'from_date_plan',
                                                          'from_date_fact', 'to_date_plan', 'to_date_fact',
                                                          'weight_payed', 'docs_list', 'type'],
                                        widgets={
                                            'date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
                                            'from_date_wanted': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
                                            'to_date_wanted': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
                                            'act_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
                                            'bill_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
                                        })


class FileUploadForm(ModelForm):
    """
    Форма загрузки документа
    """
    required_css_class = 'required'

    def as_my_style(self):
        """
        Тег шаблона для вывода формы в нужном виде
        :return: HTML-код формы в необходимом виде
        """
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='management/basic_styles/doc_as_my_style.html', context=context)

    @form_save_logging
    def save(self, commit=True):
        """
        Сохранение формы с логированием результата
        :param commit:
        :return: результат сохранения
        """
        result = super(FileUploadForm, self).save(commit)
        return result

    class Meta:
        model = Document
        fields = '__all__'


class BaseFileUploadFormset(BaseInlineFormSet):
    """
    Базовый динамический набор форм подгрузки файлов
    """
    pass


FileUploadFormset = inlineformset_factory(
    Order, Document, formset=BaseFileUploadFormset,
    extra=0, fields='__all__', form=FileUploadForm
)
