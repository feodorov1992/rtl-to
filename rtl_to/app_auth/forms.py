from django.contrib.auth.forms import UserChangeForm

from app_auth.models import User


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
