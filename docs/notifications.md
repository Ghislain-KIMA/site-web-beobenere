# Notifications des demandes de devis

Chaque nouvelle demande de devis envoyée depuis le site déclenche un e-mail vers l'adresse de l'entreprise, avec un lien direct vers la demande dans l'admin. L'envoi ne se fait **pas** pendant la requête du visiteur : il est confié à une commande lancée chaque minute par `cron`, qui renvoie automatiquement les notifications en échec.

## Fonctionnement

```
Visiteur ──▶ formulaire /devis/ ──▶ devis_create()
                                       │ enregistre le devis (notified_at = vide)
                                       └─▶ page de succès, immédiatement

cron (chaque minute) ──▶ manage.py send_devis_notifications
                            │ cherche les devis avec notified_at vide
                            │ pour chacun : envoie l'e-mail via Gmail (SMTP)
                            │   ├─ succès → notified_at = maintenant
                            │   └─ échec  → notified_at reste vide, erreur journalisée,
                            │               nouvel essai au passage suivant
```

Le champ `Devis.notified_at` sert de file d'attente :

| Valeur | Signification |
|---|---|
| vide (`NULL`) | notification pas encore envoyée, ou dernier envoi en échec |
| date | notification envoyée à cette date |

### Pourquoi ce choix

- **La page du visiteur n'attend pas l'envoi.** Un envoi Gmail prend 1 à 3 secondes, jusqu'à 10 (`EMAIL_TIMEOUT`) si Gmail ne répond pas.
- **Aucun envoi n'est perdu.** Un échec (coupure réseau, panne Gmail) laisse le devis en attente, et il est retenté à la minute suivante.
- **Pas d'infrastructure supplémentaire.** Une file de tâches classique (Celery + Redis) demanderait deux services de plus à installer et surveiller. La base de données et `cron` suffisent pour le volume de demandes du site.

Contrepartie : la notification arrive dans la minute qui suit la demande, et non instantanément.

## Fichiers concernés

| Fichier | Rôle |
|---|---|
| `apps/devis/models.py` | champ `notified_at` sur `Devis` |
| `apps/devis/migrations/0005_devis_notified_at.py` | ajoute le champ et marque les devis existants comme déjà notifiés (`RunPython`, `notified_at = created_at`) |
| `apps/devis/views.py` | `devis_create()` enregistre seulement le devis |
| `apps/devis/notifications.py` | `send_devis_notification()` (un envoi, lève une exception en cas d'échec) et `send_pending_notifications()` (parcourt les devis en attente, renvoie `(envoyées, échecs)`) |
| `apps/devis/management/commands/send_devis_notifications.py` | commande lancée par `cron` ; silencieuse quand il n'y a rien à envoyer |
| `apps/devis/tests/test_notifications.py` | tests de l'envoi, de la non-répétition, du renvoi après échec et de la commande |

## Configuration

Les réglages sont dans `beobenere/settings.py` et lisent leurs valeurs dans `.env` (chargé par `python-dotenv`, ignoré par Git).

| Variable `.env` | Exemple | Rôle |
|---|---|---|
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` | envoi réel ; sans cette variable, les e-mails s'affichent dans le terminal (backend console) |
| `EMAIL_HOST_USER` | `beobenere.business@gmail.com` | compte Gmail expéditeur |
| `EMAIL_HOST_PASSWORD` | *(16 caractères, sans espaces)* | mot de passe d'application Google, **jamais** dans le code ni dans Git |
| `DEVIS_NOTIFICATION_EMAIL` | `ghiskima@gmail.com` | adresse qui reçoit les alertes |
| `SITE_URL` | `http://100.116.252.58:8000` | base du lien « Voir la demande » ; doit être joignable depuis l'appareil où l'e-mail est lu |

Réglages fixes dans `settings.py` : `EMAIL_HOST = smtp.gmail.com`, `EMAIL_PORT = 587`, `EMAIL_USE_TLS = True`, `EMAIL_TIMEOUT = 10`, `DEFAULT_FROM_EMAIL = "BeoBenere <beobenere.business@gmail.com>"`.

Les alertes partent vers une **autre** adresse que l'expéditeur : une messagerie ne notifie généralement pas sur le téléphone un message dont on est soi-même l'expéditeur.

## Programmation avec cron

`crontab -e`, puis une seule ligne :

```
* * * * * cd /chemin/vers/website-beobenere && /usr/bin/flock -n /tmp/beobenere-notifications.lock /chemin/vers/python manage.py send_devis_notifications >> logs/cron.log 2>&1
```

| Élément | Rôle |
|---|---|
| `* * * * *` | chaque minute (passer à `*/5 * * * *` pour toutes les 5 minutes) |
| `cd …` | se placer dans le projet, pour trouver `manage.py` et `.env` |
| `flock -n …lock` | empêche deux exécutions simultanées (sinon, pendant une panne Gmail, une exécution lente pourrait chevaucher la suivante et envoyer deux fois la même notification) |
| chemin complet vers Python | `cron` ne charge pas l'environnement (conda, venv) |
| `>> logs/cron.log 2>&1` | garde la sortie et les erreurs de la commande |

Coût : une exécution sans rien à envoyer prend environ une seconde (essentiellement le chargement de Django), soit 1 à 2 % d'un cœur sur une journée.

## Journalisation

Les échecs d'envoi sont écrits par le logger `devis.notifications` dans `logs/django.log`, avec date, gravité et origine :

```
2026-10-05 09:16:18,805 ERROR devis.notifications : Échec de l'envoi de la notification pour le devis 9
```

`LOGGING` envoie le logger racine vers ce fichier : toute erreur journalisée par le code des apps y est donc enregistrée, pas seulement celles de Django.

## Tests

```bash
python manage.py test devis
```

`mail.outbox` remplace l'envoi réel pendant les tests ; `mock.patch("devis.notifications.send_mail")` simule une panne pour vérifier que le devis reste en attente.

## Dépannage

| Symptôme | Cause probable | Vérification |
|---|---|---|
| Aucune alerte reçue | `cron` non installé, ou machine éteinte | `crontab -l`, `cat logs/cron.log` |
| `Temporary failure in name resolution` dans le journal | coupure réseau ou DNS passagère | `getent hosts smtp.gmail.com` ; le renvoi automatique s'en charge |
| `Username and Password not accepted` | mot de passe d'application révoqué ou erroné | en créer un nouveau (voir ci-dessous) |
| Le lien de l'e-mail ne s'ouvre pas | `SITE_URL` injoignable depuis l'appareil | vérifier `SITE_URL` et l'adresse d'écoute du serveur |
| Une demande jamais notifiée | échecs répétés | `grep "Échec de l'envoi" logs/django.log` ; le devis a `notified_at` vide dans l'admin |

### Recréer le mot de passe d'application Google

1. Se connecter au compte `beobenere.business@gmail.com` sur `myaccount.google.com`.
2. Vérifier que la validation en deux étapes est activée (obligatoire).
3. Ouvrir `https://myaccount.google.com/apppasswords`, révoquer l'ancien mot de passe « Site BeoBenere » s'il existe, en créer un nouveau.
4. Copier les 16 caractères **sans espaces** dans `EMAIL_HOST_PASSWORD` du `.env`.
5. Aucun redémarrage nécessaire pour `cron` (chaque exécution relit `.env`) ; redémarrer `runserver` s'il tourne.

## Au déploiement

- [ ] Créer `.env` sur le serveur avec les variables ci-dessus, `SITE_URL` pointant vers le nom de domaine.
- [ ] Installer la ligne `cron` avec les chemins du serveur.
- [ ] Envoyer une demande de test et vérifier `logs/cron.log` et la réception de l'alerte.
