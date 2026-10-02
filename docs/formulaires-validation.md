# Formulaires et validation

## Les deux formulaires publics

`DevisForm` (app `devis`) et `ContactForm` (app `contact`) partagent la même logique de validation, dupliquée volontairement entre les deux plutôt que factorisée : seuls deux formulaires existent à ce jour, la duplication reste faible, et chacun a par ailleurs ses propres champs propres (`service`, `timeline` pour `DevisForm`). Une classe de base commune serait envisageable si un troisième formulaire similaire apparaissait.

## Règle 1 — email ou téléphone obligatoire

Ni `email` ni `phone` n'est individuellement obligatoire au niveau du modèle. La règle réelle — au moins l'un des deux — ne peut pas s'exprimer avec `required=True` sur un champ isolé, elle porte sur la combinaison de deux champs. Elle vit dans la méthode `clean()` du formulaire :

```python
def clean(self):
    cleaned_data = super().clean()
    email = cleaned_data.get("email")
    phone_attempted = bool(self.data.get("phone", "").strip())

    if not email and not cleaned_data.get("phone") and not phone_attempted:
        raise forms.ValidationError(
            "Merci de renseigner au moins un moyen de vous répondre : email ou téléphone."
        )
    return cleaned_data
```

**Le détail qui a demandé une correction** : si un visiteur tape un numéro invalide (trop court, par exemple), Django rejette ce champ pendant sa propre validation et le retire de `cleaned_data` — comme s'il n'avait jamais été rempli. Sans précaution, `clean()` déclenchait alors **le message générique en plus** du message spécifique au téléphone, les deux affichés en même temps pour une seule vraie erreur. La correction consiste à vérifier aussi `self.data` (la valeur brute envoyée, avant toute validation) : si le visiteur a bien tapé quelque chose dans le champ téléphone, le message générique ne se déclenche plus, seul le message précis sur le champ reste affiché.

## Règle 2 — le nom complet

Aucun champ `required` seul ne suffit à garantir un nom plausible. `clean_full_name()` rejette un nom de moins de deux caractères, et un nom composé uniquement de chiffres :

```python
def clean_full_name(self):
    full_name = self.cleaned_data["full_name"].strip()
    if len(full_name) < 2 or full_name.isdigit():
        raise forms.ValidationError("Merci d'indiquer un nom valide.")
    return full_name
```

## Pourquoi `novalidate` sur les deux formulaires

Par défaut, le navigateur bloque lui-même l'envoi d'un champ marqué `required` resté vide, avant même d'envoyer quoi que ce soit au serveur — une bulle native apparaît, avec un texte et un positionnement qui diffèrent d'un navigateur à l'autre (testé : Chrome et Firefox n'affichent ni le même texte ni la même position). Cette bulle échappe entièrement à notre contrôle, impossible à styliser, impossible à rendre cohérente avec le reste du site.

L'attribut `novalidate` sur la balise `<form>` désactive cette validation native. Tout passe désormais par Django, avec notre propre style d'erreur, cohérent quel que soit le navigateur du visiteur.

## Repositionnement après une erreur

Le header du site est fixe (`position: sticky`). Sans précaution, un rechargement de page après une erreur de validation ramène le visiteur tout en haut de la page, un contenu caché derrière le header. Résolu par :

- `action="#devis-form"` / `action="#contact-form"` sur la balise `<form>`, avec l'`id` correspondant sur ce même élément.
- `static/js/nav.js` mesure la hauteur réelle du header et recale la position exactement sous celui-ci, plutôt que de se fier au positionnement natif du navigateur (qui ignore l'existence d'un header fixe).
- Ce recalage se déclenche à plusieurs moments (`window.load`, `document.fonts.ready`, puis une dernière fois après deux images d'affichage via `requestAnimationFrame`), parce que les polices auto-hébergées peuvent encore être en train de se charger au moment où la page semble terminée, décalant légèrement la mise en page après le premier calcul.

## Le téléphone : validation à deux niveaux

**Niveau serveur**, toujours actif, y compris sans JavaScript : `PhoneNumberField` (du paquet `django-phonenumber-field`), avec `PHONENUMBER_DEFAULT_REGION = "BF"` dans `settings.py` — un numéro local sans indicatif est supposé burkinabè par défaut.

**Niveau visiteur**, un sélecteur de pays avec drapeau (`intl-tel-input`), appliqué à tout champ portant la classe `phone-input` (le formulaire devis, le formulaire contact, et les deux champs téléphone de l'admin `Company`). Un seul fichier, `static/js/phone-widget.js`, initialise ce sélecteur partout où cette classe apparaît, et réécrit la valeur du champ au format international complet juste avant l'envoi.

Ce sélecteur donne un vrai contrôle au visiteur : sans lui, un numéro malien tapé sans indicatif serait silencieusement interprété comme burkinabè par le réglage par défaut du serveur.
