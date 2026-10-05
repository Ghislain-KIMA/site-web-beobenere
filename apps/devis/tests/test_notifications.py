from io import StringIO
from unittest import mock

from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings

from devis.models import Devis
from devis.notifications import send_pending_notifications


@override_settings(
    DEVIS_NOTIFICATION_EMAIL="gestion@example.com",
    SITE_URL="https://beobenere.test",
)
class SendPendingNotificationsTests(TestCase):
    def create_devis(self, **overrides):
        data = {
            "full_name": "Jean Dupont",
            "email": "jean@example.com",
            "message": "Besoin d'un devis pour un site vitrine.",
        }
        data.update(overrides)
        return Devis.objects.create(**data)

    def test_pending_devis_is_notified_and_marked(self):
        devis = self.create_devis()

        sent, failed = send_pending_notifications()

        self.assertEqual((sent, failed), (1, 0))
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ["gestion@example.com"])
        self.assertIn("Jean Dupont", email.subject)
        self.assertIn(f"https://beobenere.test/admin/devis/devis/{devis.pk}/change/", email.body)
        devis.refresh_from_db()
        self.assertIsNotNone(devis.notified_at)

    def test_already_notified_devis_is_not_sent_again(self):
        self.create_devis()
        send_pending_notifications()

        sent, failed = send_pending_notifications()

        self.assertEqual((sent, failed), (0, 0))
        self.assertEqual(len(mail.outbox), 1)

    def test_failed_send_keeps_devis_pending(self):
        devis = self.create_devis()

        with mock.patch("devis.notifications.send_mail", side_effect=Exception("SMTP indisponible")):
            with self.assertLogs("devis.notifications", level="ERROR"):
                sent, failed = send_pending_notifications()

        self.assertEqual((sent, failed), (0, 1))
        devis.refresh_from_db()
        self.assertIsNone(devis.notified_at)

    def test_command_reports_sent_notifications(self):
        self.create_devis()
        out = StringIO()

        call_command("send_devis_notifications", stdout=out)

        self.assertIn("1 notification(s) envoyée(s)", out.getvalue())

    def test_command_is_silent_when_nothing_pending(self):
        out = StringIO()

        call_command("send_devis_notifications", stdout=out)

        self.assertEqual(out.getvalue(), "")
    