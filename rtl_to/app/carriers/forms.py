import logging

from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.forms import DateInput
from django.forms.models import ModelChoiceIterator
from django_genericfilters import forms as gf

from app_auth.models import User
from orders.models import EXT_ORDER_STATUS_LABELS, ExtOrder


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

    status = gf.ChoiceField(choices=EXT_ORDER_STATUS_LABELS, label='Статус', required=False)
    contractor_employee = FilterModelChoiceField(label='Наблюдающий сотрудник', required=False, empty_label='Все',
                                                 queryset=User.objects.all())
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
            ('number', 'Номер поручения'),
            ('date', 'Дата поручения'),
            ('contractor_employee', 'Сотрудник'),
            ('manager', 'Менеджер'),
            ('from_addr', 'Адрес отправления'),
            ('to_addr', 'Адрес доставки'),
            ('status', 'Статус'),
        ]


class ExtOrderEditForm(forms.ModelForm):
    """
    Форма редактирования исходящего поручения
    """

    class Meta:
        model = ExtOrder
        fields = ('price_carrier', 'currency', 'taxes', 'act_num', 'act_date', 'bill_num', 'bill_date')
        widgets = {
            'act_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'bill_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
