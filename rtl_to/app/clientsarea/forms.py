import logging

from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.forms import inlineformset_factory, Select, CheckboxSelectMultiple, DateInput, BaseInlineFormSet, \
    ModelForm
from django.forms.models import ModelChoiceIterator
from django_genericfilters import forms as gf

from app_auth.models import User
from orders.forms import BaseTransitFormset, CargoCalcForm, BaseCargoFormset, TransitForm
from orders.models import Transit, Cargo, Order, Document, ORDER_STATUS_LABELS


logger = logging.getLogger(__name__)


class UserAddForm(forms.ModelForm):
    """
    Форма добавления пользователя
    """
    required_css_class = 'required'

    class Meta:
        model = User
        fields = [
            'email',
            'last_name',
            'first_name',
            'second_name',
        ]


class UserEditForm(UserChangeForm):
    """
    Форма изменения пользователя
    """
    required_css_class = 'required'
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
    client_employee = FilterModelChoiceField(label='Наблюдатель', required=False, empty_label='Все',
                                             queryset=User.objects.all())
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
            ('client_number', 'Номер поручения'),
            ('order_date', 'Дата поручения'),
            ('client_employee', 'Наблюдатель'),
            ('manager', 'Менеджер'),
            ('from_addr_forlist', 'Пункты отправления'),
            ('to_addr_forlist', 'Пункты доставки'),
            ('active_segments', 'Активные плечи'),
            ('status', 'Статус'),
        ]


class OrderCreateBaseTransitFormset(BaseTransitFormset):
    """
    Базовый динамический набор форм перевозок
    """

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


class ClientTransitForm(TransitForm):
    """
    Форма перевозки (клиентская)
    """
    def as_my_style(self):
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='clientsarea/basic_styles/transit_as_my_style.html', context=context)

    class Meta:
        model = Transit
        exclude = ['status']


OrderCreateTransitFormset = inlineformset_factory(Order, Transit, formset=OrderCreateBaseTransitFormset,
                                                  form=ClientTransitForm,
                                                  extra=1,
                                                  exclude=[
                                                      'price', 'price_currency', 'from_addr_short', 'to_addr_short'
                                                  ],
                                                  widgets={'extra_services': CheckboxSelectMultiple(),
                                                           'from_date_wanted': DateInput(attrs={'type': 'date'},
                                                                                         format='%Y-%m-%d'),
                                                           'to_date_wanted': DateInput(attrs={'type': 'date'},
                                                                                       format='%Y-%m-%d')})


class FileUploadForm(forms.ModelForm):
    """
    Форма загрузки документа (клиентская)
    """
    required_css_class = 'required'

    def as_my_style(self):
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='clientsarea/basic_styles/doc_as_my_style.html', context=context)

    class Meta:
        model = Document
        fields = '__all__'


class BaseFileUploadFormset(BaseInlineFormSet):
    """
    Базовый динамический набор форм подгрузки файлов (клиентских)
    """
    def __init__(self, *args, **kwargs):
        super(BaseFileUploadFormset, self).__init__(*args, **kwargs)
        self.queryset = Document.objects.filter(public=True)


FileUploadFormset = inlineformset_factory(
    Order, Document, formset=BaseFileUploadFormset,
    extra=0, form=FileUploadForm,
    fields=['title', 'file']
)
