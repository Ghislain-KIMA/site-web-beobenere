from django.urls import reverse
from django.test import TestCase
from django.db import connection
from django.test.utils import CaptureQueriesContext

from ..models import Category, Service



class ServiceListViewTest(TestCase):
    def setUp(self):
        self.cat_a = Category.objects.create(name="Bureautique", slug="bureautique")
        self.cat_b = Category.objects.create(
            name="Maintenance & dépannage matériel", slug="maintenance-depannage-materiel"
        )
        self.cat_c = Category.objects.create(name="Branding & design", slug="branding-design")

        self.a1 = self._make_service(self.cat_a, "a1")
        self.a2 = self._make_service(self.cat_a, "a2")
        self.b1 = self._make_service(self.cat_b, "b1")
        self.c1 = self._make_service(self.cat_c, "c1")
        self.c2 = self._make_service(self.cat_c, "c2")
        self.a_inactive = self._make_service(self.cat_a, "a-inactive", is_active=False)

    def _make_service(self, category, slug, is_active=True):
        return Service.objects.create(
            name=slug,
            slug=slug,
            brief_description="Description courte.",
            category=category,
            is_active=is_active,
        )

    def test_page_loads(self):
        response = self.client.get(reverse("service:list"))
        self.assertEqual(response.status_code, 200)

    def test_default_order_is_interleaved_round_robin(self):
        """Sans filtre : 1er de chaque catégorie, puis 2e de chaque, etc."""
        response = self.client.get(reverse("service:list"))
        slugs = [s.slug for s in response.context["services"]]
        self.assertEqual(slugs, ["a1", "b1", "c1", "a2", "c2"])

    def test_inactive_services_are_excluded_by_default(self):
        response = self.client.get(reverse("service:list"))
        slugs = [s.slug for s in response.context["services"]]
        self.assertNotIn("a-inactive", slugs)

    def test_filter_shows_only_selected_category(self):
        response = self.client.get(reverse("service:list"), {"categorie": "branding-design"})
        slugs = [s.slug for s in response.context["services"]]
        self.assertEqual(slugs, ["c1", "c2"])

    def test_filter_excludes_inactive_services(self):
        response = self.client.get(reverse("service:list"), {"categorie": "bureautique"})
        slugs = [s.slug for s in response.context["services"]]
        self.assertEqual(slugs, ["a1", "a2"])

    def test_filter_sets_selected_slug_in_context(self):
        response = self.client.get(reverse("service:list"), {"categorie": "maintenance-depannage-materiel"})
        self.assertEqual(response.context["selected_slug"], "maintenance-depannage-materiel")

    def test_no_filter_leaves_selected_slug_empty(self):
        response = self.client.get(reverse("service:list"))
        self.assertFalse(response.context["selected_slug"])

    def test_categories_are_always_in_context(self):
        response = self.client.get(reverse("service:list"))
        self.assertEqual(response.context["categories"].count(), 3)

    def count_queries(self):
        """Compte les requêtes SQL faites pour afficher la page Services."""
        with CaptureQueriesContext(connection) as queries:
            self.client.get(reverse("service:list"))
        return len(queries)

    def test_query_count_does_not_grow_with_services(self):
        """Ajouter des services ne doit pas ajouter de requêtes :
        la catégorie de chaque service doit venir avec lui (select_related)."""
        before = self.count_queries()
        for i in range(3):
            self._make_service(self.cat_a, f"extra-{i}")
        self.assertEqual(self.count_queries(), before)