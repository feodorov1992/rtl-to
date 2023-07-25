from django.conf import settings
from django.urls import reverse

from app_auth.models import User
from rtl_to.mailer import MailNotification


class TransportAddedManagerNotification(MailNotification):
    model_label = 'print_forms.TransDocsData'
    html_template_path = 'print_forms/mail/transport_added.html'
    txt_template_path = 'print_forms/mail/transport_added.txt'

    def get_context(self, **kwargs):
        context = super(TransportAddedManagerNotification, self).get_context(**kwargs)
        context['segment'] = self.object.segment
        if settings.ALLOWED_HOSTS:
            context['uri'] = 'http://{domain}/{path}?query={query}'.format(
                domain=settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost',
                path=reverse("orders_list"),
                query=self.object.ext_order.order.inner_number
            )

        return context

    def get_subject(self):
        return f'{self.object.ext_order.number} - назначен транспорт ({self.object.segment.get_type_display()})'

    def collect_recipients(self):
        if self.object.ext_order.manager:
            recipients = [self.object.ext_order.manager.email]
        elif self.object.ext_order.order.manager:
            recipients = [self.object.ext_order.order.manager.email]
        else:
            recipients = User.objects.filter(user_type='manager').values_list('email', flat=True)
            recipients = list(recipients)
        if self.object.ext_order.order.created_by is not None and \
                self.object.ext_order.order.created_by.user_type == 'manager':
            recipients.append(self.object.ext_order.order.created_by.email)
        return list(set(recipients))


class TransportAddedClientNotification(MailNotification):
    model_label = 'print_forms.TransDocsData'
    html_template_path = 'print_forms/mail/transport_added.html'
    txt_template_path = 'print_forms/mail/transport_added.txt'

    def get_context(self, **kwargs):
        context = super(TransportAddedClientNotification, self).get_context(**kwargs)
        context['segment'] = self.object.segment
        return context

    def get_subject(self):
        return f'{self.object.ext_order.number} - назначен транспорт ({self.object.segment.get_type_display()})'

    def get_from_email(self):
        default_from_email = super(TransportAddedClientNotification, self).get_from_email()
        if self.object.ext_order.order.manager:
            manager_email = self.object.ext_order.order.manager.email
            if default_from_email.split('@')[-1] == manager_email.split('@')[-1]:
                return manager_email
        return default_from_email

    def collect_recipients(self):
        if self.object.ext_order.order.client_employee:
            recipients = [self.object.ext_order.order.client_employee.email]
        else:
            recipients = self.object.ext_order.order.client.users.all().values_list('email', flat=True)
        if self.object.ext_order.order.created_by is not None and \
                self.object.ext_order.order.created_by.user_type.startswith('client'):
            recipients.append(self.object.ext_order.order.created_by.email)
        return list(set(recipients))
