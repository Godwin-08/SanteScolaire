import hashlib
import hmac
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash

from app.constants import ROLE_ADMIN, ROLE_INFIRMIER, ROLE_MEDECIN
from app.db import mysql
from app.services.email_service import send_welcome_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        identifier = (request.form.get('email') or request.form.get('user_id') or '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role')

        if not identifier or not password:
            flash("Veuillez saisir votre email et votre mot de passe.", "danger")
            return render_template('login.html')

        cur = mysql.connection.cursor()
        user = None
        user_role = None
        id_col = None
        nom_col = None
        prenom_col = None

        role_configs = [
            (ROLE_ADMIN, 'admin', 'id_admin', 'nom_admin', 'prenom_admin'),
            (ROLE_MEDECIN, 'medecin', 'id_medecin', 'nom_medecin', 'prenom_medecin'),
            (ROLE_INFIRMIER, 'infirmier', 'id_infirmier', 'nom_infirmier', 'prenom_infirmier'),
        ]

        if role and role in [ROLE_ADMIN, ROLE_MEDECIN, ROLE_INFIRMIER]:
            role_configs = [c for c in role_configs if c[0] == role] + [c for c in role_configs if c[0] != role]

        for r_name, t_name, i_col, n_col, p_col in role_configs:
            if identifier.isdigit():
                cur.execute(f"SELECT * FROM {t_name} WHERE LOWER(email) = %s OR {i_col} = %s", (identifier, int(identifier)))
            else:
                cur.execute(f"SELECT * FROM {t_name} WHERE LOWER(email) = %s", (identifier,))
            
            row = cur.fetchone()
            if row:
                user = row
                user_role = r_name
                id_col = i_col
                nom_col = n_col
                prenom_col = p_col
                break

        cur.close()

        if user:
            pw_hash = user.get('password_hash', '')
            # Vérifier si le compte est en attente d'activation
            if user.get('activation_token_hash') and (not pw_hash or pw_hash.startswith('unactivated:')):
                flash("Ce compte n'est pas encore activé. Veuillez cliquer sur le lien sécurisé reçu par email pour définir votre mot de passe (valable 48h).", "warning")
                return render_template('login.html')

            if check_password_hash(pw_hash, password):
                session.clear()
                session['logged_in'] = True
                session['user_role'] = user_role
                session['must_change_password'] = False
                session['user_id'] = user[id_col]
                session['user_email'] = user.get('email', '')
                session['username'] = f"{user.get(prenom_col, '')} {user.get(nom_col, '')}".strip() or "Utilisateur"

                if user_role in [ROLE_MEDECIN, ROLE_INFIRMIER]:
                    session['must_change_password'] = bool(user.get('must_change_password'))

                flash(f"Connexion réussie. Bienvenue {session['username']} !", "success")

                if session.get('must_change_password'):
                    return redirect(url_for('auth.change_password'))
                if user_role == ROLE_ADMIN:
                    return redirect(url_for('admin.panel'))
                return redirect(url_for('dashboard.dashboard'))

        flash("Accès refusé : Email ou mot de passe incorrect.", "danger")

    return render_template('login.html')

@auth_bp.route('/activate', methods=['GET', 'POST'])
def activate_account():
    token = (request.args.get('token') if request.method == 'GET' else request.form.get('token')) or ''
    token = token.strip()

    if not token:
        flash("Lien d'activation manquant ou invalide.", "danger")
        return redirect(url_for('auth.login'))

    # Calcul de l'empreinte SHA-256 du token
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    now = datetime.now()

    cur = mysql.connection.cursor()
    target_user = None
    target_role = None
    target_table = None
    target_id_col = None
    user_nom = ""
    user_prenom = ""

    # Recherche du compte correspondant au token (non expiré, fenêtre 48h)
    for r_name, t_name, i_col, n_col, p_col in [
        (ROLE_ADMIN, 'admin', 'id_admin', 'nom_admin', 'prenom_admin'),
        (ROLE_MEDECIN, 'medecin', 'id_medecin', 'nom_medecin', 'prenom_medecin'),
        (ROLE_INFIRMIER, 'infirmier', 'id_infirmier', 'nom_infirmier', 'prenom_infirmier'),
    ]:
        cur.execute(
            f"SELECT * FROM {t_name} WHERE activation_token_hash IS NOT NULL AND activation_expires_at > %s",
            (now,)
        )
        candidates = cur.fetchall()
        for cand in candidates:
            stored_hash = cand.get('activation_token_hash') or ''
            # Comparaison en temps constant avec hmac.compare_digest
            if hmac.compare_digest(token_hash, stored_hash):
                target_user = cand
                target_role = r_name
                target_table = t_name
                target_id_col = i_col
                user_nom = cand.get(n_col, '')
                user_prenom = cand.get(p_col, '')
                break
        if target_user:
            break

    if not target_user:
        cur.close()
        flash("Ce lien d'activation est invalide ou a expiré (validité de 48 heures). Veuillez contacter l'administrateur.", "danger")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not password or len(password) < 6:
            cur.close()
            flash("Le mot de passe doit comporter au moins 6 caractères.", "warning")
            return render_template('activate.html', token=token, email=target_user['email'], user_name=f"{user_prenom} {user_nom}", role=target_role)

        if password != confirm_password:
            cur.close()
            flash("Les mots de passe ne correspondent pas.", "warning")
            return render_template('activate.html', token=token, email=target_user['email'], user_name=f"{user_prenom} {user_nom}", role=target_role)

        hashed_pw = generate_password_hash(password)
        try:
            # Enregistrement du mot de passe définitif et suppression du token (usage unique)
            cur.execute(
                f"""UPDATE {target_table} 
                   SET password_hash = %s, activation_token_hash = NULL, activation_expires_at = NULL, must_change_password = 0 
                   WHERE {target_id_col} = %s""",
                (hashed_pw, target_user[target_id_col])
            )
            mysql.connection.commit()
            
            # Déconnecter toute session précédente (admin) et connecter immédiatement le praticien
            session.clear()
            session['logged_in'] = True
            session['user_role'] = target_role
            session['user_id'] = target_user[target_id_col]
            session['user_email'] = target_user['email']
            display_name = f"{user_prenom} {user_nom}".strip() or "Praticien"
            if target_role == ROLE_MEDECIN and not display_name.lower().startswith('dr.'):
                display_name = f"Dr. {display_name}"
            session['username'] = display_name
            session['must_change_password'] = False

            flash(f"Félicitations {display_name} ! Votre compte est activé avec succès. Bienvenue sur votre espace clinique.", "success")
            
            if target_role == ROLE_ADMIN:
                return redirect(url_for('admin.panel'))
            return redirect(url_for('dashboard.dashboard'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Erreur lors de l'activation : {str(e)}", "danger")
        finally:
            cur.close()

    cur.close()
    return render_template('activate.html', token=token, email=target_user['email'], user_name=f"{user_prenom} {user_nom}", role=target_role)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Protection sécurité : l'inscription publique est désactivée.
    # Les comptes soignants sont créés uniquement par l'Administration via token d'activation.
    flash("L'accès à SanteScolaire est strictement restreint. Les comptes sont créés par l'administration via un lien d'activation sécurisé.", "info")
    return redirect(url_for('auth.login'))

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
