# BeoBenere

Site vitrine officiel de **BeoBenere**, entreprise de services informatiques
basée à Ouagadougou, Burkina Faso.

> ⚠️ **Dépôt à but de démonstration.**
> Voir [`LICENSE`](./LICENSE) — tous droits réservés, aucune réutilisation autorisée sans accord écrit préalable.

## À propos

BeoBenere propose des services informatiques de proximité pour particuliers
et petites entreprises :

- Bureautique (installation, configuration, formation)
- Maintenance et dépannage matériel/logiciel
- Réseau et sécurité de base
- Développement de sites et applications sur mesure

## Stack technique

- **Backend** : Python / Django
- **Base de données** : PostgreSQL
- **Frontend** : templates Django (HTML/CSS)

## Installation locale

Prérequis : Python 3.14, PostgreSQL.

```bash
# Cloner le dépôt
git clone https://github.com/<ton-utilisateur>/site-web-beobenere.git
cd site-web-beobenere

# Créer et activer l'environnement virtuel
python3.14 -m venv env-beobenere
source env-beobenere/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Copier le fichier d'environnement et le compléter
cp .env.example .env

# Appliquer les migrations
python manage.py migrate

# Lancer le serveur de développement
python manage.py runserver
```

Le site est alors accessible sur `http://127.0.0.1:8000/`.

## Variables d'environnement

Voir `.env.example` pour la liste complète. Ne jamais committer le fichier
`.env` réel (déjà exclu via `.gitignore`).

## Structure du projet

```
beobenere/
├── config/            # Réglages Django (settings, urls racine)
├── services/          # App : présentation des services
├── devis/             # App : demandes de devis / leads
├── contact/           # App : formulaire de contact
├── templates/         # Templates HTML partagés
├── static/            # Fichiers statiques (CSS, images)
├── .gitignore
├── LICENSE
├── requirements.txt
└── README.md
```

*(à ajuster selon la structure réelle de ton projet)*

## Licence

Ce projet est protégé par tous droits réservés. Voir le fichier
[`LICENSE`](./LICENSE) pour le détail complet des restrictions d'usage.

## Contact

**BeoBenere** — Ouagadougou, Burkina Faso

- Email : [contact.beobenere@gmail.com](mailto:contact.beobenere@gmail.com)
- WhatsApp : +226 72750096
