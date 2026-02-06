from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from db import mysql
import utils

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def panel():
    # Vérification : seul l'admin peut accéder
    if not session.get('logged_in') or session.get('user_role') != 'admin':
        flash("Accès réservé aux administrateurs.", "danger")
        return redirect(url_for('auth.login'))
        
    cur = mysql.connection.cursor()
    
    # Récupération du personnel existant
    cur.execute("SELECT * FROM medecin")
    medecins = cur.fetchall()
    
    # Fusion des données SQL avec les emails du fichier JSON
    emails = utils.get_emails()
    for m in medecins:
        # On ajoute le champ 'email' au dictionnaire médecin s'il existe dans le JSON
        m['email'] = emails.get(str(m['id_medecin']), '')
    
    cur.execute("SELECT * FROM infirmier")
    infirmiers = cur.fetchall()
    
    cur.close()
    return render_template('admin_dashboard.html', medecins=medecins, infirmiers=infirmiers)

@admin_bp.route('/admin/ajouter_personnel', methods=['POST'])
def ajouter_personnel():
    if session.get('user_role') != 'admin':
        return redirect(url_for('auth.login'))
        
    type_perso = request.form['type'] # 'medecin' ou 'infirmier'
    nom = request.form['nom']
    specialite = request.form.get('specialite', '') # Seulement pour médecin
    email = request.form.get('email', '')
    
    cur = mysql.connection.cursor()
    
    if type_perso == 'medecin':
        cur.execute("INSERT INTO medecin (nom_medecin, specialite) VALUES (%s, %s)", (nom, specialite))
        # Récupération de l'ID généré par MySQL pour lier l'email
        new_id = cur.lastrowid
        
        # Sauvegarde de l'email dans le JSON
        if email:
            emails_data = utils.get_emails()
            emails_data[str(new_id)] = email
            utils.save_emails_data(emails_data)
    else:
        cur.execute("INSERT INTO infirmier (nom_infirmier) VALUES (%s)", [nom])
        
    mysql.connection.commit()
    cur.close()
    
    flash(f"{type_perso.capitalize()} ajouté avec succès.", "success")
    return redirect(url_for('admin.panel'))

@admin_bp.route('/admin/supprimer_personnel/<type_perso>/<int:id_perso>', methods=['POST'])
def supprimer_personnel(type_perso, id_perso):
    if session.get('user_role') != 'admin':
        return redirect(url_for('auth.login'))
        
    cur = mysql.connection.cursor()
    try:
        if type_perso == 'medecin':
            cur.execute("DELETE FROM medecin WHERE id_medecin = %s", [id_perso])
            
            # Suppression de l'email associé dans le JSON
            emails_data = utils.get_emails()
            if str(id_perso) in emails_data:
                del emails_data[str(id_perso)]
                utils.save_emails_data(emails_data)
        elif type_perso == 'infirmier':
            cur.execute("DELETE FROM infirmier WHERE id_infirmier = %s", [id_perso])
        mysql.connection.commit()
        flash("Membre du personnel supprimé avec succès.", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash("Impossible de supprimer ce membre (il est probablement lié à des consultations existantes).", "danger")
    finally:
        cur.close()
        
    return redirect(url_for('admin.panel'))

@admin_bp.route('/admin/modifier_personnel', methods=['POST'])
def modifier_personnel():
    if session.get('user_role') != 'admin':
        return redirect(url_for('auth.login'))
        
    id_perso = request.form['id']
    type_perso = request.form['type']
    nom = request.form['nom']
    
    cur = mysql.connection.cursor()
    if type_perso == 'medecin':
        specialite = request.form.get('specialite', '')
        email = request.form.get('email', '')
        cur.execute("UPDATE medecin SET nom_medecin = %s, specialite = %s WHERE id_medecin = %s", (nom, specialite, id_perso))
        
        # Mise à jour de l'email dans le JSON
        emails_data = utils.get_emails()
        emails_data[str(id_perso)] = email
        utils.save_emails_data(emails_data)
    elif type_perso == 'infirmier':
        cur.execute("UPDATE infirmier SET nom_infirmier = %s WHERE id_infirmier = %s", (nom, id_perso))
    mysql.connection.commit()
    cur.close()
    
    flash("Informations mises à jour avec succès.", "success")
    return redirect(url_for('admin.panel'))