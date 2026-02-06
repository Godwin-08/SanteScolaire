# Importation des modules Flask et de la configuration DB
from flask import Flask, render_template, session, redirect, url_for
from db import mysql
from auth import auth_bp
from eleves import eleves_bp
from consultations import consultations_bp
from dashboard import dashboard_bp
from admin import admin_bp
from profile import profile_bp
import os

app = Flask(__name__)

# Clé secrète pour sécuriser les sessions
app.secret_key = os.environ.get('SECRET_KEY', 'medischool_secret_0805')

# --- CONFIGURATION BASE DE DONNÉES ---
# Paramètres de connexion MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = os.environ.get('DB_PASSWORD', '08052005Godwin@')
app.config['MYSQL_DB'] = 'gestion_hospitaliere_scolaire'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' # Pour récupérer les résultats sous forme de dictionnaire

# Initialisation de l'extension MySQL avec l'application
mysql.init_app(app)

# Enregistrement des Blueprints (Modules de routes)
app.register_blueprint(auth_bp)
app.register_blueprint(eleves_bp)
app.register_blueprint(consultations_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(profile_bp)

# Route pour la Page d'Accueil (Landing Page)
@app.route('/')
def home():
    # Vérifie si l'utilisateur est déjà connecté
    if session.get('logged_in'):
        # Redirection vers le panel admin si c'est un administrateur
        if session.get('user_role') == 'admin':
            return redirect(url_for('admin.panel'))
        # Sinon, redirection vers le tableau de bord standard (Médecin/Infirmier)
        return redirect(url_for('dashboard.dashboard'))
    # Si non connecté, affiche la page d'accueil publique
    return render_template('landing.html')

if __name__ == '__main__':
    app.run(debug=True)