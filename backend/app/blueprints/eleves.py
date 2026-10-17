from flask import Blueprint, render_template, request, redirect, session, url_for, flash, send_file

from app.constants import MSG_ACTION_NOT_ALLOWED, RDV_STATUT_PROGRAMME, ROLE_ADMIN, ROLE_SOIGNANT
from app.db import mysql
from app.decorators import login_required

eleves_bp = Blueprint('eleves', __name__)

# Page Liste des élèves (Tableau de bord principal)
@eleves_bp.route('/liste')
@login_required
def index():
    # L'admin n'a pas accès à la liste des élèves (il a son propre panel de gestion RH)
    if session.get('user_role') == ROLE_ADMIN:
        return redirect(url_for('admin.panel'))

    cur = mysql.connection.cursor()
    
    # 1. Récupération des classes (filières) pour le menu déroulant
    cur.execute("SELECT DISTINCT classe FROM eleve ORDER BY classe")
    classes_data = cur.fetchall()
    classes = [c['classe'] for c in classes_data if c['classe']]

    # 2. Récupération des filtres depuis l'URL
    selected_classe = request.args.get('classe')
    filter_rdv = request.args.get('avec_rdv')
    filter_mes_patients = request.args.get('mes_patients')

    user_role = session.get('user_role')
    user_id = session.get('user_id')

    # 3. Construction de la requête dynamique
    query = "SELECT DISTINCT e.* FROM eleve e"
    params = []
    conditions = []

    if user_role == 'medecin' and filter_mes_patients == '1':
        # Filtre spécifique : Uniquement les patients déjà pris en charge par ce médecin
        query += """
            LEFT JOIN rdv r_med ON e.id_eleve = r_med.id_eleve AND r_med.id_medecin = %s
            LEFT JOIN consultation c_med ON e.id_eleve = c_med.id_eleve AND c_med.id_medecin = %s
        """
        params.extend([user_id, user_id])
        conditions.append("(r_med.id_rdv IS NOT NULL OR c_med.id_consult IS NOT NULL)")
    elif filter_rdv:
        # Jointure pour ne garder que ceux qui ont un historique (RDV ou Consultation)
        query += " LEFT JOIN rdv r ON e.id_eleve = r.id_eleve LEFT JOIN consultation c ON e.id_eleve = c.id_eleve"
        conditions.append("(r.id_rdv IS NOT NULL OR c.id_consult IS NOT NULL)")

    if selected_classe:
        conditions.append("e.classe = %s")
        params.append(selected_classe)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY e.nom_eleve ASC"
    
    cur.execute(query, params)
    eleves = cur.fetchall()
    cur.close()
    return render_template(
        'index.html',
        eleves=eleves,
        classes=classes,
        current_classe=selected_classe,
        current_rdv=filter_rdv,
        current_mes_patients=filter_mes_patients
    )

# Page Dossier Médical d'un élève spécifique
@eleves_bp.route('/consulter/<int:id_eleve>')
@login_required
def dossier(id_eleve):
    # Restriction stricte : L'Admin ne doit pas voir le dossier médical (Confidentialité)
    if session.get('user_role') not in ROLE_SOIGNANT:
        flash("L'accès aux dossiers médicaux est réservé au personnel soignant.", "danger")
        return redirect(url_for('admin.panel'))

    cur = mysql.connection.cursor()
    
    # 1. Infos de l'élève
    cur.execute("SELECT * FROM eleve WHERE id_eleve = %s", [id_eleve])
    eleve = cur.fetchone()
    
    # 2. Antécédents médicaux & PAI
    cur.execute("""
        SELECT * FROM antecedent_medical 
        WHERE id_eleve = %s 
        ORDER BY (severite = 'Critique') DESC, id_antecedent ASC
    """, [id_eleve])
    antecedents = cur.fetchall()
    pai_actif = any(a.get('pai_signe') or a.get('severite') == 'Critique' for a in antecedents)

    # 3. Historique des consultations (avec jointures pour noms médecins/infirmiers)
    cur.execute("""
        SELECT c.*, m.nom_medecin, i.nom_infirmier 
        FROM consultation c
        LEFT JOIN medecin m ON c.id_medecin = m.id_medecin
        LEFT JOIN infirmier i ON c.id_infirmier = i.id_infirmier
        WHERE c.id_eleve = %s
        ORDER BY c.date_consult DESC
    """, [id_eleve])
    consultations = cur.fetchall()
    
    # 4. Prescriptions associées à cet élève
    cur.execute("""
        SELECT p.* FROM prescription p
        JOIN consultation c ON p.id_consult = c.id_consult
        WHERE c.id_eleve = %s
    """, [id_eleve])
    prescriptions = cur.fetchall()
    
    # 5. Rendez-vous à venir
    cur.execute("""
        SELECT r.*, m.nom_medecin 
        FROM rdv r 
        LEFT JOIN medecin m ON r.id_medecin = m.id_medecin
        WHERE r.id_eleve = %s AND r.date_rdv >= NOW() AND (r.statut = %s OR r.statut IS NULL)
        ORDER BY r.date_rdv ASC
    """, [id_eleve, RDV_STATUT_PROGRAMME])
    rdvs = cur.fetchall()

    # 6. Données pour le graphique IMC (Poids / Taille^2)
    imc_labels = []
    imc_values = []
    # On inverse l'ordre pour avoir le graphique chronologique (du plus ancien au plus récent)
    # car 'consultations' est trié par date décroissante (DESC)
    for c in reversed(consultations):
        # On vérifie que les données existent (poids et taille non nuls)
        if c.get('poids') and c.get('taille'):
            taille_m = c['taille'] / 100 # Conversion cm en m
            imc = round(c['poids'] / (taille_m * taille_m), 2)
            imc_labels.append(c['date_consult'].strftime('%d/%m/%Y'))
            imc_values.append(imc)
    
    # 7. Liste des médecins pour le formulaire de RDV
    cur.execute("SELECT id_medecin, nom_medecin FROM medecin")
    medecins = cur.fetchall()

    user_role = session.get('user_role')
    user_id = session.get('user_id')
    medecin_a_suivi = False
    if user_role == 'medecin':
        medecin_a_suivi = any(c.get('id_medecin') == user_id for c in consultations) or any(r.get('id_medecin') == user_id for r in rdvs)

    cur.close()
    return render_template(
        'dossier.html', 
        eleve=eleve, 
        antecedents=antecedents,
        pai_actif=pai_actif,
        consultations=consultations, 
        prescriptions=prescriptions, 
        rdvs=rdvs, 
        imc_labels=imc_labels, 
        imc_values=imc_values, 
        medecins=medecins,
        medecin_a_suivi=medecin_a_suivi
    )

# Traitement du formulaire d'ajout d'un nouvel élève
@eleves_bp.route('/ajouter_eleve', methods=['POST'])
@login_required
def ajouter_eleve():
    # Sécurité : Seul le personnel soignant peut créer un dossier patient
    if session.get('user_role') not in ROLE_SOIGNANT:
        flash(MSG_ACTION_NOT_ALLOWED, "danger")
        return redirect(url_for('admin.panel'))

    # Insertion du nouvel élève en base
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO eleve (nom_eleve, prenom_eleve, classe, sexe, date_naissance) 
        VALUES (%s, %s, %s, %s, %s)
    """, (request.form['nom'], request.form['prenom'], request.form['classe'], request.form['sexe'], request.form['date_naissance']))
    mysql.connection.commit()
    new_id = cur.lastrowid
    cur.close()
    
    flash("Dossier créé avec succès !", "success")
    return redirect(url_for('eleves.dossier', id_eleve=new_id))

# Mise à jour du statut d'un RDV (Fait / Annulé)
@eleves_bp.route('/rdv/statut/<int:id_rdv>/<statut>')
@login_required
def update_rdv_status(id_rdv, statut):
    if session.get('user_role') not in ROLE_SOIGNANT:
        flash(MSG_ACTION_NOT_ALLOWED, "danger")
        return redirect(url_for('dashboard.agenda'))
        
    cur = mysql.connection.cursor()
    
    # Mise à jour directe du statut
    cur.execute("UPDATE rdv SET statut = %s WHERE id_rdv = %s", (statut, id_rdv))
    mysql.connection.commit()
    flash(f"Rendez-vous marqué comme : {statut}.", "success")
    cur.close()
    return redirect(url_for('dashboard.agenda'))


@eleves_bp.route('/eleve/<int:id_eleve>/pai/pdf')
@login_required
def telecharger_pai_pdf(id_eleve):
    """Génère et télécharge la Fiche d'Urgence PAI au format PDF vectoriel pour l'équipe pédagogique."""
    if session.get('user_role') not in ROLE_SOIGNANT:
        flash("Accès non autorisé.", "warning")
        return redirect(url_for('eleves.index'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM eleve WHERE id_eleve = %s", [id_eleve])
    eleve = cur.fetchone()

    if not eleve:
        cur.close()
        flash("Élève introuvable.", "warning")
        return redirect(url_for('eleves.index'))

    cur.execute("""
        SELECT * FROM antecedent_medical 
        WHERE id_eleve = %s 
        ORDER BY (severite = 'Critique') DESC, id_antecedent ASC
    """, [id_eleve])
    antecedents = cur.fetchall()

    if not antecedents:
        cur.close()
        flash("Cet élève n'a aucun protocole d'urgence ou antécédent médical enregistré.", "info")
        return redirect(url_for('eleves.dossier', id_eleve=id_eleve))

    # Récupération éventuelle du médecin traitant/référent
    cur.execute("""
        SELECT m.nom_medecin, m.prenom_medecin, s.nom_specialite 
        FROM rdv r
        JOIN medecin m ON r.id_medecin = m.id_medecin
        LEFT JOIN specialite s ON m.id_specialite = s.id_specialite
        WHERE r.id_eleve = %s
        ORDER BY r.date_rdv DESC LIMIT 1
    """, [id_eleve])
    medecin = cur.fetchone()
    cur.close()

    from app.services.pdf_service import generate_fiche_pai_pdf
    pdf_buffer = generate_fiche_pai_pdf(eleve, antecedents, medecin)

    filename = f"Fiche_Urgence_PAI_{eleve['nom_eleve']}_{eleve['prenom_eleve']}.pdf"
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

