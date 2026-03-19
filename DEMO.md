## Demo complet SanteScolaire

### 1) Initialisation rapide
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
```

```bash
python app.py
```

### 2) Comptes de demo
- Admin: ID `1`, Nom `Admin`, Mot de passe `admin123`
- Medecin: ID `1`, Prenom `Karim`, Nom `Amrani`, Mot de passe `KARI-1-M`
- Infirmier: ID `1`, Prenom `Youssef`, Nom `Berrada`, Mot de passe `YOUS-1-I`

### 3) Scenario de demo (10–15 min)
1. **Login Admin**
   - Aller sur `/login`
   - Se connecter en admin
   - Ouvrir le panel admin, ajouter un medecin et un infirmier (avec mot de passe)

2. **Login Medecin**
   - Se connecter en medecin (ID 1)
   - Changer le mot de passe a la premiere connexion
   - Consulter le dashboard (KPIs + graphiques)
   - Ouvrir un dossier eleve, creer une consultation + prescription

3. **Login Infirmier**
   - Se connecter en infirmier (ID 1)
   - Changer le mot de passe a la premiere connexion
   - Ouvrir un dossier eleve et effectuer un triage
   - Programmer un RDV
   - Aller dans l'agenda pour filtrer par statut

4. **Agenda**
   - Filtrer par classe / statut / date
   - Annuler une journee complete

### 4) Notes utiles
- Si l'admin laisse le mot de passe vide lors de l'ajout, un mot de passe temporaire est genere au format `NOM4-ID-M` / `NOM4-ID-I`.
- Les emails de notification sont en mode simulation si SMTP non configure.
- Pour demo rapide, garder les donnees de seed.
