# Architecture du projet

## Vue d'ensemble

Le site est un projet Django classique, structuré en plusieurs apps indépendantes, chacune responsable d'un seul domaine fonctionnel. Aucun framework JavaScript n'est utilisé côté frontend ; le peu de JavaScript nécessaire (menu mobile, sélecteur de pays téléphonique, repositionnement après erreur de formulaire) est écrit à la main, en fichiers séparés, chargés directement par les templates.

## Convention de nommage des apps

Chaque app porte le nom singulier de son modèle principal plutôt qu'un nom pluriel générique (`service`, pas `services`), conformément à la convention popularisée par *Two Scoops of Django*. Le nom de l'app ne correspond pas nécessairement au préfixe visible dans l'URL : l'app `service` est servie sous `/services/`, l'URL et le nom technique sont deux choses indépendantes.

## Les cinq apps

| App | Responsabilité |
|---|---|
| `homepage` | Page d'accueil (`/`), page À propos (`/a-propos/`) et page Mentions légales et confidentialité (`/mentions-legales/`) |
| `company` | Les informations de l'entreprise (modèle singleton) |
| `service` | Catalogue de services, par catégorie |
| `devis` | Formulaire public de demande de devis |
| `contact` | Formulaire public de contact + coordonnées affichées |

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

Le menu de l'en-tête suit l'ordre **Services, À propos, Contact**, suivi d'un bouton **« Demander un devis »** (`nav-cta`), l'action principale du site, présente ainsi sur toutes les pages. Il n'y a pas de lien « Accueil » dans le menu : le logo y mène déjà. Le pied de page, lui, garde un lien « Accueil », et sa dernière ligne, à côté du copyright, mène à la page Mentions légales et confidentialité. Les formulaires de devis et de contact y renvoient aussi, juste au-dessus du bouton d'envoi (lien direct vers la section `#donnees-personnelles`). Sur mobile, le menu s'ouvre avec le bouton hamburger ; `static/js/nav.js` le referme aussi au clic en dehors du menu et avec la touche Échap, et sa hauteur est limitée à la place disponible sous l'en-tête (défilement interne si besoin).

Un cas particulier : les icônes de catégorie de service sont des petits templates SVG, un par catégorie, inclus dynamiquement à partir du slug de la catégorie :

```django
{% include "service/icons/"|add:service.category.slug|add:".html" %}
```

## Organisation du CSS

Le CSS est séparé en deux niveaux :

- **Partagé**, dans `static/css/` : `variables.css` (les tokens de couleur et de typographie), `base.css` (reset, polices), `header.css`, `footer.css`, `forms.css` (règles communes aux formulaires devis et contact, pour éviter la duplication).
- **Propre à chaque app**, dans `apps/<app>/static/<app>/css/<app>.css`, chargé uniquement sur les pages qui en ont besoin, via le bloc `{% block extra_css %}`. Une page qui a une mise en page très différente des autres pages de son app peut avoir son propre fichier : c'est le cas de `homepage/css/about.css` pour la page À propos et de `homepage/css/legal.css` pour la page Mentions légales et confidentialité.

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

Déclaré dans `TEMPLATES` → `OPTIONS` → `context_processors` de `settings.py`. Les templates utilisent toujours site_company : aucune vue ne va chercher Company elle-même. Les vues homepage et contact_page le faisaient auparavant, ce qui doublait la requête et laissait la page Contact sans protection en cas de panne de la base.

Le `try/except DatabaseError` permet aux pages d'erreur (notamment la 500) de s'afficher même quand la base de données est inaccessible : sans lui, le processeur planterait pendant l'affichage de la page d'erreur elle-même.

## Dépendances JavaScript tierces

Une seule bibliothèque externe est utilisée, `intl-tel-input`, pour le sélecteur de pays sur les champs téléphone. Elle est **entièrement auto-hébergée** (`static/vendor/intl-tel-input/`), pas chargée depuis un CDN — un choix fait après avoir constaté que certains CDN publics (jsdelivr notamment) étaient bloqués sur le réseau utilisé pour le développement. Voir `docs/decisions/` pour le détail de cette décision.

## Commandes de gestion

Certaines opérations ne passent pas par une page du site mais par des commandes `manage.py`, rangées dans `apps/<app>/management/commands/` :

| Commande | App | Rôle |
|---|---|---|
| `import_company` | `company` | importe les informations de l'entreprise depuis le classeur Excel (voir `gestion-contenu.md`) |
| `import_services` | `service` | importe le catalogue de services depuis le classeur Excel (voir `gestion-contenu.md`) |
| `send_devis_notifications` | `devis` | envoie les alertes e-mail des demandes de devis en attente ; lancée chaque minute par `cron` (voir `notifications.md`) |
| `send_contact_notifications` | `contact` | envoie les alertes e-mail des messages de contact en attente ; lancée par la même ligne `cron` (voir `notifications.md`) |

## Journalisation et signalement des erreurs

La configuration `LOGGING` de `settings.py` repose sur trois gestionnaires, tous de niveau `ERROR` :

| Gestionnaire | Destination | Actif |
|---|---|---|
| `file` | `logs/django.log`, avec date, gravité et logger d'origine | toujours |
| `console` | le terminal | toujours |
| `mail_admins` | e-mail aux adresses de `ADMINS` | en production seulement (`DEBUG=False`) |

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

| Fonctionnalité | Devis | Messages de contact |
|---|---|---|
| Colonnes | nom, contact, service, source, statut, reçu le, notifié | nom, contact, début du message, lu, reçu le, notifié |
| Modifiable directement dans la liste | statut (`list_editable`) | lu (`list_editable`) |
| Filtres | statut, source, délai, service | lu |
| Recherche | nom, e-mail, téléphone, message | nom, e-mail, téléphone, message |
| Actions groupées | — | « Marquer comme lu », « Marquer comme non lu » |

Points communs aux deux listes :

- **Colonnes calculées** par des méthodes de l'admin, pour tenir sur un écran étroit : `contact` réunit l'e-mail et le téléphone, `received` affiche la date au format court `jj/mm/aa hh:mm` (triable grâce à `ordering="created_at"`), `notified` affiche une icône ✓/✗ à la place de la date complète d'envoi de l'alerte.
- **Navigation par date** (`date_hierarchy`) et **tri du plus récent au plus ancien**.
- **`notified_at` en lecture seule** dans les fiches (et `created_at`, sauf pour une saisie manuelle de devis, voir ci-dessous).
- Les **libellés français** viennent des `verbose_name` des champs (en minuscules, Django ajoute la majuscule) et des `Meta` des modèles. Les formulaires publics définissent leurs propres libellés et n'en dépendent pas.

**Protection de ce que le client a écrit.** Une demande est une trace : si le message ou le téléphone pouvaient être modifiés, même par erreur, on perdrait ce que le client a réellement demandé.

| | Demande de devis venue du site (`source = site`) | Demande de devis saisie à la main | Message de contact |
|---|---|---|---|
| Texte du client (nom, e-mail, téléphone, service, délai, message), source, reçu le | lecture seule | modifiable | lecture seule (pas de service, délai ni source) |
| Champ de suivi | statut, modifiable | statut, modifiable | lu, modifiable |
| Ajout depuis l'admin | — | bouton « Ajouter devis » | **impossible** (`has_add_permission` renvoie `False`) |
| Suppression | possible | possible | possible |

La suppression reste possible partout : la page de confidentialité promet de supprimer les demandes 12 mois après le dernier échange, et un client peut demander l'effacement de ses données.

**Saisie manuelle d'une demande de devis** (`apps/devis/admin.py`) — pour un client qui a appelé, écrit sur WhatsApp ou est passé en personne, afin de suivre toutes les demandes au même endroit :

- `get_readonly_fields()` ajoute les champs de `CLIENT_FIELDS` aux champs en lecture seule **seulement** si la demande a `source = "site"`. Sur la page « Ajouter » (`obj` vaut `None`) et pour une saisie manuelle, tout reste modifiable, y compris « Reçu le », pour indiquer la vraie date de réception.
- `get_form()` retire le choix « Site web » de la source et présélectionne « Téléphone » : une saisie manuelle ne peut pas se faire passer pour une demande du site, ce qui la verrouillerait. La source d'une demande du site est elle-même en lecture seule.
- `save_model()` remplit `notified_at` lors d'un ajout : la commande `send_devis_notifications` ne cherche que les demandes dont ce champ est vide, et n'envoie donc pas d'alerte pour une demande que l'on vient de saisir soi-même.
- La fiche est organisée en trois sections (`fieldsets`) : Client, Demande, Suivi, avec les champs courts côte à côte.

Un client qui appelle pour un besoin donne lieu à une demande de devis, jamais à un message de contact : c'est pourquoi l'ajout n'existe que d'un côté.

Les méthodes `contact`, `received` et `notified` sont dupliquées entre les deux admins, comme le code des notifications : elles seront regroupées si un troisième cas apparaît. Elles sont testées directement (`tests/test_admin.py` de chaque app), sans passer par les pages de l'admin.
