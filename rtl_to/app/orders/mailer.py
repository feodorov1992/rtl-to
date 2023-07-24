from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

from app_auth.mailer import send_logo_mail
from app_auth.models import User
from rtl_to.mailer import MailNotification


class TransitManagerNotification(MailNotification):
    model_label = 'orders.Transit'

    def get_context(self, **kwargs):
        context = super(TransitManagerNotification, self).get_context(**kwargs)
        if settings.ALLOWED_HOSTS:
            context['uri'] = 'http://{domain}/{path}?query={query}'.format(
                domain=settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost',
                path=reverse("orders_list"),
                query=self.object.order.inner_number
            )

        return context

    def collect_recipients(self):
        if self.object.order.manager:
            recipients = [self.object.order.manager.email]
        else:
            recipients = User.objects.filter(user_type='manager').values_list('email', flat=True)
            recipients = list(recipients)
        if self.object.order.created_by is not None and self.object.order.created_by.user_type == 'manager':
            recipients.append(self.object.order.created_by.email)
        return list(set(recipients))


class TransitClientNotification(MailNotification):
    model_label = 'orders.Transit'

    def get_context(self, **kwargs):
        context = super(TransitClientNotification, self).get_context(**kwargs)
        if settings.ALLOWED_HOSTS:
            context['uri'] = 'http://{domain}/{path}?query={query}'.format(
                domain=settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost',
                path=reverse("orders_list_pub"),
                query=self.object.order.client_number
            )

        return context

    def collect_recipients(self):
        if self.object.order.client_employee:
            recipients = [self.object.order.client_employee.email]
        else:
            recipients = self.object.order.client.users.all().values_list('email', flat=True)
        if self.object.order.created_by is not None and self.object.order.created_by.user_type.startswith('client'):
            recipients.append(self.object.order.created_by.email)
        return list(set(recipients))


class FromDatePlanManagerNotification(TransitManagerNotification):
    html_template_path = 'orders/mail/from_date_plan.html'
    txt_template_path = 'orders/mail/from_date_plan.txt'

    def get_subject(self):
        return f'{self.object.number}: определена плановая дата забора груза'


class FromDatePlanClientNotification(TransitClientNotification):
    html_template_path = 'orders/mail/from_date_plan.html'
    txt_template_path = 'orders/mail/from_date_plan.txt'

    def get_subject(self):
        return f'{self.object.number}: определена плановая дата забора груза'


class FromDatePlanSenderNotification(MailNotification):
    model_label = 'orders.Transit'
    html_template_path = 'orders/mail/from_date_plan.html'
    txt_template_path = 'orders/mail/from_date_plan.txt'

    def get_subject(self):
        return f'{self.object.number}: определена плановая дата забора груза'

    def collect_recipients(self):
        recipients = self.object.from_contacts.values_list('email', flat=True)
        return [i for i in recipients if i is not None]


class FromDateFactManagerNotification(TransitManagerNotification):
    html_template_path = 'orders/mail/from_date_fact.html'
    txt_template_path = 'orders/mail/from_date_fact.txt'

    def get_subject(self):
        return f'{self.object.number}: груз забран'


class FromDateFactClientNotification(TransitClientNotification):
    html_template_path = 'orders/mail/from_date_fact.html'
    txt_template_path = 'orders/mail/from_date_fact.txt'

    def get_subject(self):
        return f'{self.object.number}: груз забран'


class ToDatePlanManagerNotification(TransitManagerNotification):
    html_template_path = 'orders/mail/to_date_plan.html'
    txt_template_path = 'orders/mail/to_date_plan.txt'

    def get_subject(self):
        return f'{self.object.number}: определена плановая дата доставки груза'


class ToDatePlanClientNotification(TransitClientNotification):
    html_template_path = 'orders/mail/to_date_plan.html'
    txt_template_path = 'orders/mail/to_date_plan.txt'

    def get_subject(self):
        return f'{self.object.number}: определена плановая дата доставки груза'


class ToDatePlanSenderNotification(MailNotification):
    model_label = 'orders.Transit'
    html_template_path = 'orders/mail/to_date_plan.html'
    txt_template_path = 'orders/mail/to_date_plan.txt'

    def get_subject(self):
        return f'{self.object.number}: определена плановая дата доставки груза'

    def collect_recipients(self):
        recipients = self.object.to_contacts.values_list('email', flat=True)
        return [i for i in recipients if i is not None]


class ToDateFactManagerNotification(TransitManagerNotification):
    html_template_path = 'orders/mail/to_date_fact.html'
    txt_template_path = 'orders/mail/to_date_fact.txt'

    def get_subject(self):
        return f'{self.object.number}: груз доставлен'


class ToDateFactClientNotification(TransitClientNotification):
    html_template_path = 'orders/mail/to_date_fact.html'
    txt_template_path = 'orders/mail/to_date_fact.txt'

    def get_subject(self):
        return f'{self.object.number}: груз доставлен'


class OrderCreatedManagerNotification(MailNotification):
    model_label = 'orders.Order'
    html_template_path = 'orders/mail/order_created.html'
    txt_template_path = 'orders/mail/order_created.txt'

    def get_context(self, **kwargs):
        context = super(OrderCreatedManagerNotification, self).get_context(**kwargs)
        context['order_number'] = self.object.inner_number
        if settings.ALLOWED_HOSTS:
            context['uri'] = 'http://{domain}/{path}?query={query}'.format(
                domain=settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost',
                path=reverse("orders_list"),
                query=self.object.inner_number
            )
        return context

    def get_subject(self):
        return f'Добавлено поручение №{ self.object.inner_number }'

    def collect_recipients(self):
        recipients = User.objects.filter(user_type='manager').values_list('email', flat=True)
        return list(recipients)


class OrderCreatedClientNotification(MailNotification):
    model_label = 'orders.Order'
    html_template_path = 'orders/mail/order_created.html'
    txt_template_path = 'orders/mail/order_created.txt'

    def get_context(self, **kwargs):
        context = super(OrderCreatedClientNotification, self).get_context(**kwargs)
        context['order_number'] = self.object.client_number
        if settings.ALLOWED_HOSTS:
            context['uri'] = 'http://{domain}/{path}?query={query}'.format(
                domain=settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost',
                path=reverse("orders_list_pub"),
                query=self.object.client_number
            )
        return context

    def get_subject(self):
        return f'Добавлено поручение №{ self.object.client_number }'

    def collect_recipients(self):
        recipients = self.object.client.users.values_list('email', flat=True)
        return list(recipients)


def order_assigned_to_manager(request, order):
    order_assigned_to_manager_for_manager(request, order)
    order_assigned_to_manager_for_client(request, order)


def order_assigned_to_manager_for_manager(request, order):
    """
    Составляет и отправляет менеджеру о назначении на него поручения
    :param request: объект запроса
    :param order: поручение
    :return: None
    """
    mail_template = 'orders/mail/order_added_for_manager.html'
    mail_context = {
        'order': order,
        'uri': request.build_absolute_uri(f"{reverse('orders_list')}?query={order.inner_number}")
    }
    subject = f'Вам назначено {order}'
    html_msg = render_to_string(mail_template, mail_context)
    txt_msg = render_to_string(mail_template.replace('html', 'txt'), mail_context)

    recipients = [order.manager.email]
    if order.created_by is not None:
        recipients.append(order.created_by.email)

    send_logo_mail(
        subject,
        txt_msg,
        html_msg,
        settings.EMAIL_HOST_USER,
        recipients
    )


def document_added_to_manager(request, ext_order, doc_type, doc_number):
    """
        Составляет и отправляет менеджеру о добавлении скана в плечо перевозки
        :param request: объект запроса
        :param ext_order: исходящее поручение
        :param doc_type: тип документа
        :param doc_number: номер документа
        :return: None
        """
    mail_template = 'orders/mail/scan_segment_added_for_manager.html'
    mail_context = {
        'order': ext_order.order,
        'ext_order': ext_order,
        'uri': request.build_absolute_uri(f"{reverse('orders_list')}?query={ext_order.order.inner_number}"),
        'doc_type': doc_type,
        'doc_number': doc_number,
        'user': request.user,
    }
    subject = f'Был добавлен скан {doc_type} №{doc_number} к поручению №{ext_order.order.inner_number}'
    html_msg = render_to_string(mail_template, mail_context)
    txt_msg = render_to_string(mail_template.replace('html', 'txt'), mail_context)

    recipients = [ext_order.order.manager.email]
    if ext_order.order.created_by is not None:
        recipients.append(ext_order.order.created_by.email)

    send_logo_mail(
        subject,
        txt_msg,
        html_msg,
        settings.EMAIL_HOST_USER,
        recipients
    )


def order_assigned_to_manager_for_client(request, order):
    """
    Составляет и отправляет клиенту о назначении менеджера в поручении
    :param request: объект запроса
    :param order: поручение
    :return: None
    """
    if order.client_employee is not None:
        mail_template = 'orders/mail/order_added_for_manager_to_client.html'
        mail_context = {
            'order': order,
            'uri': request.build_absolute_uri(f"{reverse('orders_list')}?query={order.inner_number}")
        }
        subject = f'{order} - назначен менеджер'
        html_msg = render_to_string(mail_template, mail_context)
        txt_msg = render_to_string(mail_template.replace('html', 'txt'), mail_context)

        send_logo_mail(
            subject,
            txt_msg,
            html_msg,
            settings.EMAIL_HOST_USER,
            [order.client_employee.email]
        )


def extorder_assigned_to_carrier_for_carrier(request, extorder):
    """
    Формирование и отправка уведомления перевозчику о назначении его на исходящее поручение
    :param request: объект запроса
    :param extorder: поручение
    :return: None
    """
    mail_template = 'orders/mail/extorder_assigned_to_carrier_for_carrier.html'
    mail_context = {
        'extorder': extorder,
        'uri': request.build_absolute_uri(f"{reverse('orders_list_carrier')}?query={extorder.number}")
    }
    subject = f'Поручение №{extorder.number} - Вас назначили в качестве перевозчика.'
    html_msg = render_to_string(mail_template, mail_context)
    txt_msg = render_to_string(mail_template.replace('html', 'txt'), mail_context)

    address_list = [i.email for i in (extorder.contractor.users.all())] if extorder.contractor.email is None or '@' not in str(extorder.contractor.email) else [extorder.contractor.email]

    send_logo_mail(
        subject,
        txt_msg,
        html_msg,
        settings.EMAIL_HOST_USER,
        address_list
    )


