from django.forms import TextInput, CheckboxSelectMultiple, Form, CharField, DateInput, DateTimeInput
from django.forms.models import inlineformset_factory, BaseInlineFormSet, ModelForm
from orders.models import Order, Transit, Cargo, OrderHistory, TransitHistory, TransitSegment, Document


class OrderForm(ModelForm):
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = f'order_{visible.name}'

    class Meta:
        model = Order
        fields = '__all__'
        widgets = {
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
        return result

    def save(self, commit=True):
        result = super(BaseTransitFormset, self).save(commit=commit)
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
        for visible in form.visible_fields():
            visible.field.widget.attrs['class'] = f'transit_{visible.name}'
        return form


TransitFormset = inlineformset_factory(Order, Transit, formset=BaseTransitFormset, extra=0, fields='__all__')


class TransitForm(ModelForm):
    required_css_class = 'required'

    def as_my_style(self):
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='management/basic_styles/transit_as_my_style.html', context=context)

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

    class Meta:
        model = Cargo
        fields = '__all__'


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


class BaseTransitSegmentFormset(BaseInlineFormSet):

    FIELDS_TO_COPY = [
        'quantity',
        'weight_payed',
        'from_addr',
        'to_addr'
    ]

    def __init__(self, *args, **kwargs):
        super(BaseTransitSegmentFormset, self).__init__(*args, **kwargs)
        for form in self.forms:
            for visible in form.visible_fields():
                visible.field.widget.attrs['class'] = f'segment_{visible.name}'

    @property
    def empty_form(self):
        initials = {field: getattr(self.instance, field) for field in self.FIELDS_TO_COPY}
        form = self.form(
            auto_id=self.auto_id,
            initial=initials,
            prefix=self.add_prefix('__prefix__'),
            empty_permitted=True,
            use_required_attribute=False,
            **self.get_form_kwargs(None),
            renderer=self.renderer,
        )
        self.add_fields(form, None)
        for visible in form.visible_fields():
            visible.field.widget.attrs['class'] = f'segment_{visible.name}'
        return form


TransitSegmentFormset = inlineformset_factory(
    Transit, TransitSegment, formset=BaseTransitSegmentFormset,
    extra=0, fields='__all__', form=TransitSegmentForm, widgets={
            'from_date_plan': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'from_date_fact': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'to_date_plan': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'to_date_fact': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
    }
)


class FileUploadForm(ModelForm):
    required_css_class = 'required'

    def as_my_style(self):
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='management/basic_styles/doc_as_my_style.html', context=context)

    class Meta:
        model = Document
        fields = '__all__'


class BaseFileUploadFormset(BaseInlineFormSet):
    pass


FileUploadFormset = inlineformset_factory(
    Order, Document, formset=BaseFileUploadFormset,
    extra=0, fields='__all__', form=FileUploadForm
)
