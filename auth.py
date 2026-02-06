from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from db import mysql

auth_bp = Blueprint('auth', __name__)

# Route de connexion (GET pour afficher le form, POST pour traiter)
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Récupération des données du formulaire
        user_id = request.form['user_id']
        nom = request.form['nom']
        role = request.form['role']
        
        cur = mysql.connection.cursor()
        user = None
        
        # Vérification selon le rôle (Médecin ou Infirmier)
        if role == 'admin':
            # Compte Admin "en dur" (ID: 0, Nom: Admin) pour la maintenance
            if user_id == '0' and nom == 'Admin':
                user = {'id': 0, 'nom': 'Admin'}
        elif role == 'medecin':
            # Recherche dans la table medecin
            cur.execute("SELECT * FROM medecin WHERE id_medecin = %s AND nom_medecin = %s", (user_id, nom))
            user = cur.fetchone()
        else:
            # Recherche dans la table infirmier
            cur.execute("SELECT * FROM infirmier WHERE id_infirmier = %s AND nom_infirmier = %s", (user_id, nom))
            user = cur.fetchone()

        cur.close()

        if user:
            # Création de la session utilisateur
            session['logged_in'] = True
            session['user_role'] = role
            session['username'] = nom
            
            # Stockage de l'ID pour la gestion du profil et les requêtes SQL futures
            if role == 'medecin':
                session['user_id'] = user['id_medecin']
            elif role == 'infirmier':
                session['user_id'] = user['id_infirmier']
            else:
                session['user_id'] = 0 # Admin
                
            flash(f"Connexion réussie. Bienvenue {role} {nom} !", "success")
            
            # Redirection spécifique selon le rôle
            if role == 'admin':
                return redirect(url_for('admin.panel'))
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash("Accès refusé : Identifiants ou rôle incorrects.", "danger")
            
    return render_template('login.html')

# Route de déconnexion
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for('home'))