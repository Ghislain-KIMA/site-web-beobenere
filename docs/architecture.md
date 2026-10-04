# Architecture du projet

## Vue d'ensemble

Le site est un projet Django classique, structuré en plusieurs apps indépendantes, chacune responsable d'un seul domaine fonctionnel. Aucun framework JavaScript n'est utilisé côté frontend ; le peu de JavaScript nécessaire (menu mobile, sélecteur de pays téléphonique, repositionnement après erreur de formulaire) est écrit à la main, en fichiers séparés, chargés directement par les templates.

## Convention de nommage des apps

Chaque app porte le nom singulier de son modèle principal plutôt qu'un nom pluriel générique (`service`, pas `services`), conformément à la convention popularisée par *Two Scoops of Django*. Le nom de l'app ne correspond pas nécessairement au préfixe visible dans l'URL : l'app `service` est servie sous `/services/`, l'URL et le nom technique sont deux choses indépendantes.

## Les cinq apps

| App | Responsabilité |
|---|---|
| `homepage` | Page d'accueil (`/`) |
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
    return {"site_company": Company.objects.first()}
```

Déclaré dans `TEMPLATES` → `OPTIONS` → `context_processors` de `settings.py`. La variable s'appelle `site_company`, volontairement différente de la variable locale `company` que certaines vues (comme `homepage`) transmettent elles-mêmes, pour éviter toute ambiguïté entre les deux.

## Dépendances JavaScript tierces

Une seule bibliothèque externe est utilisée, `intl-tel-input`, pour le sélecteur de pays sur les champs téléphone. Elle est **entièrement auto-hébergée** (`static/vendor/intl-tel-input/`), pas chargée depuis un CDN — un choix fait après avoir constaté que certains CDN publics (jsdelivr notamment) étaient bloqués sur le réseau utilisé pour le développement. Voir `docs/decisions/` pour le détail de cette décision.
