from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.forms import inlineformset_factory, TextInput, CheckboxSelectMultiple, ModelForm, DateInput, Select
from django.forms.widgets import Input, DateTimeInput

from app_auth.models import User
from orders.models import Order, Transit, Cargo, OrderHistory, TransitHistory
from orders.forms import BaseTransitFormset, OrderForm, CargoCalcForm, TransitForm


class UserAddForm(forms.ModelForm):
    user_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=(
            ('ORG_USER', 'Пользователь'),
            ('ORG_ADMIN', 'Администратор'),
            ('STAFF_USER', 'Сотрудник'),
        ),
        label='Права пользователя'
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
    password = None
    user_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=(
            ('ORG_USER', 'Пользователь'),
            ('ORG_ADMIN', 'Администратор'),
            ('STAFF_USER', 'Сотрудник'),
        )
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


class OrderEditBaseTransitFormset(BaseTransitFormset):

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
                                                fields='__all__',
                                                widgets={'volume': TextInput(),
                                                         'weight': TextInput(),
                                                         'quantity': TextInput(),
                                                         'volume_payed': TextInput(),
                                                         'weight_payed': TextInput(),
                                                         'quantity_payed': TextInput(),
                                                         'value': TextInput(),
                                                         'price': TextInput(),
                                                         'price_carrier': TextInput(),
                                                         'extra_services': CheckboxSelectMultiple(),
                                                         'from_date_plan': DateInput(attrs={'type': 'date'},
                                                                                     format='%Y-%m-%d'),
                                                         'from_date_fact': DateInput(attrs={'type': 'date'},
                                                                                     format='%Y-%m-%d'),
                                                         'to_date_plan': DateInput(attrs={'type': 'date'},
                                                                                   format='%Y-%m-%d'),
                                                         'to_date_fact': DateInput(attrs={'type': 'date'},
                                                                                   format='%Y-%m-%d')})

OrderEditCargoFormset = inlineformset_factory(Transit, Cargo, extra=0, fields='__all__',
                                              form=CargoCalcForm,
                                              widgets={'weight': TextInput(),
                                                       'length': TextInput(),
                                                       'width': TextInput(),
                                                       'height': TextInput(),
                                                       'value': TextInput(),
                                                       'currency': Select(attrs={'class': 'currency_select'}),
                                                       'extra_params': CheckboxSelectMultiple()
                                                       }, )


class OrderCreateBaseTransitFormset(BaseTransitFormset):

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
                                                  widgets={'volume': TextInput(),
                                                           'weight': TextInput(),
                                                           'quantity': TextInput(),
                                                           'volume_payed': TextInput(),
                                                           'weight_payed': TextInput(),
                                                           'quantity_payed': TextInput(),
                                                           'value': TextInput(),
                                                           'price': TextInput(),
                                                           'price_carrier': TextInput(),
                                                           'extra_services': CheckboxSelectMultiple(),
                                                           'from_date_plan': DateInput(attrs={'type': 'date'},
                                                                                       format='%Y-%m-%d'),
                                                           'from_date_fact': DateInput(attrs={'type': 'date'},
                                                                                       format='%Y-%m-%d'),
                                                           'to_date_plan': DateInput(attrs={'type': 'date'},
                                                                                     format='%Y-%m-%d'),
                                                           'to_date_fact': DateInput(attrs={'type': 'date'},
                                                                                     format='%Y-%m-%d')})

OrderCreateCargoFormset = inlineformset_factory(Transit, Cargo, extra=1, fields='__all__',
                                                form=CargoCalcForm,
                                                widgets={'weight': TextInput(),
                                                         'length': TextInput(),
                                                         'width': TextInput(),
                                                         'height': TextInput(),
                                                         'value': TextInput(),
                                                         'currency': Select(attrs={'class': 'currency_select'}),
                                                         'extra_params': CheckboxSelectMultiple()
                                                         }, )
