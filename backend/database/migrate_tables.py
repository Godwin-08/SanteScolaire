import sys
import os

# Ensure backend directory is in python path
backend_dir = r"c:\Users\vPro\Downloads\SanteScolaire\backend"
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app
from app.extensions import orm_db as db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Migrating database schema...")

    # 1. Table classe
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS classe (
            id_classe INT AUTO_INCREMENT PRIMARY KEY,
            nom_classe VARCHAR(50) NOT NULL UNIQUE,
            niveau VARCHAR(50) NOT NULL,
            filiere VARCHAR(100) DEFAULT NULL,
            annee_scolaire VARCHAR(20) NOT NULL DEFAULT '2025-2026'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """))

    # 2. Check and alter eleve for id_classe
    cols = [r[0] for r in db.session.execute(text("SHOW COLUMNS FROM eleve")).fetchall()]
    if 'id_classe' not in cols:
        print("Adding id_classe column to eleve...")
        db.session.execute(text("""
            ALTER TABLE eleve 
            ADD COLUMN id_classe INT DEFAULT NULL,
            ADD CONSTRAINT fk_eleve_classe FOREIGN KEY (id_classe) REFERENCES classe(id_classe) ON DELETE RESTRICT ON UPDATE CASCADE;
        """))

    # 3. Table audit_log
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id_log INT AUTO_INCREMENT PRIMARY KEY,
            action VARCHAR(100) NOT NULL,
            user_type VARCHAR(50) NOT NULL,
            user_id INT DEFAULT NULL,
            details TEXT DEFAULT NULL,
            ip_address VARCHAR(45) DEFAULT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """))

    # 4. Table antecedent_medical
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS antecedent_medical (
            id_antecedent INT AUTO_INCREMENT PRIMARY KEY,
            id_eleve INT NOT NULL,
            type VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            severite ENUM('Faible', 'Moyenne', 'Critique') NOT NULL DEFAULT 'Moyenne',
            conduite_a_tenir TEXT DEFAULT NULL,
            pai_signe TINYINT(1) NOT NULL DEFAULT 0,
            date_declaration DATE DEFAULT NULL,
            CONSTRAINT fk_antecedent_eleve FOREIGN KEY (id_eleve) REFERENCES eleve(id_eleve) ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """))

    # 5. Table stock_medicament
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS stock_medicament (
            id_medicament INT AUTO_INCREMENT PRIMARY KEY,
            nom_medicament VARCHAR(150) NOT NULL,
            forme VARCHAR(50) NOT NULL,
            quantite_stock INT NOT NULL DEFAULT 0,
            seuil_alerte INT NOT NULL DEFAULT 10,
            unite_mesure VARCHAR(30) DEFAULT 'boîtes',
            date_peremption DATE DEFAULT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """))

    # Populate classes from existing eleve.classe
    db.session.execute(text("""
        INSERT IGNORE INTO classe (nom_classe, niveau, filiere, annee_scolaire)
        SELECT DISTINCT classe, 
            CASE 
                WHEN classe LIKE '1AC%' THEN 'Collège 1ère Année'
                WHEN classe LIKE '2AC%' THEN 'Collège 2ème Année'
                WHEN classe LIKE '3AC%' THEN 'Collège 3ème Année'
                WHEN classe LIKE 'TCS%' THEN 'Tronc Commun Scientifique'
                WHEN classe LIKE '1BAC%' THEN '1ère Année Bac'
                WHEN classe LIKE '2BAC%' THEN '2ème Année Bac'
                ELSE 'Secondaire'
            END,
            CASE 
                WHEN classe LIKE '%SM%' THEN 'Sciences Mathématiques'
                WHEN classe LIKE '%PC%' THEN 'Physique Chimie'
                WHEN classe LIKE '%SVT%' THEN 'Sciences Vie et Terre'
                WHEN classe LIKE '%TCS%' THEN 'Sciences'
                ELSE 'Général'
            END,
            '2025-2026'
        FROM eleve
        WHERE classe IS NOT NULL AND classe != '';
    """))

    # Update eleve.id_classe based on eleve.classe
    db.session.execute(text("""
        UPDATE eleve e
        JOIN classe c ON e.classe = c.nom_classe
        SET e.id_classe = c.id_classe
        WHERE e.id_classe IS NULL;
    """))

    # Populate stock_medicament if empty
    stock_count = db.session.execute(text("SELECT COUNT(*) FROM stock_medicament")).scalar()
    if stock_count == 0:
        print("Seeding stock_medicament...")
        stocks = [
            ("Paracétamol 500mg", "Comprimé", 45, 15, "boîtes", "2026-12-31"),
            ("Ventoline 100µg (Salbutamol)", "Inhalateur", 3, 5, "inhalateurs", "2026-08-15"), # CRITICAL
            ("Bétadine Dermique 10%", "Flacon 125ml", 12, 5, "flacons", "2027-01-20"),
            ("Pansements Stériles assortis", "Boîte 50", 18, 10, "boîtes", "2028-05-30"),
            ("Compresses stériles 7.5x7.5cm", "Paquet", 35, 10, "paquets", "2027-11-15"),
            ("Spasfon Lyoc 80mg", "Lyophilisat", 4, 8, "boîtes", "2026-09-10"), # CRITICAL
            ("Cétirizine 10mg (Antihistaminique)", "Comprimé", 14, 6, "boîtes", "2027-03-01"),
            ("Sérum Physiologique dosettes", "Boîte 30", 25, 8, "boîtes", "2027-04-10"),
            ("Stylo Épinéphrine (Anapen/Epipen 0.3mg)", "Auto-injecteur", 1, 3, "stylos", "2026-06-30"), # CRITICAL
            ("Bande extensible Velpeau 3m x 10cm", "Rouleau", 22, 10, "rouleaux", "2028-10-01")
        ]
        for nom, forme, qte, seuil, unite, d_perempt in stocks:
            db.session.execute(text("""
                INSERT INTO stock_medicament (nom_medicament, forme, quantite_stock, seuil_alerte, unite_mesure, date_peremption)
                VALUES (:nom, :forme, :qte, :seuil, :unite, :d_perempt)
            """), {"nom": nom, "forme": forme, "qte": qte, "seuil": seuil, "unite": unite, "d_perempt": d_perempt})

    # Populate antecedent_medical if empty
    antecedent_count = db.session.execute(text("SELECT COUNT(*) FROM antecedent_medical")).scalar()
    if antecedent_count == 0:
        print("Seeding antecedent_medical...")
        # Get some student IDs
        eleves = db.session.execute(text("SELECT id_eleve, nom_eleve, prenom_eleve FROM eleve ORDER BY id_eleve LIMIT 10")).fetchall()
        if len(eleves) >= 6:
            antecedents = [
                (eleves[0][0], "Asthme d'effort", "Asthme modéré avec déclenchement à l'effort physique.", "Critique", "Garder l'inhalateur Ventoline disponible, dispenser de course d'endurance lors des crises.", 1, "2025-09-15"),
                (eleves[1][0], "Allergie alimentaire", "Allergie sévère aux arachides et fruits à coque.", "Critique", "Interdiction stricte cantine sans panier repas dédié. Épinéphrine en infirmerie.", 1, "2025-09-18"),
                (eleves[2][0], "Diabète de type 1", "Diabète insulinodépendant sous pompe à insuline.", "Critique", "Autoriser collation et resucrage immédiat en cours si glycémie < 0.70 g/L.", 1, "2025-09-20"),
                (eleves[3][0], "Épilepsie", "Crises d'épilepsie généralisées espacées.", "Moyenne", "Protéger la tête, mettre en PLS, ne rien insérer dans la bouche, appeler médecin/SAMU.", 1, "2025-10-05"),
                (eleves[4][0], "Allergie aux piqûres de guêpes", "Réaction œdémateuse locale sévère.", "Moyenne", "Désinfecter, appliquer froid, administrer antihistaminique d'urgence si prescription.", 0, "2025-11-12"),
                (eleves[5][0], "Troubles visuels (Myopie forte)", "Correction optique permanente nécessaire.", "Faible", "Placement au premier rang en classe.", 0, "2025-09-10")
            ]
            for id_e, typ, desc, sev, conduite, pai, d_decl in antecedents:
                db.session.execute(text("""
                    INSERT INTO antecedent_medical (id_eleve, type, description, severite, conduite_a_tenir, pai_signe, date_declaration)
                    VALUES (:id_e, :typ, :desc, :sev, :conduite, :pai, :d_decl)
                """), {"id_e": id_e, "typ": typ, "desc": desc, "sev": sev, "conduite": conduite, "pai": pai, "d_decl": d_decl})

    # Populate audit_log initial demo actions
    log_count = db.session.execute(text("SELECT COUNT(*) FROM audit_log")).scalar()
    if log_count == 0:
        print("Seeding audit_log...")
        logs = [
            ("INITIALISATION_SYSTEME", "ADMIN", 1, "Initialisation de la plateforme et des référentiels médicaux.", "127.0.0.1"),
            ("CREATION_COMPTE", "ADMIN", 1, "Invitation envoyée au Dr. Alami Karim (Médecin Généraliste)", "127.0.0.1"),
            ("ACTIVATION_COMPTE", "MEDECIN", 1, "Activation réussie du compte Dr. Alami Karim avec mot de passe sécurisé", "192.168.1.10"),
            ("CREATION_SPECIALITE", "ADMIN", 1, "Création de la spécialité Pédopsychiatrie (code PEDO-PSY)", "127.0.0.1"),
            ("ALERTE_STOCK", "SYSTEM", None, "Alerte automatique : Stock critique pour Ventoline 100µg (3 restants)", "127.0.0.1")
        ]
        for act, utyp, uid, details, ip in logs:
            db.session.execute(text("""
                INSERT INTO audit_log (action, user_type, user_id, details, ip_address)
                VALUES (:act, :utyp, :uid, :details, :ip)
            """), {"act": act, "utyp": utyp, "uid": uid, "details": details, "ip": ip})

    db.session.commit()
    print("Migration and seeding completed successfully!")
