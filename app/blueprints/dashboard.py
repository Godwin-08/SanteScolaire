from flask import Blueprint, render_template, redirect, session, url_for, request, flash

from app.constants import (
    RDV_STATUT_ANNULE,
    RDV_STATUT_FAIT,
    RDV_STATUT_PROGRAMME,
    ROLE_ADMIN,
    ROLE_INFIRMIER,
    ROLE_MEDECIN,
)
from app.db import mysql
from app.decorators import login_required

dashboard_bp = Blueprint('dashboard', __name__)

# Page de statistiques
@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()

    role = session.get('user_role')
    user_id = session.get('user_id')

    # --- 0. KPIs (Indicateurs Clés de Performance) ---
    if role == ROLE_MEDECIN:
        # VUE MÉDECIN : On filtre les stats pour ce médecin uniquement
        
        # Nombre de patients distincts consultés
        cur.execute("SELECT COUNT(DISTINCT id_eleve) as total FROM consultation WHERE id_medecin = %s", [user_id])
        nb_eleves = cur.fetchone()['total']

        # Nombre total de consultations réalisées
        cur.execute("SELECT COUNT(*) as total FROM consultation WHERE id_medecin = %s", [user_id])
        nb_consultations = cur.fetchone()['total']
    else:
        # VUE ADMIN & INFIRMIER : Vision globale de l'établissement
        
        # Total des élèves enregistrés
        cur.execute("SELECT COUNT(*) as total FROM eleve")
        nb_eleves = cur.fetchone()['total']

        cur.execute("SELECT COUNT(*) as total FROM consultation")
        nb_consultations = cur.fetchone()['total']

    # --- 1. Agenda (Rendez-vous à venir) ---
    rdvs = []
    if role == ROLE_MEDECIN:
        # Le médecin ne voit que ses propres RDV futurs
        cur.execute("""
            SELECT r.*, e.nom_eleve, e.prenom_eleve, m.nom_medecin
            FROM rdv r 
            JOIN eleve e ON r.id_eleve = e.id_eleve 
            LEFT JOIN medecin m ON r.id_medecin = m.id_medecin
            WHERE r.date_rdv >= NOW() AND r.id_medecin = %s AND (r.statut = %s OR r.statut IS NULL)
            ORDER BY r.date_rdv ASC 
            LIMIT 5
        """, [user_id, RDV_STATUT_PROGRAMME])
        rdvs = cur.fetchall()
    elif role == ROLE_INFIRMIER:
        # L'infirmier voit tous les RDV pour gérer le flux
        cur.execute("""
            SELECT r.*, e.nom_eleve, e.prenom_eleve, m.nom_medecin
            FROM rdv r 
            JOIN eleve e ON r.id_eleve = e.id_eleve 
            LEFT JOIN medecin m ON r.id_medecin = m.id_medecin
            WHERE r.date_rdv >= NOW() AND (r.statut = %s OR r.statut IS NULL)
            ORDER BY r.date_rdv ASC 
            LIMIT 5
        """, [RDV_STATUT_PROGRAMME])
        rdvs = cur.fetchall()
    # L'Admin (else) n'a pas accès à la liste des RDV (rdvs reste vide)

    # --- 2. Préparation des données pour le Graphique Circulaire (Camembert) ---
    pie_labels = []
    pie_values = []
    pie_title = ""
    pie_subtitle = ""
    pie_info = ""

    if role == ROLE_MEDECIN:
        # Analyse des pathologies : Quels sont les motifs récurrents ?
        pie_title = "Motifs de Consultation"
        pie_subtitle = "Pathologies fréquentes"
        cur.execute("SELECT motif, COUNT(*) as total FROM consultation WHERE id_medecin = %s GROUP BY motif ORDER BY total DESC LIMIT 5", [user_id])
        data = cur.fetchall()
        pie_labels = [d['motif'] for d in data]
        pie_values = [d['total'] for d in data]
        if data:
            pie_info = f"Motif principal : <strong class='text-primary'>{data[0]['motif']}</strong> ({data[0]['total']} cas)"
    elif role == ROLE_ADMIN:
        # VUE ADMIN : Analyse RH Répartition de la charge de travail entre médecins
        pie_title = "Répartition par Médecin"
        pie_subtitle = "Volume de consultations traité"
        cur.execute("""
            SELECT m.nom_medecin, COUNT(c.id_consult) as total
            FROM consultation c
            LEFT JOIN medecin m ON c.id_medecin = m.id_medecin
            GROUP BY m.nom_medecin
            ORDER BY total DESC
        """)
        data = cur.fetchall()
        pie_labels = [d['nom_medecin'] if d['nom_medecin'] else 'Non spécifié' for d in data]
        pie_values = [d['total'] for d in data]
        if data:
            pie_info = f"Le plus sollicité : <strong class='text-primary'>Dr. {data[0]['nom_medecin']}</strong> ({data[0]['total']} consults)"

    # --- 3. Préparation des données pour le Graphique en Barres (Activité Hebdo) ---
    bar_title = ""
    bar_subtitle = ""

    if role == ROLE_MEDECIN:
        bar_title = "Mon Activité Récente"
        bar_subtitle = "Mes consultations sur 7 jours"
        cur.execute("""
            SELECT DATE(date_consult) as jour, COUNT(id_consult) as total
            FROM consultation
            WHERE date_consult >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND id_medecin = %s
            GROUP BY DATE(date_consult)
            ORDER BY jour ASC
        """, [user_id])
    else:
        bar_title = "Flux Hebdomadaire"
        bar_subtitle = "Activité globale de l'infirmerie"
        cur.execute("""
            SELECT DATE(date_consult) as jour, COUNT(id_consult) as total
            FROM consultation
            WHERE date_consult >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DATE(date_consult)
            ORDER BY jour ASC
        """)

    stats_jours_data = cur.fetchall()
    jour_labels = [stat['jour'].strftime('%Y-%m-%d') for stat in stats_jours_data]
    jour_values = [stat['total'] for stat in stats_jours_data]
    total_semaine = sum(jour_values)

    cur.close()
    return render_template('dashboard.html', 
                           pie_labels=pie_labels, 
                           pie_values=pie_values,
                           pie_title=pie_title,
                           pie_subtitle=pie_subtitle,
                           pie_info=pie_info,
                           bar_title=bar_title,
                           bar_subtitle=bar_subtitle,
                           jour_labels=jour_labels, 
                           jour_values=jour_values,
                           nb_eleves=nb_eleves,
                           nb_consultations=nb_consultations,
                           total_semaine=total_semaine,
                           rdvs=rdvs)

@dashboard_bp.route('/agenda')
@login_required
def agenda():
    cur = mysql.connection.cursor()
    role = session.get('user_role')
    user_id = session.get('user_id')

    # 1. Récupération des classes pour le filtre
    cur.execute("SELECT DISTINCT classe FROM eleve ORDER BY classe")
    classes_data = cur.fetchall()
    classes = [c['classe'] for c in classes_data if c['classe']]

    # 2. Récupération des filtres
    selected_classe = request.args.get('classe')
    selected_statut = request.args.get('statut')
    selected_date = request.args.get('date_filter')
    
    rdvs = []
    
    # 3. Construction de la requête dynamique
    query = """
        SELECT r.*, e.nom_eleve, e.prenom_eleve, e.classe, m.nom_medecin
        FROM rdv r 
        JOIN eleve e ON r.id_eleve = e.id_eleve 
        LEFT JOIN medecin m ON r.id_medecin = m.id_medecin
        WHERE 1=1
    """
    params = []

    if role == ROLE_MEDECIN:
        query += " AND r.id_medecin = %s"
        params.append(user_id)
    
    if selected_classe:
        query += " AND e.classe = %s"
        params.append(selected_classe)

    if selected_statut:
        if selected_statut == RDV_STATUT_PROGRAMME:
            query += " AND (r.statut = %s OR r.statut IS NULL)"
            params.append(RDV_STATUT_PROGRAMME)
        else:
            query += " AND r.statut = %s"
            params.append(selected_statut)

    # Filtre par Date
    if selected_date == 'today':
        query += " AND DATE(r.date_rdv) = CURDATE()"
    elif selected_date == 'tomorrow':
        query += " AND DATE(r.date_rdv) = DATE_ADD(CURDATE(), INTERVAL 1 DAY)"
    elif selected_date == 'this_week':
        query += " AND YEARWEEK(r.date_rdv, 1) = YEARWEEK(CURDATE(), 1)"
    elif selected_date == 'next_week':
        query += " AND YEARWEEK(r.date_rdv, 1) = YEARWEEK(CURDATE(), 1) + 1"
    elif selected_date == 'history':
        query += " AND r.date_rdv < NOW()"
    elif selected_date == 'future':
        query += " AND r.date_rdv >= NOW()"

    query += " ORDER BY r.date_rdv DESC"
    
    cur.execute(query, params)
    rdvs = cur.fetchall()
    cur.close()
    
    # 4. Calcul des statistiques sur les résultats filtrés
    stats = {
        'total': len(rdvs),
        'programmes': sum(1 for r in rdvs if r['statut'] == RDV_STATUT_PROGRAMME or not r['statut']),
        'faits': sum(1 for r in rdvs if r['statut'] == RDV_STATUT_FAIT),
        'annules': sum(1 for r in rdvs if r['statut'] == RDV_STATUT_ANNULE)
    }
    
    return render_template('agenda.html', rdvs=rdvs, classes=classes, current_classe=selected_classe, current_statut=selected_statut, current_date_filter=selected_date, stats=stats)

@dashboard_bp.route('/agenda/annuler_journee', methods=['POST'])
@login_required
def annuler_journee():
    role = session.get('user_role')
    user_id = session.get('user_id')
    date_annulation = request.form.get('date_annulation')

    if not date_annulation:
        flash("Veuillez sélectionner une date valide.", "warning")
        return redirect(url_for('dashboard.agenda'))

    cur = mysql.connection.cursor()
    
    # On ne touche que les RDV "programmé" ou NULL (pas ceux déjà faits ou annulés)
    query = "UPDATE rdv SET statut = %s WHERE DATE(date_rdv) = %s AND (statut = %s OR statut IS NULL)"
    params = [RDV_STATUT_ANNULE, date_annulation, RDV_STATUT_PROGRAMME]

    if role == ROLE_MEDECIN:
        # Le médecin ne peut annuler que SES rendez-vous
        query += " AND id_medecin = %s"
        params.append(user_id)

    cur.execute(query, params)
    mysql.connection.commit()
    affected = cur.rowcount
    cur.close()

    if affected > 0:
        flash(f"{affected} rendez-vous ont été annulés pour la journée du {date_annulation}.", "success")
    else:
        flash(f"Aucun rendez-vous programmé trouvé pour cette date.", "info")
        
    return redirect(url_for('dashboard.agenda'))
