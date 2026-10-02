# Modèles de données

## Vue d'ensemble

Le projet compte cinq modèles, répartis sur quatre apps (`homepage` n'a pas de modèle propre). Deux d'entre eux, `Category` et `Service`, vivent dans la même app, `service`.

## `Company` (app `company`)

Modèle **singleton** : une seule ligne existe en base, représentant BeoBenere elle-même. Rien n'empêche techniquement d'en créer une seconde, mais tout le code (processeur de contexte, vues) suppose qu'une seule existe et lit systématiquement la première trouvée.

| Champ | Type | Contrainte |
|---|---|---|
| `name` | `CharField` | obligatoire |
| `slogan` | `CharField` | optionnel |
| `description` | `TextField` | optionnel |
| `sector` | `CharField` | optionnel |
| `logo_url` | `CharField` | optionnel — chemin relatif vers `static/`, pas une vraie URL |
| `email` | `EmailField` | obligatoire, unique |
| `phone` | `PhoneNumberField` | obligatoire, unique |
| `address` | `CharField` | optionnel — laissé vide, pas de bureau fixe |
| `whatsapp` | `PhoneNumberField` | optionnel |
| `facebook_url` | `URLField` | optionnel |
| `business_hours` | `CharField` | optionnel |
| `service_area` | `CharField` | optionnel |

`email` et `phone` ont tous deux été rendus obligatoires après un ajustement en cours de route : `email` était initialement optionnel (l'entreprise n'avait pas encore d'adresse au moment de la conception), `phone` était obligatoire dès le départ. Les deux ont été harmonisés sur « obligatoire », cohérent avec le fait que les deux sont toujours renseignés en pratique.

## `Category` et `Service` (app `service`)

```
Category 1 ──── * Service
```

**`Category`** : `name`, `slug` (unique), `image_url` (présent mais non utilisé par aucun template actuellement).

**`Service`** : `name`, `slug` (unique), `brief_description` (obligatoire, résumé court affiché sur la liste), `description` (texte complet), `image_url` (non utilisé), `is_active` (booléen, `True` par défaut — permet de masquer un service sans le supprimer), `created_at`, `updated_at`, `category` (clé étrangère vers `Category`).

La relation utilise `on_delete=PROTECT` : impossible de supprimer une catégorie tant qu'au moins un service lui est rattaché. Voir `docs/decisions/` pour le raisonnement complet derrière ce choix plutôt que `CASCADE`.

## `Devis` (app `devis`)

Représente une demande de devis soumise par un visiteur, sans compte requis.

| Champ | Type | Contrainte |
|---|---|---|
| `full_name` | `CharField` | obligatoire |
| `email` | `EmailField` | optionnel |
| `phone` | `PhoneNumberField` | optionnel |
| `service` | FK vers `Service` | optionnel, `on_delete=SET_NULL` |
| `message` | `TextField` | obligatoire |
| `timeline` | `CharField` + choix | optionnel (`urgent`, `within_month`, `not_urgent`) |
| `status` | `CharField` + choix | `new` par défaut (`new`, `contacted`, `converted`, `closed`) |
| `created_at` | `DateTimeField` | automatique |

`email` et `phone` sont tous deux optionnels **au niveau du modèle**, mais le formulaire impose qu'au moins l'un des deux soit rempli — une règle qui ne peut pas s'exprimer avec de simples contraintes de champ, elle vit dans `DevisForm.clean()` (voir `formulaires-validation.md`).

La relation vers `Service` utilise `on_delete=SET_NULL` plutôt que `PROTECT` ou `CASCADE` : si un service est retiré du catalogue, les demandes de devis qui le mentionnaient restent en base, avec ce champ simplement vidé. L'historique des demandes ne doit jamais disparaître à cause d'un changement de catalogue.

`status` n'est jamais exposé dans le formulaire public — un visiteur ne peut pas choisir son propre statut. Seule l'admin permet de le faire évoluer.

## `ContactMessage` (app `contact`)

Représente un message libre envoyé depuis la page Contact, distinct d'une demande de devis.

| Champ | Type | Contrainte |
|---|---|---|
| `full_name` | `CharField` | obligatoire |
| `email` | `EmailField` | optionnel |
| `phone` | `PhoneNumberField` | optionnel |
| `message` | `TextField` | obligatoire |
| `is_read` | `BooleanField` | `False` par défaut |
| `created_at` | `DateTimeField` | automatique |

Même règle « email ou téléphone obligatoire » que `Devis`, appliquée dans `ContactForm.clean()`. Pas de relation vers un autre modèle — ce modèle est entièrement autonome.

`Devis` et `ContactMessage` existent comme deux modèles séparés plutôt qu'un seul formulaire générique, parce qu'ils ne servent pas le même objectif : une demande de devis porte sur un service précis et suit un cycle de traitement commercial (`status`), un message de contact est une simple prise de contact, sans ce suivi.
