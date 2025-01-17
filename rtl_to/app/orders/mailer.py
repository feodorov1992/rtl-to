from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

from app_auth.mailer import send_logo_mail
from app_auth.models import User
from rtl_to.mailer import MailNotification


class ManagerNotification(MailNotification):

    def get_context(self, **kwargs):
        context = super(ManagerNotification, self).get_context(**kwargs)
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
            recipients = User.objects.filter(user_type='manager', is_superuser=False).values_list('email', flat=True)
            recipients = list(recipients)
        if self.object.order.created_by is not None and self.object.order.created_by.user_type == 'manager':
            recipients.append(self.object.order.created_by.email)
        return list(set(recipients))


class ClientNotification(MailNotification):

    def get_context(self, **kwargs):
        context = super(ClientNotification, self).get_context(**kwargs)
        if settings.ALLOWED_HOSTS:
            context['uri'] = 'http://{domain}/{path}?query={query}'.format(
                domain=settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost',
                path=reverse("orders_list_pub"),
                query=self.object.order.client_number
            )

        return context

    def get_from_email(self):
        default_from_email = super(ClientNotification, self).get_from_email()
        if self.object.order.manager:
            manager_email = self.object.order.manager.email
            if default_from_email.split('@')[-1] == manager_email.split('@')[-1]:
                return manager_email
        return default_from_email

    def collect_recipients(self):
        if self.object.order.client_employee:
            recipients = [self.object.order.client_employee.email]
        else:
            recipients = self.object.order.client.users.all().values_list('email', flat=True)
        if self.object.order.created_by is not None and self.object.order.created_by.user_type.startswith('client'):
            recipients.append(self.object.order.created_by.email)
        return list(set(recipients))


class CarrierNotification(MailNotification):

    def get_context(self, **kwargs):
        context = super(CarrierNotification, self).get_context(**kwargs)
        if settings.ALLOWED_HOSTS:
            context['uri'] = 'http://{domain}/{path}?query={query}'.format(
                domain=settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost',
                path=reverse("orders_list_carrier"),
                query=self.object.number
            )

        return context

    def get_from_email(self):
        default_from_email = super(CarrierNotification, self).get_from_email()
        if self.object.manager:
            manager_email = self.object.manager.email
        elif self.object.order.manager:
            manager_email = self.object.order.manager.email
        else:
            manager_email = '@'
        if default_from_email.split('@')[-1] == manager_email.split('@')[-1]:
            return manager_email
        return default_from_email

    def collect_recipients(self):
        if self.object.contractor_employee:
            recipients = [self.object.contractor_employee.email]
        else:
            recipients = self.object.contractor.users.all().values_list('email', flat=True)
        return list(set(recipients))


class FromDatePlanManagerNotification(ManagerNotification):
    model_label = 'orders.ExtOrder'
    html_template_path = 'orders/mail/from_date_plan.html'
    txt_template_path = 'orders/mail/from_date_plan.txt'

    def get_context(self, **kwargs):
        context = super(FromDatePlanManagerNotification, self).get_context(**kwargs)
        context['obj_num_label'] = 'Номер поручения'
        context['obj_num'] = self.object.number
        context['weight'] = self.object.transit.weight
        context['quantity'] = self.object.transit.quantity
        return context

    def get_subject(self):
        return f'Поручение №{self.object.number} ({self.object.contractor}): определена плановая дата забора груза'


class FromDatePlanClientNotification(ClientNotification):
    model_label = 'orders.Transit'
    html_template_path = 'orders/mail/from_date_plan.html'
    txt_template_path = 'orders/mail/from_date_plan.txt'

    def get_context(self, **kwargs):
        context = super(FromDatePlanClientNotification, self).get_context(**kwargs)
        context['obj_num_label'] = 'Номер маршрута'
        context['obj_num'] = self.object.number
        return context

    def get_subject(self):
        return f'{self.object.number}: определена плановая дата забора груза'


class FromDateFactSenderNotification(MailNotification):
    model_label = 'orders.Transit'
    html_template_path = 'orders/mail/from_date_fact.html'
    txt_template_path = 'orders/mail/from_date_fact.txt'

    def get_context(self, **kwargs):
        context = super(FromDateFactSenderNotification, self).get_context(**kwargs)
        context['obj_num_label'] = 'Номер маршрута'
        context['obj_num'] = self.object.number
        return context

    def get_subject(self):
        return f'Определена фактическая дата забора груза'

    def collect_recipients(self):
        recipients = self.object.from_contacts.values_list('email', flat=True)
        return [i for i in recipients if i is not None]


class FromDatePlanCarrierNotification(CarrierNotification):
    model_label = 'orders.ExtOrder'
    html_template_path = 'orders/mail/from_date_plan.html'
    txt_template_path = 'orders/mail/from_date_plan.txt'

    def get_context(self, **kwargs):
        context = super(FromDatePlanCarrierNotification, self).get_context(**kwargs)
        context['obj_num_label'] = 'Номер поручения'
        context['obj_num'] = self.object.number
        context['weight'] = self.object.transit.weight
        context['quantity'] = self.object.transit.quantity
        return context

    def get_subject(self):
        return f'Поручение №{self.object.number}: определена плановая дата забора груза'


class FromDateFactManagerNotification(ManagerNotification):
    model_label = 'orders.ExtOrder'
    html_template_path = 'orders/mail/from_date_fact.html'
    txt_template_path = 'orders/mail/from_date_fact.txt'

    def get_context(self, **kwargs):
        context = super(FromDateFactManagerNotification, self).get_context(**kwargs)
        context['obj_num_label'] = 'Номер поручения'
        context['obj_num'] = self.object.number
        context['weight'] = self.object.transit.weight
        context['quantity'] = self.object.transit.quantity
        return context

    def get_subject(self):
        return f'Поручение №{self.object.number} ({self.object.contractor}): определена фактическая дата забора груза'


class FromDateFactClientNotification(ClientNotification):
    model_label = 'orders.Transit'
    html_template_path = 'orders/mail/from_date_fact.html'
    txt_template_path = 'orders/mail/from_date_fact.txt'

    def get_context(self, **kwargs):
        context = super(FromDateFactClientNotification, self).get_context(**kwargs)
        context['obj_num_label'] = 'Номер маршрута'
        context['obj_num'] = self.object.number
        return context

    def get_subject(self):
        return f'{self.object.number}: определена фактическая дата забора груза'


class FromDateFactCarrierNotification(CarrierNotification):
    model_label = 'orders.ExtOrder'
    html_template_path = 'orders/mail/from_date_fact.html'
    txt_template_path = 'orders/mail/from_date_fact.txt'

    def get_context(self, **kwargs):
        context = super(FromDateFactCarrierNotification, self).get_context(**kwargs)
        context['obj_num_label'] = 'Номер поручения'
        context['obj_num'] = self.object.number
        context['weight'] = self.object.transit.weight
        context['quantity'] = self.object.transit.quantity
        return context

    def get_subject(self):
        return f'Поручение №{self.object.number}: определена фактическая дата забора груза'


class ToDatePlanManagerNotification(ManagerNotification):
    model_label = 'orders.ExtOrder'
    html_template_path = 'orders/mail/to_date_plan.html'
    txt_template_path = 'orders/mail/to_date_plan.txt'

    def get_context(self, **kwargs):
        context = super(ToDatePlanManagerNotification, self).get_context(**kwargs)
        context['obj_num_label'] = 'Номер поручения'
        context['obj_num'] = self.object.number
        context['weight'] = self.object.transit.weight
        context['quantity'] = self.object.transit.quantity
        return context

    def get_subject(self):
        return f'Поручение №{self.object.number} ({self.object.contractor}): определена плановая дата доставки груза'


class ToDatePlanClientNotification(ClientNotification):
    model_label = 'orders.Transit'
    html_template_path = 'orders/mail/to_date_plan.html'
    txt_template_path = 'orders/mail/to_date_plan.txt'

    def get_context(self, **kwargs):
        context = super(ToDatePlanClientNotification, self).get_context(**kwargs)
        context['obj_num_label'] = 'Номер маршрута'
        context['obj_num'] = self.object.number
        return context

    def get_subject(self):
        return f'{self.object.number}: определена плановая дата доставки груза'


class ToDateFactReceiverNotification(MailNotification):
    model_label = 'orders.Transit'
    html_template_path = 'orders/mail/to_date_fact.html'
    txt_template_path = 'orders/mail/to_date_fact.txt'

    def get_context(self, **kwargs):
        context = super(ToDateFactReceiverNotification, self).get_context(**kwargs)
        context['obj_num_label'] = 'Номер маршрута'
        context['obj_num'] = self.object.number
        return context

    def get_subject(self):
        return f'Определена фактическая дата доставки груза'

    def collect_recipients(self):
        recipients = self.object.to_contacts.values_list('email', flat=True)
        return [i for i in recipients if i is not None]


class ToDatePlanCarrierNotification(CarrierNotification):
    model_label = 'orders.ExtOrder'
    html_template_path = 'orders/mail/to_date_plan.html'
    txt_template_path = 'orders/mail/to_date_plan.txt'

    def get_context(self, **kwargs):
        context = super(ToDatePlanCarrierNotification, self).get_context(**kwargs)
        context['obj_num_label'] = 'Номер поручения'
        context['obj_num'] = self.object.number
        context['weight'] = self.object.transit.weight
        context['quantity'] = self.object.transit.quantity
        return context

    def get_subject(self):
        return f'Поручение №{self.object.number}: определена плановая дата доставки груза'


class ToDateFactManagerNotification(ManagerNotification):
    model_label = 'orders.ExtOrder'
    html_template_path = 'orders/mail/to_date_fact.html'
    txt_template_path = 'orders/mail/to_date_fact.txt'

    def get_context(self, **kwargs):
        context = super(ToDateFactManagerNotification, self).get_context(**kwargs)
        context['obj_num_label'] = 'Номер поручения'
        context['obj_num'] = self.object.number
        context['weight'] = self.object.transit.weight
        context['quantity'] = self.object.transit.quantity
        return context

    def get_subject(self):
        return f'Поручение №{self.object.number} ({self.object.contractor}): определена фактическая дата доставки груза'


class ToDateFactClientNotification(ClientNotification):
    model_label = 'orders.Transit'
    html_template_path = 'orders/mail/to_date_fact.html'
    txt_template_path = 'orders/mail/to_date_fact.txt'

    def get_context(self, **kwargs):
        context = super(ToDateFactClientNotification, self).get_context(**kwargs)
        context['obj_num_label'] = 'Номер маршрута'
        context['obj_num'] = self.object.number
        return context

    def get_subject(self):
        return f'{self.object.number}: определена фактическая дата доставки груза'


class ToDateFactCarrierNotification(CarrierNotification):
    model_label = 'orders.ExtOrder'
    html_template_path = 'orders/mail/to_date_fact.html'
    txt_template_path = 'orders/mail/to_date_fact.txt'

    def get_context(self, **kwargs):
        context = super(ToDateFactCarrierNotification, self).get_context(**kwargs)
        context['obj_num_label'] = 'Номер поручения'
        context['obj_num'] = self.object.number
        context['weight'] = self.object.transit.weight
        context['quantity'] = self.object.transit.quantity
        return context

    def get_subject(self):
        return f'Поручение №{self.object.number}: определена фактическая дата доставки груза'


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
        recipients = User.objects.filter(user_type='manager', is_superuser=False).values_list('email', flat=True)
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

    def get_from_email(self):
        default_from_email = super(OrderCreatedClientNotification, self).get_from_email()
        if self.object.manager:
            manager_email = self.object.manager.email
            if default_from_email.split('@')[-1] == manager_email.split('@')[-1]:
                return manager_email
        return default_from_email

    def collect_recipients(self):
        recipients = self.object.client.users.values_list('email', flat=True)
        return list(recipients)


class AddressChangedCarrierNotification(MailNotification):
    model_label = 'orders.ExtOrder'
    html_template_path = 'orders/mail/address_changed.html'
    txt_template_path = 'orders/mail/address_changed.txt'

    def get_context(self, **kwargs):
        context = super(AddressChangedCarrierNotification, self).get_context(**kwargs)
        if settings.ALLOWED_HOSTS:
            context['uri'] = 'http://{domain}/{path}?query={query}'.format(
                domain=settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost',
                path=reverse("orders_list_carrier"),
                query=self.object.number
            )
        return context

    def get_subject(self):
        return f'{self.object.number} - изменен маршрут'

    def get_from_email(self):
        default_from_email = super(AddressChangedCarrierNotification, self).get_from_email()
        if self.object.manager:
            manager_email = self.object.manager.email
            if default_from_email.split('@')[-1] == manager_email.split('@')[-1]:
                return manager_email
        return default_from_email

    def collect_recipients(self):
        if self.object.contractor_employee:
            recipients = [self.object.contractor_employee.email]
        else:
            recipients = self.object.contractor.users.all().values_list('email', flat=True)
        return list(set(recipients))


class DocumentAddedManagerNotification(ManagerNotification):
    model_label = 'orders.Document'
    html_template_path = 'orders/mail/document_added.html'
    txt_template_path = 'orders/mail/document_added.txt'

    def get_context(self, **kwargs):
        context = super(DocumentAddedManagerNotification, self).get_context(**kwargs)
        context['order_number'] = self.object.order.inner_number
        return context

    def get_subject(self):
        return f'{self.object.order.inner_number}: добавлен документ'


class DocumentAddedClientNotification(ClientNotification):
    model_label = 'orders.Document'
    html_template_path = 'orders/mail/document_added.html'
    txt_template_path = 'orders/mail/document_added.txt'

    def get_context(self, **kwargs):
        context = super(DocumentAddedClientNotification, self).get_context(**kwargs)
        context['order_number'] = self.object.order.client_number
        return context

    def get_subject(self):
        return f'{self.object.order.client_number}: добавлен документ'


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


class ExtOrderAssignedCarrierNotification(CarrierNotification):
    model_label = 'orders.ExtOrder'
    html_template_path = 'orders/mail/extorder_assigned_to_carrier_for_carrier.html'
    txt_template_path = 'orders/mail/extorder_assigned_to_carrier_for_carrier.txt'

    def get_subject(self):
        return f'{self.object.number}: Вас назначили в качестве перевозчика'
