from django.urls import reverse
from django.test import TestCase

from company.models import Company


class HomepageViewTest(TestCase):
    def test_page_loads(self):
        response = self.client.get(reverse("homepage:homepage"))
        self.assertEqual(response.status_code, 200)

    def test_shows_company_name_when_company_exists(self):
        Company.objects.create(
            name="BeoBenere",
            email="beobenere.business@gmail.com",
            phone="+22672750096",
        )
        response = self.client.get(reverse("homepage:homepage"))
        self.assertContains(response, "BeoBenere")

    def test_does_not_crash_when_no_company_exists(self):
        """Company.objects.first() peut renvoyer None, la page ne doit pas planter pour autant."""
        response = self.client.get(reverse("homepage:homepage"))
        self.assertEqual(response.status_code, 200)