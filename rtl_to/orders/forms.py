import json
from abc import ABC
from typing import Any

from django.forms import TextInput, CheckboxSelectMultiple, Form, CharField, DateInput, DateField, DateTimeInput
# from django.forms.formsets import DELETION_FIELD_NAME
from django.forms.models import inlineformset_factory, BaseInlineFormSet, ModelForm, ModelChoiceField
# from tapeforms.mixins import TapeformMixin

from orders.models import Order, Transit, Cargo, OrderHistory, TransitHistory


class OrderForm(ModelForm):
    # client_employee = ModelChoiceField(queryset=request)

    class Meta:
        model = Order
        fields = '__all__'
        widgets = {
            'price': TextInput(),
            'price_carrier': TextInput(),
            'from_date_plan': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'from_date_fact': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'to_date_plan': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'to_date_fact': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        }


class BaseTransitFormset(BaseInlineFormSet):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('sub_number')

    def add_fields(self, form, index):
        super(BaseTransitFormset, self).add_fields(form, index)
        form.nested = CargoFormset(
            data=form.data if form.is_bound else None,
            instance=form.instance,
            prefix='%s-%s' % (form.prefix, CargoFormset.get_default_prefix())
        )

    def is_valid(self):
        result = super(BaseTransitFormset, self).is_valid()
        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    for n in form.nested:
                        val = n.is_valid()
                        result = result and val
                        if not val:
                            print(n.errors)
        return result

    def save(self, commit=True):
        result = super(BaseTransitFormset, self).save(commit=commit)
        print('result:', result)
        for form in self.forms:
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)

        return result

    @property
    def empty_form(self):
        form = self.form(
            auto_id=self.auto_id,
            prefix=self.add_prefix('__tprefix__'),
            empty_permitted=True,
            use_required_attribute=False,
            **self.get_form_kwargs(None),
            renderer=self.renderer,
        )
        self.add_fields(form, None)
        return form


TransitFormset = inlineformset_factory(Order, Transit, formset=BaseTransitFormset, extra=0, fields='__all__',
                                       widgets={'volume': TextInput(),
                                                'weight': TextInput(),
                                                'quantity': TextInput(),
                                                'volume_payed': TextInput(),
                                                'weight_payed': TextInput(),
                                                'quantity_payed': TextInput(),
                                                'value': TextInput(),
                                                'price': TextInput(),
                                                'price_carrier': TextInput()})


class TransitForm(ModelForm):
    def as_my_style(self):
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='management/basic_styles/transit_as_my_style.html', context=context)

    class Meta:
        model = Cargo
        fields = '__all__'


class CargoCalcForm(ModelForm):

    def as_my_style(self):
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='management/basic_styles/cargo_as_my_style.html', context=context)

    class Meta:
        model = Cargo
        fields = '__all__'


CargoFormset = inlineformset_factory(Transit, Cargo, extra=0, fields='__all__',
                                     form=CargoCalcForm,
                                     widgets={'weight': TextInput(),
                                              'length': TextInput(),
                                              'width': TextInput(),
                                              'height': TextInput(),
                                              'value': TextInput(),
                                              'extra_services': CheckboxSelectMultiple()}, )


class CalcForm(Form):
    from_addr = CharField(max_length=255, label='Адрес отправки')
    to_addr = CharField(max_length=255, label='Адрес доставки')


CargoCalcFormset = inlineformset_factory(Transit, Cargo, extra=1, form=CargoCalcForm,
                                         exclude=['mark', 'transit'],
                                         widgets={'weight': TextInput(),
                                                  'length': TextInput(),
                                                  'width': TextInput(),
                                                  'height': TextInput(),
                                                  'value': TextInput(),
                                                  'extra_services': CheckboxSelectMultiple()})


class OrderStatusForm(ModelForm):

    def as_my_style(self):
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='management/basic_styles/status_as_my_style.html', context=context)

    class Meta:
        model = OrderHistory
        fields = '__all__'


class TransitStatusForm(ModelForm):

    def as_my_style(self):
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='management/basic_styles/status_as_my_style.html', context=context)

    class Meta:
        model = TransitHistory
        fields = '__all__'


OrderStatusFormset = inlineformset_factory(
    Order, OrderHistory, extra=0, fields='__all__', form=OrderStatusForm,
    widgets={'created_at': DateTimeInput(attrs={'type': 'datetime-local'}, format="%Y-%m-%dT%H:%M:%S")}
)
TransitStatusFormset = inlineformset_factory(
    Transit, TransitHistory, extra=0, fields='__all__', form=TransitStatusForm,
    widgets={'created_at': DateTimeInput(attrs={'type': 'datetime-local'}, format="%Y-%m-%dT%H:%M:%S")}
)
