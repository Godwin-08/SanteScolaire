from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from db import mysql
import utils

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profil')
def mon_profil():
    # Vérification de connexion
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
    
    role = session.get('user_role')
    user_id = session.get('user_id')
    
    # Cas Admin (Compte statique) : Pas de requête SQL
    if role == 'admin':
        user = {'nom': 'Admin', 'id': 0, 'role': 'Administrateur'}
        return render_template('profile.html', user=user, is_admin=True)

    cur = mysql.connection.cursor()
    if role == 'medecin':
        # Récupération des infos médecin
        cur.execute("SELECT *, nom_medecin as nom FROM medecin WHERE id_medecin = %s", [user_id])
        user = cur.fetchone()
        # Injection de l'email depuis le JSON auxiliaire
        if user: user['email'] = utils.get_emails().get(str(user_id), '')
    else:
        # Récupération des infos infirmier
        cur.execute("SELECT *, nom_infirmier as nom FROM infirmier WHERE id_infirmier = %s", [user_id])
        user = cur.fetchone()
        
    cur.close()
    
    return render_template('profile.html', user=user, is_admin=False)

@profile_bp.route('/profil/update', methods=['POST'])
def update_profil():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
        
    role = session.get('user_role')
    user_id = session.get('user_id')
    nouveau_nom = request.form['nom']
    
    cur = mysql.connection.cursor()
    
    if role == 'medecin':
        specialite = request.form['specialite']
        email = request.form['email']
        cur.execute("UPDATE medecin SET nom_medecin = %s, specialite = %s WHERE id_medecin = %s", (nouveau_nom, specialite, user_id))
        
        # Mise à jour JSON
        emails_data = utils.get_emails()
        emails_data[str(user_id)] = email
        utils.save_emails_data(emails_data)
    elif role == 'infirmier':
        cur.execute("UPDATE infirmier SET nom_infirmier = %s WHERE id_infirmier = %s", (nouveau_nom, user_id))
        
    mysql.connection.commit()
    cur.close()
    
    session['username'] = nouveau_nom # Mise à jour de la session
    flash("Votre profil a été mis à jour avec succès.", "success")
    return redirect(url_for('profile.mon_profil'))