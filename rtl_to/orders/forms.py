import logging

from django.core.exceptions import ValidationError
from django.forms import TextInput, CheckboxSelectMultiple, Form, CharField, DateInput, DateTimeInput
from django.forms.models import inlineformset_factory, BaseInlineFormSet, ModelForm

import rtl_to.settings
from orders.models import Order, Transit, Cargo, OrderHistory, TransitHistory, TransitSegment, Document, ExtOrder

logger = logging.getLogger(__name__)


def form_save_logging(method):
    def wrapper(ref, commit=True):
        result = method(ref, commit)
        if ref.initial:
            changed_data_tracked = {i: {'old': ref.initial.get(i), 'new': ref.cleaned_data.get(i)} for i in
                                    ref.changed_data}
            log_msg = f'{ref._meta.model.__name__} (pk={result.pk}) updated: {changed_data_tracked}'
        else:
            changed_data_tracked = ref.cleaned_data
            log_msg = f'{ref._meta.model.__name__} (pk={result.pk}) created: {changed_data_tracked}'
        if changed_data_tracked:
            if rtl_to.settings.DEBUG:
                print(log_msg)
            else:
                logger.debug(log_msg)
        return result

    return wrapper


class OrderForm(ModelForm):
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        if 'status' in self.fields:
            self.fields['status'].widget.choices = self.instance.get_status_list()
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = f'order_{visible.name}'

    @form_save_logging
    def save(self, commit=True):
        result = super(OrderForm, self).save(commit)
        if self.initial and 'insurance_currency' in self.changed_data:
            result.currency_rate = None
        if any([i in self.changed_data for i in
                ('insurance', 'sum_insured_coeff', 'insurance_currency', 'currency_rate')]):
            result.collect('transits', 'value')
        if 'client' in self.changed_data:
            result.auditors.set(result.client.auditors.all())
        return result

    class Meta:
        model = Order
        exclude = ['value', 'contract', 'auditors']
        widgets = {
            'order_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
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

    def clean(self):
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
        result = super(BaseTransitFormset, self).is_valid()
        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    for n in form.nested:
                        val = n.is_valid()
                        result = result and val
        return result

    def save(self, commit=True):
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
    'sum_insured',
    'insurance_premium',
    'volume',
    'weight',
    'quantity',
])


class TransitForm(ModelForm):
    required_css_class = 'required'

    def as_my_style(self):
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='management/basic_styles/transit_as_my_style.html', context=context)

    @form_save_logging
    def save(self, commit=True):
        return super(TransitForm, self).save(commit)

    class Meta:
        model = Transit
        fields = '__all__'


class CargoCalcForm(ModelForm):
    required_css_class = 'required'

    def sizes_label(self):
        return self["length"].label_tag("Габариты (ДхШхВ), см")

    def as_my_style(self):
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='management/basic_styles/cargo_as_my_style.html', context=context)

    @form_save_logging
    def save(self, commit=True):
        return super(CargoCalcForm, self).save(commit)

    class Meta:
        model = Cargo
        exclude = ['title']


CargoFormset = inlineformset_factory(Transit, Cargo, extra=0, fields='__all__',
                                     form=CargoCalcForm,
                                     widgets={'extra_services': CheckboxSelectMultiple()}, )


class CalcForm(Form):
    from_addr = CharField(max_length=255, label='Адрес отправки')
    to_addr = CharField(max_length=255, label='Адрес доставки')


class BaseCargoFormset(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        super(BaseCargoFormset, self).__init__(*args, **kwargs)
        for form in self.forms:
            for visible in form.visible_fields():
                visible.field.widget.attrs['class'] = f'cargo_{visible.name}'

    @property
    def empty_form(self):
        form = super().empty_form
        for visible in form.visible_fields():
            visible.field.widget.attrs['class'] = f'cargo_{visible.name}'
        return form

    def save(self, commit=True):
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
                                         exclude=['mark', 'transit'],
                                         widgets={'extra_services': CheckboxSelectMultiple()})


class OrderStatusForm(ModelForm):
    required_css_class = 'required'

    def as_my_style(self):
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='management/basic_styles/status_as_my_style.html', context=context)

    @form_save_logging
    def save(self, commit=True):
        return super(OrderStatusForm, self).save(commit)

    class Meta:
        model = OrderHistory
        fields = '__all__'


class TransitStatusForm(ModelForm):
    required_css_class = 'required'

    def as_my_style(self):
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='management/basic_styles/status_as_my_style.html', context=context)

    @form_save_logging
    def save(self, commit=True):
        return super(TransitStatusForm, self).save(commit)

    class Meta:
        model = TransitHistory
        fields = '__all__'


class TransitSegmentForm(ModelForm):
    required_css_class = 'required'

    def as_my_style(self):
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='management/basic_styles/segment_as_my_style.html', context=context)

    @form_save_logging
    def save(self, commit=True):
        return super(TransitSegmentForm, self).save(commit)

    class Meta:
        model = TransitSegment
        fields = '__all__'


OrderStatusFormset = inlineformset_factory(
    Order, OrderHistory, extra=0, fields='__all__', form=OrderStatusForm,
    widgets={'created_at': DateTimeInput(attrs={'type': 'datetime-local'}, format="%Y-%m-%dT%H:%M:%S")}
)
TransitStatusFormset = inlineformset_factory(
    Transit, TransitHistory, extra=0, fields='__all__', form=TransitStatusForm,
    widgets={'created_at': DateTimeInput(attrs={'type': 'datetime-local'}, format="%Y-%m-%dT%H:%M:%S")}
)


# class AeroTransitForm(ModelForm):
#     required_css_class = 'required'
#
#     def as_my_style(self):
#         context = super().get_context()
#         context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
#         context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
#         return self.render(template_name='management/basic_styles/aero_transit_as_my_style.html', context=context)
#
#     @form_save_logging
#     def save(self, commit=True):
#         return super(AeroTransitForm, self).save(commit)
#
#     class Meta:
#         model = AeroTransit
#         exclude = [
#             'segment'
#         ]
#         widgets = {
#             'awb_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
#         }
#
#
# class AutoTransitForm(ModelForm):
#     required_css_class = 'required'
#
#     def as_my_style(self):
#         context = super().get_context()
#         context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
#         context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
#         return self.render(template_name='management/basic_styles/auto_transit_as_my_style.html', context=context)
#
#     @form_save_logging
#     def save(self, commit=True):
#         return super(AutoTransitForm, self).save(commit)
#
#     class Meta:
#         model = AutoTransit
#         exclude = [
#             'segment'
#         ]


class BaseTransitSegmentFormset(BaseInlineFormSet):
    FIELDS_TO_COPY = [
        'quantity',
        'from_addr',
        'to_addr',
        'weight'
    ]

    CROSS_EXCHANGE = [
        'from_addr',
        'to_addr',
        'sender',
        'receiver'
    ]

    def __init__(self, *args, initials=None, **kwargs):
        super(BaseTransitSegmentFormset, self).__init__(*args, **kwargs)
        self.initials = initials
        for form in self.forms:
            if 'status' in form.fields:
                form.fields['status'].widget.choices = form.instance.get_status_list()

            for field_name in self.CROSS_EXCHANGE:
                form.fields[field_name].widget.attrs['class'] = 'cross_exchange'
            for visible in form.visible_fields():
                if visible.field.widget.attrs.get('class') is not None:
                    visible.field.widget.attrs['class'] += f' segment_{visible.name}'
                else:
                    visible.field.widget.attrs['class'] = f'segment_{visible.name}'

    # def add_fields(self, form, index):
    #     super(BaseTransitSegmentFormset, self).add_fields(form, index)
    #     form.aero = AeroTransitForm(
    #         prefix=form.prefix,
    #         instance=form.instance.aero if hasattr(form.instance, 'aero') else None,
    #         data=form.data if form.is_bound else None
    #     )
    #     form.auto = AutoTransitForm(
    #         prefix=form.prefix,
    #         instance=form.instance.auto if hasattr(form.instance, 'auto') else None,
    #         data=form.data if form.is_bound else None
    #     )

    @property
    def empty_form(self):
        # print(self.instance.__dict__)
        # if hasattr(self.instance, 'transit'):
        #     initials = {field: getattr(self.instance.transit, field) for field in self.FIELDS_TO_COPY}
        #     initials['weight_payed'] = getattr(self.instance.transit, 'weight')
        # else:
        #     initials = {field: getattr(self.instance, field) for field in self.FIELDS_TO_COPY}
        #     initials['weight_payed'] = getattr(self.instance, 'weight')
        # print(self.forms)

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

    # def is_valid(self):
    #     result = super(BaseTransitSegmentFormset, self).is_valid()
    #     # if self.is_bound:
    #     #     for form in self.forms:
    #     #         print(form.instance, form.aero.is_valid(), form.auto.is_valid())
    #     #         result = result and any([form.aero.is_valid(), form.auto.is_valid()])
    #     return result

    def save(self, commit=True):
        result = super(BaseTransitSegmentFormset, self).save(commit)
        changed_data = list()
        for form in self.forms:
            check = form.changed_data if form.initial else form.cleaned_data
            for field in check:
                if field not in changed_data:
                    changed_data.append(field)
            # if not self._should_delete_form(form):
            #
            #     sub_item = None
            #
            #     if form.instance.type == 'plane':
            #         if form.aero.is_valid():
            #             sub_item = form.aero.save(commit=False)
            #         elif not hasattr(form.instance, 'aero'):
            #             sub_item = AeroTransit()
            #         else:
            #             sub_item = form.instance.aero
            #
            #     elif form.instance.type == 'auto':
            #         if form.auto.is_valid():
            #             sub_item = form.auto.save(commit=False)
            #         elif not hasattr(form.instance, 'auto'):
            #             sub_item = AutoTransit()
            #         else:
            #             sub_item = form.instance.auto
            #
            #     if sub_item is not None:
            #         if commit:
            #             if sub_item.segment is None:
            #                 sub_item.segment = form.instance
            #             sub_item.save()
        if changed_data and result:
            result[0].update_related('transit', *changed_data, related_name='segments')
        return result


# TransitSegmentFormset = inlineformset_factory(
#     Transit, TransitSegment, formset=BaseTransitSegmentFormset,
#     extra=0, fields='__all__', form=TransitSegmentForm, widgets={
#         'from_date_plan': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
#         'from_date_fact': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
#         'to_date_plan': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
#         'to_date_fact': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
#     }
# )

ExtOrderSegmentFormset = inlineformset_factory(
    ExtOrder, TransitSegment, formset=BaseTransitSegmentFormset,
    extra=0, exclude=['transit', 'price', 'price_carrier', 'taxes', 'currency'], form=TransitSegmentForm, widgets={
        'from_date_plan': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        'from_date_fact': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        'to_date_plan': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        'to_date_fact': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        'tracking_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
    }
)


class BaseExtOrderFormset(BaseInlineFormSet):

    CROSS_EXCHANGE = [
        'from_addr',
        'to_addr',
    ]

    def __init__(self, *args, segments_initials=None, initials=None, **kwargs):
        super(BaseExtOrderFormset, self).__init__(*args, **kwargs)
        self.segments_initials = segments_initials
        self.initials = initials
        for form in self.forms:
            if 'status' in form.fields:
                form.fields['status'].widget.choices = form.instance.get_status_list()

            for field_name in self.CROSS_EXCHANGE:
                form.fields[field_name].widget.attrs['class'] = 'ext_order_cross_exchange'

            for visible in form.visible_fields():
                if visible.field.widget.attrs.get('class') is not None:
                    visible.field.widget.attrs['class'] += f' ext_order_{visible.name}'
                else:
                    visible.field.widget.attrs['class'] = f'ext_order_{visible.name}'

    def add_fields(self, form, index):
        super(BaseExtOrderFormset, self).add_fields(form, index)
        form.nested = ExtOrderSegmentFormset(
            data=form.data if form.is_bound else None,
            instance=form.instance,
            prefix='%s-%s' % (form.prefix, ExtOrderSegmentFormset.get_default_prefix()),
            initials=self.segments_initials
        )

    def is_valid(self):
        result = super(BaseExtOrderFormset, self).is_valid()
        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    for n in form.nested:
                        val = n.is_valid()
                        result = result and val

        return result

    def save(self, commit=True):
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
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='management/basic_styles/ext_order_as_my_style.html', context=context)

    @form_save_logging
    def save(self, commit=True):
        result = super(ExtOrderForm, self).save(commit)
        return result

    def is_valid(self):
        result = super(ExtOrderForm, self).is_valid()
        return result

    class Meta:
        model = OrderHistory
        fields = '__all__'


ExtOrderFormset = inlineformset_factory(Transit, ExtOrder, formset=BaseExtOrderFormset, form=ExtOrderForm,
                                        extra=0, exclude=['order'], widgets={
                                            'date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
                                            'from_date_wanted': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
                                            'to_date_wanted': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
                                        })


class FileUploadForm(ModelForm):
    required_css_class = 'required'

    def as_my_style(self):
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='management/basic_styles/doc_as_my_style.html', context=context)

    @form_save_logging
    def save(self, commit=True):
        return super(FileUploadForm, self).save(commit)

    class Meta:
        model = Document
        fields = '__all__'


class BaseFileUploadFormset(BaseInlineFormSet):
    pass


FileUploadFormset = inlineformset_factory(
    Order, Document, formset=BaseFileUploadFormset,
    extra=0, fields='__all__', form=FileUploadForm
)
