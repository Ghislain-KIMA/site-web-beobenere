from django.test import TestCase
from ..forms import DevisForm


class DevisFormTest(TestCase):
    def valid_data(self, **overrides):
        data = {
            "full_name": "Jean Dupont",
            "email": "",
            "phone": "",
            "service": "",
            "message": "Besoin d'un devis pour un site vitrine.",
            "timeline": "",
        }
        data.update(overrides)
        return data

    def test_valid_with_email_only(self):
        form = DevisForm(data=self.valid_data(email="jean@example.com"))
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_with_phone_only(self):
        form = DevisForm(data=self.valid_data(phone="+22670000000"))
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_when_email_and_phone_both_blank(self):
        form = DevisForm(data=self.valid_data())
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Merci de renseigner au moins un moyen",
            form.errors["__all__"][0],
        )

    def test_invalid_phone_does_not_trigger_duplicate_error(self):
        """Un numéro mal formé doit afficher une seule erreur, pas le message générique en plus."""
        form = DevisForm(data=self.valid_data(phone="123"))
        self.assertFalse(form.is_valid())
        self.assertNotIn("__all__", form.errors)
        self.assertIn("phone", form.errors)

    def test_full_name_too_short_is_rejected(self):
        form = DevisForm(data=self.valid_data(full_name="J", email="jean@example.com"))
        self.assertFalse(form.is_valid())
        self.assertIn("full_name", form.errors)

    def test_full_name_all_digits_is_rejected(self):
        form = DevisForm(data=self.valid_data(full_name="12345", email="jean@example.com"))
        self.assertFalse(form.is_valid())
        self.assertIn("full_name", form.errors)

    def test_full_name_is_stripped(self):
        form = DevisForm(data=self.valid_data(full_name="  Jean Dupont  ", email="jean@example.com"))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["full_name"], "Jean Dupont")
