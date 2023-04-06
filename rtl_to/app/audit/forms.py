from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.forms import inlineformset_factory, CheckboxSelectMultiple, DateInput, BaseInlineFormSet, \
    ModelForm
from django.forms.models import ModelChoiceIterator
from django_genericfilters import forms as gf
from app_auth.models import User, Client
from orders.models import Transit, Order, Document, ORDER_STATUS_LABELS


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

    client = forms.ModelChoiceField(label='Заказчик', required=False, empty_label='Все', queryset=Client.objects.all())
    status = gf.ChoiceField(choices=ORDER_STATUS_LABELS, label='Статус', required=False)
    client_employee = FilterModelChoiceField(label='Наблюдатель', required=False, empty_label='Все', queryset=User.objects.all())
    type = gf.ChoiceField(choices=Order.TYPES, label='Вид поручения', required=False)
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
            ('client_number', 'Номер поручения'),
            ('order_date', 'Дата поручения'),
            ('client', 'Заказчик'),
            ('client_employee', 'Наблюдатель'),
            ('manager', 'Менеджер'),
            ('from_addr_forlist', 'Пункты отправления'),
            ('to_addr_forlist', 'Пункты доставки'),
            ('active_segments', 'Активные плечи'),
            ('status', 'Статус'),
        ]
