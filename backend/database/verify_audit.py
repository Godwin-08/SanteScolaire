import sys
import os

backend_dir = r"c:\Users\vPro\Downloads\SanteScolaire\backend"
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app
from app.extensions import orm_db as db
from sqlalchemy import text

app = create_app()
with app.app_context():
    print("=== 1. VÉRIFICATION COMPLÈTE BASE DE DONNÉES ===")
    tables = [r[0] for r in db.session.execute(text("SHOW TABLES")).fetchall()]
    print("Tables existantes :", tables)

    expected_tables = [
        'admin', 'specialite', 'medecin', 'infirmier', 'classe', 
        'eleve', 'antecedent_medical', 'stock_medicament', 
        'audit_log', 'consultation', 'prescription', 'rdv'
    ]
    missing = [t for t in expected_tables if t not in tables]
    print("Tables manquantes :", missing if missing else "AUCUNE (100% conformes)")

    print("\n=== COMPTEURS DE LIGNES PAR TABLE ===")
    for t in expected_tables:
        cnt = db.session.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
        print(f"  • {t:22}: {cnt} enregistrements")

    print("\n=== VÉRIFICATION DU MODÈLE ELEVE & CLASSE ===")
    eleve_cols = [r[0] for r in db.session.execute(text("SHOW COLUMNS FROM eleve")).fetchall()]
    print("Colonne id_classe présente dans eleve :", "OUI" if "id_classe" in eleve_cols else "NON")
    total_eleves = db.session.execute(text("SELECT COUNT(*) FROM eleve")).scalar()
    linked_eleves = db.session.execute(text("SELECT COUNT(*) FROM eleve WHERE id_classe IS NOT NULL")).scalar()
    print(f"Élèves associés à leur classe normalisée : {linked_eleves} / {total_eleves}")

    print("\n=== 2. VÉRIFICATION DU MOTEUR D'ALERTES & KPIS ===")
    stocks_critiques = db.session.execute(text("SELECT nom_medicament, quantite_stock, seuil_alerte FROM stock_medicament WHERE quantite_stock <= seuil_alerte")).fetchall()
    print(f"Articles en alerte stock critique ({len(stocks_critiques)}) :")
    for s in stocks_critiques:
        print(f"  - {s[0]} : {s[1]} restants (seuil: {s[2]})")

    antecedents_critiques = db.session.execute(text("SELECT id_eleve, type, severite, pai_signe FROM antecedent_medical WHERE severite = 'Critique' OR pai_signe = 1")).fetchall()
    print(f"\nCas médicaux prioritaires (PAI / Sévérité Critique) : {len(antecedents_critiques)}")
    for a in antecedents_critiques:
        print(f"  - Élève #{a[0]} : {a[1]} (Sévérité: {a[2]}, PAI signé: {'OUI' if a[3] else 'NON'})")

    audit_count = db.session.execute(text("SELECT COUNT(*) FROM audit_log")).scalar()
    print(f"\nJournal d'audit : {audit_count} événements enregistrés")
    recent_logs = db.session.execute(text("SELECT action, details, created_at FROM audit_log ORDER BY created_at DESC LIMIT 3")).fetchall()
    for l in recent_logs:
        print(f"  - [{l[2]}] {l[0]}: {l[1]}")

