from flask import Blueprint, render_template, request, redirect, session, url_for, flash, jsonify, send_file

from app.constants import (
    MSG_ACTION_NOT_ALLOWED,
    RDV_STATUT_PROGRAMME,
    ROLE_INFIRMIER,
    ROLE_MEDECIN,
    ROLE_SOIGNANT,
)
from app.db import mysql
from app.decorators import login_required
from app.services.email_service import send_rdv_notification

consultations_bp = Blueprint('consultations', __name__)

# Formulaire de nouvelle consultation
@consultations_bp.route('/nouvelle_visite/<int:id_eleve>')
@login_required
def nouvelle_visite(id_eleve):
    if session.get('user_role') not in ROLE_SOIGNANT:
        flash("Accès non autorisé.", "warning")
        return redirect(url_for('eleves.dossier', id_eleve=id_eleve))
        
    cur = mysql.connection.cursor()
    # 1. Infos de l'élève pour l'en-tête
    cur.execute("SELECT * FROM eleve WHERE id_eleve = %s", [id_eleve])
    eleve = cur.fetchone()

    # 2. Antécédents médicaux & PAI actif (vigilance pour le médecin)
    cur.execute("""
        SELECT * FROM antecedent_medical 
        WHERE id_eleve = %s 
        ORDER BY (severite = 'Critique') DESC, id_antecedent ASC
    """, [id_eleve])
    antecedents = cur.fetchall()
    pai_actif = any(a.get('pai_signe') or a.get('severite') == 'Critique' for a in antecedents)

    # 3. Dernières constantes enregistrées au triage (avec auteur infirmier si existant)
    cur.execute("""
        SELECT c.poids, c.taille, c.temperature, c.tension, c.date_consult,
               i.nom_infirmier
        FROM consultation c
        LEFT JOIN infirmier i ON c.id_infirmier = i.id_infirmier
        WHERE c.id_eleve = %s 
          AND (c.temperature IS NOT NULL OR c.tension IS NOT NULL OR c.poids IS NOT NULL)
        ORDER BY c.date_consult DESC LIMIT 1
    """, [id_eleve])
    dernieres_constantes = cur.fetchone() or {}

    # 4. Liste des médecins pour le menu déroulant (cas infirmier)
    cur.execute("SELECT id_medecin, nom_medecin, specialite FROM medecin")
    medecins = cur.fetchall()

    # 5. Médicaments fréquents et référentiel pour suggestions et autocomplétion rapide
    cur.execute("SELECT DISTINCT nom_medicament FROM stock_medicament ORDER BY nom_medicament ASC")
    stock_meds = [r['nom_medicament'] for r in cur.fetchall()]

    cur.execute("SELECT DISTINCT medicament FROM prescription WHERE medicament IS NOT NULL ORDER BY medicament ASC")
    presc_meds = [r['medicament'] for r in cur.fetchall()]

    try:
        cur.execute("SELECT DISTINCT nom_commercial FROM referentiel_medicament ORDER BY nom_commercial ASC")
        ref_meds = [r['nom_commercial'] for r in cur.fetchall()]
    except Exception:
        ref_meds = []

    suggestions_medicaments = sorted(list(set(stock_meds + presc_meds + ref_meds)))

    cur.close()
    return render_template(
        'ajouter_consultation.html', 
        eleve=eleve, 
        antecedents=antecedents,
        pai_actif=pai_actif,
        dernieres_constantes=dernieres_constantes,
        medecins=medecins,
        suggestions_medicaments=suggestions_medicaments
    )

# Enregistrement de la consultation et des prescriptions
@consultations_bp.route('/enregistrer_visite', methods=['POST'])
@login_required
def enregistrer_visite():
    role = session.get('user_role')
    user_id = session.get('user_id')

    if role not in ROLE_SOIGNANT:
        flash(MSG_ACTION_NOT_ALLOWED, "danger")
        return redirect(url_for('eleves.index'))

    id_e = request.form['id_eleve']
    
    cur = mysql.connection.cursor()
    try:
        # --- 1. Gestion du RDV (Spécifique Infirmier / Triage) ---
        date_rdv = request.form.get('date_rdv')
        id_medecin_rdv = request.form.get('id_medecin_rdv')

        if date_rdv and id_medecin_rdv:
            # Correction du format de date (HTML datetime-local envoie 'T', MySQL préfère ' ')
            date_rdv = date_rdv.replace('T', ' ')

            # Vérification de la disponibilité (Pas de RDV dans les +/- 15 min pour ce médecin)
            cur.execute("""
                SELECT COUNT(*) as cnt FROM rdv 
                WHERE id_medecin = %s 
                AND date_rdv BETWEEN DATE_SUB(%s, INTERVAL 15 MINUTE) AND DATE_ADD(%s, INTERVAL 15 MINUTE)
                AND (statut = %s OR statut IS NULL)
            """, (id_medecin_rdv, date_rdv, date_rdv, RDV_STATUT_PROGRAMME))
            
            if cur.fetchone()['cnt'] > 0:
                flash("Le médecin n'est pas disponible sur ce créneau (RDV existant proche).", "danger")
                return redirect(url_for('consultations.nouvelle_visite', id_eleve=id_e))

            # Si dispo, on insère le RDV
            cur.execute(
                "INSERT INTO rdv (id_eleve, date_rdv, id_medecin, statut) VALUES (%s, %s, %s, %s)",
                (id_e, date_rdv, id_medecin_rdv, RDV_STATUT_PROGRAMME),
            )

        # --- 2. Insertion de la consultation (Données Vitales) ---
        poids = request.form.get('poids') or None
        taille = request.form.get('taille') or None
        temp = request.form.get('temperature') or None
        tension = request.form.get('tension') or None
        
        # Gestion des IDs selon qui est connecté
        id_medecin = user_id if role == ROLE_MEDECIN else None
        id_infirmier = user_id if role == ROLE_INFIRMIER else None
        
        # Observations : Saisie par médecin, ou auto-générée pour infirmier
        observations = request.form.get('observations')
        if role == ROLE_INFIRMIER:
            observations = "Triage Infirmier - Prise de constantes"

        cur.execute("""
            INSERT INTO consultation (date_consult, motif, observations, id_eleve, id_medecin, id_infirmier, poids, taille, temperature, tension) 
            VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (request.form['motif'], observations, id_e, id_medecin, id_infirmier, poids, taille, temp, tension))
        
        id_consultation = cur.lastrowid

        # --- 3. Prescriptions (Réservé aux Médecins) ---
        if role == ROLE_MEDECIN:
            # Récupération des listes (tableaux) pour les médicaments
            meds = request.form.getlist('medicament[]')
            dosages = request.form.getlist('dosage[]')
            durees = request.form.getlist('duree[]')

            for i in range(len(meds)):
                if meds[i].strip():
                    cur.execute("""
                        INSERT INTO prescription (medicament, dosage, duree, id_consult)
                        VALUES (%s, %s, %s, %s)
                    """, (meds[i], dosages[i], durees[i], id_consultation))

        mysql.connection.commit()
        
        if role == ROLE_INFIRMIER and date_rdv:
            # Envoi de l'email de confirmation au médecin
            try:
                cur.execute("SELECT nom_medecin, email FROM medecin WHERE id_medecin = %s", [id_medecin_rdv])
                med_info = cur.fetchone()
                cur.execute("SELECT nom_eleve, prenom_eleve FROM eleve WHERE id_eleve = %s", [id_e])
                eleve_info = cur.fetchone()
                
                if med_info and eleve_info:
                    send_rdv_notification(
                        id_medecin_rdv, med_info['nom_medecin'], 
                        f"{eleve_info['nom_eleve']} {eleve_info['prenom_eleve']}", date_rdv,
                        medecin_email=med_info.get('email')
                    )
            except Exception as e:
                print(f"Erreur notification email: {e}")
                
            flash("Triage effectué et RDV programmé avec succès !", "success")
        else:
            flash("Consultation enregistrée avec succès !", "success")
            
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Erreur : {str(e)}", "danger")
    finally:
        cur.close()

    return redirect(url_for('eleves.dossier', id_eleve=id_e))

# API : Vérification des disponibilités (AJAX)
@consultations_bp.route('/api/creneaux_occupes/<int:id_medecin>/<string:date_jour>')
@login_required
def creneaux_occupes(id_medecin, date_jour):
    cur = mysql.connection.cursor()
    # Récupère les heures des RDV pour ce médecin et ce jour (format HH:MM)
    # Note : %%H:%%i est utilisé pour échapper les % dans la requête SQL formatée
    cur.execute("""
        SELECT DATE_FORMAT(date_rdv, '%%H:%%i') as heure 
        FROM rdv 
        WHERE id_medecin = %s 
        AND DATE(date_rdv) = %s 
        AND (statut = %s OR statut IS NULL)
    """, (id_medecin, date_jour, RDV_STATUT_PROGRAMME))
    rdvs = cur.fetchall()
    cur.close()
    # Retourne une liste simple : ['09:00', '10:30', ...]
    return jsonify([r['heure'] for r in rdvs])

# API : Recherche dynamique autocomplétée dans le référentiel des médicaments
@consultations_bp.route('/api/medicaments/recherche')
@login_required
def api_recherche_medicaments():
    """Recherche AJAX rapide pour autocompléter la prescription des médecins."""
    q = request.args.get('q', '').strip()
    cur = mysql.connection.cursor()
    try:
        from app.services.medicament_service import rechercher_medicaments
        resultats = rechercher_medicaments(q, cur, limit=20)
        return jsonify(resultats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()

# Suppression d'une consultation
@consultations_bp.route('/supprimer_consultation/<int:id_consult>', methods=['POST'])
@login_required
def supprimer_consultation(id_consult):
    # Sécurité : Seul un médecin peut supprimer une consultation
    if session.get('user_role') != ROLE_MEDECIN:
        flash(MSG_ACTION_NOT_ALLOWED, "danger")
        return redirect(url_for('eleves.index'))

    user_id = session.get('user_id')
    cur = mysql.connection.cursor()
    try:
        # 1. Récupérer la consultation et vérifier qu'elle appartient à CE médecin
        cur.execute(
            "SELECT id_eleve, id_medecin FROM consultation WHERE id_consult = %s",
            [id_consult]
        )
        result = cur.fetchone()

        if not result:
            flash("Consultation introuvable.", "warning")
            return redirect(url_for('eleves.index'))

        # 🔒 Vérification de propriété : un médecin ne peut supprimer QUE ses propres consultations
        if result['id_medecin'] != user_id:
            flash("Vous ne pouvez supprimer que vos propres consultations.", "danger")
            return redirect(url_for('eleves.dossier', id_eleve=result['id_eleve']))

        id_eleve = result['id_eleve']

        # 2. Supprimer les prescriptions associées (Nettoyage)
        cur.execute("DELETE FROM prescription WHERE id_consult = %s", [id_consult])

        # 3. Supprimer la consultation
        cur.execute("DELETE FROM consultation WHERE id_consult = %s", [id_consult])

        mysql.connection.commit()
        flash("Consultation supprimée définitivement.", "success")
        return redirect(url_for('eleves.dossier', id_eleve=id_eleve))

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Erreur : {str(e)}", "danger")
        return redirect(url_for('eleves.index'))
    finally:
        cur.close()

# Vue & Impression de l'Ordonnance Médicale Officielle (Conforme aux normes cliniques)
@consultations_bp.route('/consultation/ordonnance/<int:id_consult>')
@login_required
def afficher_ordonnance(id_consult):
    cur = mysql.connection.cursor()
    # 1. Consultation, Patient & Médecin
    cur.execute("""
        SELECT c.*, 
               e.nom_eleve, e.prenom_eleve, e.classe, e.date_naissance, e.sexe,
               m.nom_medecin, m.prenom_medecin, m.specialite, m.email as email_medecin
        FROM consultation c
        JOIN eleve e ON c.id_eleve = e.id_eleve
        LEFT JOIN medecin m ON c.id_medecin = m.id_medecin
        WHERE c.id_consult = %s
    """, [id_consult])
    consultation = cur.fetchone()

    if not consultation:
        cur.close()
        flash("Consultation introuvable.", "warning")
        return redirect(url_for('eleves.index'))

    # 2. Prescriptions associées
    cur.execute("""
        SELECT * FROM prescription 
        WHERE id_consult = %s 
        ORDER BY id_prescription ASC
    """, [id_consult])
    prescriptions_raw = cur.fetchall()

    if not prescriptions_raw:
        cur.close()
        flash("Cette consultation ne comporte aucune prescription médicamenteuse.", "info")
        return redirect(url_for('eleves.dossier', id_eleve=consultation['id_eleve']))

    # 3. Vérification de disponibilité dans la pharmacie de l'école
    from app.services.medicament_service import verifier_disponibilite_ecole
    prescriptions = []
    nb_dispo_ecole = 0
    for p in prescriptions_raw:
        dispo_info = verifier_disponibilite_ecole(p['medicament'], cur)
        est_dispo = dispo_info.get('disponible', False)
        if est_dispo:
            nb_dispo_ecole += 1
        prescriptions.append({
            'medicament': p['medicament'],
            'dosage': p['dosage'],
            'duree': p['duree'],
            'dispo_ecole': est_dispo,
            'lieu_delivrance': dispo_info.get('lieu')
        })

    cur.close()
    return render_template(
        'ordonnance.html',
        consultation=consultation,
        prescriptions=prescriptions,
        nb_dispo_ecole=nb_dispo_ecole,
        total_prescriptions=len(prescriptions)
    )


@consultations_bp.route('/ordonnance/<int:id_consult>/pdf')
@login_required
def telecharger_ordonnance_pdf(id_consult):
    """Génère et télécharge l'ordonnance médicale officielle au format PDF vectoriel."""
    if session.get('user_role') not in ROLE_SOIGNANT:
        flash("Accès non autorisé.", "warning")
        return redirect(url_for('eleves.index'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT c.*, e.nom_eleve, e.prenom_eleve, e.classe, e.date_naissance, e.sexe,
               m.nom_medecin, m.prenom_medecin, s.nom_specialite as specialite
        FROM consultation c
        JOIN eleve e ON c.id_eleve = e.id_eleve
        LEFT JOIN medecin m ON c.id_medecin = m.id_medecin
        LEFT JOIN specialite s ON m.id_specialite = s.id_specialite
        WHERE c.id_consult = %s
    """, [id_consult])
    consultation = cur.fetchone()

    if not consultation:
        cur.close()
        flash("Consultation introuvable.", "warning")
        return redirect(url_for('eleves.index'))

    cur.execute("""
        SELECT * FROM prescription 
        WHERE id_consult = %s 
        ORDER BY id_prescription ASC
    """, [id_consult])
    prescriptions_raw = cur.fetchall()

    from app.services.medicament_service import verifier_disponibilite_ecole
    prescriptions = []
    for p in prescriptions_raw:
        dispo_info = verifier_disponibilite_ecole(p['medicament'], cur)
        prescriptions.append({
            'medicament': p['medicament'],
            'dosage': p['dosage'],
            'duree': p['duree'],
            'dispo_ecole': dispo_info.get('disponible', False),
            'lieu_delivrance': dispo_info.get('lieu')
        })

    cur.close()

    from app.services.pdf_service import generate_ordonnance_pdf
    pdf_buffer = generate_ordonnance_pdf(consultation, prescriptions)

    filename = f"Ordonnance_{consultation['nom_eleve']}_{consultation['prenom_eleve']}_{id_consult}.pdf"
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


