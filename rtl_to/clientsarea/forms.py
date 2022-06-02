from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.forms import inlineformset_factory, TextInput, Select, CheckboxSelectMultiple, DateInput, BaseInlineFormSet, \
    ModelForm

from app_auth.models import User
from orders.forms import BaseTransitFormset, CargoCalcForm, BaseCargoFormset
from orders.models import Transit, Cargo, Order, Document


class UserAddForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'email',
            'last_name',
            'first_name',
            'second_name',
        ]


class UserEditForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = [
            'email',
            'last_name',
            'first_name',
            'second_name',
            'username'
        ]


OrderCreateCargoFormset = inlineformset_factory(Transit, Cargo, extra=1,
                                                form=CargoCalcForm, formset=BaseCargoFormset,
                                                widgets={'currency': Select(),
                                                         'extra_params': CheckboxSelectMultiple()
                                                         },
                                                fields='__all__',
                                                )


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


class TransitForm(ModelForm):

    def as_my_style(self):
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='clientsarea/basic_styles/transit_as_my_style.html', context=context)

    class Meta:
        model = Transit
        fields = '__all__'


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


class FileUploadForm(forms.ModelForm):

    def as_my_style(self):
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='clientsarea/basic_styles/doc_as_my_style.html', context=context)

    class Meta:
        model = Document
        fields = '__all__'


class BaseFileUploadFormset(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        super(BaseFileUploadFormset, self).__init__(*args, **kwargs)
        self.queryset = Document.objects.filter(public=True)


FileUploadFormset = inlineformset_factory(
    Order, Document, formset=BaseFileUploadFormset,
    extra=0, form=FileUploadForm,
    fields=['title', 'file']
)
