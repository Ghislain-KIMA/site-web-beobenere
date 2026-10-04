import logging

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

logger = logging.getLogger(__name__)


def notify_new_devis(devis, request):
    """Prévient l'entreprise par e-mail qu'une nouvelle demande de devis est arrivée."""
    admin_url = request.build_absolute_uri(
        reverse("admin:devis_devis_change", args=[devis.pk])
    )

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

    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.DEVIS_NOTIFICATION_EMAIL])
    except Exception:
        logger.exception("Échec de l'envoi de la notification pour le devis %s", devis.pk)
