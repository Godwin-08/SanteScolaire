from flask import Flask, render_template, session, redirect, url_for

from app.config import Config
from app.constants import ROLE_ADMIN
from app.db import mysql
from app.extensions import migrate, orm_db
from app.blueprints.auth import auth_bp
from app.blueprints.eleves import eleves_bp
from app.blueprints.consultations import consultations_bp
from app.blueprints.dashboard import dashboard_bp
from app.blueprints.admin import admin_bp
from app.blueprints.profile import profile_bp


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config())
    app.secret_key = app.config["SECRET_KEY"]

    if app.config["MYSQL_PASSWORD"] is None:
        raise RuntimeError(
            "DB_PASSWORD n'est pas defini. Ajoute-le dans un fichier .env ou dans les variables d'environnement."
        )

    orm_db.init_app(app)
    migrate.init_app(app, orm_db)

    mysql.init_app(app)

    # Import models for migration autogenerate
    from app import models  # noqa: F401

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(eleves_bp)
    app.register_blueprint(consultations_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(profile_bp)

    # Landing page
    @app.route("/")
    def home():
        if session.get("logged_in"):
            if session.get("user_role") == ROLE_ADMIN:
                return redirect(url_for("admin.panel"))
            return redirect(url_for("dashboard.dashboard"))
        return render_template("landing.html")

    return app
