from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.forms import DateInput

from app_auth.models import User, Counterparty, Contact, Auditor, ReportParams, ClientContract, ContractorContract


class ProfileEditForm(UserChangeForm):
    """
    Форма профиля
    """
    required_css_class = 'required'
    password = None

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'last_name',
            'first_name',
            'second_name',
        ]


class ContractSelectForm(forms.Form):
    """
    Форма выбора договора
    """
    contract = forms.ModelChoiceField(queryset=None, label='Выберите договор',
                                      widget=forms.RadioSelect())

    def __init__(self, queryset, *args, **kwargs):
        super(ContractSelectForm, self).__init__(*args, **kwargs)
        self.fields['contract'].queryset = queryset


class CounterpartySelectForm(forms.Form):
    """
    Форма выбора контрагента
    """
    counterparty = forms.ModelChoiceField(queryset=None, label='Выберите организацию',
                                          widget=forms.RadioSelect())

    def __init__(self, queryset, *args, **kwargs):
        super(CounterpartySelectForm, self).__init__(*args, **kwargs)
        self.fields['counterparty'].queryset = queryset


class ClientContractForm(forms.ModelForm):
    """
    Форма редактирования договора с заказчиком
    """
    required_css_class = 'required'

    class Meta:
        model = ClientContract
        exclude = ['client', 'current_sum']
        widgets = {
            'sign_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'start_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'expiration_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'add_agreement_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }


class ContractorContractForm(forms.ModelForm):
    """
    Форма редактирования договора с подрядчиком
    """
    required_css_class = 'required'

    def save(self, commit=True):
        result = super(ContractorContractForm, self).save(commit)
        if commit:
            result.update_current_sum()
        print(self.cleaned_data)
        return result

    class Meta:
        model = ContractorContract
        exclude = ['contractor', 'current_sum']
        widgets = {
            'sign_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'start_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'expiration_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'add_agreement_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }


def get_contract_form(owner_type):
    """
    Выбор генератора формы договора в зависимости от типа юр. лица в договоре
    :param owner_type: тип юр. лица в договоре
    :return: соответствующий генератор
    """
    if owner_type == 'client':
        return ClientContractForm
    elif owner_type == 'contractor':
        return ContractorContractForm


class CounterpartyForm(forms.ModelForm):
    """
    Форма редактирования контрагента
    """
    required_css_class = 'required'

    class Meta:
        model = Counterparty
        fields = '__all__'
        exclude = ['client', 'contractor', 'admin']


class ContactSelectForm(forms.Form):
    """
    Форма выбора контактных лиц
    """
    contact = forms.ModelMultipleChoiceField(queryset=None, label='Выберите одно или несколько контактных лиц',
                                             widget=forms.CheckboxSelectMultiple())

    def __init__(self, queryset, *args, **kwargs):
        super(ContactSelectForm, self).__init__(*args, **kwargs)
        self.fields['contact'].queryset = queryset


class ContactForm(forms.ModelForm):
    """
    Форма редактирования контактных лиц
    """
    required_css_class = 'required'

    class Meta:
        model = Contact
        exclude = ['cp']


class AuditorForm(forms.ModelForm):
    """
    Форма редактирования аудитора
    """

    def save(self, commit=True):
        result = super(AuditorForm, self).save(commit)
        orders_list = list()
        for client in result.controlled_clients.all():
            orders_list += list(client.orders.all())
        result.orders.set(orders_list)
        return result

    class Meta:
        model = Auditor
        fields = '__all__'


class ReportTemplateForm(forms.ModelForm):
    """
    Форма сохранения шаблона отчета
    """
    class Meta:
        model = ReportParams
        fields = '__all__'
