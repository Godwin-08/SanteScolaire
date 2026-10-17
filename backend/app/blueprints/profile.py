from flask import Blueprint, render_template, request, redirect, session, url_for, flash

from app.constants import ROLE_ADMIN, ROLE_INFIRMIER, ROLE_MEDECIN
from app.db import mysql

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profil')
def mon_profil():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
    
    role = session.get('user_role')
    user_id = session.get('user_id')
    
    cur = mysql.connection.cursor()
    if role == ROLE_ADMIN:
        cur.execute("SELECT id_admin as id, nom_admin as nom, prenom_admin as prenom, email FROM admin WHERE id_admin = %s", [user_id])
        user = cur.fetchone() or {'nom': 'Administrateur', 'id': user_id, 'email': ''}
        cur.close()
        return render_template('profile.html', user=user, is_admin=True)

    if role == ROLE_MEDECIN:
        cur.execute("SELECT *, nom_medecin as nom, prenom_medecin as prenom FROM medecin WHERE id_medecin = %s", [user_id])
        user = cur.fetchone()
    else:
        cur.execute("SELECT *, nom_infirmier as nom, prenom_infirmier as prenom FROM infirmier WHERE id_infirmier = %s", [user_id])
        user = cur.fetchone()
        
    cur.close()
    return render_template('profile.html', user=user, is_admin=False)

@profile_bp.route('/profil/update', methods=['POST'])
def update_profil():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
        
    role = session.get('user_role')
    user_id = session.get('user_id')
    prenom = request.form.get('prenom', '').strip()
    nom = request.form.get('nom', '').strip()
    email = request.form.get('email', '').strip().lower()
    
    cur = mysql.connection.cursor()
    try:
        # Si un email est renseigné, vérifier qu'il n'est pas déjà pris par un autre utilisateur
        if email:
            for t_name, id_col in [('admin', 'id_admin'), ('medecin', 'id_medecin'), ('infirmier', 'id_infirmier')]:
                if t_name == role:
                    cur.execute(f"SELECT email FROM {t_name} WHERE LOWER(email) = %s AND {id_col} != %s", (email, user_id))
                else:
                    cur.execute(f"SELECT email FROM {t_name} WHERE LOWER(email) = %s", (email,))
                if cur.fetchone():
                    flash("Cette adresse email est déjà utilisée par un autre compte.", "danger")
                    return redirect(url_for('profile.mon_profil'))

        if role == ROLE_ADMIN:
            if email:
                cur.execute("UPDATE admin SET nom_admin = %s, prenom_admin = %s, email = %s WHERE id_admin = %s", (nom, prenom, email, user_id))
            else:
                cur.execute("UPDATE admin SET nom_admin = %s, prenom_admin = %s WHERE id_admin = %s", (nom, prenom, user_id))
        elif role == ROLE_MEDECIN:
            specialite = request.form.get('specialite', '').strip()
            cur.execute("UPDATE medecin SET nom_medecin = %s, prenom_medecin = %s, specialite = %s, email = %s WHERE id_medecin = %s", (nom, prenom, specialite, email, user_id))
        elif role == ROLE_INFIRMIER:
            cur.execute("UPDATE infirmier SET nom_infirmier = %s, prenom_infirmier = %s, email = %s WHERE id_infirmier = %s", (nom, prenom, email, user_id))
            
        mysql.connection.commit()
        session['username'] = f"{prenom} {nom}".strip()
        if email:
            session['user_email'] = email
        flash("Votre profil a été mis à jour avec succès.", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Erreur lors de la mise à jour : {str(e)}", "danger")
    finally:
        cur.close()

    return redirect(url_for('profile.mon_profil'))
