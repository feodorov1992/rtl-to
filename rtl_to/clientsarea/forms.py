from django import forms
from django.contrib.auth.forms import UserChangeForm

from app_auth.models import User


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
