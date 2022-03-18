import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class Organisation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, verbose_name=_('наименование'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('organisation')
        verbose_name_plural = _('organisations')


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    last_name = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('фамилия'))
    first_name = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('имя'))
    second_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('отчество'))
    email = models.EmailField(blank=False, null=False, verbose_name=_('email'), unique=True)

    org = models.ForeignKey(Organisation, on_delete=models.CASCADE, verbose_name=_('организация'), related_name='users',
                            null=True, blank=True)
    is_org_admin = models.BooleanField(default=False, verbose_name=_('администратор организации'))

    def __str__(self):
        if not self.second_name:
            return f'{self.first_name} {self.last_name}'
        else:
            return f'{self.last_name} {self.first_name} {self.second_name}'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
