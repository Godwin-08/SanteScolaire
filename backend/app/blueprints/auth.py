from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash

from app import utils
from app.constants import ROLE_ADMIN, ROLE_INFIRMIER, ROLE_MEDECIN
from app.db import mysql
from app.services.email_service import send_welcome_email

auth_bp = Blueprint('auth', __name__)

# Route de connexion (GET pour afficher le form, POST pour traiter)
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Si l'utilisateur est déjà connecté, on le redirige vers le dashboard
    # Commentez ces deux lignes temporairement si vous voulez forcer l'affichage pour le design
    if session.get('logged_in'):
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        role = request.form['role']
        password = request.form.get('password', '')

        cur = mysql.connection.cursor()
        user = None

        # Mapping des tables et colonnes par rôle
        role_map = {
            ROLE_ADMIN: ('admin', 'id_admin', 'nom_admin', 'prenom_admin'),
            ROLE_MEDECIN: ('medecin', 'id_medecin', 'nom_medecin', 'prenom_medecin'),
            ROLE_INFIRMIER: ('infirmier', 'id_infirmier', 'nom_infirmier', 'prenom_infirmier')
        }

        if role not in role_map:
            flash("Rôle invalide.", "danger")
            return render_template('login.html')

        table, id_col, nom_col, prenom_col = role_map[role]
        
        # Sécurité : On utilise l'ID pour la recherche primaire
        cur.execute(f"SELECT * FROM {table} WHERE {id_col} = %s", (user_id,))
        user = cur.fetchone()

        cur.close()

        if user and check_password_hash(user.get('password_hash', ''), password):
            # Protection contre la fixation de session
            session.clear()
            session['logged_in'] = True
            session['user_role'] = role
            session['must_change_password'] = False
            session['user_id'] = user[id_col]
            session['username'] = f"{user.get(prenom_col, '')} {user.get(nom_col, '')}".strip() or "Utilisateur"

            if role in [ROLE_MEDECIN, ROLE_INFIRMIER]:
                session['must_change_password'] = bool(user.get('must_change_password'))

            flash(f"Connexion réussie. Bienvenue {session['username']} !", "success")

            if session.get('must_change_password'):
                return redirect(url_for('auth.change_password'))
            if role == ROLE_ADMIN:
                return redirect(url_for('admin.panel'))
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash("Accès refusé : Identifiant ou mot de passe incorrect.", "danger")

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('logged_in'):
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        prenom = request.form.get('prenom', '').strip()
        nom = request.form.get('nom', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not prenom or not nom or not email or not role or not password:
            flash("Tous les champs sont obligatoires.", "danger")
            return render_template('register.html')

        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "danger")
            return render_template('register.html')

        cur = mysql.connection.cursor()
        
        role_map = {
            ROLE_ADMIN: 'admin',
            ROLE_MEDECIN: 'medecin',
            ROLE_INFIRMIER: 'infirmier'
        }

        if role not in role_map:
            flash("Rôle invalide.", "danger")
            return render_template('register.html')

        table = role_map[role]
        hashed_pw = generate_password_hash(password)

        try:
            # Insertion du nouvel utilisateur
            if role == ROLE_MEDECIN:
                cur.execute(f"INSERT INTO {table} (nom_medecin, prenom_medecin, password_hash, must_change_password) VALUES (%s, %s, %s, 0)", (nom, prenom, hashed_pw))
            elif role == ROLE_INFIRMIER:
                cur.execute(f"INSERT INTO {table} (nom_infirmier, prenom_infirmier, password_hash, must_change_password) VALUES (%s, %s, %s, 0)", (nom, prenom, hashed_pw))
            else:
                cur.execute(f"INSERT INTO {table} (nom_admin, prenom_admin, password_hash) VALUES (%s, %s, %s)", (nom, prenom, hashed_pw))
            
            # Récupération de l'ID généré par MySQL
            new_id = cur.lastrowid
            
            mysql.connection.commit()

            # Sauvegarde de l'email via le système utilitaire du projet
            if email:
                emails_data = utils.get_emails()
                # Note: On peut préfixer la clé pour éviter les collisions d'ID entre tables
                key = f"{role}_{new_id}"
                emails_data[key] = email
                utils.save_emails_data(emails_data)

            # Envoi de l'email de bienvenue avec les infos de connexion
            try:
                send_welcome_email(email, f"{prenom} {nom}", new_id, role)
            except Exception as e:
                print(f"Erreur d'envoi mail: {e}")

            flash(f"Compte créé avec succès ! Votre identifiant de connexion est : {new_id}. Notez-le bien.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Erreur lors de la création : {str(e)}", "danger")
        finally:
            cur.close()

    return render_template('register.html')

# Route de déconnexion
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    role = session.get('user_role')
    user_id = session.get('user_id')

    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not new_password or new_password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "warning")
            return redirect(url_for('auth.change_password'))

        cur = mysql.connection.cursor()
        
        # Utilisation du mapping pour la cohérence avec la fonction login
        role_map = {
            ROLE_ADMIN: ('admin', 'id_admin'),
            ROLE_MEDECIN: ('medecin', 'id_medecin'),
            ROLE_INFIRMIER: ('infirmier', 'id_infirmier')
        }

        if role not in role_map:
            flash("Session invalide.", "danger")
            return redirect(url_for('auth.logout'))

        table, id_col = role_map[role]
        cur.execute(f"SELECT * FROM {table} WHERE {id_col} = %s", [user_id])
        user = cur.fetchone()

        if not user or not check_password_hash(user.get('password_hash', ''), current_password):
            cur.close()
            flash("Mot de passe actuel incorrect.", "danger")
            return redirect(url_for('auth.change_password'))

        cur.execute(
            f"UPDATE {table} SET password_hash = %s WHERE {id_col} = %s",
            (generate_password_hash(new_password), user_id),
        )

        if role in [ROLE_MEDECIN, ROLE_INFIRMIER]:
            cur.execute(
                f"UPDATE {table} SET must_change_password = 0 WHERE {id_col} = %s",
                [user_id],
            )

        mysql.connection.commit()
        cur.close()

        session['must_change_password'] = False
        flash("Mot de passe mis à jour avec succès.", "success")

        if role == ROLE_ADMIN:
            return redirect(url_for('admin.panel'))
        return redirect(url_for('dashboard.dashboard'))

    return render_template('change_password.html')
