# 🏥 SanteScolaire — Système de Gestion Médicale

![Python](https://img.shields.io/badge/Python-3.9-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)

**SanteScolaire** est une application web Flask pour digitaliser l'infirmerie d'un établissement scolaire : dossiers élèves, consultations, agenda et statistiques, avec une gestion des accès par rôle (admin, médecin, infirmier).

## Fonctionnalités
- Dossiers élèves et historique médical
- Consultations et rendez-vous
- Tableau de bord et statistiques (Chart.js)
- Administration du personnel médical

## Captures
![Tableau de bord](assets/screenshots/dashboard-2026-02-06.png)
![Capture d'écran](assets/screenshots/screen-2026-02-06-142609.png)

## Stack
- Python 3.9+, Flask 3.x
- MySQL 8.x
- Bootstrap 5, Chart.js

## Structure
- `app/` : application Flask (blueprints, templates, static)
- `app/blueprints/` : routes et logique web
- `app/models.py` : modèles SQLAlchemy (migrations)
- `app/services/` : services (ex: emails)
- `database/schema.sql` : schéma MySQL
- `database/seed.sql` : données de démo (optionnel)
- `app.py` : point d'entrée développement
- `wsgi.py` : point d'entrée déploiement

## Installation rapide
1. Cloner le dépôt
```bash
git clone https://github.com/Godwin-08/SanteScolaire.git
cd SanteScolaire
```
2. Installer les dépendances
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```
3. Importer le schéma MySQL
```bash
mysql -u root -p < database/schema.sql
```
4. (Optionnel) Charger des données de démo
```bash
mysql -u root -p < database/seed.sql
```
5. Lancer l'application
```bash
python app.py
```

## Identifiants de démo (si seed.sql chargé)
- Admin: ID `1`, Nom `Admin`, Mot de passe `admin123`
- M?decin: ID `1`, Prenom `Karim`, Nom `Amrani`, Mot de passe `KARI-1-M`
- Infirmier: ID `1`, Prenom `Youssef`, Nom `Berrada`, Mot de passe `YOUS-1-I`

## Configuration
Créer un fichier `.env` à la racine (ou définir des variables d'environnement).
Vous pouvez partir de `.env.example`.

- `SECRET_KEY` : clé de session
- `DB_PASSWORD` : mot de passe MySQL (requis, laisser vide si pas de mot de passe)
- `MYSQL_HOST` : hôte MySQL (optionnel, défaut `localhost`)
- `MYSQL_USER` : utilisateur MySQL (optionnel, défaut `root`)
- `MYSQL_DB` : base MySQL (optionnel, défaut `gestion_hospitaliere_scolaire`)

## Notes
- Le schéma est fourni dans `database/schema.sql`.
- Les données de démo sont dans `database/seed.sql`.
- Un guide de démonstration est disponible dans `DEMO.md`.
- Les comptes médecins/infirmiers doivent changer leur mot de passe à la première connexion.
- Si l'admin laisse le mot de passe vide lors de l'ajout, un mot de passe temporaire est genere au format `NOM4-ID-M` / `NOM4-ID-I`.

## Migrations (Flask-Migrate)
```bash
flask --app app:create_app db init
flask --app app:create_app db migrate -m "init"
flask --app app:create_app db upgrade
```

## Tests
```bash
pip install -r requirements-dev.txt
pytest
```

## Auteur
- Godwin — ENSA Khouribga (IID)
