import uuid
from email.mime.image import MIMEImage
from functools import lru_cache
from smtplib import SMTPRecipientsRefused
from typing import List

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string

from rtl_to.celery import app


class MailNotification:
    model: models.base.ModelBase = None
    subject: str = None
    from_email: str = settings.EMAIL_HOST_USER
    recipients: List[str] = None
    html_template_path: str = None
    txt_template_path: str = None
    logo_path: str = 'img/logo.png'

    def __init__(self, main_object_id: uuid.UUID):
        self.main_object_id = main_object_id
        self.object = self.get_object()
        self.context = self.get_context()

    @lru_cache()
    def __logo_data(self):
        with open(finders.find(self.logo_path), 'rb') as f:
            logo_data = f.read()
        logo = MIMEImage(logo_data)
        logo.add_header('Content-ID', '<logo>')
        return logo

    def __send_logo_mail(self, subject, body_text, body_html, from_email, recipients, **kwargs):
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

        try:
            return message.send(fail_silently=False)
        except SMTPRecipientsRefused:
            return 0

    def get_object(self):
        return self.model.objects.get(pk=self.main_object_id)

    def get_context(self, **kwargs):
        model_title = self.model.__name__.lower()
        return {'object': self.object, model_title: self.object, **kwargs}

    def get_subject(self):
        return str(self.object)

    def collect_recipients(self):
        return ['feodorov1992@mail.ru']

    def send(self):
        return self.__send_logo_mail(
            subject=self.subject if self.subject else self.get_subject(),
            body_text=render_to_string(self.txt_template_path, self.context),
            body_html=render_to_string(self.html_template_path, self.context),
            from_email=self.from_email,
            recipients=self.recipients if self.recipients else self.collect_recipients()
        )

