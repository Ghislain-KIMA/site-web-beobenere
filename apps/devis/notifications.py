import logging

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone

from .models import Devis

logger = logging.getLogger(__name__)


def send_devis_notification(devis):
    """Envoie l'e-mail de notification d'un devis. Lève une exception en cas d'échec."""
    admin_url = settings.SITE_URL.rstrip("/") + reverse("admin:devis_devis_change", args=[devis.pk])

    subject = f"Nouvelle demande de devis — {devis.full_name}"
    body = (
        f"Nom : {devis.full_name}\n"
        f"E-mail : {devis.email or '—'}\n"
        f"Téléphone : {devis.phone or '—'}\n"
        f"Service : {devis.service or '—'}\n"
        f"Délai : {devis.get_timeline_display() or '—'}\n\n"
        f"Message :\n{devis.message}\n\n"
        f"Voir la demande : {admin_url}"
    )
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.DEVIS_NOTIFICATION_EMAIL])


def send_pending_notifications():
    """Envoie les notifications des devis pas encore notifiés. Renvoie (envoyées, échecs)."""
    sent, failed = 0, 0
    for devis in Devis.objects.filter(notified_at__isnull=True).order_by("created_at"):
        try:
            send_devis_notification(devis)
        except Exception:
            logger.exception("Échec de l'envoi de la notification pour le devis %s", devis.pk)
            failed += 1
        else:
            devis.notified_at = timezone.now()
            devis.save(update_fields=["notified_at"])
            sent += 1
    return sent, failed
