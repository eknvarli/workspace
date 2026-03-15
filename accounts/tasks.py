from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_account_email(subject: str, message: str, recipients: list[str]) -> int:
    return send_mail(subject, message, None, recipients, fail_silently=True)
