from datetime import datetime, timezone as dt_timezone

from django.contrib import admin
from django.test import TestCase, override_settings

from devis.admin import DevisAdmin
from devis.models import Devis


class DevisAdminTests(TestCase):
    def setUp(self):
        self.model_admin = DevisAdmin(Devis, admin.site)

    def create_devis(self, **overrides):
        data = {"full_name": "Jean Dupont", "email": "jean@example.com", "message": "Besoin d'un site."}
        data.update(overrides)
        devis = Devis.objects.create(**data)
        devis.refresh_from_db()
        return devis

    def test_contact_shows_email_and_phone(self):
        devis = self.create_devis(phone="+22670123456")
        self.assertEqual(self.model_admin.contact(devis), "jean@example.com / +22670123456")

    def test_contact_shows_dash_when_empty(self):
        devis = self.create_devis(email="", phone="")
        self.assertEqual(self.model_admin.contact(devis), "—")

    def test_notified_reflects_notified_at(self):
        devis = self.create_devis()
        self.assertFalse(self.model_admin.notified(devis))

        devis.notified_at = devis.created_at
        self.assertTrue(self.model_admin.notified(devis))

    @override_settings(TIME_ZONE="UTC")
    def test_received_uses_short_format(self):
        devis = self.create_devis()
        Devis.objects.filter(pk=devis.pk).update(created_at=datetime(2026, 10, 5, 17, 42, tzinfo=dt_timezone.utc))
        devis.refresh_from_db()

        self.assertEqual(self.model_admin.received(devis), "05/10/26 17:42")