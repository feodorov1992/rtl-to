import logging

from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.forms import inlineformset_factory, CheckboxSelectMultiple, DateInput, Select
from django.forms.models import ModelChoiceIterator
from django_genericfilters import forms as gf

from app_auth.models import User, Client, Contractor, Auditor
from management.reports import ReportGenerator
from orders.forms import BaseTransitFormset, CargoCalcForm, TransitForm, BaseCargoFormset, OrderForm, \
    InternationalTransitForm
from orders.models import Order, Transit, Cargo, ORDER_STATUS_LABELS, EXT_ORDER_STATUS_LABELS

logger = logging.getLogger(__name__)


class UserAddForm(forms.ModelForm):
    """
    Форма добавления пользователя
    """
    required_css_class = 'required'

    def clean(self):
        cleaned_data = super(UserAddForm, self).clean()
        user_type = cleaned_data.get('user_type')
        if '_' in user_type:
            org_type, _ = user_type.split('_')
            if cleaned_data.get(org_type) is None:
                self.add_error(org_type, 'Необходимо что-то выбрать!')

    class Meta:
        model = User
        exclude = [
            'created_at',
            'last_update',
            'username',
            'password',
            'is_superuser',
            'groups',
            'user_permissions',
            'is_staff',
            'is_active',
            'date_joined',
            'last_login',
            'boss'
        ]
        widgets = {
            'user_type': forms.RadioSelect()
        }


class UserEditForm(UserChangeForm):
    """
    Форма редактирования пользователя
    """
    required_css_class = 'required'
    password = None

    def clean(self):
        cleaned_data = super(UserEditForm, self).clean()
        user_type = cleaned_data.get('user_type')
        if '_' in user_type:
            org_type, _ = user_type.split('_')
            if cleaned_data.get(org_type) is None:
                self.add_error(org_type, 'Необходимо что-то выбрать!')

    class Meta:
        model = User
        exclude = [
            'created_at',
            'last_update',
            'username',
            'password',
            'is_superuser',
            'groups',
            'user_permissions',
            'is_staff',
            'is_active',
            'date_joined',
            'last_login'
        ]
        widgets = {
            'user_type': forms.RadioSelect()
        }


class FilterModelChoiceIterator(ModelChoiceIterator):
    """
    Итератор для генерации набора значений фильтра с возможностью фильтра по NULL
    """

    def __iter__(self):
        if self.field.empty_label is not None:
            yield 'none', 'Не назначен'
        for obj in super(FilterModelChoiceIterator, self).__iter__():
            yield obj


class FilterModelChoiceField(forms.ModelChoiceField):
    """
    Кастомное поле модели фильтра
    """
    iterator = FilterModelChoiceIterator

    def clean(self, value):
        if value == 'none':
            return value
        return super(FilterModelChoiceField, self).clean(value)


class OrderListFilters(gf.FilteredForm):
    """
    Форма фильтрации поручений
    """
    query = forms.CharField(label='Поиск', required=False)

    status = gf.ChoiceField(choices=ORDER_STATUS_LABELS, label='Статус', required=False)
    client = forms.ModelChoiceField(label='Заказчик', required=False, empty_label='Все', queryset=Client.objects.all())
    manager = FilterModelChoiceField(queryset=User.objects.filter(user_type='manager'),
                                     label='Менеджер', required=False, empty_label='Все')
    type = gf.ChoiceField(choices=Order.TYPES, label='Виды поручения', required=False)
    from_date = forms.DateField(label='Не ранее', required=False, widget=DateInput(attrs={'type': 'date'},
                                                                                   format='%Y-%m-%d'))
    to_date = forms.DateField(label='Не позднее', required=False, widget=DateInput(attrs={'type': 'date'},
                                                                                   format='%Y-%m-%d'))

    def is_valid(self):
        if self.errors:
            logger.error(self.errors)
        return super(OrderListFilters, self).is_valid()

    def get_order_by_choices(self):
        return [
            ('inner_number', 'Номер поручения'),
            ('order_date', 'Дата поручения'),
            ('manager', 'Менеджер'),
            ('from_addr_forlist', 'Пункты отправления'),
            ('to_addr_forlist', 'Пункты доставки'),
            ('active_segments', 'Активные плечи'),
            ('status', 'Статус'),
        ]


class OrderEditBaseTransitFormset(BaseTransitFormset):
    """
    Базовый динамический набор форм перевозок, используемый на странице редактирования поручения
    """

    def __init__(self, *args, **kwargs):
        super(OrderEditBaseTransitFormset, self).__init__(*args, **kwargs)
        for form in self.forms:
            if 'status' in form.fields:
                form.fields['status'].widget.choices = form.instance.get_status_list()
            for visible in form.visible_fields():
                visible.field.widget.attrs['class'] = f'transit_{visible.name}'
                if visible.field.required:
                    visible.field.widget.attrs['class'] += ' required'

    def add_fields(self, form, index):
        super(OrderEditBaseTransitFormset, self).add_fields(form, index)
        form.nested = OrderEditCargoFormset(
            data=form.data if form.is_bound else None,
            instance=form.instance,
            prefix='%s-%s' % (form.prefix, OrderEditCargoFormset.get_default_prefix())
        )


OrderEditTransitFormset = inlineformset_factory(Order, Transit, formset=OrderEditBaseTransitFormset,
                                                form=TransitForm,
                                                extra=0,
                                                exclude=[
                                                    'created_at',
                                                    'last_update',
                                                    'sum_insured',
                                                    'insurance_premium',
                                                    'volume',
                                                    'weight',
                                                    'weight_payed',
                                                    'weight_fact',
                                                    'quantity',
                                                    'quantity_fact',
                                                    'status',
                                                    'type',
                                                    'number',
                                                    'price_carrier',
                                                    'from_date_plan',
                                                    'from_date_fact',
                                                    'to_date_plan',
                                                    'to_date_fact',
                                                    'from_addr_short',
                                                    'to_addr_short',
                                                    'from_addr_eng',
                                                    'to_addr_eng',
                                                    'docs_list',
                                                    'price_non_rub',
                                                    'packages',
                                                    'cargo_handling',
                                                    'price_from_eo'
                                                ],
                                                widgets={'extra_services': CheckboxSelectMultiple(),
                                                         'from_date_wanted': DateInput(attrs={'type': 'date'},
                                                                                       format='%Y-%m-%d'),
                                                         'to_date_wanted': DateInput(attrs={'type': 'date'},
                                                                                     format='%Y-%m-%d'),
                                                         'price_approval_req_date': DateInput(attrs={'type': 'date'},
                                                                                              format='%Y-%m-%d')})

InternationalOrderEditTransitFormset = inlineformset_factory(Order, Transit, formset=OrderEditBaseTransitFormset,
                                                             form=InternationalTransitForm,
                                                             extra=0,
                                                             exclude=[
                                                                 'created_at',
                                                                 'last_update',
                                                                 'sum_insured',
                                                                 'insurance_premium',
                                                                 'volume',
                                                                 'weight',
                                                                 'weight_payed',
                                                                 'weight_fact',
                                                                 'quantity',
                                                                 'quantity_fact',
                                                                 'status',
                                                                 'type',
                                                                 'number',
                                                                 'price_carrier',
                                                                 'from_date_plan',
                                                                 'from_date_fact',
                                                                 'to_date_plan',
                                                                 'to_date_fact',
                                                                 'docs_list',
                                                                 'packages',
                                                                 'cargo_handling',
                                                                 'price_from_eo',
                                                                 'price',
                                                                 'price_currency'
                                                             ],
                                                             widgets={'extra_services': CheckboxSelectMultiple(),
                                                                      'from_date_wanted': DateInput(
                                                                          attrs={'type': 'date'},
                                                                          format='%Y-%m-%d'),
                                                                      'to_date_wanted': DateInput(
                                                                          attrs={'type': 'date'},
                                                                          format='%Y-%m-%d'),
                                                                      'price_approval_req_date': DateInput(
                                                                          attrs={'type': 'date'},
                                                                          format='%Y-%m-%d')})

OrderEditCargoFormset = inlineformset_factory(Transit, Cargo, extra=0, exclude=['created_at', 'last_update'],
                                              form=CargoCalcForm, formset=BaseCargoFormset,
                                              widgets={'currency': Select(),
                                                       'extra_params': CheckboxSelectMultiple()
                                                       }, )


class OrderCreateBaseTransitFormset(BaseTransitFormset):
    """
    Базовый динамический набор форм перевозок, используемый на странице добавления нового поручения
    """

    def __init__(self, *args, **kwargs):
        super(OrderCreateBaseTransitFormset, self).__init__(*args, **kwargs)
        for form in self.forms:
            if 'status' in form.fields:
                form.fields['status'].widget.choices = form.fields['status'].widget.choices[:1]
            for visible in form.visible_fields():
                visible.field.widget.attrs['class'] = f'transit_{visible.name}'
                if visible.field.required:
                    visible.field.widget.attrs['class'] += ' required'

    def add_fields(self, form, index):
        super(OrderCreateBaseTransitFormset, self).add_fields(form, index)
        form.nested = OrderCreateCargoFormset(
            data=form.data if form.is_bound else None,
            instance=form.instance,
            prefix='%s-%s' % (form.prefix, OrderCreateCargoFormset.get_default_prefix())
        )


OrderCreateTransitFormset = inlineformset_factory(Order, Transit, formset=OrderCreateBaseTransitFormset,
                                                  form=TransitForm,
                                                  extra=1,
                                                  exclude=[
                                                      'created_at',
                                                      'last_update',
                                                      'status',
                                                      'bill_number',
                                                      'from_date_plan',
                                                      'from_date_fact',
                                                      'to_date_plan',
                                                      'to_date_fact',
                                                      'from_addr_short',
                                                      'to_addr_short',
                                                      'from_addr_eng',
                                                      'to_addr_eng',
                                                      'docs_list',
                                                      'price_non_rub',
                                                      'price_currency',
                                                      'packages',
                                                      'cargo_handling',
                                                      'price_approval_req_date'
                                                  ],
                                                  widgets={'extra_services': CheckboxSelectMultiple(),
                                                           'from_date_wanted': DateInput(attrs={'type': 'date'},
                                                                                         format='%Y-%m-%d'),
                                                           'to_date_wanted': DateInput(attrs={'type': 'date'},
                                                                                       format='%Y-%m-%d')})

InternationalOrderCreateTransitFormset = inlineformset_factory(Order, Transit, formset=OrderCreateBaseTransitFormset,
                                                               form=InternationalTransitForm,
                                                               extra=1,
                                                               exclude=[
                                                                   'created_at',
                                                                   'last_update',
                                                                   'status',
                                                                   'bill_number',
                                                                   'from_date_plan',
                                                                   'from_date_fact',
                                                                   'to_date_plan',
                                                                   'to_date_fact',
                                                                   'docs_list',
                                                                   'packages',
                                                                   'cargo_handling',
                                                                   'price',
                                                                   'price_currency',
                                                                   'price_approval_req_date'
                                                               ],
                                                               widgets={'extra_services': CheckboxSelectMultiple(),
                                                                        'from_date_wanted': DateInput(
                                                                            attrs={'type': 'date'},
                                                                            format='%Y-%m-%d'),
                                                                        'to_date_wanted': DateInput(
                                                                            attrs={'type': 'date'},
                                                                            format='%Y-%m-%d')})

OrderCreateCargoFormset = inlineformset_factory(Transit, Cargo, extra=1, fields='__all__',
                                                form=CargoCalcForm, formset=BaseCargoFormset,
                                                widgets={'currency': Select(),
                                                         'extra_params': CheckboxSelectMultiple()
                                                         }, )


def get_fields_choices(model_class):
    """
    Ищет полный набор полей модели
    :param model_class: класс модели поиска
    :return: набор пар из технического и человекочитаемого наименований полей моедли
    """
    fields = model_class._meta.get_fields()
    return [(i.name, i.verbose_name) for i in fields]


class ReportsForm(forms.Form):
    """
    Форма формирования отчетов
    """
    field_choices = ReportGenerator([]).fields_list()

    order_fields = forms.MultipleChoiceField(
        widget=CheckboxSelectMultiple(), label='Поля входящего поручения',
        choices=field_choices.get('order'),
        required=False
    )
    transit_fields = forms.MultipleChoiceField(
        widget=CheckboxSelectMultiple(), label='Поля перевозки',
        choices=field_choices.get('transit'),
        required=False
    )
    ext_order_fields = forms.MultipleChoiceField(
        widget=CheckboxSelectMultiple(), label='Поля исходящего поручения',
        choices=field_choices.get('ext_order'),
        required=False
    )
    segment_fields = forms.MultipleChoiceField(
        widget=CheckboxSelectMultiple(), label='Поля плеча перевозки',
        choices=field_choices.get('segment'),
        required=False
    )
    report_name = forms.CharField(required=False)
    report_type = forms.ChoiceField(choices=[('web', 'web'), ('csv', 'csv'), ('xlsx', 'xlsx')], initial='web')

    def select_all(self):
        for field_name in 'order_fields', 'transit_fields', 'ext_order_fields', 'segment_fields':
            field = self.fields[field_name]
            field.initial = [i[0] for i in field.choices]


class M2MChoiceField(forms.ModelChoiceField):

    def clean(self, value):
        return [super(M2MChoiceField, self).clean(value)]


class ReportsFilterForm(forms.Form):
    """
    Форма фильтрации данных для формирования отчетов
    """
    order__order_date__gte = forms.DateField(required=False, label='Не ранее', widget=DateInput(attrs={'type': 'date'},
                                                                                                format='%Y-%m-%d'))
    order__order_date__lte = forms.DateField(required=False, label='Не позднее',
                                             widget=DateInput(attrs={'type': 'date'},
                                                              format='%Y-%m-%d'))
    order__from_date__gte = forms.DateField(required=False, label='Не ранее',
                                            widget=DateInput(attrs={'type': 'date'},
                                                             format='%Y-%m-%d'))
    order__from_date__lte = forms.DateField(required=False, label='Не позднее',
                                            widget=DateInput(attrs={'type': 'date'},
                                                             format='%Y-%m-%d'))
    order__to_date__gte = forms.DateField(required=False, label='Не ранее',
                                          widget=DateInput(attrs={'type': 'date'},
                                                           format='%Y-%m-%d'))
    order__to_date__lte = forms.DateField(required=False, label='Не позднее',
                                          widget=DateInput(attrs={'type': 'date'},
                                                           format='%Y-%m-%d'))

    ext_order__contractor = forms.ModelChoiceField(Contractor.objects.all(), label='Перевозчик')
    order__client = forms.ModelChoiceField(Client.objects.all(), label='Заказчик')
    order__auditors__in = M2MChoiceField(Auditor.objects.all(), label='Аудитор')
    order__manager = forms.ModelChoiceField(User.objects.filter(user_type='manager'), label='Менеджер')

    def serialized_result(self):
        """
        Фильтрует и возвращает набор ключ-значение из выбранных фильтров
        """
        if not hasattr(self, 'cleaned_data'):
            self.full_clean()
        return {key: value for key, value in self.cleaned_data.items() if value is not None}


class BillOutputForm(forms.Form):
    """
    Форма для подготовки детализаций
    """
    required_css_class = 'required'

    client = forms.ModelChoiceField(label='Заказчик', queryset=Client.objects.all())
    type = forms.CharField(label='Вид поручения', widget=Select(choices=Order.TYPES[::-1]))
    delivered_from = forms.DateField(label='Начало периода',
                                     widget=DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    delivered_to = forms.DateField(label='Конец периода',
                                   widget=DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    empty_only = forms.BooleanField(label='Только пустые', required=False)


class BillOutputSearchForm(forms.Form):
    search = forms.CharField(label='Номер счета', required=False,
                             widget=forms.TextInput(attrs={'placeholder': 'Номер счета'}))


class ExtOrderListFilters(gf.FilteredForm):
    """
    Форма фильтрации поручений
    """
    query = forms.CharField(label='Поиск', required=False)

    status = gf.ChoiceField(choices=EXT_ORDER_STATUS_LABELS, label='Статус', required=False)
    client = forms.ModelChoiceField(label='Заказчик', required=False, empty_label='Все', queryset=Client.objects.all())
    manager = FilterModelChoiceField(queryset=User.objects.filter(client=None).order_by('last_name', 'first_name'),
                                     label='Менеджер', required=False, empty_label='Все')
    type = gf.ChoiceField(choices=Order.TYPES, label='Виды поручения', required=False)
    from_date = forms.DateField(label='Не ранее', required=False, widget=DateInput(attrs={'type': 'date'},
                                                                                   format='%Y-%m-%d'))
    to_date = forms.DateField(label='Не позднее', required=False, widget=DateInput(attrs={'type': 'date'},
                                                                                   format='%Y-%m-%d'))

    def is_valid(self):
        if self.errors:
            logger.error(self.errors)
        return super(ExtOrderListFilters, self).is_valid()

    def get_order_by_choices(self):
        return [
            ('number', 'Номер поручения'),
            ('date', 'Дата поручения'),
            ('manager', 'Менеджер'),
            ('from_addr_forlist', 'Пункты отправления'),
            ('to_addr_forlist', 'Пункты доставки'),
            ('active_segments', 'Активные плечи'),
            ('status', 'Статус'),
        ]


class ExtOrderListFilters1(gf.FilteredForm):
    """
    Форма фильтрации поручений
    """
    query = forms.CharField(label='Поиск', required=False)

    status = gf.ChoiceField(choices=EXT_ORDER_STATUS_LABELS, label='Статус', required=False)
    contractor = FilterModelChoiceField(label='Перевозчик', required=False, empty_label='Все',
                                        queryset=Contractor.objects.all())
    manager = FilterModelChoiceField(label='Менеджер', required=False, empty_label='Все',
                                     queryset=User.objects.filter(user_type='manager'))
    from_date = forms.DateField(label='Не ранее', required=False, widget=DateInput(attrs={'type': 'date'},
                                                                                   format='%Y-%m-%d'))
    to_date = forms.DateField(label='Не позднее', required=False, widget=DateInput(attrs={'type': 'date'},
                                                                                   format='%Y-%m-%d'))

    def get_order_by_choices(self):
        return [
            ('number', 'Номер поручения'),
            ('date', 'Дата поручения'),
            ('contractor', 'Перевозчик'),
            ('manager', 'Менеджер'),
            ('from_addr', 'Адрес отправления'),
            ('to_addr', 'Адрес доставки'),
            ('status', 'Статус'),
        ]


class ClientForm(forms.ModelForm):

    class Meta:
        model = Client
        exclude = ['created_at', 'last_update']


class ContractorForm(forms.ModelForm):

    class Meta:
        model = Contractor
        exclude = ['created_at', 'last_update']
