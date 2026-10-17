from flask import Blueprint, render_template, redirect, session, url_for, request, flash, jsonify
from datetime import datetime, date, timedelta

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
from app.services.stats_service import (
    get_kpi_medecin,
    get_kpi_infirmier,
    get_tendance_mensuelle_consultations,
    get_repartition_pathologies_par_cycle,
)
from app.models import StockMedicament

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()
    role = session.get('user_role')
    user_id = session.get('user_id')

    # ── Variables partagées ─────────────────────────────────────────────────
    pie_labels = []
    pie_values = []
    pie_title = ""
    pie_subtitle = ""
    pie_info = ""
    bar_title = ""
    bar_subtitle = ""
    kpi_medecin = None
    kpi_infirmier = None
    tendance = None
    repartition = None
    stocks_critiques = []
    stocks_tous = []
    passages_recents = []

    # ── Graphique barres (Exactement les 7 derniers jours réels) ────────────
    today = date.today()
    jours_semaine = [today - timedelta(days=i) for i in range(6, -1, -1)]
    jours_fr = {'Mon': 'Lun', 'Tue': 'Mar', 'Wed': 'Mer', 'Thu': 'Jeu', 'Fri': 'Ven', 'Sat': 'Sam', 'Sun': 'Dim'}

    if role == ROLE_MEDECIN:
        bar_title = "Mon Activité Récente"
        bar_subtitle = "Mes consultations sur les 7 derniers jours"
        cur.execute("""
            SELECT DATE(date_consult) as jour, COUNT(id_consult) as total
            FROM consultation
            WHERE DATE(date_consult) BETWEEN %s AND %s AND id_medecin = %s
            GROUP BY DATE(date_consult)
        """, [jours_semaine[0], today, user_id])
    else:
        bar_title = "Flux Hebdomadaire"
        bar_subtitle = "Passages des 7 derniers jours à l'infirmerie"
        cur.execute("""
            SELECT DATE(date_consult) as jour, COUNT(id_consult) as total
            FROM consultation
            WHERE DATE(date_consult) BETWEEN %s AND %s
            GROUP BY DATE(date_consult)
        """, [jours_semaine[0], today])

    counts_by_day = {row['jour']: row['total'] for row in cur.fetchall()}

    jour_labels = []
    jour_values = []
    for d in jours_semaine:
        if d == today:
            jour_labels.append("Aujourd'hui")
        else:
            day_name = jours_fr.get(d.strftime('%a'), d.strftime('%a'))
            jour_labels.append(f"{day_name} {d.strftime('%d/%m')}")
        jour_values.append(counts_by_day.get(d, 0))

    total_semaine = sum(jour_values)

    # ── VUE MÉDECIN ────────────────────────────────────────────────────────
    if role == ROLE_MEDECIN:
        kpi_medecin = get_kpi_medecin(user_id)
        tendance = get_tendance_mensuelle_consultations()
        repartition = get_repartition_pathologies_par_cycle()

        # Graphique camembert : motifs de consultation
        pie_title = "Motifs de Consultation"
        pie_subtitle = "Pathologies fréquentes"
        cur.execute(
            "SELECT motif, COUNT(*) as total FROM consultation WHERE id_medecin = %s GROUP BY motif ORDER BY total DESC LIMIT 5",
            [user_id]
        )
        data = cur.fetchall()
        pie_labels = [d['motif'] for d in data]
        pie_values = [d['total'] for d in data]
        if data:
            pie_info = f"Motif principal : <strong class='text-primary'>{data[0]['motif']}</strong> ({data[0]['total']} cas)"

    # ── VUE INFIRMIER ──────────────────────────────────────────────────────
    elif role == ROLE_INFIRMIER:
        kpi_infirmier = get_kpi_infirmier(user_id)
        tendance = get_tendance_mensuelle_consultations()

        # Graphique Donut pour l'infirmerie : motifs d'accueil fréquents
        pie_title = "Motifs d'Accueil & Triage"
        pie_subtitle = "Urgences & soins les plus fréquents"
        cur.execute("""
            SELECT motif, COUNT(*) as total 
            FROM consultation 
            GROUP BY motif 
            ORDER BY total DESC 
            LIMIT 5
        """)
        data_inf = cur.fetchall()
        pie_labels = [d['motif'] for d in data_inf]
        pie_values = [d['total'] for d in data_inf]
        if data_inf:
            pie_info = f"Motif le plus fréquent : <strong class='text-primary'>{data_inf[0]['motif']}</strong> ({data_inf[0]['total']} cas)"

        # Tous les stocks pour la pharmacie
        from app.extensions import orm_db as db
        from sqlalchemy import case
        stocks_tous = (
            StockMedicament.query
            .order_by(
                case((StockMedicament.quantite_stock <= StockMedicament.seuil_alerte, 0), else_=1),
                StockMedicament.nom_medicament
            )
            .all()
        )
        stocks_critiques = kpi_infirmier['stocks_critiques']

        # Passages récents au poste d'infirmerie (soins et triage)
        cur.execute("""
            SELECT c.id_consult, c.date_consult, c.motif, c.temperature,
                   e.id_eleve, e.nom_eleve, e.prenom_eleve, e.classe,
                   EXISTS(SELECT 1 FROM antecedent_medical a WHERE a.id_eleve = e.id_eleve AND (a.pai_signe = 1 OR a.severite = 'Critique')) as a_pai
            FROM consultation c
            JOIN eleve e ON c.id_eleve = e.id_eleve
            ORDER BY c.date_consult DESC
            LIMIT 6
        """)
        passages_recents = cur.fetchall()

        # RDV à venir (pour l'infirmier)
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

    # ── VUE ADMIN (redirect) ───────────────────────────────────────────────
    elif role == ROLE_ADMIN:
        cur.close()
        return redirect(url_for('admin.panel'))

    # Pour médecin, rdvs = file du jour (dans kpi_medecin['visites_du_jour'])
    if role == ROLE_MEDECIN:
        rdvs = []  # pas utilisé, on utilise kpi_medecin['visites_du_jour']
    elif role != ROLE_INFIRMIER:
        rdvs = []

    cur.close()

    return render_template(
        'dashboard.html',
        role=role,
        # Charts
        pie_labels=pie_labels,
        pie_values=pie_values,
        pie_title=pie_title,
        pie_subtitle=pie_subtitle,
        pie_info=pie_info,
        bar_title=bar_title,
        bar_subtitle=bar_subtitle,
        jour_labels=jour_labels,
        jour_values=jour_values,
        total_semaine=total_semaine,
        # KPIs
        kpi_medecin=kpi_medecin,
        kpi_infirmier=kpi_infirmier,
        tendance=tendance,
        repartition=repartition,
        # Pharmacie
        stocks_critiques=stocks_critiques,
        stocks_tous=stocks_tous,
        passages_recents=passages_recents,
        # Agenda
        rdvs=rdvs,
    )


@dashboard_bp.route('/agenda')
@login_required
def agenda():
    cur = mysql.connection.cursor()
    role = session.get('user_role')
    user_id = session.get('user_id')

    # 1. Classes pour le filtre
    cur.execute("SELECT DISTINCT classe FROM eleve ORDER BY classe")
    classes_data = cur.fetchall()
    classes = [c['classe'] for c in classes_data if c['classe']]

    # 2. Filtres URL
    selected_classe = request.args.get('classe')
    selected_statut = request.args.get('statut')
    selected_date = request.args.get('date_filter')

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
    if selected_date in ['today', 'tomorrow']:
        query += " ORDER BY r.date_rdv ASC"
    else:
        query += " ORDER BY r.date_rdv DESC"

    cur.execute(query, params)
    rdvs = cur.fetchall()
    cur.close()

    stats = {
        'total': len(rdvs),
        'programmes': sum(1 for r in rdvs if r['statut'] == RDV_STATUT_PROGRAMME or not r['statut']),
        'faits': sum(1 for r in rdvs if r['statut'] == RDV_STATUT_FAIT),
        'annules': sum(1 for r in rdvs if r['statut'] == RDV_STATUT_ANNULE)
    }

    return render_template(
        'agenda.html',
        rdvs=rdvs,
        classes=classes,
        current_classe=selected_classe,
        current_statut=selected_statut,
        current_date_filter=selected_date,
        stats=stats
    )


@dashboard_bp.route('/agenda/events')
@login_required
def agenda_events():
    """Fournit les événements de l'agenda au format JSON pour FullCalendar."""
    cur = mysql.connection.cursor()
    role = session.get('user_role')
    user_id = session.get('user_id')

    query = """
        SELECT r.id_rdv, r.date_rdv, r.statut,
               e.id_eleve, e.nom_eleve, e.prenom_eleve, e.classe,
               m.nom_medecin, m.prenom_medecin
        FROM rdv r
        JOIN eleve e ON r.id_eleve = e.id_eleve
        LEFT JOIN medecin m ON r.id_medecin = m.id_medecin
        WHERE 1=1
    """
    params = []
    if role == ROLE_MEDECIN:
        query += " AND r.id_medecin = %s"
        params.append(user_id)

    cur.execute(query, params)
    rdvs = cur.fetchall()
    cur.close()

    events = []
    for r in rdvs:
        statut = (r.get('statut') or 'programmé').lower()
        if 'fait' in statut:
            bg_color = '#10b981'  # vert
            border_color = '#059669'
            statut_label = 'Effectué'
        elif 'annul' in statut:
            bg_color = '#ef4444'  # rouge
            border_color = '#dc2626'
            statut_label = 'Annulé'
        else:
            bg_color = '#3b82f6'  # bleu
            border_color = '#2563eb'
            statut_label = 'Programmé'

        dt = r['date_rdv']
        iso_str = dt.isoformat() if isinstance(dt, datetime) else str(dt)

        nom_med = f"Dr. {r.get('nom_medecin', 'Scolaire')}" if r.get('nom_medecin') else ""

        events.append({
            'id': r['id_rdv'],
            'title': f"{r['nom_eleve']} {r['prenom_eleve']} ({r['classe']})",
            'start': iso_str,
            'backgroundColor': bg_color,
            'borderColor': border_color,
            'textColor': '#ffffff',
            'extendedProps': {
                'id_eleve': r['id_eleve'],
                'eleve_nom': f"{r['nom_eleve']} {r['prenom_eleve']}",
                'classe': r['classe'],
                'medecin': nom_med,
                'statut': statut_label,
                'url_dossier': url_for('eleves.dossier', id_eleve=r['id_eleve'])
            }
        })

    return jsonify(events)



@dashboard_bp.route('/agenda/annuler_journee', methods=['POST'])
@login_required
def annuler_journee():
    role = session.get('user_role')
    user_id = session.get('user_id')
    date_annulation = request.form.get('date_annulation')

    if not date_annulation:
        flash("Veuillez sélectionner une date valide.", "warning")
        return redirect(url_for('dashboard.agenda'))

    try:
        datetime.strptime(date_annulation, '%Y-%m-%d')

        cur = mysql.connection.cursor()
        query = "UPDATE rdv SET statut = %s WHERE DATE(date_rdv) = %s AND (statut = %s OR statut IS NULL)"
        params = [RDV_STATUT_ANNULE, date_annulation, RDV_STATUT_PROGRAMME]

        if role == ROLE_MEDECIN:
            query += " AND id_medecin = %s"
            params.append(user_id)

        cur.execute(query, params)
        mysql.connection.commit()
        affected = cur.rowcount
        cur.close()
    except ValueError:
        flash("Format de date invalide.", "danger")
        return redirect(url_for('dashboard.agenda'))

    if affected > 0:
        flash(f"{affected} rendez-vous ont été annulés pour la journée du {date_annulation}.", "success")
    else:
        flash("Aucun rendez-vous programmé trouvé pour cette date.", "info")

    return redirect(url_for('dashboard.agenda'))


@dashboard_bp.route('/stock/ajuster', methods=['POST'])
@login_required
def ajuster_stock():
    """
    API endpoint pour ajuster le stock d'un médicament (+/-).
    Accessible infirmier & médecin uniquement.
    """
    from app.extensions import orm_db as db
    from app.constants import ROLE_SOIGNANT

    if session.get('user_role') not in ROLE_SOIGNANT:
        return jsonify({'error': 'Non autorisé'}), 403

    id_med = request.json.get('id')
    delta = int(request.json.get('delta', 0))

    if delta == 0 or abs(delta) > 500:
        return jsonify({'error': 'Delta invalide'}), 400

    med = StockMedicament.query.get(id_med)
    if not med:
        return jsonify({'error': 'Médicament introuvable'}), 404

    nouvelle_qte = max(0, med.quantite_stock + delta)
    med.quantite_stock = nouvelle_qte
    db.session.commit()

    return jsonify({
        'id': med.id_medicament,
        'nouvelle_qte': nouvelle_qte,
        'en_alerte': med.est_en_alerte,
        'seuil': med.seuil_alerte
    })


@dashboard_bp.route('/pharmacie')
@login_required
def pharmacie():
    """
    Page dédiée de gestion de la Pharmacie & des Stocks de l'Infirmerie.
    Accessible aux soignants (infirmier, médecin) et à l'administrateur.
    """
    cur = mysql.connection.cursor()
    search_q = request.args.get('search', '').strip()
    statut_filter = request.args.get('statut', '')

    query = 'SELECT * FROM stock_medicament'
    filters = []
    params = []
    if search_q:
        filters.append('(nom_medicament LIKE %s OR forme LIKE %s)')
        params.extend([f'%{search_q}%', f'%{search_q}%'])
    if statut_filter == 'critique':
        filters.append('quantite_stock <= seuil_alerte')
    elif statut_filter == 'ok':
        filters.append('quantite_stock > seuil_alerte')
    if filters:
        query += ' WHERE ' + ' AND '.join(filters)
    query += ' ORDER BY (quantite_stock <= seuil_alerte) DESC, nom_medicament ASC'
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
        'pharmacie.html',
        stocks=stocks,
        search_q=search_q,
        statut_filter=statut_filter,
        total_medicaments=total_medicaments,
        nb_critiques=nb_critiques,
        nb_ok=nb_ok,
        total_unites=int(total_unites)
    )


@dashboard_bp.route('/pharmacie/ajouter', methods=['POST'])
@login_required
def ajouter_medicament_stock():
    """Ajoute une nouvelle référence dans la pharmacie de l'école."""
    nom = request.form.get('nom_medicament', '').strip()
    forme = request.form.get('forme', '').strip() or 'Unité'
    quantite = int(request.form.get('quantite_stock', 0) or 0)
    seuil = int(request.form.get('seuil_alerte', 5) or 5)
    unite = request.form.get('unite_mesure', 'boîtes').strip() or 'unités'

    if nom:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO stock_medicament (nom_medicament, forme, quantite_stock, seuil_alerte, unite_mesure)
            VALUES (%s, %s, %s, %s, %s)
        """, (nom, forme, quantite, seuil, unite))
        mysql.connection.commit()
        cur.close()
        flash(f"Médicament « {nom} » ajouté avec succès au stock de l'infirmerie.", "success")
    else:
        flash("Veuillez spécifier le nom du médicament.", "warning")

    return redirect(url_for('dashboard.pharmacie'))

