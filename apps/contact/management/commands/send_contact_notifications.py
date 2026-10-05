from django.core.management.base import BaseCommand
from django.utils import timezone

from contact.notifications import send_pending_notifications


class Command(BaseCommand):
    help = "Envoie les notifications des messages de contact pas encore notifiés."

    def handle(self, *args, **options):
        sent, failed = send_pending_notifications()
        if sent or failed:
            self.stdout.write(
                f"{timezone.localtime():%Y-%m-%d %H:%M} Contact : "
                f"{sent} notification(s) envoyée(s), {failed} échec(s)."
            )