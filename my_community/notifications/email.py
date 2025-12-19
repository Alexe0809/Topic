from enum import Enum

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class MessageTypes(Enum):
    EMAIL_CONFIRMATION = {
        "subject": "Подтверждение email",
        "template_name_html": "emails/confirmation.html",
        "template_name_txt": "emails/confirmation.txt",
    }
    RESET_PASSWORD = {
        "subject": "Сброс пароля",
        "template_name_html": "emails/reset_password.html",
        "template_name_txt": "emails/reset_password.txt",
    }


class EmailSender:
    @classmethod
    def send_email(cls, data: dict, target_email, message_type: MessageTypes):
        admin_email = settings.ADMIN_EMAIL
        admin_password = settings.ADMIN_PASSWORD

        if not admin_email or not admin_password:
            return "Email credentials not configured in environment variables"

        context = {
            "confirmation_url": f'http://0.0.0.0:8000/{data.get("url")}',
            "username": data.get("username"),
            "site_url": "#",
        }
        html_content = render_to_string(
            message_type.value["template_name_html"], context
        )

        text_content = render_to_string(
            message_type.value["template_name_txt"], context
        )

        email = EmailMultiAlternatives(
            subject=message_type.value["subject"],
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[target_email],
        )

        email.attach_alternative(html_content, "text/html")

        try:
            email.send(fail_silently=False)
            return f"email with data {data} sent to {target_email}"
        except Exception as e:
            return f"Failed to send email: {e}"
