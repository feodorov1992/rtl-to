from functools import lru_cache

from django.apps import apps
from django.contrib.staticfiles import finders
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from email.mime.image import MIMEImage

from app_auth.tokens import TokenGenerator
from rtl_to import settings
import logging

from rtl_to.mailer import MailNotification

logger = logging.getLogger(__name__)


@lru_cache()
def logo_data():
    """
    Осуществляет поиск файла логотипа для использования в e-mail
    :return: подготовленный к использованию в письме логотип
    """
    logo_path = settings.BRANDING.static_files().get('LOGO')
    with open(finders.find(logo_path), 'rb') as f:
        logo_bcont = f.read()
    finders.find(logo_path, True)
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
        'user': user,
        'requisites': settings.BRANDING.requisites,
        'email_color': settings.BRANDING.coloring.get('EMAIL_COLOR', '#f08500')
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


class ContractDepletionManagerNotification(MailNotification):
    model_label = 'app_auth.ContractorContract'
    html_template_path = 'app_auth/mail/contract_depleted.html'
    txt_template_path = 'app_auth/mail/contract_depleted.txt'

    def get_context(self, **kwargs):
        context = super(ContractDepletionManagerNotification, self).get_context(**kwargs)
        if settings.ALLOWED_HOSTS:
            context['uri'] = 'http://{domain}/{path}'.format(
                domain=settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost',
                path=reverse("contractor_detail", kwargs={'pk': self.object.contractor.pk}),
            )

        return context

    def get_subject(self):
        return f'Договор №{self.object} истекает!'

    def collect_recipients(self):
        user_model = apps.get_model('app_auth', 'User')
        recipients = user_model.objects.filter(user_type='manager', boss=True).values_list('email', flat=True)
        if not recipients.exists():
            recipients = user_model.objects.filter(user_type='manager').values_list('email', flat=True)
        recipients = list(recipients)
        return list(set(recipients))
