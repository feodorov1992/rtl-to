import logging
import uuid
from email.mime.image import MIMEImage
from functools import lru_cache
from smtplib import SMTPRecipientsRefused, SMTPDataError, SMTPResponseException
from typing import List

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.mail import EmailMultiAlternatives
from django.apps import apps
from django.template.loader import render_to_string

from rtl_to.celery import app


class MailNotification:
    model_label: str = None
    subject: str = None
    from_email: str = None
    recipients: List[str] = None
    html_template_path: str = None
    txt_template_path: str = None
    logo_path: str = settings.BRANDING.static_files()['LOGO']
    email_color = settings.BRANDING.coloring.get('EMAIL_COLOR', '#f08500')

    def __init__(self, main_object_id: uuid.UUID):
        self.main_object_id = main_object_id
        self.object = self.get_object()
        self.context = self.get_context()
        self.context['email_color'] = self.email_color
        self.model = None

    @lru_cache()
    def __logo_data(self):
        with open(finders.find(self.logo_path), 'rb') as f:
            logo_data = f.read()
        logo = MIMEImage(logo_data)
        logo.add_header('Content-ID', '<logo>')
        return logo

    def __send_logo_mail(self, subject, body_text, body_html, from_email, recipients, **kwargs):

        if not recipients:
            return 'NO_RECIPIENTS'

        message = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=from_email,
            to=recipients,
            **kwargs
        )
        message.mixed_subtype = 'related'
        message.attach_alternative(body_html, "text/html")
        message.attach(self.__logo_data())
        result = 'SUCCESS'

        if settings.ALLOW_TO_SEND_MAIL:
            log_msg = [
                f'from_email: {from_email}',
                f'recipients: {", ".join([i for i in recipients if i is not None])}'
            ]
            log = logging.info
            try:
                if not message.send(fail_silently=False):
                    result = 'UNKNOWN_ERROR'
                log_msg.append(f'status: {result}')
            except Exception as e:
                result = 'ERROR'
                log_msg.append(f'error: {e}')
                log = logging.error
            log('; '.join(log_msg))
        return result

    def get_object(self):
        split_label = self.model_label.split('.')
        self.model = apps.get_model(split_label[0], split_label[-1])
        return self.model.objects.get(pk=self.main_object_id)

    def get_context(self, **kwargs):
        model_title = self.model.__name__.lower()
        return {'object': self.object, model_title: self.object, **kwargs}

    def get_subject(self):
        return str(self.object)

    def get_from_email(self):
        if self.from_email is None:
            self.from_email = settings.EMAIL_HOST_USER
        return self.from_email

    def collect_recipients(self) -> list:
        raise NotImplementedError(
            "You must either provide 'recipients' list or inherit 'collect_recipients' method to generate it"
        )

    def send(self):
        recipients = self.recipients if self.recipients else self.collect_recipients()
        if hasattr(settings, 'EMAIL_HOST_ONLY') and settings.EMAIL_HOST_ONLY:
            from_email = settings.EMAIL_HOST_USER
        else:
            from_email = self.get_from_email()
        return self.__send_logo_mail(
            subject=self.subject if self.subject else self.get_subject(),
            body_text=render_to_string(self.txt_template_path, self.context),
            body_html=render_to_string(self.html_template_path, self.context),
            from_email=from_email,
            recipients=[i for i in recipients if i is not None]
        )
