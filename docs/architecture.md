# Architecture du projet

## Vue d'ensemble

Le site est un projet Django classique, structuré en plusieurs apps indépendantes, chacune responsable d'un seul domaine fonctionnel. Aucun framework JavaScript n'est utilisé côté frontend ; le peu de JavaScript nécessaire (menu mobile, sélecteur de pays téléphonique, repositionnement après erreur de formulaire) est écrit à la main, en fichiers séparés, chargés directement par les templates.

## Convention de nommage des apps

Chaque app porte le nom singulier de son modèle principal plutôt qu'un nom pluriel générique (`service`, pas `services`), conformément à la convention popularisée par *Two Scoops of Django*. Le nom de l'app ne correspond pas nécessairement au préfixe visible dans l'URL : l'app `service` est servie sous `/services/`, l'URL et le nom technique sont deux choses indépendantes.

## Les cinq apps

| App          | Responsabilité                                                                |
| ------------ | ------------------------------------------------------------------------------ |
| `homepage` | Page d'accueil (`/`) et page À propos (`/a-propos/`)Page d'accueil (`/` |
| `company`  | Les informations de l'entreprise (modèle singleton)                           |
| `service`  | Catalogue de services, par catégorie                                          |
| `devis`    | Formulaire public de demande de devis                                          |
| `contact`  | Formulaire public de contact + coordonnées affichées                         |

Chaque app suit la même structure interne : `models.py`, `admin.py`, `forms.py` (quand elle a un formulaire), `views.py`, `urls.py`, un dossier `templates/<app>/`, un dossier `static/<app>/css/`, et un dossier `tests/` contenant `test_models.py`, `test_forms.py`, `test_views.py` selon ce qui s'applique.

## Le dossier `apps/` et le choix technique derrière

Toutes les apps vivent physiquement dans un dossier `apps/`, plutôt qu'à la racine du projet. Ce dossier **n'est volontairement pas** un vrai package Python : il ne contient aucun fichier `__init__.py`. À la place, `beobenere/settings.py` ajoute ce dossier directement au chemin de recherche de Python :

```python
import sys
sys.path.insert(0, str(BASE_DIR / 'apps'))
```

Conséquence directe de ce choix : partout dans le code, les imports restent courts et identiques à ce qu'ils seraient sans ce dossier (`from service.models import Service`, pas `from apps.service.models import Service`). C'est un compromis déjà utilisé par plusieurs projets Django pour réduire l'encombrement à la racine du dépôt sans alourdir chaque import d'un niveau supplémentaire.

**Une conséquence pratique à connaître** : `manage.py test` sans argument ne trouve aucun test, puisque Django ne sait pas explorer un dossier qui n'est pas un vrai package. Il faut toujours lister les apps explicitement :

```bash
python manage.py test company devis contact service homepage
```

## Organisation des templates

Chaque app possède ses propres templates, dans `apps/<app>/templates/<app>/`, le doublement du nom de dossier étant la convention Django standard pour éviter les collisions de noms entre apps. Un seul template racine, `templates/base.html`, définit la structure commune (en-tête, pied de page, blocs `extra_css` et `extra_js`) et chaque template d'app en hérite avec `{% extends "base.html" %}`.

Un cas particulier : les icônes de catégorie de service sont des petits templates SVG, un par catégorie, inclus dynamiquement à partir du slug de la catégorie :

```django
{% include "service/icons/"|add:service.category.slug|add:".html" %}
```

## Organisation du CSS

Le CSS est séparé en deux niveaux :

- **Partagé**, dans `static/css/` : `variables.css` (les tokens de couleur et de typographie), `base.css` (reset, polices), `header.css`, `footer.css`, `forms.css` (règles communes aux formulaires devis et contact, pour éviter la duplication).
- **Propre à chaque app**, dans `apps/<app>/static/<app>/css/<app>.css`, chargé uniquement sur les pages qui en ont besoin, via le bloc `{% block extra_css %}`.

## Processeur de contexte

Les coordonnées de l'entreprise (téléphone, email, logo…) sont nécessaires sur presque toutes les pages (footer, page Contact, header). Plutôt que de les transmettre manuellement depuis chaque vue, un processeur de contexte les injecte automatiquement dans tous les templates :

```python
# company/context_processors.py
def company(request):
    try:
        site_company = Company.objects.first()
    except DatabaseError:
        site_company = None

    return {"site_company": site_company}
```

Déclaré dans `TEMPLATES` → `OPTIONS` → `context_processors` de `settings.py`. La variable s'appelle `site_company`, volontairement différente de la variable locale `company` que certaines vues (comme `homepage`) transmettent elles-mêmes, pour éviter toute ambiguïté entre les deux.

Le `try/except DatabaseError` permet aux pages d'erreur (notamment la 500) de s'afficher même quand la base de données est inaccessible : sans lui, le processeur planterait pendant l'affichage de la page d'erreur elle-même. La vue `homepage` applique la même protection.

## Dépendances JavaScript tierces

Une seule bibliothèque externe est utilisée, `intl-tel-input`, pour le sélecteur de pays sur les champs téléphone. Elle est **entièrement auto-hébergée** (`static/vendor/intl-tel-input/`), pas chargée depuis un CDN — un choix fait après avoir constaté que certains CDN publics (jsdelivr notamment) étaient bloqués sur le réseau utilisé pour le développement. Voir `docs/decisions/` pour le détail de cette décision.

## Commandes de gestion

Certaines opérations ne passent pas par une page du site mais par des commandes `manage.py`, rangées dans `apps/<app>/management/commands/` :

| Commande                       | App         | Rôle                                                                                                                         |
| ------------------------------ | ----------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `import_company`             | `company` | importe les informations de l'entreprise depuis le classeur Excel (voir`gestion-contenu.md`)                                |
| `import_services`            | `service` | importe le catalogue de services depuis le classeur Excel (voir`gestion-contenu.md`)                                        |
| `send_devis_notifications`   | `devis`   | envoie les alertes e-mail des demandes de devis en attente ; lancée chaque minute par`cron` (voir `notifications.md`)    |
| `send_contact_notifications` | `contact` | envoie les alertes e-mail des messages de contact en attente ; lancée par la même ligne`cron` (voir `notifications.md`) |

## Journalisation et signalement des erreurs

La configuration `LOGGING` de `settings.py` repose sur trois gestionnaires, tous de niveau `ERROR` :

| Gestionnaire    | Destination                                                  | Actif                                     |
| --------------- | ------------------------------------------------------------ | ----------------------------------------- |
| `file`        | `logs/django.log`, avec date, gravité et logger d'origine | toujours                                  |
| `console`     | le terminal                                                  | toujours                                  |
| `mail_admins` | e-mail aux adresses de`ADMINS`                             | en production seulement (`DEBUG=False`) |

- Le **logger racine** écrit dans `file` et `console` : toute erreur journalisée par le code des apps (par exemple `devis.notifications` ou `contact.notifications`) est donc enregistrée, pas seulement celles de Django.
- Le **logger `django`** écrit en plus vers `mail_admins`, pour être prévenu des erreurs des pages (erreurs 500). Il a `propagate: False`, pour ne pas écrire deux fois chaque erreur dans le fichier.
- `mail_admins` n'est volontairement **pas** branché sur le logger racine : un échec d'envoi des notifications déclencherait alors un e-mail d'erreur qui échouerait lui aussi.

Les rapports d'erreur envoyés par e-mail masquent automatiquement les réglages sensibles (`SECRET_KEY`, mots de passe). Les vues des formulaires devis et contact portent en plus le décorateur `@sensitive_post_parameters()`, qui masque les données saisies par les visiteurs.

Variables d'environnement concernées : `ADMINS` (adresses séparées par des virgules ; sans elle, personne n'est prévenu), et `SERVER_EMAIL`, qui reprend `DEFAULT_FROM_EMAIL`.

En production, `logs/django.log` et `logs/cron.log` se trouvent sur le serveur, pas sur la machine de développement.

## Administration

L'admin de Django sert d'espace de gestion interne : consulter et traiter les demandes de devis et les messages de contact. Seul son **fonctionnement** est personnalisé ; son apparence reste celle de Django, à l'exception de l'en-tête.

**En-tête** (dans `beobenere/urls.py`) :

```python
admin.site.site_header = "BeoBenere — Gestion"
admin.site.site_title = "BeoBenere"
admin.site.index_title = "Tableau de bord"
```

**Listes des devis et des messages de contact** (`apps/devis/admin.py`, `apps/contact/admin.py`) :

| Fonctionnalité                      | Devis                                             | Messages de contact                                     |
| ------------------------------------ | ------------------------------------------------- | ------------------------------------------------------- |
| Colonnes                             | nom, contact, service, statut, reçu le, notifié | nom, contact, début du message, lu, reçu le, notifié |
| Modifiable directement dans la liste | statut (`list_editable`)                        | lu (`list_editable`)                                  |
| Filtres                              | statut, délai, service                           | lu                                                      |
| Recherche                            | nom, e-mail, téléphone, message                 | nom, e-mail, téléphone, message                       |
| Actions groupées                    | —                                                | « Marquer comme lu », « Marquer comme non lu »      |

Points communs aux deux listes :

- **Colonnes calculées** par des méthodes de l'admin, pour tenir sur un écran étroit : `contact` réunit l'e-mail et le téléphone, `received` affiche la date au format court `jj/mm/aa hh:mm` (triable grâce à `ordering="created_at"`), `notified` affiche une icône ✓/✗ à la place de la date complète d'envoi de l'alerte.
- **Navigation par date** (`date_hierarchy`) et **tri du plus récent au plus ancien**.
- **`created_at` et `notified_at` en lecture seule** dans les fiches.
- Les **libellés français** viennent des `verbose_name` des champs (en minuscules, Django ajoute la majuscule) et des `Meta` des modèles. Les formulaires publics définissent leurs propres libellés et n'en dépendent pas.

Les méthodes `contact`, `received` et `notified` sont dupliquées entre les deux admins, comme le code des notifications : elles seront regroupées si un troisième cas apparaît. Elles sont testées directement (`tests/test_admin.py` de chaque app), sans passer par les pages de l'admin.
