from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse

from app_auth.tokens import TokenGenerator


def send_technical_mail(request, user, subject, from_email, link_name, mail_template):
    restore_passwd_token = TokenGenerator()
    token = restore_passwd_token.make_token(user)
    html_message = render_to_string(mail_template, {
        'uri': request.build_absolute_uri(reverse(link_name, args=[user.id, token])),
        'user': user
    })
    email = EmailMessage(subject, html_message, from_email=from_email, to=[user.email])
    email.content_subtype = "html"
    email.send()
