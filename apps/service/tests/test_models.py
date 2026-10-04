from django.db.models import ProtectedError
from django.test import TestCase

from ..models import Category, Service


class CategoryModelTest(TestCase):
    def test_str_returns_name(self):
        category = Category.objects.create(name="Bureautique", slug="bureautique")
        self.assertEqual(str(category), "Bureautique")

    def test_slug_must_be_unique(self):
        Category.objects.create(name="Bureautique", slug="bureautique")
        with self.assertRaises(Exception):
            Category.objects.create(name="Autre nom", slug="bureautique")


class ServiceModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Bureautique", slug="bureautique")

    def test_str_returns_name(self):
        service = Service.objects.create(
            name="Installation", slug="installation",
            brief_description="Description courte.", category=self.category,
        )
        self.assertEqual(str(service), "Installation")

    def test_is_active_defaults_to_true(self):
        service = Service.objects.create(
            name="Installation", slug="installation",
            brief_description="Description courte.", category=self.category,
        )
        self.assertTrue(service.is_active)

    def test_category_cannot_be_deleted_while_services_exist(self):
        """on_delete=PROTECT : une catégorie utilisée ne doit jamais pouvoir être supprimée."""
        Service.objects.create(
            name="Installation", slug="installation",
            brief_description="Description courte.", category=self.category,
        )
        with self.assertRaises(ProtectedError):
            self.category.delete()