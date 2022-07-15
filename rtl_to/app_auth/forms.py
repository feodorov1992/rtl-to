from django.contrib.auth.forms import UserChangeForm
from django import forms

from app_auth.models import User, Counterparty, Contact


class ProfileEditForm(UserChangeForm):
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


class CounterpartySelectForm(forms.Form):
    counterparty = forms.ModelChoiceField(queryset=None, label='Выберите организацию',
                                          widget=forms.RadioSelect())

    def __init__(self, queryset, *args, **kwargs):
        super(CounterpartySelectForm, self).__init__(*args, **kwargs)
        self.fields['counterparty'].queryset = queryset


class CounterpartyCreateForm(forms.ModelForm):

    class Meta:
        model = Counterparty
        fields = '__all__'
        exclude = ['client']


class ContactSelectForm(forms.Form):
    contact = forms.ModelMultipleChoiceField(queryset=None, label='Выберите одно или несколько контактных лиц',
                                             widget=forms.CheckboxSelectMultiple())

    def __init__(self, queryset, *args, **kwargs):
        super(ContactSelectForm, self).__init__(*args, **kwargs)
        self.fields['contact'].queryset = queryset


class ContactCreateForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = '__all__'
        exclude = ['cp']
