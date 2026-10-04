# PROTECT plutôt que CASCADE entre Category et Service

**Date** : septembre 2026
**Statut** : actif

## Contexte

`Service.category` est une clé étrangère obligatoire vers `Category`. Django demande de choisir un comportement pour `on_delete` : que doit-il se passer si quelqu'un supprime une catégorie encore utilisée par des services ?

## Options envisagées

- **`CASCADE`** — supprimer une catégorie supprimerait automatiquement tous les services qui lui sont rattachés.
- **`PROTECT`** — Django refuse purement et simplement la suppression tant qu'au moins un service existe dans cette catégorie.
- **`SET_NULL`** — la catégorie du service deviendrait vide, mais n'a pas de sens ici : `category` est un champ obligatoire du modèle `Service`, un service sans catégorie n'est pas censé exister.

## Décision

`PROTECT`.

## Raisonnement

`CASCADE` est dangereux dans ce contexte précis : une suppression de catégorie faite par erreur, ou sans réaliser qu'elle contient encore des services actifs, effacerait silencieusement tout le catalogue associé, sans avertissement ni confirmation distincte. `PROTECT` force à traiter explicitement les services existants (les réassigner à une autre catégorie, ou les supprimer un par un en toute connaissance de cause) avant de pouvoir supprimer la catégorie elle-même.

## Conséquence

Vérifié par un test automatisé (`test_category_cannot_be_deleted_while_services_exist`, dans `apps/service/tests/test_models.py`), qui s'assure que ce comportement ne régresse jamais silencieusement vers `CASCADE`.
