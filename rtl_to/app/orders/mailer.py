from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

from app_auth.mailer import send_logo_mail


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

    send_logo_mail(
        subject,
        txt_msg,
        html_msg,
        settings.EMAIL_HOST_USER,
        [order.manager.email]
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

    send_logo_mail(
        subject,
        txt_msg,
        html_msg,
        settings.EMAIL_HOST_USER,
        [ext_order.order.manager.email]
    )


def order_assigned_to_manager_for_client(request, order):
    """
    Составляет и отправляет клиенту о назначении менеджера в поручении
    :param request: объект запроса
    :param order: поручение
    :return: None
    """
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
    Составляет и отправляет клиенту о назначении менеджера в поручении
    :param request: объект запроса
    :param order: поручение
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

