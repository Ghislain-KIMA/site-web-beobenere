from unittest.mock import patch

from django.db import DatabaseError
from django.test import RequestFactory, TestCase

from ..context_processors import company
from ..models import Company


class CompanyContextProcessorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_returns_company_when_database_is_available(self):
        Company.objects.create(
            name="BeoBenere",
            email="beobenere.business@gmail.com",
            phone="+22672750096",
        )
        request = self.factory.get("/")
        context = company(request)
        self.assertEqual(context["site_company"].name, "BeoBenere")

    def test_returns_none_when_database_is_unavailable(self):
        """Le processeur ne doit jamais planter, même si la base de données ne répond pas."""
        request = self.factory.get("/")
        with patch(
            "company.context_processors.Company.objects.first",
            side_effect=DatabaseError,
        ):
            context = company(request)
        self.assertIsNone(context["site_company"])

    def test_homepage_still_responds_when_database_is_unavailable(self):
        """Test de bout en bout : une vraie page continue de répondre malgré la panne simulée."""
        with patch(
            "company.context_processors.Company.objects.first",
            side_effect=DatabaseError,
        ):
            response = self.client.get("/")
        self.assertEqual(response.status_code, 200)