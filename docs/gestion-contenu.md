# Gestion du contenu

## Le principe

Tout le contenu que l'administrateur (Ghislain) remplit lui-même — les informations de l'entreprise, les catégories, les services — a une seule source de vérité : un classeur Excel, `data/services-beobenere.xlsx`. L'admin Django reste utilisable pour des ajustements ponctuels, mais ce classeur permet de reconstruire l'intégralité de ce contenu en une seule commande, sans jamais avoir à ressaisir quoi que ce soit à la main.

Ce que ce mécanisme **ne couvre pas** : les demandes de devis et les messages de contact. Ce sont des données soumises par les visiteurs, jamais par l'administrateur, et aucune commande d'import ne les concerne.

## Structure du classeur

Trois feuilles utiles, plus une feuille `Légende` de documentation interne :

- **`company`** — une seule ligne de données, les en-têtes correspondant exactement aux noms des champs du modèle `Company`.
- **`Categories`** — une ligne par catégorie, colonnes `name` et `slug`.
- **`Services`** — une ligne par service, colonnes `name`, `slug`, `brief_description`, `description`, `image_url`, `is_active`, `category_slug`.

La colonne `category_slug` de la feuille `Services` n'existe dans aucune base de données : c'est un pont de lecture, utilisé uniquement au moment de l'import pour retrouver la bonne `Category` et l'assigner au vrai champ `category`, une clé étrangère. Elle est protégée par une liste déroulante dans le classeur lui-même (validation de données Excel, sourcée depuis la colonne slug de la feuille `Categories`), pour empêcher toute faute de frappe.

## Les deux commandes d'import

```bash
python manage.py import_company data/services-beobenere.xlsx
python manage.py import_services data/services-beobenere.xlsx
```

Toutes deux sont **idempotentes** : les relancer plusieurs fois de suite sur le même fichier ne crée jamais de doublon, elles mettent à jour l'existant (recherche par `slug`, ou ligne unique pour `Company`) plutôt que de réinsérer.

**`import_company`** lit la feuille `company`, construit un dictionnaire à partir des en-têtes, et met à jour l'unique ligne `Company` (ou la crée si elle n'existe pas encore).

**`import_services`** traite `Categories` puis `Services`, dans cet ordre, puisque les services ont besoin que leurs catégories existent déjà.

## Validation avant enregistrement

Les deux commandes appellent `full_clean()` avant tout `.save()`, exactement la validation qu'un formulaire ou l'admin déclencherait normalement. Sans cet appel, un `.save()` direct écrit en base sans vérifier quoi que ce soit — un numéro de téléphone mal formé, par exemple, s'enregistrerait silencieusement.

Les deux commandes réagissent différemment à une ligne invalide, pour une raison liée à la nature de chaque modèle :

- **`import_company`** interrompt tout l'import si la donnée est invalide. `Company` n'a qu'une seule ligne : il n'y a pas de sens à importer partiellement une entreprise.
- **`import_services`** ignore uniquement la ligne fautive, avec un avertissement affiché, et continue les suivantes. Plusieurs catégories et services existent indépendamment les uns des autres ; bloquer tout l'import pour une seule ligne en faute serait disproportionné.

## Un bug réel rencontré et corrigé

La liste déroulante ajoutée sur `category_slug` a, à un moment, élargi la zone que la feuille Excel considère comme « utilisée » jusqu'à 24 colonnes, alors que seules 7 contiennent de vraies données. `openpyxl` (la bibliothèque Python qui lit le fichier) renvoyait alors des lignes de 24 valeurs là où le code attendait exactement 7, provoquant une erreur de correspondance. Corrigé en limitant explicitement la lecture aux colonnes réellement utiles (`max_col=7` pour `Services`, `max_col=2` pour `Categories`), peu importe ce que la mise en forme du fichier laisse penser.
