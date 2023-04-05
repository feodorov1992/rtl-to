import logging

from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.forms import inlineformset_factory, CheckboxSelectMultiple, DateInput, Select
from django.forms.models import ModelChoiceIterator
from django_genericfilters import forms as gf

from app_auth.models import User, Client, Contractor
from management.reports import ReportGenerator
from orders.forms import BaseTransitFormset, CargoCalcForm, TransitForm, BaseCargoFormset
from orders.models import Order, Transit, Cargo, ORDER_STATUS_LABELS

logger = logging.getLogger(__name__)


class UserAddForm(forms.ModelForm):
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


class UserEditForm(UserChangeForm):
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

    def __iter__(self):
        if self.field.empty_label is not None:
            yield 'none', 'Не назначен'
        for obj in super(FilterModelChoiceIterator, self).__iter__():
            yield obj


class FilterModelChoiceField(forms.ModelChoiceField):
    iterator = FilterModelChoiceIterator

    def clean(self, value):
        if value == 'none':
            return value
        return super(FilterModelChoiceField, self).clean(value)


class OrderListFilters(gf.FilteredForm):
    query = forms.CharField(label='Поиск', required=False)

    status = gf.ChoiceField(choices=ORDER_STATUS_LABELS, label='Статус', required=False)
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
            print(self.errors)
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
                                                    'sum_insured',
                                                    'insurance_premium',
                                                    'volume',
                                                    'weight',
                                                    'weight_payed',
                                                    'quantity',
                                                    'status',
                                                    'type',
                                                    'number',
                                                    'bill_number',
                                                    'price_carrier',
                                                    'from_date_plan',
                                                    'from_date_fact',
                                                    'to_date_plan',
                                                    'to_date_fact',
                                                    'from_addr_short',
                                                    'to_addr_short',
                                                ],
                                                widgets={'extra_services': CheckboxSelectMultiple(),
                                                         'from_date_wanted': DateInput(attrs={'type': 'date'},
                                                                                       format='%Y-%m-%d'),
                                                         'to_date_wanted': DateInput(attrs={'type': 'date'},
                                                                                     format='%Y-%m-%d')})

OrderEditCargoFormset = inlineformset_factory(Transit, Cargo, extra=0, fields='__all__',
                                              form=CargoCalcForm, formset=BaseCargoFormset,
                                              widgets={'currency': Select(),
                                                       'extra_params': CheckboxSelectMultiple()
                                                       }, )


class OrderCreateBaseTransitFormset(BaseTransitFormset):

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
                                                      'status',
                                                      'bill_number',
                                                      'from_date_plan',
                                                      'from_date_fact',
                                                      'to_date_plan',
                                                      'to_date_fact',
                                                      'from_addr_short',
                                                      'to_addr_short'
                                                  ],
                                                  widgets={'extra_services': CheckboxSelectMultiple(),
                                                           'from_date_wanted': DateInput(attrs={'type': 'date'},
                                                                                         format='%Y-%m-%d'),
                                                           'to_date_wanted': DateInput(attrs={'type': 'date'},
                                                                                       format='%Y-%m-%d')})

OrderCreateCargoFormset = inlineformset_factory(Transit, Cargo, extra=1, fields='__all__',
                                                form=CargoCalcForm, formset=BaseCargoFormset,
                                                widgets={'currency': Select(),
                                                         'extra_params': CheckboxSelectMultiple()
                                                         }, )


def get_fields_choices(model_class):
    fields = model_class._meta.get_fields()
    return [(i.name, i.verbose_name) for i in fields]


class ReportsForm(forms.Form):
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


class ReportsFilterForm(forms.Form):
    order__order_date__gte = forms.DateField(required=False, label='Не ранее', widget=DateInput(attrs={'type': 'date'},
                                                                                                format='%Y-%m-%d'))
    order__order_date__lte = forms.DateField(required=False, label='Не позднее',
                                             widget=DateInput(attrs={'type': 'date'},
                                                              format='%Y-%m-%d'))
    order__to_date_fact__gte = forms.DateField(required=False, label='Не ранее',
                                               widget=DateInput(attrs={'type': 'date'},
                                                                format='%Y-%m-%d'))
    order__to_date_fact__lte = forms.DateField(required=False, label='Не позднее',
                                               widget=DateInput(attrs={'type': 'date'},
                                                                format='%Y-%m-%d'))

    ext_order__carrier = forms.ModelChoiceField(Contractor.objects.all(), label='Перевозчик')
    order__client = forms.ModelChoiceField(Client.objects.all(), label='Заказчик')

    def serialized_result(self, model_label=None):
        if not hasattr(self, 'cleaned_data'):
            self.full_clean()
        # result = dict()
        # for key, value in self.cleaned_data.items():
        #     _model_label, field = key.split('__', maxsplit=1)
        #     if _model_label == model_label and value is not None:
        #         result[field] = value
        # return result
        return {key: value for key, value in self.cleaned_data.items() if value is not None}


class BillOutputForm(forms.Form):
    required_css_class = 'required'

    client = forms.ModelChoiceField(label='Заказчик', queryset=Client.objects.all())
    delivered_from = forms.DateField(label='Начало периода',
                                     widget=DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    delivered_to = forms.DateField(label='Конец периода',
                                   widget=DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    empty_only = forms.BooleanField(label='Только пустые', required=False)
