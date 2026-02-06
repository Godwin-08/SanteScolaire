from flask import Blueprint, render_template, request, redirect, session, url_for, flash, jsonify
from db import mysql
from decorators import login_required

consultations_bp = Blueprint('consultations', __name__)

# Formulaire de nouvelle consultation
@consultations_bp.route('/nouvelle_visite/<int:id_eleve>')
@login_required
def nouvelle_visite(id_eleve):
    if session.get('user_role') not in ['medecin', 'infirmier']:
        flash("Accès non autorisé.", "warning")
        return redirect(url_for('eleves.dossier', id_eleve=id_eleve))
        
    cur = mysql.connection.cursor()
    # Infos de l'élève pour l'en-tête
    cur.execute("SELECT * FROM eleve WHERE id_eleve = %s", [id_eleve])
    eleve = cur.fetchone()
    
    # Liste des médecins pour le menu déroulant
    cur.execute("SELECT id_medecin, nom_medecin, specialite FROM medecin")
    medecins = cur.fetchall()
    
    cur.close()
    return render_template('ajouter_consultation.html', eleve=eleve, medecins=medecins)

# Enregistrement de la consultation et des prescriptions
@consultations_bp.route('/enregistrer_visite', methods=['POST'])
@login_required
def enregistrer_visite():
    role = session.get('user_role')
    user_id = session.get('user_id')

    if role not in ['medecin', 'infirmier']:
        flash("Action non autorisée.", "danger")
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
                AND (statut = 'programmé' OR statut IS NULL)
            """, (id_medecin_rdv, date_rdv, date_rdv))
            
            if cur.fetchone()['cnt'] > 0:
                flash("Le médecin n'est pas disponible sur ce créneau (RDV existant proche).", "danger")
                return redirect(url_for('consultations.nouvelle_visite', id_eleve=id_e))

            # Si dispo, on insère le RDV
            cur.execute("INSERT INTO rdv (id_eleve, date_rdv, id_medecin, statut) VALUES (%s, %s, %s, 'programmé')", 
                       (id_e, date_rdv, id_medecin_rdv))

        # --- 2. Insertion de la consultation (Données Vitales) ---
        poids = request.form.get('poids') or None
        taille = request.form.get('taille') or None
        temp = request.form.get('temperature') or None
        tension = request.form.get('tension') or None
        
        # Gestion des IDs selon qui est connecté
        id_medecin = user_id if role == 'medecin' else None
        id_infirmier = user_id if role == 'infirmier' else None
        
        # Observations : Saisie par médecin, ou auto-générée pour infirmier
        observations = request.form.get('observations')
        if role == 'infirmier':
            observations = "Triage Infirmier - Prise de constantes"

        cur.execute("""
            INSERT INTO consultation (date_consult, motif, observations, id_eleve, id_medecin, id_infirmier, poids, taille, temperature, tension) 
            VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (request.form['motif'], observations, id_e, id_medecin, id_infirmier, poids, taille, temp, tension))
        
        id_consultation = cur.lastrowid

        # --- 3. Prescriptions (Réservé aux Médecins) ---
        if role == 'medecin':
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
        
        if role == 'infirmier' and date_rdv:
            # Envoi de l'email de confirmation au médecin
            try:
                import utils
                cur.execute("SELECT nom_medecin FROM medecin WHERE id_medecin = %s", [id_medecin_rdv])
                med_info = cur.fetchone()
                cur.execute("SELECT nom_eleve, prenom_eleve FROM eleve WHERE id_eleve = %s", [id_e])
                eleve_info = cur.fetchone()
                
                if med_info and eleve_info:
                    utils.send_rdv_notification(
                        id_medecin_rdv, med_info['nom_medecin'], 
                        f"{eleve_info['nom_eleve']} {eleve_info['prenom_eleve']}", date_rdv
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
        AND (statut = 'programmé' OR statut IS NULL)
    """, (id_medecin, date_jour))
    rdvs = cur.fetchall()
    cur.close()
    # Retourne une liste simple : ['09:00', '10:30', ...]
    return jsonify([r['heure'] for r in rdvs])

# Suppression d'une consultation
@consultations_bp.route('/supprimer_consultation/<int:id_consult>', methods=['POST'])
@login_required
def supprimer_consultation(id_consult):
    # Sécurité : Seul un médecin peut supprimer une consultation
    if session.get('user_role') != 'medecin':
        flash("Action non autorisée.", "danger")
        return redirect(url_for('eleves.index'))

    cur = mysql.connection.cursor()
    try:
        # 1. Récupérer l'ID élève pour la redirection
        cur.execute("SELECT id_eleve FROM consultation WHERE id_consult = %s", [id_consult])
        result = cur.fetchone()
        
        if not result:
            flash("Consultation introuvable.", "warning")
            return redirect(url_for('eleves.index'))
            
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