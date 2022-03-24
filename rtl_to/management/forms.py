from django import forms
from django.contrib.auth.forms import UserChangeForm

from app_auth.models import User


class UserAddForm(forms.ModelForm):
    user_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=(
            ('ORG_USER', 'Пользователь'),
            ('ORG_ADMIN', 'Администратор'),
            ('STAFF_USER', 'Сотрудник'),
        ),
        label='Права пользователя'
    )

    class Meta:
        model = User
        fields = [
            'email',
            'last_name',
            'first_name',
            'second_name',
            'client',
        ]


class UserEditForm(UserChangeForm):
    password = None
    user_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=(
            ('ORG_USER', 'Пользователь'),
            ('ORG_ADMIN', 'Администратор'),
            ('STAFF_USER', 'Сотрудник'),
        )
    )

    class Meta:
        model = User
        fields = [
            'email',
            'last_name',
            'first_name',
            'second_name',
            'client'
        ]
