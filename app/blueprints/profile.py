from flask import Blueprint, render_template, request, redirect, session, url_for, flash

from app import utils
from app.constants import ROLE_ADMIN, ROLE_INFIRMIER, ROLE_MEDECIN
from app.db import mysql



def _split_full_name(full_name):
    parts = (full_name or '').strip().split()
    if not parts:
        return '', ''
    prenom = parts[0]
    nom = ' '.join(parts[1:])
    return prenom, nom
profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profil')
def mon_profil():
    # Vérification de connexion
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
    
    role = session.get('user_role')
    user_id = session.get('user_id')
    
    # Cas Admin : info depuis la table admin
    if role == ROLE_ADMIN:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_admin as id, nom_admin as nom FROM admin WHERE id_admin = %s", [user_id])
        user = cur.fetchone() or {'nom': 'Administrateur', 'id': user_id}
        cur.close()
        return render_template('profile.html', user=user, is_admin=True)

    cur = mysql.connection.cursor()
    if role == ROLE_MEDECIN:
        # Récupération des infos médecin
        cur.execute("SELECT *, nom_medecin as nom FROM medecin WHERE id_medecin = %s", [user_id])
        user = cur.fetchone()
        # Injection de l'email depuis le JSON auxiliaire
        if user:
            user['email'] = utils.get_emails().get(str(user_id), '')
            user['prenom'], user['nom_famille'] = _split_full_name(user.get('nom', ''))
    else:
        # Récupération des infos infirmier
        cur.execute("SELECT *, nom_infirmier as nom FROM infirmier WHERE id_infirmier = %s", [user_id])
        user = cur.fetchone()
        if user:
            user['prenom'], user['nom_famille'] = _split_full_name(user.get('nom', ''))
        
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
    nouveau_nom = ' '.join([p for p in [prenom, nom] if p]).strip()
    
    cur = mysql.connection.cursor()
    
    if role == ROLE_MEDECIN:
        specialite = request.form['specialite']
        email = request.form['email']
        cur.execute("UPDATE medecin SET nom_medecin = %s, specialite = %s WHERE id_medecin = %s", (nouveau_nom, specialite, user_id))
        
        # Mise à jour JSON
        emails_data = utils.get_emails()
        emails_data[str(user_id)] = email
        utils.save_emails_data(emails_data)
    elif role == ROLE_INFIRMIER:
        cur.execute("UPDATE infirmier SET nom_infirmier = %s WHERE id_infirmier = %s", (nouveau_nom, user_id))
        
    mysql.connection.commit()
    cur.close()
    
    session['username'] = nouveau_nom # Mise à jour de la session
    flash("Votre profil a été mis à jour avec succès.", "success")
    return redirect(url_for('profile.mon_profil'))
