from django.contrib.auth.forms import UserChangeForm

from app_auth.models import User


class ProfileEditForm(UserChangeForm):
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
