from django.conf import settings

if settings.USE_CELERY:
    import smtplib

    from celery import shared_task
    from celery.exceptions import Reject

    from .email import EmailSender, MessageTypes
    from .schemas import EmailMessageData

    message_type_table = {
        "confirmation": MessageTypes.EMAIL_CONFIRMATION,
        "reset_password": MessageTypes.RESET_PASSWORD,
    }

    @shared_task(
        bind=True,
        autoretry_for=(smtplib.SMTPException,),
        retry_kwargs={"max_retries": 5, "countdown": 30},
        retry_backoff=True,
        retry_jitter=True,
    )
    def send_email(self, email_message_data: dict, message_type: str):
        if message_type in message_type_table:
            message_type = message_type_table[message_type]
        else:
            raise ValueError(
                f"message type '{message_type}' is not supported, use '{message_type_table.keys()}'"
            )

        data = EmailMessageData(**email_message_data)

        try:

            return EmailSender.send_email(
                task_id=self.request.id,
                data=data,
                message_type=message_type,
            )

        except smtplib.SMTPException as exc:
            if self.request.retries >= self.max_retries:
                raise Reject(exc, requeue=False)

            raise
