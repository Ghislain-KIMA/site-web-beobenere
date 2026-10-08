from django.urls import reverse
from django.test import TestCase
from django.core import mail

from ..models import Devis
from service.models import Category, Service



class DevisViewTest(TestCase):
    def valid_data(self, **overrides):
        data = {
            "full_name": "Jean Dupont",
            "email": "jean@example.com",
            "phone": "",
            "service": "",
            "message": "Besoin d'un devis pour un site vitrine.",
            "timeline": "",
        }
        data.update(overrides)
        return data

    def test_get_shows_empty_form(self):
        response = self.client.get(reverse("devis:create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Demander un devis")

    def test_valid_post_creates_devis_and_redirects(self):
        response = self.client.post(reverse("devis:create"), data=self.valid_data())
        self.assertRedirects(response, reverse("devis:success"))
        self.assertEqual(Devis.objects.count(), 1)
        self.assertEqual(Devis.objects.first().full_name, "Jean Dupont")

    def test_invalid_post_does_not_create_devis(self):
        response = self.client.post(
            reverse("devis:create"), data=self.valid_data(email="", phone="")
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Devis.objects.count(), 0)

    def test_new_devis_has_default_status(self):
        self.client.post(reverse("devis:create"), data=self.valid_data())
        self.assertEqual(Devis.objects.first().status, "new")

    def test_success_page_loads(self):
        response = self.client.get(reverse("devis:success"))
        self.assertEqual(response.status_code, 200)

    def test_valid_post_does_not_send_email_immediately(self):
        self.client.post(reverse("devis:create"), data=self.valid_data())

        self.assertEqual(len(mail.outbox), 0)
        self.assertIsNone(Devis.objects.first().notified_at)

    def test_honeypot_is_rendered_but_protected_from_autofill(self):
        response = self.client.get(reverse("devis:create"))
        self.assertContains(response, 'name="website"')
        self.assertContains(response, 'autocomplete="off"')

    def test_bot_filling_honeypot_sees_success_but_nothing_is_saved(self):
        response = self.client.post(
            reverse("devis:create"), data=self.valid_data(website="http://spam.example")
        )
        self.assertRedirects(response, reverse("devis:success"))
        self.assertEqual(Devis.objects.count(), 0)

    def test_bot_with_invalid_data_still_sees_success(self):
        """Le piège est vérifié avant la validation : un robot ne voit jamais de message d'erreur."""
        response = self.client.post(
            reverse("devis:create"),
            data=self.valid_data(email="", phone="", website="http://spam.example"),
        )
        self.assertRedirects(response, reverse("devis:success"))
        self.assertEqual(Devis.objects.count(), 0)

    def test_human_with_empty_honeypot_is_saved(self):
        """Un navigateur envoie le champ vide : la demande doit être enregistrée normalement."""
        response = self.client.post(reverse("devis:create"), data=self.valid_data(website=""))
        self.assertRedirects(response, reverse("devis:success"))
        self.assertEqual(Devis.objects.count(), 1)

    def make_service(self, slug, is_active=True):
        category, _ = Category.objects.get_or_create(name="Bureautique", slug="bureautique")
        return Service.objects.create(
            name=slug, slug=slug, brief_description="x",
            category=category, is_active=is_active,
        )

    def test_service_in_query_string_is_preselected(self):
        """Le lien « Demander un devis » d'une carte de service présélectionne ce service."""
        service = self.make_service("installation")
        response = self.client.get(reverse("devis:create") + "?service=installation")
        self.assertContains(response, f'value="{service.pk}" selected')

    def test_unknown_service_in_query_string_is_ignored(self):
        """Une adresse modifiée à la main ne doit pas faire planter la page."""
        response = self.client.get(reverse("devis:create") + "?service=nexiste-pas")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["form"].initial.get("service"))

    def test_inactive_service_in_query_string_is_not_preselected(self):
        service = self.make_service("ancien", is_active=False)
        response = self.client.get(reverse("devis:create") + "?service=ancien")
        self.assertNotContains(response, f'value="{service.pk}" selected')
