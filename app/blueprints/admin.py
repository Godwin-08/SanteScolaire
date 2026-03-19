from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash
import re
import secrets
import unicodedata

from app import utils
from app.constants import ROLE_ADMIN
from app.db import mysql

admin_bp = Blueprint('admin', __name__)

def _normalize_name(value):
    value = (value or "").strip()
    if not value:
        return "USER"
    normalized = unicodedata.normalize("NFKD", value)
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^A-Za-z0-9]", "", normalized).upper()
    return normalized or "USER"

def _build_temp_password(nom, user_id, role_code):
    name_part = _normalize_name(nom)[:4]
    return f"{name_part}-{user_id}-{role_code.upper()}"

@admin_bp.route('/admin')
def panel():
    # Vérification : seul l'admin peut accéder
    if not session.get('logged_in') or session.get('user_role') != ROLE_ADMIN:
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
    if session.get('user_role') != ROLE_ADMIN:
        return redirect(url_for('auth.login'))
        
    type_perso = request.form['type'] # 'medecin' ou 'infirmier'
    prenom = request.form.get('prenom', '').strip()
    nom = request.form.get('nom', '').strip()
    full_name = " ".join([p for p in [prenom, nom] if p]).strip()
    specialite = request.form.get('specialite', '') # Seulement pour medecin
    email = request.form.get('email', '')
    password = request.form.get('password', '').strip()
    temp_password = None
    placeholder_password = secrets.token_urlsafe(16)
    password_hash = generate_password_hash(password or placeholder_password)
    
    cur = mysql.connection.cursor()
    
    try:
        if type_perso == 'medecin':
            cur.execute(
                "INSERT INTO medecin (nom_medecin, specialite, password_hash, must_change_password) VALUES (%s, %s, %s, 1)",
                (full_name, specialite, password_hash),
            )
            # Recuperation de l'ID genere par MySQL pour lier l'email
            new_id = cur.lastrowid
            
            if not password:
                temp_password = _build_temp_password(full_name, new_id, "M")
                cur.execute(
                    "UPDATE medecin SET password_hash = %s, must_change_password = 1 WHERE id_medecin = %s",
                    (generate_password_hash(temp_password), new_id),
                )
            
            # Sauvegarde de l'email dans le JSON
            if email:
                emails_data = utils.get_emails()
                emails_data[str(new_id)] = email
                utils.save_emails_data(emails_data)
        else:
            cur.execute(
                "INSERT INTO infirmier (nom_infirmier, password_hash, must_change_password) VALUES (%s, %s, 1)",
                (full_name, password_hash),
            )
            new_id = cur.lastrowid
            
            if not password:
                temp_password = _build_temp_password(full_name, new_id, "I")
                cur.execute(
                    "UPDATE infirmier SET password_hash = %s, must_change_password = 1 WHERE id_infirmier = %s",
                    (generate_password_hash(temp_password), new_id),
                )
        
        mysql.connection.commit()
    except Exception:
        mysql.connection.rollback()
        flash("Impossible d'ajouter ce membre du personnel.", "danger")
        return redirect(url_for('admin.panel'))
    finally:
        cur.close()
    
    flash(f"{type_perso.capitalize()} ajoute avec succes.", "success")
    if temp_password:
        flash(
            f"Mot de passe temporaire pour {type_perso} (ID {new_id}) : {temp_password}",
            "info",
        )
    return redirect(url_for('admin.panel'))

@admin_bp.route('/admin/supprimer_personnel/<type_perso>/<int:id_perso>', methods=['POST'])
def supprimer_personnel(type_perso, id_perso):
    if session.get('user_role') != ROLE_ADMIN:
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
    if session.get('user_role') != ROLE_ADMIN:
        return redirect(url_for('auth.login'))
        
    id_perso = request.form['id']
    type_perso = request.form['type']
    prenom = request.form.get('prenom', '').strip()
    nom = request.form.get('nom', '').strip()
    full_name = " ".join([p for p in [prenom, nom] if p]).strip()
    
    cur = mysql.connection.cursor()
    if type_perso == 'medecin':
        specialite = request.form.get('specialite', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        cur.execute("UPDATE medecin SET nom_medecin = %s, specialite = %s WHERE id_medecin = %s", (full_name, specialite, id_perso))

        if password:
            cur.execute(
                "UPDATE medecin SET password_hash = %s, must_change_password = 1 WHERE id_medecin = %s",
                (generate_password_hash(password), id_perso),
            )
        
        # Mise à jour de l'email dans le JSON
        emails_data = utils.get_emails()
        emails_data[str(id_perso)] = email
        utils.save_emails_data(emails_data)
    elif type_perso == 'infirmier':
        password = request.form.get('password', '')
        cur.execute("UPDATE infirmier SET nom_infirmier = %s WHERE id_infirmier = %s", (full_name, id_perso))

        if password:
            cur.execute(
                "UPDATE infirmier SET password_hash = %s, must_change_password = 1 WHERE id_infirmier = %s",
                (generate_password_hash(password), id_perso),
            )
    mysql.connection.commit()
    cur.close()
    
    flash("Informations mises à jour avec succès.", "success")
    return redirect(url_for('admin.panel'))
