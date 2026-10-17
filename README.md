# SanteScolaire — Système Intégré de Santé Scolaire et Hospitalière

![Python](https://img.shields.io/badge/Python-3.9%20%7C%203.13-blue.svg?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey.svg?logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg?logo=mysql)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg?logo=bootstrap)
![ReportLab](https://img.shields.io/badge/ReportLab-PDF-red.svg)
![FullCalendar](https://img.shields.io/badge/FullCalendar-v6-success.svg)

**SanteScolaire** est un progiciel de gestion médicale scolaire complet (SIH Scolaire) développé en Python / Flask et adossé à une base de données relationnelle MySQL. Il a été conçu pour digitaliser, organiser et sécuriser la chaîne de soins au sein des établissements d'enseignement primaire, secondaire ou supérieur.

La solution assure la gestion transversale des dossiers médicaux des élèves, le suivi des protocoles d'accueil individualisé (PAI), les consultations cliniques, la pharmacie scolaire et la planification des examens périodiques, tout en garantissant une étanchéité absolue entre la gouvernance administrative et le secret médical.

---

## Sommaire

1. [Contexte et Enjeux Métier](#1-contexte-et-enjeux-métier)
2. [Matrice des Rôles et Cloisonnement de Sécurité](#2-matrice-des-rôles-et-cloisonnement-de-sécurité)
3. [Fonctionnalités du Système](#3-fonctionnalités-du-système)
   - [3.1. Espace Clinique & Dossier Médical Unique](#31-espace-clinique--dossier-médical-unique)
   - [3.2. Protocole d'Accueil Individualisé (PAI)](#32-protocole-daccueil-individualisé-pai)
   - [3.3. Consultations, Soins et Pharmacovigilance](#33-consultations-soins-et-pharmacovigilance)
   - [3.4. Gestion de la Pharmacie & Stocks de l'Infirmerie](#34-gestion-de-la-pharmacie--stocks-de-linfirmerie)
   - [3.5. Moteur d'Édition Documentaire Vectoriel (PDF)](#35-moteur-dédition-documentaire-vectoriel-pdf)
   - [3.6. Module d'Agenda et de Planification Interactive](#36-module-dagenda-et-de-planification-interactive)
   - [3.7. Administration RH, Spécialités et Audit de Sécurité](#37-administration-rh-spécialités-et-audit-de-sécurité)
4. [Architecture Technique et Choix Logiciels](#4-architecture-technique-et-choix-logiciels)
5. [Schéma de la Base de Données (Modèle Relationnel)](#5-schéma-de-la-base-de-données-modèle-relationnel)
6. [Procédure Complète d'Installation et Déploiement](#6-procédure-complète-dinstallation-et-déploiement)
7. [Comptes de Démonstration et Jeux de Données](#7-comptes-de-démonstration-et-jeux-de-données)
8. [Arborescence Détaillée du Code Source](#8-arborescence-détaillée-du-code-source)
9. [Cycle de Tests, Assurance Qualité et Non-Régression](#9-cycle-de-tests-assurance-qualité-et-non-régression)
10. [Auteur et Cadre Institutionnel](#10-auteur-et-cadre-institutionnel)

---

## 1. Contexte et Enjeux Métier

En milieu scolaire, les structures médicales font face à des contraintes opérationnelles, administratives et juridiques spécifiques :

* **Réactivité d'urgence** : mise à disposition immédiate de la conduite médicale à adopter face à un choc anaphylactique, une crise d'asthme sévère ou un malaise vagal.
* **Respect du secret médical partagé** : la législation impose une séparation stricte entre les données de scolarité (accessibles par la direction) et les données sensibles de santé (réservées au corps soignant).
* **Traçabilité médico-légale** : enregistrement horodaté de chaque soin infirmier, consultation, délivrance de médicament ou modification de mot de passe dans un journal d'audit inaltérable.
* **Coordination pluridisciplinaire** : synchronisation du travail de l'infirmier(ère) au triage et du médecin scolaire référent pour la prise en charge thérapeutique.

---

## 2. Matrice des Rôles et Cloisonnement de Sécurité

L'application repose sur un contrôle d'accès basé sur les rôles (RBAC — *Role-Based Access Control*). Les privilèges sont strictement vérifiés côté serveur par décorateurs Python avant chaque requête.

| Espace & Module | Administrateur | Médecin Scolaire | Infirmier(ère) |
| :--- | :---: | :---: | :---: |
| **Administration RH & Gestion des Spécialités** | Lecture / Écriture | Accès Interdit | Accès Interdit |
| **Invitations & Liens d'Activation Sécurisés** | Émission / Relance | Accès Interdit | Accès Interdit |
| **Gestion des Stocks Pharmaceutiques** | Lecture / Ajout de produits | Accès Interdit | Gestion Opérationnelle |
| **Journal d'Audit et Sécurité Système** | Consultation Totale | Accès Interdit | Accès Interdit |
| **Annuaire Complet des Élèves** | Accès Interdit | Lecture / Recherche | Lecture / Recherche |
| **Dossier Médical & Antécédents de l'Élève** | Accès Interdit | Consultation / Saisie | Consultation / Saisie |
| **Fiche de Consultation & Examen Clinique** | Accès Interdit | Diagnostic & Prescription | Triage & Constantes |
| **Prescription Médicamenteuse & Ordonnance** | Accès Interdit | Émission & Export PDF | Consultation |
| **Fiche d'Urgence PAI** | Accès Interdit | Validation & Export PDF | Validation & Export PDF |
| **Agenda Clinique & Prise de Rendez-vous** | Accès Interdit | Planning Personnel | Planning Global |

---

## 3. Fonctionnalités du Système

### 3.1. Espace Clinique & Dossier Médical Unique
* **Fiche d'identification clinique** : identifiant unique de dossier, classe, date de naissance, âge calculé, sexe et coordonnées d'urgence.
* **Suivi de la croissance et biométrie** : calcul automatique de l'Indice de Masse Corporelle (IMC) et tracé de la courbe d'évolution pondérale et staturale au fil des visites.
* **Filtrage de la file active** : possibilité pour le médecin scolaire de basculer instantanément entre l'annuaire global de l'établissement et sa propre liste de « Patients suivis ».

### 3.2. Protocole d'Accueil Individualisé (PAI)
* **Identification des élèves prioritaires** : bandeau d'alerte spécifique appliqué aux dossiers signalant une affection de longue durée (diabète, épilepsie, drépanocytose, allergies alimentaires graves).
* **Conduite d'urgence formalisée** : affichage explicite des gestes d'urgence, des thérapeutiques de secours à administrer sans délai et des conditions d'évacuation vers les structures hospitalières.

### 3.3. Consultations, Soins et Pharmacovigilance
* **Poste de soins et triage infirmier** : saisie des constantes vitales (pression artérielle, température corporelle, fréquence respiratoire, glycémie capillaire).
* **Examen médical complet** : anamnèse, motif de la consultation, observations cliniques détaillées, décision médicale et orientation.
* **Liaison intelligente des prescriptions** : vérification algorithmique instantanée entre les produits prescrits par le médecin et le stock réel de la pharmacie scolaire.

### 3.4. Gestion de la Pharmacie & Stocks de l'Infirmerie
* **Référentiel des produits de santé** : dénomination commune internationale, forme galénique (comprimés, collyres, pommades, injectables), conditionnement et date de péremption.
* **Surveillance dynamique des approvisionnements** : calcul des indicateurs de confort ou de pénurie avec alerte visuelle dès le franchissement du seuil minimum.
* **Ajustement rapide du stock** : boutons interactifs d'incrémentation et décrémentation des stocks lors de la délivrance aux élèves.

### 3.5. Moteur d'Édition Documentaire Vectoriel (PDF)
* **Ordonnance Médicale Officielle (A4)** :
  * Génération vectorielle native via le moteur **ReportLab** (aucune dégradation visuelle à l'impression).
  * Intégration de l'en-tête médical réglementaire, du numéro d'inscription à l'Ordre National des Médecins, de la date d'émission et de la référence du dossier.
  * Distinction visuelle claire entre les spécialités délivrées à l'infirmerie et celles à la charge des parents en pharmacie de ville.
  * Cadre légal de signature, conditions de validité (3 mois) et bloc réservé au cachet officiel.
* **Fiche d'Urgence PAI (A4)** :
  * Document officiel certifié destiné à être transmis aux chefs d'établissement, aux professeurs principaux et aux surveillants généraux.
  * Encadré de haute visibilité reprenant la pathologie, la gravité, les symptômes précurseurs et le protocole d'urgence immédiat.
  * Numéros d'urgence nationaux pré-imprimés (SAMU 15, Pompiers 18, Urgence Européenne 112, Infirmerie poste 104).
  * Zone de signature tripartite (Médecin scolaire, Chef d'établissement, Représentants légaux).

### 3.6. Module d'Agenda et de Planification Interactive
* **Double modalité de visualisation** :
  * **Vue Tabulaire** : liste séquentielle triée avec filtres multicritères (par date, statut, médecin ou classe).
  * **Vue Calendrier (FullCalendar v6)** : affichage interactif au mois, à la semaine ou à la journée, calé sur les heures d'ouverture de l'établissement (08:00 - 18:00).
* **Gestion des états de rendez-vous** : codification couleur par état clinique (Bleu : Programmé, Vert : Effectué, Rouge : Annulé).
* **Modalité de prise en charge au clic** : fenêtre modale récapitulative permettant l'ouverture directe du dossier médical de l'élève sélectionné.
* **Outil d'annulation collective** : formulaire sécurisé permettant d'annuler en une seule opération tous les créneaux d'une journée en cas de force majeure.

### 3.7. Administration RH, Spécialités et Audit de Sécurité
* **Workflow d'onboarding par courriel** :
  * Envoi d'une invitation personnalisée au format HTML via SMTP avec authentification chiffrée.
  * Génération d'un jeton cryptographique aléatoire de 64 caractères à usage unique.
  * Portail d'activation guidé : vérification d'identité, définition du mot de passe avec jauge de robustesse dynamique et connexion automatique.
  * Bouton de relance pour les invitations en attente ou expirées.
* **Journalisation d'audit** : enregistrement chronologique de chaque transaction sensible (connexions, déconnexions, invitations, délivrances de médicaments et modifications).

---

## 4. Architecture Technique et Choix Logiciels

Le projet adopte le modèle architectural **MVC** (Modèle - Vue - Contrôleur) articulé autour du mécanisme des **Blueprints Flask** pour garantir modularité et maintenabilité :

```text
[ Navigateur Web Client ]
       │
       ▼ (Requêtes HTTP / HTTPS)
[ Serveur WSGI / Reverse Proxy ]
       │
       ▼
[ Application Flask (Factory Pattern) ]
  ├── Middleware d'authentification & Sécurité RBAC
  ├── Blueprints Métier (Auth, Admin, Élèves, Consultations, Dashboard)
  ├── Services Applicatifs (Générateur PDF ReportLab, Service SMTP, Pharmacie)
  └── Moteur de rendu Jinja2 (Templates HTML5 + Bootstrap 5 + Alpine.js)
       │
       ▼ (Connexions SQL gérées)
[ Base de Données MySQL 8.0 (Moteur de stockage InnoDB) ]
```

### Détail des Technologies Employées

| Couche | Composant | Rôle Technique |
| :--- | :--- | :--- |
| **Serveur & Cadriciel** | Python 3.9 / 3.13 — Flask 3.x | Gestion du routage, contextes d'application et de session |
| **Base de Données** | MySQL 8.0 Community Server | Moteur relationnel transactionnel (InnoDB, encodage UTF-8 MB4) |
| **Gestion ORM & Migrations** | SQLAlchemy & Flask-Migrate | Gestionnaire objet-relationnel et traçabilité des évolutions de schéma |
| **Moteur d'Édition PDF** | ReportLab Platypus | Moteur vectoriel de flux de documents (*Flowables*, styles et typographie) |
| **Planification Interactive** | FullCalendar v6 (CDN global) | Moteur d'agenda dynamique en JavaScript natif |
| **Interface & Présentation** | Bootstrap 5.3 & CSS3 personnalisé | Système de grilles responsive, utilitaires et typographie Inter |
| **Réactivité Frontend** | Alpine.js & Vanilla JavaScript | Gestion d'état locale réactive sans surcoût de framework lourd |
| **Protocole de Messagerie** | Python standard `smtplib` & `email.mime` | Construction et routage des messages électroniques multipart HTML |

---

## 5. Schéma de la Base de Données (Modèle Relationnel)

Le schéma de données comprend **13 tables relationnelles** soumises à des contraintes d'intégrité référentielle rigoureuses :

1. `admin` : identifiants et clés d'accès des administrateurs du système.
2. `specialite` : référentiel des disciplines médicales représentées (pédiatrie, pédopsychiatrie, médecine générale, etc.).
3. `medecin` : praticiens hospitaliers et scolaires, rattachés à une spécialité.
4. `infirmier` : personnels soignants en charge du triage et des premiers secours.
5. `classe` : référentiel des divisions scolaires, filières et niveaux académiques.
6. `eleve` : annuaire démographique des élèves inscrits dans l'établissement.
7. `antecedent_medical` : registre des pathologies, allergies et signalements PAI (sévérité faible, moyenne ou critique).
8. `stock_medicament` : inventaire de la pharmacie centrale de l'établissement.
9. `audit_log` : journal inaltérable de traçabilité des accès et modifications.
10. `consultation` : historique complet des passages, examens cliniques et biométries.
11. `prescription` : ordonnances et lignes de traitements associées à une consultation.
12. `rdv` : créneaux de consultation planifiés entre un élève et un praticien.
13. `referentiel_medicament` : catalogue des molécules autorisées en milieu scolaire.

---

## 6. Procédure Complète d'Installation et Déploiement

### 6.1. Prérequis Système
* **Système d'exploitation** : Windows 10/11, Ubuntu 20.04+ ou macOS.
* **Environnement d'exécution** : Python 3.9, 3.10, 3.11, 3.12 ou 3.13.
* **SGBD** : MySQL Server version 8.0 ou supérieure.
* **Gestionnaire de versions** : Git.

### 6.2. Clonage du Répertoire Source
```bash
git clone https://github.com/Godwin-08/SanteScolaire.git
cd SanteScolaire
```

### 6.3. Création et Activation de l'Environnement Virtuel
* **Sous Windows (PowerShell) :**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
* **Sous Linux ou macOS :**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 6.4. Installation des Dépendances Logicielles
```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### 6.5. Déploiement du Schéma de Base de Données
Dans votre interface en ligne de commande MySQL :
```sql
CREATE DATABASE IF NOT EXISTS gestion_hospitaliere_scolaire 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
```

Importez la structure tabulaire et les données de test :
* **Sous Windows (PowerShell) :**
  ```powershell
  Get-Content backend/database/schema.sql | mysql -u root -p gestion_hospitaliere_scolaire
  Get-Content backend/database/seed.sql | mysql -u root -p gestion_hospitaliere_scolaire
  ```
* **Sous Linux / macOS :**
  ```bash
  mysql -u root -p gestion_hospitaliere_scolaire < backend/database/schema.sql
  mysql -u root -p gestion_hospitaliere_scolaire < backend/database/seed.sql
  ```

### 6.6. Fichier de Configuration `.env`
Créez un fichier `.env` dans le répertoire `backend/` :
```ini
# Paramètres d'environnement applicatif
FLASK_APP=app:create_app
FLASK_ENV=development
SECRET_KEY=votre_cle_de_securite_session_tres_longue_et_aleatoire

# Paramètres de connexion MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=votre_mot_de_passe_mysql
MYSQL_DB=gestion_hospitaliere_scolaire

# Configuration SMTP (Messagerie d'invitation)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=votre_adresse_professionnelle@gmail.com
SMTP_PASSWORD=votre_mot_de_passe_application_google
```

### 6.7. Exécution du Serveur Local
```bash
cd backend
python app.py
```
Le serveur démarre sur le port standard : **http://127.0.0.1:5000**

---

## 7. Comptes de Démonstration et Jeux de Données

Le fichier `seed.sql` configure un environnement clinique complet comprenant 120 élèves répartis sur plusieurs niveaux, des historiques de consultations et des stocks de pharmacie.

| Profil | Identité du Praticien | Adresse Électronique | Mot de Passe |
| :--- | :--- | :--- | :--- |
| **Administrateur** | Yassine El Idrissi | `admin@santescolaire.ma` | `admin123` |
| **Médecin (Généraliste)** | Dr. Karim Amrani | `dr.amrani@santescolaire.ma` | `Pass1234!` |
| **Médecin (Pédiatre)** | Dr. Samira El Fassi | `dr.elfassi@santescolaire.ma` | `Pass1234!` |
| **Médecin (Pédopsychiatre)**| Dr. Mehdi Bennani | `dr.bennani@santescolaire.ma` | `Pass1234!` |
| **Infirmier Référent** | Youssef Berrada | `inf.berrada@santescolaire.ma` | `Pass1234!` |
| **Infirmière Clinicienne** | Imane Rachidi | `inf.rachidi@santescolaire.ma` | `Pass1234!` |

> **Détection automatique de compte :** Le formulaire d'authentification (`/login`) analyse automatiquement l'adresse électronique saisie afin d'aiguiller l'utilisateur vers son tableau de bord spécifique sans étape intermédiaire.

---

## 8. Arborescence Détaillée du Code Source

```text
SanteScolaire/
├── backend/
│   ├── app.py                              # Point d'entrée de développement Flask
│   ├── wsgi.py                             # Adaptateur standard pour serveur de production
│   ├── app/
│   │   ├── __init__.py                     # Fabrique d'application Flask (Factory Pattern)
│   │   ├── config.py                       # Déclaration des paramètres et variables d'environnement
│   │   ├── constants.py                    # Constantes du domaine médical et droits d'accès
│   │   ├── context_processors.py           # Variables globales injectées dans les gabarits
│   │   ├── db.py                           # Instance de connexion MySQL native
│   │   ├── decorators.py                   # Décorateurs de sécurité et contrôle des rôles
│   │   ├── extensions.py                   # Extensions ORM et gestionnaires SQLAlchemy
│   │   ├── models.py                       # Modèles déclaratifs SQLAlchemy pour Flask-Migrate
│   │   ├── blueprints/                     # Découpage modulaire des fonctionnalités
│   │   │   ├── admin.py                    # Administration RH, gestion des spécialités et stocks
│   │   │   ├── auth.py                     # Authentification, déconnexion et activation de compte
│   │   │   ├── consultations.py            # Saisie clinique, prescriptions et export d'ordonnances
│   │   │   ├── dashboard.py                # Tableaux de bord opérationnels et planning interactif
│   │   │   ├── eleves.py                   # Annuaire des élèves, dossiers PAI et biométrie
│   │   │   └── profile.py                  # Gestion du profil praticien et mot de passe
│   │   └── services/                       # Composants métier spécialisés
│   │       ├── email_service.py            # Formatage et transmission des courriels SMTP
│   │       ├── medicament_service.py       # Contrôle de pharmacovigilance et stocks école
│   │       └── pdf_service.py              # Moteur ReportLab de génération des ordonnances et PAI
│   └── database/
│       ├── schema.sql                      # Définition des 13 tables, index et clés étrangères
│       └── seed.sql                        # Données de démonstration prêtes à l'emploi
├── frontend/
│   ├── static/                             # Ressources statiques livrées au navigateur
│   │   ├── css/                            # Feuilles de style (design système médical)
│   │   ├── img/                            # Logotype officiel et pictogrammes cliniques
│   │   └── js/                             # Scripts interactifs et utilitaires
│   └── templates/                          # Gabarits HTML structurés (Jinja2)
│       ├── base.html                       # Shell principal avec barre latérale et navigation
│       ├── activate.html                   # Portail d'accueil pour la première connexion
│       ├── agenda.html                     # Interface double vue (tableau et calendrier)
│       ├── dossier.html                    # Dossier médical unique avec suivi PAI
│       ├── ordonnance.html                 # Gabarit de prévisualisation de l'ordonnance
│       ├── admin_personnel_liste.html      # Tableau de bord RH de l'administrateur
│       ├── admin_pharmacie.html            # Gestionnaire des approvisionnements
│       └── index.html                      # Annuaire complet des élèves
├── README.md                               # Documentation technique et opérationnelle
└── requirements.txt                        # Dépendances logicielles verrouillées
```

---

## 9. Cycle de Tests, Assurance Qualité et Non-Régression

Le code source fait l'objet d'une couverture de tests automatisés via le framework `pytest`. Les suites de tests valident les aspects critiques suivants :
* Étanchéité des routes de consultation (impossibilité d'accéder à un dossier élève sans privilège soignant).
* Vérification de la création des jetons cryptographiques d'activation et délai d'expiration à 48 heures.
* Contrôle de la génération vectorielle des documents PDF (conformité des entêtes MIME et des flux binaires).
* Fiabilité des requêtes JSON alimentant le composant FullCalendar.

Exécution de la suite de tests :
```bash
pip install -r backend/requirements-dev.txt
pytest -v
```

---

## 10. Auteur et Cadre Institutionnel

* **Concepteur & Développeur** : Godwin — Étudiant ingénieur à l'**École Nationale des Sciences Appliquées de Khouribga (ENSA Khouribga)**, spécialité Génie Informatique et Ingénierie des Données (IID).
* **Finalité du projet** : Conception et déploiement d'une architecture applicative robuste répondant aux défis de la modernisation des systèmes d'information hospitaliers et scolaires.
