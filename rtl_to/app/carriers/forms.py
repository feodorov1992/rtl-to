import logging

from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.forms import DateInput
from django.forms.models import ModelChoiceIterator
from django_genericfilters import forms as gf

from app_auth.models import User
from orders.forms import ExtOrderForm
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

    def clean(self):
        cleaned_data = super(ExtOrderEditForm, self).clean()
        contract = self.instance.contract
        if contract is not None:
            price_carrier = cleaned_data.get('price_carrier')
            currency = cleaned_data.get('currency')
            bill_date = cleaned_data.get('bill_date')

            if not contract.check_sum(price_carrier, currency, bill_date):

                if int(contract.current_sum) == contract.current_sum:
                    sum_float = int(contract.current_sum)
                else:
                    sum_float = round(contract.current_sum, 2)

                sum_str = '{:,} {}'.format(
                    sum_float, contract.get_currency_display()
                ).replace(',', ' ').replace('.', ',')

                self.add_error('price_carrier', f'Остаток договора недостаточен для данного поручения: {sum_str}!')

    def save(self, commit=True):
        result = super(ExtOrderEditForm, self).save(commit)
        contract_affecting_fields = ('price_carrier', 'currency', 'bill_date')
        if any([i in self.changed_data for i in contract_affecting_fields]):
            result.contract.update_current_sum()
            result.update_related('transit', 'price_carrier', related_name='ext_orders')
        return result

    class Meta:
        model = ExtOrder
        fields = ('price_carrier', 'currency', 'taxes', 'act_num', 'act_date', 'bill_num', 'bill_date')
        widgets = {
            'act_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'bill_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }


class CarrierExtOrderForm(ExtOrderForm):

    def __init__(self, *args, **kwargs):
        super(CarrierExtOrderForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.field.widget.attrs.get('class') is not None:
                visible.field.widget.attrs['class'] += f' ext_order_{visible.name}'
            else:
                visible.field.widget.attrs['class'] = f'ext_order_{visible.name}'
        for field in self.fields:
            self.fields[field].disabled = True

    class Meta:
        model = ExtOrder
        exclude = ['order', 'number', 'status', 'from_date_plan', 'from_date_fact', 'to_date_plan', 'to_date_fact',
                   'approx_price', 'necessary_docs', 'insurance_detail', 'price_client', 'currency_client',
                   'weight_payed', 'bill_client']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'from_date_wanted': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'to_date_wanted': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'act_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'bill_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
        labels = {
            'price_carrier': 'Ставка'
        }
