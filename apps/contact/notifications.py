import logging

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone

from .models import ContactMessage

logger = logging.getLogger(__name__)


def send_contact_notification(contact_message):
    """Envoie l'e-mail de notification d'un message de contact. Lève une exception en cas d'échec."""
    admin_url = settings.SITE_URL.rstrip("/") + reverse(
        "admin:contact_contactmessage_change", args=[contact_message.pk]
    )

    subject = f"Nouveau message de contact — {contact_message.full_name}"
    body = (
        f"Nom : {contact_message.full_name}\n"
        f"E-mail : {contact_message.email or '—'}\n"
        f"Téléphone : {contact_message.phone or '—'}\n\n"
        f"Message :\n{contact_message.message}\n\n"
        f"Voir le message : {admin_url}"
    )
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.CONTACT_NOTIFICATION_EMAIL])


def send_pending_notifications():
    """Envoie les notifications des messages pas encore notifiés. Renvoie (envoyées, échecs)."""
    sent, failed = 0, 0
    for contact_message in ContactMessage.objects.filter(notified_at__isnull=True).order_by("created_at"):
        try:
            send_contact_notification(contact_message)
        except Exception:
            logger.exception("Échec de l'envoi de la notification pour le message %s", contact_message.pk)
            failed += 1
        else:
            contact_message.notified_at = timezone.now()
            contact_message.save(update_fields=["notified_at"])
            sent += 1
    return sent, failed