from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash

from app.constants import ROLE_ADMIN, ROLE_INFIRMIER, ROLE_MEDECIN
from app.db import mysql

auth_bp = Blueprint('auth', __name__)

# Route de connexion (GET pour afficher le form, POST pour traiter)
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # R?cup?ration des donn?es du formulaire
        user_id = request.form['user_id']
        prenom = request.form.get('prenom', '').strip()
        nom = request.form.get('nom', '').strip()
        role = request.form['role']
        password = request.form.get('password', '')

        def _normalize_name(value):
            return " ".join((value or "").strip().split()).lower()

        def _build_name_candidates(first_name, last_name):
            candidates = []
            full_name = " ".join([p for p in [first_name, last_name] if p]).strip()
            if full_name:
                candidates.append(full_name)
            if first_name and last_name:
                candidates.append(f"{last_name} {first_name}")
            if last_name:
                candidates.append(last_name)
            if first_name:
                candidates.append(first_name)
            return {_normalize_name(c) for c in candidates if _normalize_name(c)}

        name_candidates = _build_name_candidates(prenom, nom)

        cur = mysql.connection.cursor()
        user = None

        # V?rification selon le r?le (M?decin ou Infirmier)
        if role == ROLE_ADMIN:
            cur.execute(
                "SELECT * FROM admin WHERE id_admin = %s",
                (user_id,),
            )
            user = cur.fetchone()
            if user and _normalize_name(user.get('nom_admin', '')) not in name_candidates:
                user = None
        elif role == ROLE_MEDECIN:
            # Recherche dans la table medecin
            cur.execute("SELECT * FROM medecin WHERE id_medecin = %s", (user_id,))
            user = cur.fetchone()
            if user and _normalize_name(user.get('nom_medecin', '')) not in name_candidates:
                user = None
        else:
            # Recherche dans la table infirmier
            cur.execute("SELECT * FROM infirmier WHERE id_infirmier = %s", (user_id,))
            user = cur.fetchone()
            if user and _normalize_name(user.get('nom_infirmier', '')) not in name_candidates:
                user = None

        cur.close()

        if user and check_password_hash(user.get('password_hash', ''), password):
            # Cr?ation de la session utilisateur
            session['logged_in'] = True
            session['user_role'] = role
            session['must_change_password'] = False

            # Stockage de l'ID pour la gestion du profil et les requ?tes SQL futures
            if role == ROLE_MEDECIN:
                session['user_id'] = user['id_medecin']
                session['username'] = user.get('nom_medecin', nom)
                session['must_change_password'] = bool(user.get('must_change_password'))
            elif role == ROLE_INFIRMIER:
                session['user_id'] = user['id_infirmier']
                session['username'] = user.get('nom_infirmier', nom)
                session['must_change_password'] = bool(user.get('must_change_password'))
            else:
                session['user_id'] = user['id_admin'] # Admin
                session['username'] = user.get('nom_admin', nom)

            flash(f"Connexion r?ussie. Bienvenue {role} {session['username']} !", "success")

            # Redirection sp?cifique selon le r?le
            if session.get('must_change_password'):
                return redirect(url_for('auth.change_password'))
            if role == ROLE_ADMIN:
                return redirect(url_for('admin.panel'))
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash("Acc?s refus? : Identifiants, r?le ou mot de passe incorrects.", "danger")

    return render_template('login.html')

# Route de déconnexion
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for('home'))


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

        if role == ROLE_ADMIN:
            cur.execute("SELECT * FROM admin WHERE id_admin = %s", [user_id])
            user = cur.fetchone()
            table = "admin"
            id_col = "id_admin"
        elif role == ROLE_MEDECIN:
            cur.execute("SELECT * FROM medecin WHERE id_medecin = %s", [user_id])
            user = cur.fetchone()
            table = "medecin"
            id_col = "id_medecin"
        else:
            cur.execute("SELECT * FROM infirmier WHERE id_infirmier = %s", [user_id])
            user = cur.fetchone()
            table = "infirmier"
            id_col = "id_infirmier"

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
