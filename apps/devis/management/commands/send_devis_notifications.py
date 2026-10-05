from django.core.management.base import BaseCommand

from devis.notifications import send_pending_notifications


class Command(BaseCommand):
    help = "Envoie les notifications des demandes de devis pas encore notifiées."

    def handle(self, *args, **options):
        sent, failed = send_pending_notifications()
        if sent or failed:
            self.stdout.write(f"{sent} notification(s) envoyée(s), {failed} échec(s).")
