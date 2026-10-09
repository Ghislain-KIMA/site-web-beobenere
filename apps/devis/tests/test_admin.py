from datetime import datetime, timezone as dt_timezone

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

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


class DevisAdminProtectionTests(TestCase):
    """Le texte d'une demande venue du site ne peut pas être modifié dans l'admin."""

    CLIENT_FIELDS = {"full_name", "email", "phone", "service", "timeline", "message", "source", "created_at"}

    def setUp(self):
        self.model_admin = DevisAdmin(Devis, admin.site)
        self.request = RequestFactory().get("/admin/")
        self.request.user = get_user_model().objects.create_superuser("admin", "admin@example.com", "motdepasse")

    def create_devis(self, **overrides):
        data = {"full_name": "Jean Dupont", "email": "jean@example.com", "message": "Besoin d'un site."}
        data.update(overrides)
        return Devis.objects.create(**data)

    def test_site_devis_locks_client_fields(self):
        devis = self.create_devis(source="site")
        readonly = set(self.model_admin.get_readonly_fields(self.request, devis))
        self.assertTrue(self.CLIENT_FIELDS <= readonly)

    def test_site_devis_keeps_status_editable(self):
        devis = self.create_devis(source="site")
        self.assertNotIn("status", self.model_admin.get_readonly_fields(self.request, devis))

    def test_manual_devis_stays_editable(self):
        devis = self.create_devis(source="phone")
        readonly = set(self.model_admin.get_readonly_fields(self.request, devis))
        self.assertFalse(self.CLIENT_FIELDS & readonly)

    def test_add_form_has_editable_client_fields(self):
        readonly = set(self.model_admin.get_readonly_fields(self.request, None))
        self.assertFalse(self.CLIENT_FIELDS & readonly)

    def test_add_form_does_not_offer_site_source(self):
        form = self.model_admin.get_form(self.request, None)
        values = [value for value, _ in form.base_fields["source"].choices]
        self.assertNotIn("site", values)
        self.assertEqual(form.base_fields["source"].initial, "phone")


class DevisAdminManualEntryTests(TestCase):
    """Saisie d'une demande reçue par téléphone, WhatsApp ou en personne."""

    def setUp(self):
        user = get_user_model().objects.create_superuser("admin", "admin@example.com", "motdepasse")
        self.client.force_login(user)

    def valid_data(self, **overrides):
        data = {
            "full_name": "Issa Sawadogo",
            "email": "",
            "phone": "+22670123456",
            "message": "Réparation d'un ordinateur portable.",
            "timeline": "",
            "source": "whatsapp",
            "status": "new",
            "created_at_0": "07/10/2026",
            "created_at_1": "09:30:00",
        }
        data.update(overrides)
        return data

    def test_manual_entry_is_saved_with_its_source(self):
        response = self.client.post(reverse("admin:devis_devis_add"), data=self.valid_data())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Devis.objects.get().source, "whatsapp")

    def test_manual_entry_is_not_notified_by_email(self):
        self.client.post(reverse("admin:devis_devis_add"), data=self.valid_data())
        self.assertIsNotNone(Devis.objects.get().notified_at)

    def test_manual_entry_keeps_the_real_received_date(self):
        self.client.post(reverse("admin:devis_devis_add"), data=self.valid_data())
        received = timezone.localtime(Devis.objects.get().created_at)
        self.assertEqual((received.day, received.month, received.hour, received.minute), (7, 10, 9, 30))

    def test_manual_entry_cannot_claim_site_source(self):
        response = self.client.post(reverse("admin:devis_devis_add"), data=self.valid_data(source="site"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Devis.objects.exists())

    def test_editing_site_devis_does_not_change_client_text(self):
        devis = Devis.objects.create(full_name="Jean Dupont", email="jean@example.com", message="Texte d'origine.")
        self.client.post(
            reverse("admin:devis_devis_change", args=[devis.pk]),
            data=self.valid_data(message="Texte modifié.", status="contacted"),
        )
        devis.refresh_from_db()
        self.assertEqual(devis.message, "Texte d'origine.")
        self.assertEqual(devis.status, "contacted")