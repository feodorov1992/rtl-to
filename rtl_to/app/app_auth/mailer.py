from functools import lru_cache
from django.contrib.staticfiles import finders
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from email.mime.image import MIMEImage
from app_auth.tokens import TokenGenerator
from rtl_to import settings
import logging

logger = logging.getLogger(__name__)


@lru_cache()
def logo_data():
    """
    Осуществляет поиск файла логотипа для использования в e-mail
    :return: подготовленный к использованию в письме логотип
    """
    with open(finders.find('img/logo.png'), 'rb') as f:
        logo_bcont = f.read()
    finders.find('img/logo.png', True)
    logo = MIMEImage(logo_bcont)
    logo.add_header('Content-ID', '<logo>')
    return logo


def send_logo_mail(subject, body_text, body_html, from_email, recipients, **kwargs):
    """
    Генератор "красивого" письма
    :param subject: тема письма
    :param body_text: содержимое письма в текстовом виде
    :param body_html: содержимое письма в виде HTML-кода
    :param from_email: отправитель
    :param recipients: список получателей
    :param kwargs: другие именованные атрибуты (игнорируются)
    :return: None
    """
    message = EmailMultiAlternatives(
        subject=subject,
        body=body_text,
        from_email=from_email,
        to=recipients,
        **kwargs
    )
    message.mixed_subtype = 'related'
    message.attach_alternative(body_html, "text/html")
    message.attach(logo_data())

    message.send(fail_silently=False)


def send_technical_mail(request, user, subject, link_name, mail_template):
    """
    Генератор письма, содержащего токен (для восстановления пароля и иже с ним)
    :param request: объект запроса
    :param user: пользователь, для которого генерится токен
    :param subject: тема письма
    :param link_name: техническое наименование URL для генерации ссылки
    :param mail_template: путь и название файла шаблона письма
    :return: None
    """
    restore_passwd_token = TokenGenerator()
    token = restore_passwd_token.make_token(user)

    mail_context = {
        'uri': request.build_absolute_uri(reverse(link_name, args=[user.id, token])),
        'user': user
    }

    html_msg = render_to_string(mail_template, mail_context)
    txt_msg = render_to_string(mail_template.replace('html', 'txt'), mail_context)

    send_logo_mail(
        subject,
        txt_msg,
        html_msg,
        settings.EMAIL_HOST_USER,
        [user.email]
    )
