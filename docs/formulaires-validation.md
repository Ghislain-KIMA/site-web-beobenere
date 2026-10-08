# Formulaires et validation

## Les deux formulaires publics

`DevisForm` (app `devis`) et `ContactForm` (app `contact`) partagent la même logique de validation, dupliquée volontairement entre les deux plutôt que factorisée : seuls deux formulaires existent à ce jour, la duplication reste faible, et chacun a par ailleurs ses propres champs propres (`service`, `timeline` pour `DevisForm`). Une classe de base commune serait envisageable si un troisième formulaire similaire apparaissait.

## Règle 1 — email ou téléphone obligatoire

Ni `email` ni `phone` n'est individuellement obligatoire au niveau du modèle. La règle réelle — au moins l'un des deux — ne peut pas s'exprimer avec `required=True` sur un champ isolé, elle porte sur la combinaison de deux champs. Elle vit dans la méthode `clean()` du formulaire :

```python
def clean(self):
    cleaned_data = super().clean()
    email = cleaned_data.get("email")
    phone = cleaned_data.get("phone")

    email_attempted = bool(self.data.get("email", "").strip())
    phone_attempted = bool(self.data.get("phone", "").strip())

    if not email and not phone and not email_attempted and not phone_attempted:
        raise forms.ValidationError(
            "Merci de renseigner au moins un moyen de vous répondre : email ou téléphone."
        )
    return cleaned_data
```

**Le détail qui a demandé une correction** : si un visiteur tape un numéro invalide (trop court, par exemple), Django rejette ce champ pendant sa propre validation et le retire de `cleaned_data` — comme s'il n'avait jamais été rempli. Sans précaution, `clean()` déclenchait alors **le message générique en plus** du message spécifique au téléphone, les deux affichés en même temps pour une seule vraie erreur. La correction consiste à vérifier aussi self.data (la valeur brute envoyée, avant toute validation) : si le visiteur a bien tapé quelque chose dans le champ téléphone ou e-mail, le message générique ne se déclenche plus, seul le message précis sur le champ reste affiché. Le cas de l’e-mail a été oublié lors de la première correction et ajouté ensuite (un e-mail comme d produisait les deux messages) ; les tests test_invalid_phone_does_not_trigger_duplicate_error et test_invalid_email_does_not_trigger_duplicate_error verrouillent les deux cas.

## Règle 2 — le nom complet

Aucun champ `required` seul ne suffit à garantir un nom plausible. `clean_full_name()` rejette un nom de moins de deux caractères, et un nom composé uniquement de chiffres :

```python
def clean_full_name(self):
    # Ramène tous les blancs (retours à la ligne, tabulations, espaces multiples) à un seul espace
    full_name = " ".join(self.cleaned_data["full_name"].split())
    if len(full_name) < 2 or full_name.isdigit():
        raise forms.ValidationError("Merci d'indiquer un nom valide.")
    return full_name
```

Les blancs sont normalisés et pas seulement retirés aux deux bouts : le nom est repris dans le sujet de l'e-mail de notification, et un retour à la ligne dans un sujet fait échouer l'envoi. La notification échouait alors à chaque passage du cron, sans fin.


## Règle 3 — seuls les services actifs sont proposés

Le champ service de DevisForm ne propose que les services avec is_active=True, triés par catégorie puis par nom (le queryset est remplacé dans __init__). Un identifiant de service désactivé envoyé à la main est refusé. La restriction est dans le formulaire public, pas dans le modèle (limit_choices_to) : dans l'admin, un ancien devis lié à un service désactivé depuis doit rester modifiable.

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

## Protection anti-spam : le champ piège

Les deux formulaires contiennent un champ website, absent du modèle, caché aux humains par la classe CSS .form-honeypot (dans static/css/forms.css, placé hors de l'écran plutôt qu'en display: none). Un humain le laisse vide ; un robot le remplit en général.

La vue vérifie ce champ avant is_valid(). S'il est rempli, elle redirige vers la page de remerciement sans rien enregistrer : le robot ne voit jamais d'erreur et ne peut pas savoir que son envoi a été écarté, et aucune notification n'est envoyée.

Les attributs du champ protègent les vrais visiteurs : autocomplete="off" (le remplissage automatique du navigateur ne doit pas le remplir, sinon la demande d'un vrai client serait jetée sans bruit), tabindex="-1" (la navigation au clavier le saute) et aria-hidden="true" sur son conteneur (les lecteurs d'écran ne l'annoncent pas).

Limite connue : ce piège arrête les robots automatiques, pas un humain qui remplirait le formulaire à la main.