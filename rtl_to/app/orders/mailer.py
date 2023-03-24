from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

from app_auth.mailer import send_logo_mail


def order_assigned_to_manager(request, order):
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
