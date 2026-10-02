from django.urls import reverse
from django.test import TestCase

from ..models import ContactMessage
from company.models import Company


class ContactViewTest(TestCase):
    def setUp(self):
        Company.objects.create(
            name="BeoBenere",
            email="beobenere.business@gmail.com",
            phone="+22672750096",
        )

    def valid_data(self, **overrides):
        data = {
            "full_name": "Jean Dupont",
            "email": "jean@example.com",
            "phone": "",
            "message": "Je voudrais plus d'informations sur vos services.",
        }
        data.update(overrides)
        return data

    def test_get_shows_empty_form(self):
        response = self.client.get(reverse("contact:page"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Contactez-nous")

    def test_valid_post_creates_message_and_redirects(self):
        response = self.client.post(reverse("contact:page"), data=self.valid_data())
        self.assertRedirects(response, reverse("contact:success"))
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(ContactMessage.objects.first().full_name, "Jean Dupont")

    def test_invalid_post_does_not_create_message(self):
        response = self.client.post(
            reverse("contact:page"), data=self.valid_data(email="", phone="")
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_new_message_is_unread_by_default(self):
        self.client.post(reverse("contact:page"), data=self.valid_data())
        self.assertFalse(ContactMessage.objects.first().is_read)

    def test_success_page_loads(self):
        response = self.client.get(reverse("contact:success"))
        self.assertEqual(response.status_code, 200)

    def test_page_shows_company_contact_details(self):
        """La page Contact doit afficher les coordonnées de Company, injectées via le contexte."""
        response = self.client.get(reverse("contact:page"))
        self.assertContains(response, "beobenere.business@gmail.com")