# Tests automatisés

## État actuel

57 tests, répartis sur les cinq apps, pour une couverture de 98% du code applicatif. Les seules portions non couvertes sont `asgi.py`/`wsgi.py` (jamais utilisés en développement), `manage.py` (sa ligne de lancement), et une méthode isolée de `company/admin.py`.

## Commandes

```bash
# Lancer les tests d'une ou plusieurs apps (manage.py test seul ne trouve rien,
# puisque apps/ n'est volontairement pas un vrai package Python)
python manage.py test company devis contact service homepage

# Avec mesure de couverture
coverage run --source='.' manage.py test company devis contact service homepage
coverage report -m
```

## Organisation

Chaque app a un dossier `tests/` (pas un simple fichier `tests.py`), avec jusqu'à trois fichiers selon ce qui s'applique :

- `test_models.py` — contraintes, valeurs par défaut, comportement des suppressions en cascade
- `test_forms.py` — règles de validation (email/téléphone, nom complet)
- `test_views.py` — comportement des pages (affichage, soumission, redirection)

`homepage` n'a qu'un seul fichier `tests.py`, vu sa taille réduite (une seule vue, pas de formulaire).

## Ce que les tests protègent réellement

Au-delà du chiffre de couverture, chaque test vérifie une règle explicitement décidée pendant la construction du projet, pour qu'elle ne régresse jamais silencieusement :

- La règle « email ou téléphone obligatoire », et son cas limite (un numéro invalide ne doit déclencher qu'un seul message d'erreur, pas deux).
- L'ordre exact d'entrelacement des services par catégorie sur la page `/services/` (round-robin), la logique la plus particulière du projet.
- `on_delete=PROTECT` entre `Category` et `Service` : une catégorie encore utilisée ne peut jamais être supprimée.
- `on_delete=SET_NULL` entre `Devis` et `Service` : supprimer un service ne doit jamais effacer l'historique des demandes de devis qui le mentionnaient.
- Qu'un envoi de formulaire invalide ne laisse jamais de trace en base (aucune ligne créée).
- Que la page d'accueil ne plante pas si aucune entreprise n'existe en base, un cas qui ne devrait jamais se produire en production mais qui s'est produit pendant le développement (base de test vidée par erreur).

## Deux incohérences de modèle découvertes grâce aux tests

En relançant les tests existants après une modification du champ `phone` de `Company` (passage à `PhoneNumberField`), deux problèmes réels sont apparus, indépendamment de tout bug visible sur le site :

1. `phone` n'avait ni `blank=True` ni `null=True`, contrairement à `email` qui avait les deux — un test créant une entreprise sans numéro provoquait une collision de contrainte d'unicité sur deux chaînes vides.
2. Décision pour corriger : harmoniser les deux champs sur « obligatoire », plutôt que l'inverse, puisque c'est le reflet de l'usage réel (les deux sont toujours renseignés).

C'est l'exemple concret de ce que des tests automatisés apportent au-delà de la détection de bugs : ils révèlent aussi des incohérences de conception qui seraient restées invisibles tant que personne ne les aurait testées directement.
