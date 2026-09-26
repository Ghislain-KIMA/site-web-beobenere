# BeoBenere

Site vitrine officiel de **BeoBenere**, entreprise de services informatiques
basée à Ouagadougou, Burkina Faso.

> ⚠️ **Dépôt à but de démonstration.** Ce code est rendu public à titre de
> portfolio professionnel. Voir [`LICENSE`](./LICENSE) — tous droits réservés,
> aucune réutilisation autorisée sans accord écrit préalable.

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

## Licence

Ce projet est protégé par tous droits réservés. Voir le fichier
[`LICENSE`](./LICENSE) pour le détail complet des restrictions d'usage.

## Contact

**BeoBenere** — Ouagadougou, Burkina Faso

- Email : [contact.beobenere@gmail.com](contact.beobenere@gmail.com)
- WhatsApp : +226 72750096

## TODO

- [X] Demander l'avis de claude sur mon logo.
- [X] Pauser la question à claude Quelle variante de la couleur verte est passe partout ?
- [X] (Ghislain KIMA 24-09-2026): Montrer à claude, mon réorganisation de ce fichier CSS pour voir son avis.
- [X] (Ghislain KIMA 25-09-2026): Rendre la position du hero dynamique toujours au centre, et faire en sorte qu'il respecte la charte graphique.
- [ ] Faire des maquettes pour les interfaces graphiques.
- [ ] Peupler les tables Service et Category dans la base de données via l'admin
- [ ] Faire une migration Django avec `RunPython`, qui insère les objets `Category` puis `Service` directement en Python.
- [ ] Générer les images pour les services avec ChatGPT.
- [ ] Écrire des test pour l'app service.
- [ ] **Prochaine étape logique** : créer la page qui affiche la liste des services depuis la base de données (une vue + un template dans l'app `service`), et relier le lien "Services" du header vers cette page — exactement le même principe qu'on a fait pour `homepage` avec `Company`.
- [X] Bien. On peut passer à la saisie des services dans l'admin maintenant.
- [ ] Pauser la question à claude, dois-je ajouter dans la table Company, des urls ou scémin sur les logo, icône et favicon ?
- [ ] Expliquer à claude de temps long de chargement du style CSS. Y'a-t-il possiblité d'optimisation ?
- [ ] Se mettre à jour du code déjà écrit avant d'en ajouter d'autres.
- [ ] Renommer mon environnement de "beonbenere-website" en "website-beobenere"
- [ ] Ajouter le mode claire/sombre, automatique et bouton d'action.
- [ ] Modéliser la table Services
- [ ] Confirmer les indications de la charte graphique en créer une nouveau logo de A à Z
