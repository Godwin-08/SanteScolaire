import hashlib
import re
import secrets
import unicodedata
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash

from app.constants import ROLE_ADMIN, ROLE_INFIRMIER, ROLE_MEDECIN
from app.db import mysql
from app.services.email_service import send_activation_email
from app.services.export_service import export_personnel_csv, export_personnel_excel, export_pilotage_pdf

admin_bp = Blueprint('admin', __name__)

def _normalize_name(value):
    value = (value or "").strip()
    if not value:
        return "USER"
    normalized = unicodedata.normalize("NFKD", value)
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^A-Za-z0-9]", "", normalized).upper()
    return normalized or "USER"

def log_audit(action, details, user_type="ADMIN", user_id=None):
    """Enregistre un événement dans la table audit_log"""
    try:
        cur = mysql.connection.cursor()
        ip = request.remote_addr if request else "127.0.0.1"
        cur.execute(
            "INSERT INTO audit_log (action, user_type, user_id, details, ip_address, created_at) VALUES (%s, %s, %s, %s, %s, NOW())",
            (action, user_type, user_id or session.get('user_id'), details, ip)
        )
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        print(f"Erreur d'audit log: {e}")

def _get_personnel_list(cur, role_filter=None, status_filter=None, spe_filter=None, search_query=None):
    """Récupère et filtre la liste unifiée du personnel médical (Médecins & Infirmiers)"""
    now = datetime.now()
    personnel = []

    # 1. Médecins
    if not role_filter or role_filter in ['all', 'medecin']:
        cur.execute("""
            SELECT m.*, s.nom_specialite, s.code_specialite 
            FROM medecin m
            LEFT JOIN specialite s ON m.id_specialite = s.id_specialite
            ORDER BY m.nom_medecin ASC
        """)
        for m in cur.fetchall():
            # Détermination du statut d'activation
            if not m.get('activation_token_hash'):
                statut = 'Actif'
            elif m.get('activation_expires_at') and m['activation_expires_at'] < now:
                statut = 'Expiré'
            else:
                statut = 'En attente'

            p_item = {
                'id': m['id_medecin'],
                'type': 'Médecin',
                'raw_type': 'medecin',
                'nom': m['nom_medecin'],
                'prenom': m['prenom_medecin'],
                'email': m['email'],
                'specialite': m.get('nom_specialite') or m.get('specialite') or 'Généraliste',
                'id_specialite': m.get('id_specialite'),
                'statut': statut,
                'token_hash': m.get('activation_token_hash'),
                'date_expiration': m['activation_expires_at'].strftime('%d/%m/%Y %H:%M') if m.get('activation_expires_at') else '-'
            }
            personnel.append(p_item)

    # 2. Infirmiers
    if not role_filter or role_filter in ['all', 'infirmier']:
        cur.execute("SELECT * FROM infirmier ORDER BY nom_infirmier ASC")
        for i in cur.fetchall():
            if not i.get('activation_token_hash'):
                statut = 'Actif'
            elif i.get('activation_expires_at') and i['activation_expires_at'] < now:
                statut = 'Expiré'
            else:
                statut = 'En attente'

            p_item = {
                'id': i['id_infirmier'],
                'type': 'Infirmier',
                'raw_type': 'infirmier',
                'nom': i['nom_infirmier'],
                'prenom': i['prenom_infirmier'],
                'email': i['email'],
                'specialite': 'Soins infirmiers',
                'id_specialite': None,
                'statut': statut,
                'token_hash': i.get('activation_token_hash'),
                'date_expiration': i['activation_expires_at'].strftime('%d/%m/%Y %H:%M') if i.get('activation_expires_at') else '-'
            }
            personnel.append(p_item)

    # Application des filtres combinés
    filtered = []
    for p in personnel:
        # Filtre statut
        if status_filter and status_filter != 'all' and p['statut'].lower() != status_filter.lower():
            continue
        # Filtre spécialité
        if spe_filter and spe_filter != 'all':
            if str(p.get('id_specialite')) != str(spe_filter) and spe_filter.lower() not in p['specialite'].lower():
                continue
        # Recherche textuelle
        if search_query:
            q = search_query.lower()
            if q not in p['nom'].lower() and q not in p['prenom'].lower() and q not in p['email'].lower() and q not in p['specialite'].lower():
                continue
        filtered.append(p)

    return filtered

@admin_bp.route('/admin')
def panel():
    if not session.get('logged_in') or session.get('user_role') != ROLE_ADMIN:
        flash("Accès réservé aux administrateurs.", "danger")
        return redirect(url_for('auth.login'))
        
    cur = mysql.connection.cursor()

    # Filtres depuis l'URL
    role_filter = request.args.get('role', 'all')
    status_filter = request.args.get('statut', 'all')
    spe_filter = request.args.get('specialite', 'all')
    search_query = request.args.get('search', '').strip()

    # Liste du personnel filtrée
    personnel = _get_personnel_list(cur, role_filter, status_filter, spe_filter, search_query)

    # Récupération brute pour les KPIs
    all_personnel = _get_personnel_list(cur)
    total_medecins = sum(1 for p in all_personnel if p['raw_type'] == 'medecin')
    total_infirmiers = sum(1 for p in all_personnel if p['raw_type'] == 'infirmier')
    total_personnel = len(all_personnel)
    total_actifs = sum(1 for p in all_personnel if p['statut'] == 'Actif')
    taux_activation = round((total_actifs / total_personnel * 100), 1) if total_personnel > 0 else 0

    # Spécialités avec compteur
    cur.execute("""
        SELECT s.*, COUNT(m.id_medecin) as nb_medecins
        FROM specialite s
        LEFT JOIN medecin m ON s.id_specialite = m.id_specialite
        GROUP BY s.id_specialite, s.nom_specialite, s.code_specialite, s.description
        ORDER BY s.nom_specialite ASC
    """)
    specialites = cur.fetchall()

    # Filtres interactifs du tableau de bord (Année, Période & Classe)
    annee_filter = request.args.get('annee', 'all')
    periode_filter = request.args.get('periode', 'all')
    classe_filter = request.args.get('classe', 'all')

    # Années disponibles dans l'historique
    cur.execute("SELECT DISTINCT YEAR(date_consult) as annee FROM consultation WHERE date_consult IS NOT NULL ORDER BY annee DESC")
    annees_disponibles = [int(r['annee']) for r in cur.fetchall()]
    if not annees_disponibles:
        annees_disponibles = [datetime.now().year]

    # Condition de date dynamique
    date_conditions = []
    if annee_filter != 'all' and annee_filter.isdigit():
        date_conditions.append(f"YEAR(c.date_consult) = {int(annee_filter)}")
    
    if periode_filter == 'today':
        date_conditions.append("DATE(c.date_consult) = CURDATE()")
    elif periode_filter == 'week':
        date_conditions.append("c.date_consult >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)")
    elif periode_filter == 'month':
        date_conditions.append("c.date_consult >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)")
    elif periode_filter == 'year':
        date_conditions.append("c.date_consult >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)")

    date_condition = " AND ".join(date_conditions) if date_conditions else "1=1"

    # Condition de classe dynamique
    classe_condition = "1=1"
    classe_param = []
    if classe_filter != 'all':
        classe_condition = "e.classe = %s"
        classe_param = [classe_filter]

    # Liste des classes pour le menu déroulant
    cur.execute("SELECT DISTINCT classe FROM eleve WHERE classe IS NOT NULL AND classe != '' ORDER BY classe ASC")
    toutes_classes = [r['classe'] for r in cur.fetchall()]

    # KPIs Population & Santé Scolaire
    cur.execute("SELECT COUNT(*) as cnt FROM eleve")
    total_eleves = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(DISTINCT id_eleve) as cnt FROM antecedent_medical WHERE pai_signe = 1 OR severite = 'Critique'")
    eleves_avec_pai = cur.fetchone()['cnt']

    # Consultations selon les filtres
    if classe_param:
        cur.execute(f"""
            SELECT COUNT(*) as cnt 
            FROM consultation c 
            JOIN eleve e ON c.id_eleve = e.id_eleve 
            WHERE {date_condition} AND {classe_condition}
        """, tuple(classe_param))
    else:
        cur.execute(f"""
            SELECT COUNT(*) as cnt 
            FROM consultation c 
            JOIN eleve e ON c.id_eleve = e.id_eleve 
            WHERE {date_condition} AND {classe_condition}
        """)
    total_consultations = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) as cnt FROM rdv")
    total_rdv = cur.fetchone()['cnt']

    # Stocks critiques en pharmacie
    cur.execute("SELECT * FROM stock_medicament WHERE quantite_stock <= seuil_alerte ORDER BY quantite_stock ASC")
    stocks_critiques_list = cur.fetchall()
    stocks_critiques = len(stocks_critiques_list)

    # Journal d'audit (10 dernières actions)
    cur.execute("SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 10")
    audit_logs = cur.fetchall()
    
    # Points d'attention & Alertes
    points_attention = []

    # Données graphiques Chart.js (Spécialités & Rendez-vous)
    spe_labels = [s['nom_specialite'] for s in specialites if s['nb_medecins'] > 0]
    spe_counts = [int(s['nb_medecins']) for s in specialites if s['nb_medecins'] > 0]

    cur.execute("SELECT IFNULL(statut, 'Non défini') as st, COUNT(*) as cnt FROM rdv GROUP BY statut")
    rdv_rows = cur.fetchall()
    rdv_labels = [r['st'].capitalize() for r in rdv_rows]
    rdv_counts = [int(r['cnt']) for r in rdv_rows]

    # 1. Évolution mensuelle des visites (Janvier à Décembre multi-années)
    noms_mois = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
    mois_labels = noms_mois

    # Déterminer les années à tracer (si année choisie -> cette année, sinon -> comparatif des années récentes)
    if annee_filter != 'all' and annee_filter.isdigit():
        annees_a_tracer = [int(annee_filter)]
    else:
        annees_a_tracer = annees_disponibles[:3]

    color_palette = [
        {'border': '#10ac84', 'bg': 'rgba(16, 172, 132, 0.12)'},  # Émeraude
        {'border': '#0284c7', 'bg': 'rgba(2, 132, 199, 0.08)'},   # Bleu cyan
        {'border': '#f59e0b', 'bg': 'rgba(245, 158, 11, 0.08)'},  # Ambre
        {'border': '#8b5cf6', 'bg': 'rgba(139, 92, 246, 0.08)'},  # Violet
    ]

    chart_datasets = []
    for i, yr in enumerate(annees_a_tracer):
        counts = [0] * 12
        if classe_param:
            cur.execute(f"""
                SELECT MONTH(c.date_consult) as num_mois, COUNT(*) as total 
                FROM consultation c 
                JOIN eleve e ON c.id_eleve = e.id_eleve 
                WHERE {classe_condition} AND YEAR(c.date_consult) = %s
                GROUP BY num_mois 
                ORDER BY num_mois ASC
            """, tuple(classe_param + [yr]))
        else:
            cur.execute("""
                SELECT MONTH(c.date_consult) as num_mois, COUNT(*) as total 
                FROM consultation c 
                WHERE YEAR(c.date_consult) = %s
                GROUP BY num_mois 
                ORDER BY num_mois ASC
            """, (yr,))
        
        for row in cur.fetchall():
            idx = row['num_mois'] - 1
            if 0 <= idx < 12:
                counts[idx] = int(row['total'])

        pal = color_palette[i % len(color_palette)]
        chart_datasets.append({
            'annee': yr,
            'label': f"Année {yr} ({sum(counts)} visites)",
            'data': counts,
            'borderColor': pal['border'],
            'backgroundColor': pal['bg'],
            'total': sum(counts)
        })

    mois_counts = chart_datasets[0]['data'] if chart_datasets else [0] * 12

    # 2. Visites par classe (filtrée par période)
    cur.execute(f"""
        SELECT e.classe, COUNT(c.id_consult) as total 
        FROM consultation c 
        JOIN eleve e ON c.id_eleve = e.id_eleve 
        WHERE e.classe IS NOT NULL AND e.classe != '' AND {date_condition}
        GROUP BY e.classe 
        ORDER BY total DESC 
        LIMIT 6
    """)
    classe_rows = cur.fetchall()
    classe_labels = [r['classe'] for r in classe_rows]
    classe_counts = [int(r['total']) for r in classe_rows]

    # 3. Principaux motifs de consultation (filtrés par période et classe)
    if classe_param:
        cur.execute(f"""
            SELECT c.motif, COUNT(*) as total 
            FROM consultation c 
            JOIN eleve e ON c.id_eleve = e.id_eleve 
            WHERE c.motif IS NOT NULL AND c.motif != '' AND {date_condition} AND {classe_condition}
            GROUP BY c.motif 
            ORDER BY total DESC 
            LIMIT 5
        """, tuple(classe_param))
    else:
        cur.execute(f"""
            SELECT c.motif, COUNT(*) as total 
            FROM consultation c 
            JOIN eleve e ON c.id_eleve = e.id_eleve 
            WHERE c.motif IS NOT NULL AND c.motif != '' AND {date_condition} AND {classe_condition}
            GROUP BY c.motif 
            ORDER BY total DESC 
            LIMIT 5
        """)
    motif_rows = cur.fetchall()
    motif_labels = [r['motif'] for r in motif_rows]
    motif_counts = [int(r['total']) for r in motif_rows]

    cur.close()

    kpis = {
        'total_personnel': total_personnel,
        'total_medecins': total_medecins,
        'total_infirmiers': total_infirmiers,
        'total_actifs': total_actifs,
        'taux_activation': taux_activation,
        'nb_specialites': len(specialites),
        'total_eleves': total_eleves,
        'eleves_avec_pai': eleves_avec_pai,
        'total_consultations': total_consultations,
        'total_rdv': total_rdv,
        'stocks_critiques': stocks_critiques
    }

    current_filters = {
        'role': role_filter,
        'statut': status_filter,
        'specialite': spe_filter,
        'search': search_query
    }

    return render_template(
        'admin_dashboard.html',
        personnel=personnel,
        specialites=specialites,
        kpis=kpis,
        points_attention=points_attention,
        audit_logs=audit_logs,
        current_filters=current_filters,
        spe_labels=spe_labels,
        spe_counts=spe_counts,
        rdv_labels=rdv_labels,
        rdv_counts=rdv_counts,
        mois_labels=mois_labels,
        mois_counts=mois_counts,
        classe_labels=classe_labels,
        classe_counts=classe_counts,
        motif_labels=motif_labels,
        motif_counts=motif_counts,
        toutes_classes=toutes_classes,
        periode_filter=periode_filter,
        classe_filter=classe_filter,
        total_medecins=total_medecins,
        total_infirmiers=total_infirmiers,
        total_personnel=total_personnel,
        total_actifs=total_actifs,
        total_eleves=total_eleves,
        total_consultations=total_consultations,
        total_rdv=total_rdv,
        eleves_avec_pai=eleves_avec_pai,
        stocks_critiques=stocks_critiques,
        role_filter=role_filter,
        status_filter=status_filter,
        spe_filter=spe_filter,
        search_query=search_query,
        annee_filter=annee_filter,
        annees_disponibles=annees_disponibles,
        chart_datasets=chart_datasets
    )

# --- ROUTES D'EXPORTS (CSV, EXCEL, PDF) ---

@admin_bp.route('/admin/export/<export_type>')
def export_data(export_type):
    if not session.get('logged_in') or session.get('user_role') != ROLE_ADMIN:
        return redirect(url_for('auth.login'))
        
    cur = mysql.connection.cursor()
    
    role_filter = request.args.get('role', 'all')
    status_filter = request.args.get('statut', 'all')
    spe_filter = request.args.get('specialite', 'all')
    search_query = request.args.get('search', '').strip()
    
    personnel_data = _get_personnel_list(cur, role_filter, status_filter, spe_filter, search_query)
    all_personnel = _get_personnel_list(cur)
    
    cur.execute("SELECT COUNT(*) as cnt FROM eleve")
    total_eleves = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(DISTINCT id_eleve) as cnt FROM antecedent_medical WHERE pai_signe = 1 OR severite = 'Critique'")
    eleves_avec_pai = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM consultation")
    total_consultations = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM rdv")
    total_rdv = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM stock_medicament WHERE quantite_stock <= seuil_alerte")
    stocks_critiques = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM specialite")
    nb_specialites = cur.fetchone()['cnt']
    
    cur.close()

    total_personnel = len(all_personnel)
    total_actifs = sum(1 for p in all_personnel if p['statut'] == 'Actif')
    taux_activation = round((total_actifs / total_personnel * 100), 1) if total_personnel > 0 else 0

    kpis_data = {
        'total_personnel': total_personnel,
        'total_medecins': sum(1 for p in all_personnel if p['raw_type'] == 'medecin'),
        'total_infirmiers': sum(1 for p in all_personnel if p['raw_type'] == 'infirmier'),
        'taux_activation': taux_activation,
        'nb_specialites': nb_specialites,
        'total_eleves': total_eleves,
        'eleves_avec_pai': eleves_avec_pai,
        'total_consultations': total_consultations,
        'total_rdv': total_rdv,
        'stocks_critiques': stocks_critiques
    }

    log_audit("EXPORT_DONNEES", f"Export au format {export_type.upper()} ({len(personnel_data)} enregistrements)")

    if export_type == 'csv':
        return export_personnel_csv(personnel_data)
    elif export_type == 'excel':
        return export_personnel_excel(personnel_data, kpis_data)
    elif export_type == 'pdf':
        dummy_alerts = [
            {'type': 'Information', 'titre': 'Sécurité 48h', 'message': f"Taux d'onboarding actif à {taux_activation}%"},
            {'type': 'Pharmacie', 'titre': 'Stock d\'urgence', 'message': f"{stocks_critiques} médicament(s) sous le seuil d'alerte"}
        ]
        return export_pilotage_pdf(personnel_data, kpis_data, dummy_alerts)
    else:
        flash("Format d'exportation non supporté.", "danger")
        return redirect(url_for('admin.panel'))

# --- ACTIONS CRUD PERSONNEL & SÉCURITÉ ---

@admin_bp.route('/admin/ajouter_personnel', methods=['POST'])
def ajouter_personnel():
    if session.get('user_role') != ROLE_ADMIN:
        return redirect(url_for('auth.login'))
        
    type_perso = request.form.get('type_personnel') or request.form.get('type', 'medecin')
    prenom = request.form.get('prenom', '').strip()
    nom = request.form.get('nom', '').strip()
    id_specialite = request.form.get('id_specialite') or None
    email = request.form.get('email', '').strip().lower()

    if not email:
        clean_prenom = _normalize_name(prenom).lower()
        clean_nom = _normalize_name(nom).lower()
        prefix = "dr" if type_perso == "medecin" else "inf"
        email = f"{prefix}.{clean_prenom}.{clean_nom}@santescolaire.ma"

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
    expires_at = datetime.now() + timedelta(hours=48)
    placeholder_pw = f"unactivated:{secrets.token_hex(16)}"
    
    cur = mysql.connection.cursor()
    try:
        for t in ['admin', 'medecin', 'infirmier']:
            cur.execute(f"SELECT email FROM {t} WHERE LOWER(email) = %s", (email,))
            if cur.fetchone():
                flash(f"L'adresse email {email} est déjà utilisée.", "danger")
                return redirect(url_for('admin.panel'))

        if type_perso == 'medecin':
            nom_spe = ""
            if id_specialite:
                cur.execute("SELECT nom_specialite FROM specialite WHERE id_specialite = %s", [id_specialite])
                row_spe = cur.fetchone()
                if row_spe:
                    nom_spe = row_spe['nom_specialite']

            cur.execute(
                """INSERT INTO medecin 
                   (nom_medecin, prenom_medecin, email, id_specialite, specialite, password_hash, must_change_password, activation_token_hash, activation_expires_at) 
                   VALUES (%s, %s, %s, %s, %s, %s, 0, %s, %s)""",
                (nom, prenom, email, id_specialite, nom_spe, placeholder_pw, token_hash, expires_at),
            )
        else:
            cur.execute(
                """INSERT INTO infirmier 
                   (nom_infirmier, prenom_infirmier, email, password_hash, must_change_password, activation_token_hash, activation_expires_at) 
                   VALUES (%s, %s, %s, %s, 0, %s, %s)""",
                (nom, prenom, email, placeholder_pw, token_hash, expires_at),
            )
        
        mysql.connection.commit()
        log_audit("INVITATION_PERSONNEL", f"Création et envoi de lien d'activation (48h) pour {prenom} {nom} ({email})")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Impossible d'ajouter ce membre du personnel : {str(e)}", "danger")
        return redirect(url_for('admin.panel'))
    finally:
        cur.close()

    activation_link = url_for('auth.activate_account', token=raw_token, _external=True)

    try:
        send_activation_email(email, f"{prenom} {nom}", activation_link, type_perso)
    except Exception as e:
        print(f"Erreur envoi email: {e}")

    flash(f"Invitation envoyée avec succès à {prenom} {nom} ({email}) ! Un email d'activation lui a été envoyé.", "success")
    flash(f"Lien d'activation de secours (valable 48h) : {activation_link}", "info")
    return redirect(request.referrer or url_for('admin.liste_personnel'))

@admin_bp.route('/admin/renvoyer_activation/<type_perso>/<int:id_perso>', methods=['POST'])
def renvoyer_activation(type_perso, id_perso):
    if session.get('user_role') != ROLE_ADMIN:
        return redirect(url_for('auth.login'))

    cur = mysql.connection.cursor()
    try:
        if type_perso == 'medecin':
            cur.execute("SELECT nom_medecin as nom, prenom_medecin as prenom, email FROM medecin WHERE id_medecin = %s", [id_perso])
        else:
            cur.execute("SELECT nom_infirmier as nom, prenom_infirmier as prenom, email FROM infirmier WHERE id_infirmier = %s", [id_perso])
        user = cur.fetchone()

        if not user:
            flash("Praticien introuvable.", "danger")
            return redirect(request.referrer or url_for('admin.liste_personnel'))

        email = user['email']
        full_name = f"{user.get('prenom', '')} {user.get('nom', '')}".strip()

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
        expires_at = datetime.now() + timedelta(hours=48)

        table = 'medecin' if type_perso == 'medecin' else 'infirmier'
        id_col = 'id_medecin' if type_perso == 'medecin' else 'id_infirmier'

        cur.execute(
            f"UPDATE {table} SET activation_token_hash = %s, activation_expires_at = %s, must_change_password = 0 WHERE {id_col} = %s",
            [token_hash, expires_at, id_perso]
        )
        mysql.connection.commit()

        activation_link = url_for('auth.activate_account', token=raw_token, _external=True)

        try:
            send_activation_email(email, full_name, activation_link, type_perso)
        except Exception as e:
            print(f"Erreur envoi email: {e}")

        log_audit("RELANCE_INVITATION", f"Renvoi de l'invitation d'activation (48h) pour {full_name} ({email})")
        flash(f"Nouvelle invitation d'activation envoyée avec succès à {full_name} ({email}) !", "success")
        flash(f"Lien d'activation (valable 48h) : {activation_link}", "info")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Erreur lors du renvoi de l'invitation : {e}", "danger")
    finally:
        cur.close()

    return redirect(request.referrer or url_for('admin.liste_personnel'))

@admin_bp.route('/admin/supprimer_personnel/<type_perso>/<int:id_perso>', methods=['POST'])
def supprimer_personnel(type_perso, id_perso):
    if session.get('user_role') != ROLE_ADMIN:
        return redirect(url_for('auth.login'))
        
    cur = mysql.connection.cursor()
    try:
        if type_perso == 'medecin':
            cur.execute("SELECT nom_medecin, prenom_medecin FROM medecin WHERE id_medecin = %s", [id_perso])
            m = cur.fetchone()
            cur.execute("DELETE FROM medecin WHERE id_medecin = %s", [id_perso])
            label = f"Dr. {m['prenom_medecin']} {m['nom_medecin']}" if m else f"Médecin #{id_perso}"
        elif type_perso == 'infirmier':
            cur.execute("SELECT nom_infirmier, prenom_infirmier FROM infirmier WHERE id_infirmier = %s", [id_perso])
            inf = cur.fetchone()
            cur.execute("DELETE FROM infirmier WHERE id_infirmier = %s", [id_perso])
            label = f"{inf['prenom_infirmier']} {inf['nom_infirmier']}" if inf else f"Infirmier #{id_perso}"
        
        mysql.connection.commit()
        log_audit("SUPPRESSION_PERSONNEL", f"Suppression du membre : {label}")
        flash("Membre du personnel supprimé avec succès.", "success")
    except Exception:
        mysql.connection.rollback()
        flash("Impossible de supprimer ce membre : il est rattaché à des consultations ou des rendez-vous existants.", "danger")
    finally:
        cur.close()
        
    return redirect(url_for('admin.panel'))

@admin_bp.route('/admin/modifier_personnel', methods=['POST'])
def modifier_personnel():
    if session.get('user_role') != ROLE_ADMIN:
        return redirect(url_for('auth.login'))
        
    id_perso = request.form['id']
    type_perso = request.form['type']
    prenom = request.form.get('prenom', '').strip()
    nom = request.form.get('nom', '').strip()
    email = request.form.get('email', '').strip().lower()
    id_specialite = request.form.get('id_specialite') or None
    password = request.form.get('password', '').strip()
    
    cur = mysql.connection.cursor()
    try:
        if type_perso == 'medecin':
            nom_spe = ""
            if id_specialite:
                cur.execute("SELECT nom_specialite FROM specialite WHERE id_specialite = %s", [id_specialite])
                row_spe = cur.fetchone()
                if row_spe:
                    nom_spe = row_spe['nom_specialite']

            cur.execute(
                "UPDATE medecin SET nom_medecin = %s, prenom_medecin = %s, email = %s, id_specialite = %s, specialite = %s WHERE id_medecin = %s",
                (nom, prenom, email, id_specialite, nom_spe, id_perso),
            )
            if password:
                cur.execute(
                    "UPDATE medecin SET password_hash = %s, must_change_password = 0, activation_token_hash = NULL WHERE id_medecin = %s",
                    (generate_password_hash(password), id_perso),
                )
        elif type_perso == 'infirmier':
            cur.execute(
                "UPDATE infirmier SET nom_infirmier = %s, prenom_infirmier = %s, email = %s WHERE id_infirmier = %s",
                (nom, prenom, email, id_perso),
            )
            if password:
                cur.execute(
                    "UPDATE infirmier SET password_hash = %s, must_change_password = 0, activation_token_hash = NULL WHERE id_infirmier = %s",
                    (generate_password_hash(password), id_perso),
                )
        mysql.connection.commit()
        log_audit("MODIFICATION_PERSONNEL", f"Mise à jour des informations pour {prenom} {nom} ({type_perso})")
        flash("Informations du personnel mises à jour avec succès.", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Erreur lors de la modification : {str(e)}", "danger")
    finally:
        cur.close()
        
    return redirect(url_for('admin.panel'))

# --- CRUD SPÉCIALITÉS MÉDICALES ---

@admin_bp.route('/admin/specialite/ajouter', methods=['POST'])
def ajouter_specialite():
    if session.get('user_role') != ROLE_ADMIN:
        return redirect(url_for('auth.login'))

    nom = request.form.get('nom_specialite', '').strip()
    code = request.form.get('code_specialite', '').strip().upper()
    description = request.form.get('description', '').strip()

    if not nom:
        flash("Le nom de la spécialité est obligatoire.", "warning")
        return redirect(url_for('admin.panel'))

    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT id_specialite FROM specialite WHERE LOWER(nom_specialite) = LOWER(%s)", (nom,))
        if cur.fetchone():
            flash(f"La spécialité « {nom} » existe déjà.", "danger")
            return redirect(url_for('admin.panel'))

        cur.execute(
            "INSERT INTO specialite (nom_specialite, code_specialite, description) VALUES (%s, %s, %s)",
            (nom, code or nom[:4].upper(), description)
        )
        mysql.connection.commit()
        log_audit("CREATION_SPECIALITE", f"Création de la spécialité « {nom} » (Code: {code})")
        flash(f"Spécialité « {nom} » créée avec succès.", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Erreur lors de la création de la spécialité : {str(e)}", "danger")
    finally:
        cur.close()

    return redirect(url_for('admin.panel'))

@admin_bp.route('/admin/specialite/modifier', methods=['POST'])
def modifier_specialite():
    if session.get('user_role') != ROLE_ADMIN:
        return redirect(url_for('auth.login'))

    id_spe = request.form.get('id_specialite')
    nom = request.form.get('nom_specialite', '').strip()
    code = request.form.get('code_specialite', '').strip().upper()
    description = request.form.get('description', '').strip()

    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "UPDATE specialite SET nom_specialite = %s, code_specialite = %s, description = %s WHERE id_specialite = %s",
            (nom, code, description, id_spe)
        )
        cur.execute("UPDATE medecin SET specialite = %s WHERE id_specialite = %s", (nom, id_spe))
        mysql.connection.commit()
        log_audit("MODIFICATION_SPECIALITE", f"Mise à jour de la spécialité « {nom} »")
        flash(f"Spécialité « {nom} » mise à jour avec succès.", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Erreur lors de la modification : {str(e)}", "danger")
    finally:
        cur.close()

    return redirect(url_for('admin.panel'))

@admin_bp.route('/admin/specialite/supprimer/<int:id_specialite>', methods=['POST'])
def supprimer_specialite(id_specialite):
    if session.get('user_role') != ROLE_ADMIN:
        return redirect(url_for('auth.login'))

    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT nom_specialite FROM specialite WHERE id_specialite = %s", [id_specialite])
        spe_row = cur.fetchone()
        spe_nom = spe_row['nom_specialite'] if spe_row else f"#{id_specialite}"

        cur.execute("SELECT COUNT(*) as cnt FROM medecin WHERE id_specialite = %s", [id_specialite])
        cnt = cur.fetchone()['cnt']
        if cnt > 0:
            flash(f"Suppression impossible : {cnt} médecin(s) sont actuellement rattachés à cette spécialité.", "danger")
            return redirect(url_for('admin.panel'))

        cur.execute("DELETE FROM specialite WHERE id_specialite = %s", [id_specialite])
        mysql.connection.commit()
        log_audit("SUPPRESSION_SPECIALITE", f"Suppression de la spécialité « {spe_nom} »")
        flash("Spécialité supprimée avec succès.", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Erreur lors de la suppression : {str(e)}", "danger")
    finally:
        cur.close()

    return redirect(url_for('admin.panel'))

# --- VUES DÉTAILLÉES (PAGES DÉTAILS DÉDIÉES) ---

@admin_bp.route('/admin/personnel/<type_perso>/<int:id_perso>')
def personnel_detail(type_perso, id_perso):
    if not session.get('logged_in') or session.get('user_role') != ROLE_ADMIN:
        flash("Accès réservé aux administrateurs.", "danger")
        return redirect(url_for('auth.login'))

    if type_perso not in ['medecin', 'infirmier']:
        flash("Type de personnel invalide.", "danger")
        return redirect(url_for('admin.panel'))

    cur = mysql.connection.cursor()
    now = datetime.now()

    if type_perso == 'medecin':
        cur.execute("""
            SELECT m.*, s.nom_specialite, s.code_specialite 
            FROM medecin m
            LEFT JOIN specialite s ON m.id_specialite = s.id_specialite
            WHERE m.id_medecin = %s
        """, (id_perso,))
        row = cur.fetchone()
        if not row:
            cur.close()
            flash("Médecin introuvable.", "warning")
            return redirect(url_for('admin.panel'))

        statut = 'Actif' if not row.get('activation_token_hash') else ('Expiré' if row.get('activation_expires_at') and row['activation_expires_at'] < now else 'En attente')
        membre = {
            'id': row['id_medecin'],
            'type': 'Médecin',
            'raw_type': 'medecin',
            'nom': row['nom_medecin'],
            'prenom': row['prenom_medecin'],
            'email': row['email'],
            'specialite': row.get('nom_specialite') or row.get('specialite') or 'Généraliste',
            'id_specialite': row.get('id_specialite'),
            'statut': statut,
            'must_change_password': row.get('must_change_password', 0),
            'token_hash': row.get('activation_token_hash'),
            'date_expiration': row['activation_expires_at'].strftime('%d/%m/%Y %H:%M') if row.get('activation_expires_at') else '-'
        }

        # Consultations de ce médecin
        cur.execute("""
            SELECT c.*, e.nom_eleve, e.prenom_eleve
            FROM consultation c
            JOIN eleve e ON c.id_eleve = e.id_eleve
            WHERE c.id_medecin = %s
            ORDER BY c.date_consult DESC LIMIT 10
        """, (id_perso,))
        consultations = cur.fetchall()

        # Rendez-vous de ce médecin
        cur.execute("""
            SELECT r.*, e.nom_eleve, e.prenom_eleve
            FROM rdv r
            JOIN eleve e ON r.id_eleve = e.id_eleve
            WHERE r.id_medecin = %s
            ORDER BY r.date_rdv DESC LIMIT 10
        """, (id_perso,))
        rdvs = cur.fetchall()

    else:
        cur.execute("SELECT * FROM infirmier WHERE id_infirmier = %s", (id_perso,))
        row = cur.fetchone()
        if not row:
            cur.close()
            flash("Infirmier introuvable.", "warning")
            return redirect(url_for('admin.panel'))

        statut = 'Actif' if not row.get('activation_token_hash') else ('Expiré' if row.get('activation_expires_at') and row['activation_expires_at'] < now else 'En attente')
        membre = {
            'id': row['id_infirmier'],
            'type': 'Infirmier',
            'raw_type': 'infirmier',
            'nom': row['nom_infirmier'],
            'prenom': row['prenom_infirmier'],
            'email': row['email'],
            'specialite': 'Soins infirmiers',
            'id_specialite': None,
            'statut': statut,
            'must_change_password': row.get('must_change_password', 0),
            'token_hash': row.get('activation_token_hash'),
            'date_expiration': row['activation_expires_at'].strftime('%d/%m/%Y %H:%M') if row.get('activation_expires_at') else '-'
        }

        # Consultations assistées
        cur.execute("""
            SELECT c.*, e.nom_eleve, e.prenom_eleve
            FROM consultation c
            JOIN eleve e ON c.id_eleve = e.id_eleve
            WHERE c.id_infirmier = %s
            ORDER BY c.date_consult DESC LIMIT 10
        """, (id_perso,))
        consultations = cur.fetchall()
        rdvs = []

    # Récupération des spécialités pour le formulaire de modification
    cur.execute("SELECT id_specialite, nom_specialite FROM specialite ORDER BY nom_specialite ASC")
    specialites = cur.fetchall()

    # Logs d'audit relatifs à ce membre
    cur.execute("""
        SELECT * FROM audit_log 
        WHERE (user_type = %s AND user_id = %s) 
           OR details LIKE %s
        ORDER BY created_at DESC LIMIT 5
    """, (type_perso.upper(), id_perso, f"%{membre['nom']}%"))
    logs = cur.fetchall()

    cur.close()

    activation_link = None
    if membre['token_hash']:
        # Lien théorique informatif
        activation_link = url_for('auth.activate_account', token='[TOKEN_GENERE_LORS_DE_L_INVITATION]', _external=True)

    return render_template(
        'admin_personnel_detail.html',
        membre=membre,
        consultations=consultations,
        rdvs=rdvs,
        specialites=specialites,
        logs=logs,
        activation_link=activation_link
    )

@admin_bp.route('/admin/specialite/<int:id_spe>')
def specialite_detail(id_spe):
    if not session.get('logged_in') or session.get('user_role') != ROLE_ADMIN:
        flash("Accès réservé aux administrateurs.", "danger")
        return redirect(url_for('auth.login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM specialite WHERE id_specialite = %s", (id_spe,))
    specialite = cur.fetchone()
    if not specialite:
        cur.close()
        flash("Spécialité introuvable.", "warning")
        return redirect(url_for('admin.panel'))

    # Médecins rattachés à cette spécialité
    cur.execute("""
        SELECT * FROM medecin 
        WHERE id_specialite = %s 
        ORDER BY nom_medecin ASC
    """, (id_spe,))
    medecins = cur.fetchall()
    cur.close()

    return render_template(
        'admin_specialite_detail.html',
        specialite=specialite,
        medecins=medecins,
        now=datetime.now()
    )


# ==========================================================
# ROUTES DES PAGES DÉDIÉES (STYLE GTM / WORKSTATION HOSPITAL)
# ==========================================================

@admin_bp.route('/admin/personnel')
def liste_personnel():
    if not session.get('logged_in') or session.get('user_role') != ROLE_ADMIN:
        flash("Accès réservé aux administrateurs.", "danger")
        return redirect(url_for('auth.login'))
    
    cur = mysql.connection.cursor()
    role_filter = request.args.get('role', 'all')
    status_filter = request.args.get('statut', 'all')
    spe_filter = request.args.get('specialite', 'all')
    search_query = request.args.get('search', '').strip()
    
    personnel = _get_personnel_list(cur, role_filter, status_filter, spe_filter, search_query)
    all_personnel = _get_personnel_list(cur)
    
    cur.execute('SELECT * FROM specialite ORDER BY nom_specialite ASC')
    specialites = cur.fetchall()
    
    total_medecins = sum(1 for p in all_personnel if p['raw_type'] == 'medecin')
    total_infirmiers = sum(1 for p in all_personnel if p['raw_type'] == 'infirmier')
    total_actifs = sum(1 for p in all_personnel if p['statut'] == 'Actif')
    total_en_attente = sum(1 for p in all_personnel if p['statut'] == 'En attente')
    total_expires = sum(1 for p in all_personnel if p['statut'] == 'Expiré')
    cur.close()
    
    return render_template(
        'admin_personnel_liste.html',
        personnel=personnel,
        specialites=specialites,
        total_medecins=total_medecins,
        total_infirmiers=total_infirmiers,
        total_actifs=total_actifs,
        total_en_attente=total_en_attente,
        total_expires=total_expires,
        role_filter=role_filter,
        status_filter=status_filter,
        spe_filter=spe_filter,
        search_query=search_query
    )


@admin_bp.route('/admin/specialites')
def liste_specialites():
    if not session.get('logged_in') or session.get('user_role') != ROLE_ADMIN:
        flash("Accès réservé aux administrateurs.", "danger")
        return redirect(url_for('auth.login'))
    
    cur = mysql.connection.cursor()
    search_q = request.args.get('search', '').strip()
    cur.execute("""
        SELECT s.*, COUNT(m.id_medecin) as nb_medecins
        FROM specialite s 
        LEFT JOIN medecin m ON s.id_specialite = m.id_specialite
        GROUP BY s.id_specialite 
        ORDER BY s.nom_specialite ASC
    """)
    specialites_raw = cur.fetchall()
    
    if search_q:
        specialites = [
            s for s in specialites_raw 
            if search_q.lower() in s['nom_specialite'].lower() or 
               search_q.lower() in (s.get('code_specialite', '') or '').lower()
        ]
    else:
        specialites = specialites_raw
        
    total_avec_medecins = sum(1 for s in specialites_raw if s['nb_medecins'] > 0)
    total_sans_medecins = sum(1 for s in specialites_raw if s['nb_medecins'] == 0)
    
    cur.execute('SELECT id_medecin, nom_medecin, prenom_medecin FROM medecin ORDER BY nom_medecin ASC')
    tous_medecins = cur.fetchall()
    cur.close()
    
    return render_template(
        'admin_specialites_liste.html',
        specialites=specialites,
        search_q=search_q,
        total_avec_medecins=total_avec_medecins,
        total_sans_medecins=total_sans_medecins,
        tous_medecins=tous_medecins
    )


@admin_bp.route('/admin/eleves')
def liste_eleves():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
    flash("Accès restreint : Conformément au secret médical et au RGPD, les dossiers nominatifs des élèves sont strictement réservés à l'équipe soignante (médecins & infirmiers).", "warning")
    return redirect(url_for('admin.panel'))
    search_q = request.args.get('search', '').strip()
    classe_filter = request.args.get('classe', '')
    
    query = '''
        SELECT e.*,
               COUNT(DISTINCT c.id_consult) as nb_consultations,
               COUNT(DISTINCT a.id_antecedent) as nb_antecedents,
               MAX(CASE WHEN a.pai_signe=1 OR a.severite='Critique' THEN 1 ELSE 0 END) as a_pai
        FROM eleve e
        LEFT JOIN consultation c ON e.id_eleve = c.id_eleve
        LEFT JOIN antecedent_medical a ON e.id_eleve = a.id_eleve
    '''
    filters = []
    params = []
    if search_q:
        filters.append('(e.nom_eleve LIKE %s OR e.prenom_eleve LIKE %s OR e.classe LIKE %s)')
        params += [f'%{search_q}%', f'%{search_q}%', f'%{search_q}%']
    if classe_filter:
        filters.append('e.classe = %s')
        params.append(classe_filter)
    if filters:
        query += ' WHERE ' + ' AND '.join(filters)
    query += ' GROUP BY e.id_eleve ORDER BY e.nom_eleve ASC'
    
    cur.execute(query, params)
    eleves = cur.fetchall()
    
    cur.execute('SELECT COUNT(*) as cnt FROM eleve')
    total_eleves = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(DISTINCT id_eleve) as cnt FROM antecedent_medical WHERE pai_signe=1 OR severite='Critique'")
    eleves_pai = cur.fetchone()['cnt']
    cur.execute('SELECT DISTINCT classe FROM eleve WHERE classe IS NOT NULL ORDER BY classe ASC')
    classes = [r['classe'] for r in cur.fetchall()]
    cur.close()
    
    return render_template(
        'admin_eleves_liste.html',
        eleves=eleves,
        classes=classes,
        search_q=search_q,
        classe_filter=classe_filter,
        total_eleves=total_eleves,
        eleves_pai=eleves_pai
    )


@admin_bp.route('/admin/consultations')
def liste_consultations():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
    flash("Accès restreint : Conformément au secret médical, les actes cliniques et consultations sont strictement réservés à l'équipe soignante (médecins & infirmiers).", "warning")
    return redirect(url_for('admin.panel'))
    search_q = request.args.get('search', '').strip()
    date_filter = request.args.get('date_filter', '')
    medecin_filter = request.args.get('medecin', '')
    
    query = '''
        SELECT c.*, 
               e.nom_eleve, e.prenom_eleve, e.classe,
               CONCAT(m.prenom_medecin, ' ', m.nom_medecin) as nom_medecin
        FROM consultation c
        LEFT JOIN eleve e ON c.id_eleve = e.id_eleve
        LEFT JOIN medecin m ON c.id_medecin = m.id_medecin
    '''
    filters = []
    params = []
    if search_q:
        filters.append('(e.nom_eleve LIKE %s OR e.prenom_eleve LIKE %s OR c.motif LIKE %s)')
        params += [f'%{search_q}%', f'%{search_q}%', f'%{search_q}%']
    if date_filter == 'today':
        filters.append('DATE(c.date_consult) = CURDATE()')
    elif date_filter == 'week':
        filters.append('YEARWEEK(c.date_consult, 1) = YEARWEEK(CURDATE(), 1)')
    elif date_filter == 'month':
        filters.append('MONTH(c.date_consult) = MONTH(CURDATE()) AND YEAR(c.date_consult) = YEAR(CURDATE())')
    if medecin_filter:
        filters.append('c.id_medecin = %s')
        params.append(medecin_filter)
    if filters:
        query += ' WHERE ' + ' AND '.join(filters)
    query += ' ORDER BY c.date_consult DESC LIMIT 150'
    
    cur.execute(query, params)
    consultations = cur.fetchall()
    
    cur.execute('SELECT COUNT(*) as cnt FROM consultation')
    total_consultations = cur.fetchone()['cnt']
    cur.execute('SELECT COUNT(*) as cnt FROM consultation WHERE DATE(date_consult) = CURDATE()')
    consultations_aujourd_hui = cur.fetchone()['cnt']
    cur.execute('SELECT COUNT(*) as cnt FROM consultation WHERE MONTH(date_consult) = MONTH(CURDATE()) AND YEAR(date_consult) = YEAR(CURDATE())')
    consultations_mois = cur.fetchone()['cnt']
    cur.execute('SELECT id_medecin, CONCAT(prenom_medecin, " ", nom_medecin) as nom FROM medecin ORDER BY nom_medecin ASC')
    medecins = cur.fetchall()
    cur.close()
    
    return render_template(
        'admin_consultations_liste.html',
        consultations=consultations,
        medecins=medecins,
        total_consultations=total_consultations,
        consultations_aujourd_hui=consultations_aujourd_hui,
        consultations_mois=consultations_mois,
        search_q=search_q,
        date_filter=date_filter,
        medecin_filter=medecin_filter
    )


@admin_bp.route('/admin/pharmacie')
def pharmacie():
    if not session.get('logged_in') or session.get('user_role') != ROLE_ADMIN:
        flash("Accès réservé aux administrateurs.", "danger")
        return redirect(url_for('auth.login'))
    
    cur = mysql.connection.cursor()
    search_q = request.args.get('search', '').strip()
    statut_filter = request.args.get('statut', '')
    
    query = 'SELECT * FROM stock_medicament'
    filters = []
    params = []
    if search_q:
        filters.append('nom_medicament LIKE %s')
        params.append(f'%{search_q}%')
    if statut_filter == 'critique':
        filters.append('quantite_stock <= seuil_alerte')
    elif statut_filter == 'ok':
        filters.append('quantite_stock > seuil_alerte')
    if filters:
        query += ' WHERE ' + ' AND '.join(filters)
    query += ' ORDER BY quantite_stock ASC'
    
    cur.execute(query, params)
    stocks = cur.fetchall()
    
    cur.execute('SELECT COUNT(*) as cnt FROM stock_medicament')
    total_medicaments = cur.fetchone()['cnt']
    cur.execute('SELECT COUNT(*) as cnt FROM stock_medicament WHERE quantite_stock <= seuil_alerte')
    nb_critiques = cur.fetchone()['cnt']
    cur.execute('SELECT COUNT(*) as cnt FROM stock_medicament WHERE quantite_stock > seuil_alerte')
    nb_ok = cur.fetchone()['cnt']
    cur.execute('SELECT SUM(quantite_stock) as total FROM stock_medicament')
    total_unites = cur.fetchone()['total'] or 0
    cur.close()
    
    return render_template(
        'admin_pharmacie.html',
        stocks=stocks,
        search_q=search_q,
        statut_filter=statut_filter,
        total_medicaments=total_medicaments,
        nb_critiques=nb_critiques,
        nb_ok=nb_ok,
        total_unites=int(total_unites)
    )


@admin_bp.route('/admin/rdv')
def liste_rdv():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
    flash("Accès restreint : Conformément au secret médical, les rendez-vous nominatifs des élèves sont strictement réservés à l'équipe soignante (médecins & infirmiers).", "warning")
    return redirect(url_for('admin.panel'))
    statut_filter = request.args.get('statut', '')
    date_filter = request.args.get('date_filter', '')
    medecin_filter = request.args.get('medecin', '')
    search_q = request.args.get('search', '').strip()
    
    query = '''
        SELECT r.*,
               e.nom_eleve, e.prenom_eleve, e.classe,
               CONCAT(m.prenom_medecin, ' ', m.nom_medecin) as nom_medecin
        FROM rdv r
        LEFT JOIN eleve e ON r.id_eleve = e.id_eleve
        LEFT JOIN medecin m ON r.id_medecin = m.id_medecin
    '''
    filters = []
    params = []
    if statut_filter:
        filters.append('r.statut = %s')
        params.append(statut_filter)
    if date_filter == 'today':
        filters.append('DATE(r.date_rdv) = CURDATE()')
    elif date_filter == 'week':
        filters.append('YEARWEEK(r.date_rdv, 1) = YEARWEEK(CURDATE(), 1)')
    elif date_filter == 'upcoming':
        filters.append('r.date_rdv >= NOW()')
    if medecin_filter:
        filters.append('r.id_medecin = %s')
        params.append(medecin_filter)
    if search_q:
        filters.append('(e.nom_eleve LIKE %s OR e.prenom_eleve LIKE %s)')
        params += [f'%{search_q}%', f'%{search_q}%']
    if filters:
        query += ' WHERE ' + ' AND '.join(filters)
    query += ' ORDER BY r.date_rdv DESC LIMIT 150'
    
    cur.execute(query, params)
    rdvs = cur.fetchall()
    
    cur.execute('SELECT COUNT(*) as cnt FROM rdv')
    total_rdv = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM rdv WHERE statut = 'programmé' AND date_rdv >= NOW()")
    rdv_a_venir = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM rdv WHERE DATE(date_rdv) = CURDATE()")
    rdv_aujourd_hui = cur.fetchone()['cnt']
    cur.execute('SELECT id_medecin, CONCAT(prenom_medecin, " ", nom_medecin) as nom FROM medecin ORDER BY nom_medecin ASC')
    medecins = cur.fetchall()
    cur.close()
    
    return render_template(
        'admin_rdv_liste.html',
        rdvs=rdvs,
        medecins=medecins,
        total_rdv=total_rdv,
        rdv_a_venir=rdv_a_venir,
        rdv_aujourd_hui=rdv_aujourd_hui,
        statut_filter=statut_filter,
        date_filter=date_filter,
        medecin_filter=medecin_filter,
        search_q=search_q
    )


@admin_bp.route('/admin/audit')
def journal_audit():
    if not session.get('logged_in') or session.get('user_role') != ROLE_ADMIN:
        flash("Accès réservé aux administrateurs.", "danger")
        return redirect(url_for('auth.login'))
    
    cur = mysql.connection.cursor()
    action_filter = request.args.get('action', '')
    user_type_filter = request.args.get('user_type', '')
    date_filter = request.args.get('date_filter', '')
    
    query = 'SELECT * FROM audit_log'
    filters = []
    params = []
    if action_filter:
        filters.append('action LIKE %s')
        params.append(f'%{action_filter}%')
    if user_type_filter:
        filters.append('user_type = %s')
        params.append(user_type_filter)
    if date_filter == 'today':
        filters.append('DATE(created_at) = CURDATE()')
    elif date_filter == 'week':
        filters.append('YEARWEEK(created_at, 1) = YEARWEEK(CURDATE(), 1)')
    if filters:
        query += ' WHERE ' + ' AND '.join(filters)
    query += ' ORDER BY created_at DESC LIMIT 200'
    
    cur.execute(query, params)
    logs = cur.fetchall()
    
    cur.execute('SELECT COUNT(*) as cnt FROM audit_log')
    total_logs = cur.fetchone()['cnt']
    cur.execute('SELECT COUNT(*) as cnt FROM audit_log WHERE DATE(created_at) = CURDATE()')
    logs_aujourd_hui = cur.fetchone()['cnt']
    cur.execute('SELECT DISTINCT action FROM audit_log ORDER BY action ASC')
    actions_types = [r['action'] for r in cur.fetchall()]
    cur.close()
    
    return render_template(
        'admin_audit.html',
        logs=logs,
        actions_types=actions_types,
        total_logs=total_logs,
        logs_aujourd_hui=logs_aujourd_hui,
        action_filter=action_filter,
        user_type_filter=user_type_filter,
        date_filter=date_filter
    )
