from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.forms import inlineformset_factory, TextInput, CheckboxSelectMultiple, DateInput, Select
from app_auth.models import User
from orders.models import Order, Transit, Cargo
from orders.forms import BaseTransitFormset, CargoCalcForm, TransitForm, BaseCargoFormset


class UserAddForm(forms.ModelForm):
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
    password = None
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
            'client'
        ]


class OrderEditBaseTransitFormset(BaseTransitFormset):

    def __init__(self, *args, **kwargs):
        super(OrderEditBaseTransitFormset, self).__init__(*args, **kwargs)
        for form in self.forms:
            for visible in form.visible_fields():
                visible.field.widget.attrs['class'] = f'transit_{visible.name}'

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
                                              form=CargoCalcForm, formset=BaseCargoFormset,
                                              widgets={'weight': TextInput(),
                                                       'length': TextInput(),
                                                       'width': TextInput(),
                                                       'height': TextInput(),
                                                       'value': TextInput(),
                                                       'currency': Select(),
                                                       'extra_params': CheckboxSelectMultiple()
                                                       }, )


class OrderCreateBaseTransitFormset(BaseTransitFormset):

    def __init__(self, *args, **kwargs):
        super(OrderCreateBaseTransitFormset, self).__init__(*args, **kwargs)
        for form in self.forms:
            for visible in form.visible_fields():
                visible.field.widget.attrs['class'] = f'transit_{visible.name}'

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
                                                form=CargoCalcForm, formset=BaseCargoFormset,
                                                widgets={'weight': TextInput(),
                                                         'length': TextInput(),
                                                         'width': TextInput(),
                                                         'height': TextInput(),
                                                         'value': TextInput(),
                                                         'currency': Select(),
                                                         'extra_params': CheckboxSelectMultiple()
                                                         }, )
