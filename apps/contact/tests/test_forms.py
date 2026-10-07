from django.test import TestCase

from ..forms import ContactForm


class ContactFormTest(TestCase):
    def valid_data(self, **overrides):
        data = {
            "full_name": "Jean Dupont",
            "email": "",
            "phone": "",
            "message": "Je voudrais plus d'informations sur vos services.",
        }
        data.update(overrides)
        return data

    def test_valid_with_email_only(self):
        form = ContactForm(data=self.valid_data(email="jean@example.com"))
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_with_phone_only(self):
        form = ContactForm(data=self.valid_data(phone="+22670000000"))
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_when_email_and_phone_both_blank(self):
        form = ContactForm(data=self.valid_data())
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Merci de renseigner au moins un moyen",
            form.errors["__all__"][0],
        )

    def test_invalid_phone_does_not_trigger_duplicate_error(self):
        form = ContactForm(data=self.valid_data(phone="123"))
        self.assertFalse(form.is_valid())
        self.assertNotIn("__all__", form.errors)
        self.assertIn("phone", form.errors)

    def test_full_name_too_short_is_rejected(self):
        form = ContactForm(data=self.valid_data(full_name="J", email="jean@example.com"))
        self.assertFalse(form.is_valid())
        self.assertIn("full_name", form.errors)

    def test_full_name_all_digits_is_rejected(self):
        form = ContactForm(data=self.valid_data(full_name="12345", email="jean@example.com"))
        self.assertFalse(form.is_valid())
        self.assertIn("full_name", form.errors)

    def test_full_name_is_stripped(self):
        form = ContactForm(data=self.valid_data(full_name="  Jean Dupont  ", email="jean@example.com"))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["full_name"], "Jean Dupont")

    def test_full_name_whitespace_is_normalized(self):
        """Retours à la ligne, tabulations et espaces multiples deviennent un seul espace :
        un saut de ligne dans le nom ferait échouer l'e-mail de notification (sujet invalide)."""
        form = ContactForm(data=self.valid_data(
            full_name="  Jean\n\tDupont   Junior ",
            email="jean@example.com",
        ))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["full_name"], "Jean Dupont Junior")