from django.test import TestCase

from ..models import Devis
from service.models import Category, Service


class DevisModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Bureautique", slug="bureautique")
        self.service = Service.objects.create(
            name="Installation", slug="installation",
            brief_description="Description courte.", category=self.category,
        )

    def test_str_includes_name_and_status(self):
        devis = Devis.objects.create(
            full_name="Jean Dupont", email="jean@example.com",
            message="Besoin d'un devis.",
        )
        self.assertIn("Jean Dupont", str(devis))

    def test_status_defaults_to_new(self):
        devis = Devis.objects.create(
            full_name="Jean Dupont", email="jean@example.com",
            message="Besoin d'un devis.",
        )
        self.assertEqual(devis.status, "new")

    def test_service_is_optional(self):
        devis = Devis.objects.create(
            full_name="Jean Dupont", email="jean@example.com",
            message="Besoin d'un devis.",
        )
        self.assertIsNone(devis.service)

    def test_deleting_service_sets_null_instead_of_deleting_devis(self):
        """on_delete=SET_NULL : supprimer un service ne doit jamais effacer l'historique des demandes."""
        devis = Devis.objects.create(
            full_name="Jean Dupont", email="jean@example.com",
            message="Besoin d'un devis.", service=self.service,
        )
        self.service.delete()
        devis.refresh_from_db()
        self.assertIsNone(devis.service)
        self.assertTrue(Devis.objects.filter(pk=devis.pk).exists())