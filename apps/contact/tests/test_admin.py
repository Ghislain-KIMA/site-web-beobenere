from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings

from datetime import datetime, timezone as dt_timezone

from contact.admin import ContactMessageAdmin
from contact.models import ContactMessage


class ContactMessageAdminTests(TestCase):
    def setUp(self):
        self.model_admin = ContactMessageAdmin(ContactMessage, admin.site)

    def create_message(self, **overrides):
        data = {"full_name": "Awa Ouédraogo", "email": "awa@example.com", "message": "Bonjour."}
        data.update(overrides)
        contact_message = ContactMessage.objects.create(**data)
        contact_message.refresh_from_db()
        return contact_message

    def test_contact_shows_email_and_phone(self):
        contact_message = self.create_message(phone="+22670123456")
        self.assertEqual(self.model_admin.contact(contact_message), "awa@example.com / +22670123456")

    def test_short_message_keeps_short_messages_intact(self):
        contact_message = self.create_message(message="Bonjour.")
        self.assertEqual(self.model_admin.short_message(contact_message), "Bonjour.")

    def test_short_message_truncates_long_messages(self):
        contact_message = self.create_message(message="a" * 100)
        result = self.model_admin.short_message(contact_message)

        self.assertEqual(len(result), 60)
        self.assertTrue(result.endswith("…"))

    def test_notified_reflects_notified_at(self):
        contact_message = self.create_message()
        self.assertFalse(self.model_admin.notified(contact_message))

    def test_mark_as_read_action(self):
        self.create_message()
        self.create_message()

        self.model_admin.mark_as_read(None, ContactMessage.objects.all())

        self.assertEqual(ContactMessage.objects.filter(is_read=True).count(), 2)

    def test_mark_as_unread_action(self):
        self.create_message(is_read=True)

        self.model_admin.mark_as_unread(None, ContactMessage.objects.all())

        self.assertEqual(ContactMessage.objects.filter(is_read=False).count(), 1)

    @override_settings(TIME_ZONE="UTC")
    def test_received_uses_short_format(self):
        contact_message = self.create_message()
        ContactMessage.objects.filter(pk=contact_message.pk).update(
            created_at=datetime(2026, 10, 5, 17, 43, tzinfo=dt_timezone.utc)
        )
        contact_message.refresh_from_db()

        self.assertEqual(self.model_admin.received(contact_message), "05/10/26 17:43")


class ContactMessageAdminProtectionTests(TestCase):
    """Les messages viennent uniquement du site et ne se modifient pas."""

    def setUp(self):
        self.model_admin = ContactMessageAdmin(ContactMessage, admin.site)
        self.request = RequestFactory().get("/admin/")
        self.request.user = get_user_model().objects.create_superuser("admin", "admin@example.com", "motdepasse")

    def test_client_fields_are_read_only(self):
        contact_message = ContactMessage.objects.create(full_name="Awa Ouédraogo", message="Bonjour.")
        readonly = set(self.model_admin.get_readonly_fields(self.request, contact_message))
        self.assertTrue({"full_name", "email", "phone", "message"} <= readonly)

    def test_is_read_stays_editable(self):
        contact_message = ContactMessage.objects.create(full_name="Awa Ouédraogo", message="Bonjour.")
        self.assertNotIn("is_read", self.model_admin.get_readonly_fields(self.request, contact_message))

    def test_messages_cannot_be_added_in_admin(self):
        self.assertFalse(self.model_admin.has_add_permission(self.request))