import logging
from abc import ABC

from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.forms import inlineformset_factory, CheckboxSelectMultiple, DateInput, Select
from django.forms.models import ModelChoiceIterator
from django_genericfilters import forms as gf

from app_auth.models import User
from orders.models import Order, Transit, Cargo, ORDER_STATUS_LABELS
from orders.forms import BaseTransitFormset, CargoCalcForm, TransitForm, BaseCargoFormset


logger = logging.getLogger(__name__)


class UserAddForm(forms.ModelForm):
    required_css_class = 'required'
    user_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=(
            ('ORG_USER', 'Обычный пользователь'),
            ('ORG_ADMIN', 'Администратор клиента'),
            ('STAFF_USER', 'Сотрудник РТЛ-ТО'),
        ),
        label='Тип пользователя'
    )

    class Meta:
        model = User
        fields = [
            'email',
            'last_name',
            'first_name',
            'second_name',
            'client',
        ]


class UserEditForm(UserChangeForm):
    required_css_class = 'required'
    password = None
    user_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=(
            ('ORG_USER', 'Обычный пользователь'),
            ('ORG_ADMIN', 'Расширенный пользователь'),
            ('STAFF_USER', 'Сотрудник РТЛ-ТО'),
        ),
        label='Тип пользователя'
    )

    class Meta:
        model = User
        fields = [
            'email',
            'last_name',
            'first_name',
            'second_name',
            'client'
        ]


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
            ('client_number', 'Номер клиента'),
            ('inner_number', 'Внутренний номер'),
            ('manager', 'Менеджер'),
            ('from_addr_forlist', 'Адрес отправления'),
            ('to_addr_forlist', 'Адрес доставки'),
            ('order_date', 'Дата поручения'),
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
                                                    'quantity',
                                                ],
                                                widgets={'extra_services': CheckboxSelectMultiple(),
                                                         'from_date_plan': DateInput(attrs={'type': 'date'},
                                                                                     format='%Y-%m-%d'),
                                                         'from_date_fact': DateInput(attrs={'type': 'date'},
                                                                                     format='%Y-%m-%d'),
                                                         'to_date_plan': DateInput(attrs={'type': 'date'},
                                                                                   format='%Y-%m-%d'),
                                                         'to_date_fact': DateInput(attrs={'type': 'date'},
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
                                                  fields='__all__',
                                                  widgets={'extra_services': CheckboxSelectMultiple(),
                                                           'from_date_plan': DateInput(attrs={'type': 'date'},
                                                                                       format='%Y-%m-%d'),
                                                           'from_date_fact': DateInput(attrs={'type': 'date'},
                                                                                       format='%Y-%m-%d'),
                                                           'to_date_plan': DateInput(attrs={'type': 'date'},
                                                                                     format='%Y-%m-%d'),
                                                           'to_date_fact': DateInput(attrs={'type': 'date'},
                                                                                     format='%Y-%m-%d')})

OrderCreateCargoFormset = inlineformset_factory(Transit, Cargo, extra=1, fields='__all__',
                                                form=CargoCalcForm, formset=BaseCargoFormset,
                                                widgets={'currency': Select(),
                                                         'extra_params': CheckboxSelectMultiple()
                                                         }, )
