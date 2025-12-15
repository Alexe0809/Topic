from celery import shared_task

from .email import EmailSender, MessageTypes


@shared_task
def send_email_confirm(email_message_data: dict):
    result = EmailSender.send_email(
        data=email_message_data,
        target_email=email_message_data.get("email"),
        message_type=MessageTypes.EMAIL_CONFIRMATION,
    )
    return result


@shared_task
def send_email_reset_password(email_message_data: dict):
    result = EmailSender.send_email(
        data=email_message_data,
        target_email=email_message_data.get("email"),
        message_type=MessageTypes.RESET_PASSWORD,
    )
    return result
