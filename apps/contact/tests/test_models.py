from django.test import TestCase

from ..models import ContactMessage


class ContactMessageModelTest(TestCase):
    def test_str_includes_full_name(self):
        message = ContactMessage.objects.create(
            full_name="Jean Dupont", email="jean@example.com",
            message="Je voudrais plus d'informations.",
        )
        self.assertIn("Jean Dupont", str(message))

    def test_is_read_defaults_to_false(self):
        message = ContactMessage.objects.create(
            full_name="Jean Dupont", email="jean@example.com",
            message="Je voudrais plus d'informations.",
        )
        self.assertFalse(message.is_read)

    def test_created_at_is_set_automatically(self):
        message = ContactMessage.objects.create(
            full_name="Jean Dupont", email="jean@example.com",
            message="Je voudrais plus d'informations.",
        )
        self.assertIsNotNone(message.created_at)