import logging
import smtplib
from enum import Enum

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string

from my_community.notifications.schemas import EmailMessageData, MessageType


class MessageTypes(Enum):
    EMAIL_CONFIRMATION = MessageType(
        **{
            "subject": "Подтверждение email",
            "template_name_html": "emails/confirmation.html",
            "template_name_txt": "emails/confirmation.txt",
        }
    )
    RESET_PASSWORD = MessageType(
        **{
            "subject": "Сброс пароля",
            "template_name_html": "emails/reset_password.html",
            "template_name_txt": "emails/reset_password.txt",
        }
    )


class EmailSender:
    @classmethod
    def send_email(
        cls, task_id, data: EmailMessageData, message_type: MessageTypes
    ):

        context = ContextBuilder(data)

        try:
            html_content = ContextStringRender(
                message_type.value.template_name_html, context.to_dict()
            ).render()

            text_content = ContextStringRender(
                message_type.value.template_name_txt, context.to_dict()
            ).render()
        except Exception as exc:
            logging.error("Template render failed: %s", exc)
            raise ValueError("Email template error")

        connection = get_connection(timeout=10)

        email = EmailMultiAlternatives(
            subject=message_type.value.subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[data.email],
            connection=connection,
        )

        email.attach_alternative(html_content, "text/html")

        try:
            email.send(fail_silently=False)
            logging.log(
                logging.INFO,
                f"message: type={message_type}, task_id={task_id} was delivered",
            )
            return True
        except smtplib.SMTPException as e:
            logging.log(logging.ERROR, e)
            raise


class ContextBuilder:
    def __init__(self, data: EmailMessageData):
        self.confirmation_url = (
            f"{settings.FRONTEND_URL}{data.url}"  # тестовое решение
        )
        self.username = data.username
        self.site_url = "#"

    def to_dict(self):
        return {
            "confirmation_url": self.confirmation_url,
            "username": self.username,
            "site_url": self.site_url,
        }


class ContextStringRender:
    def __init__(self, template_path: str, context_dict: dict):
        self.template_path = template_path
        self.context_dict = context_dict

    def render(self):
        return render_to_string(self.template_path, self.context_dict)
