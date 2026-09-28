from django.db.utils import IntegrityError
from django.test import TestCase

from company.models import Company


class CompanyModelTest(TestCase):
    """Tests pour le modèle Company."""

    def setUp(self):
        """Exécuté avant chaque test : crée une instance de base réutilisable."""
        self.company = Company.objects.create(
            name="BeoBenere",
            slogan="Votre informatique, gérée sans jargon",
            email="contact@beobenere.bf",
            phone="+22670000000",
        )

    def test_str_returns_company_name(self):
        """__str__ doit renvoyer le nom de l'entreprise."""
        self.assertEqual(str(self.company), "BeoBenere")

    def test_company_created_successfully(self):
        """Une entreprise créée doit être récupérable en base."""
        self.assertEqual(Company.objects.count(), 1)
        self.assertEqual(self.company.name, "BeoBenere")

    def test_optional_fields_can_be_blank(self):
        """Les champs facultatifs (slogan, description, sector...) doivent
        accepter une valeur vide sans lever d'erreur."""
        company = Company.objects.create(name="Entreprise Minimale")
        self.assertEqual(company.slogan, "")
        self.assertEqual(company.description, "")
        self.assertEqual(company.sector, "")
        self.assertEqual(company.address, "")

    def test_name_is_required(self):
        """name ne doit pas être vide — c'est le seul champ obligatoire (not null)."""
        with self.assertRaises(IntegrityError):
            # full_clean() n'est pas appelé automatiquement par .create(),
            # donc on force une violation de contrainte NOT NULL directement en base.
            Company.objects.create(name=None)

    def test_email_must_be_unique(self):
        """Deux entreprises ne doivent pas pouvoir partager le même email."""
        with self.assertRaises(IntegrityError):
            Company.objects.create(
                name="Autre Entreprise",
                email="contact@beobenere.bf",  # même email que self.company
            )

    def test_phone_must_be_unique(self):
        """Deux entreprises ne doivent pas pouvoir partager le même téléphone."""
        with self.assertRaises(IntegrityError):
            Company.objects.create(
                name="Autre Entreprise",
                phone="+22670000000",  # même téléphone que self.company
            )

    def test_email_and_phone_can_both_be_null(self):
        """Plusieurs entreprises sans email/téléphone doivent pouvoir coexister
        (null=True doit éviter un faux conflit d'unicité entre deux valeurs vides)."""
        Company.objects.create(name="Entreprise A")
        Company.objects.create(name="Entreprise B")
        self.assertEqual(Company.objects.filter(email__isnull=True).count(), 2)

    def test_created_at_is_set_automatically(self):
        """created_at doit être rempli automatiquement à la création."""
        self.assertIsNotNone(self.company.created_at)

    def test_db_table_name(self):
        """La table doit bien s'appeler 'company', sans préfixe d'app."""
        self.assertEqual(Company._meta.db_table, "company")
