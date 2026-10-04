# PostgreSQL plutôt que SQLite

**Date** : octobre 2026
**Statut** : actif

## Contexte

Django propose SQLite comme base de données par défaut, sans aucune configuration nécessaire, suffisant pour la grande majorité des petits projets en développement.

## Décision

PostgreSQL a été choisi dès le départ, avec sa propre configuration (`beobenere_db`, utilisateur dédié, identifiants dans `.env` via `python-dotenv`), plutôt que de rester sur SQLite.

## Raisonnement

Même si SQLite aurait amplement suffi aux besoins actuels du site (faible volume de données, un seul visiteur simultané en développement), le choix de PostgreSQL dès le début évite une migration de base de données plus tard, au moment du déploiement en production — un changement de moteur de base de données après coup implique de revalider tous les types de champs, les contraintes, et le comportement de certaines requêtes, un risque évitable en partant directement sur le moteur qui sera réellement utilisé en production.

PostgreSQL gère aussi correctement, nativement, les contraintes d'unicité combinées à des valeurs nulles — un détail qui s'est avéré pertinent pendant le projet, lors du débogage du champ `Company.phone` (voir `docs/tests.md`).

## Conséquence

Le projet nécessite PostgreSQL installé et démarré localement pour tourner, y compris pour exécuter les tests (`python manage.py test` échoue sinon avec une erreur de connexion, pas une erreur liée au code).
