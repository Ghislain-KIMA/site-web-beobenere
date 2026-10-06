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

    def test_about_page_loads(self):
        response = self.client.get(reverse("homepage:about"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "homepage/about.html")

    def test_about_page_shows_company_practical_info(self):
        Company.objects.create(
            name="BeoBenere",
            email="contact@example.com",
            phone="+22670000000",
            service_area="Ouagadougou et environs",
            business_hours="Lundi – Vendredi, 8h – 18h",
        )

        response = self.client.get(reverse("homepage:about"))

        self.assertContains(response, "Ouagadougou et environs")
        self.assertContains(response, "Lundi – Vendredi, 8h – 18h")

    def test_about_page_hides_practical_section_without_company(self):
        response = self.client.get(reverse("homepage:about"))
        self.assertNotContains(response, "Où et quand")