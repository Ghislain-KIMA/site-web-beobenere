from django.urls import reverse
from django.test import TestCase

from ..models import Devis


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