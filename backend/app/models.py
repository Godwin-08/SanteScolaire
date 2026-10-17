from app.extensions import orm_db as db
from datetime import datetime


class Admin(db.Model):
    __tablename__ = "admin"

    id_admin = db.Column(db.Integer, primary_key=True)
    nom_admin = db.Column(db.String(100), nullable=False)
    prenom_admin = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(191), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    activation_token_hash = db.Column(db.String(64), nullable=True)
    activation_expires_at = db.Column(db.DateTime, nullable=True)


class Specialite(db.Model):
    __tablename__ = "specialite"

    id_specialite = db.Column(db.Integer, primary_key=True)
    nom_specialite = db.Column(db.String(100), nullable=False, unique=True)
    code_specialite = db.Column(db.String(20))
    description = db.Column(db.String(255))
    medecins = db.relationship("Medecin", backref="specialite_ref", lazy=True)


class Medecin(db.Model):
    __tablename__ = "medecin"

    id_medecin = db.Column(db.Integer, primary_key=True)
    nom_medecin = db.Column(db.String(100), nullable=False)
    prenom_medecin = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(191), nullable=False, unique=True)
    specialite = db.Column(db.String(100))
    id_specialite = db.Column(db.Integer, db.ForeignKey("specialite.id_specialite"), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    must_change_password = db.Column(db.Boolean, nullable=False, default=False)
    activation_token_hash = db.Column(db.String(64), nullable=True)
    activation_expires_at = db.Column(db.DateTime, nullable=True)


class Infirmier(db.Model):
    __tablename__ = "infirmier"

    id_infirmier = db.Column(db.Integer, primary_key=True)
    nom_infirmier = db.Column(db.String(100), nullable=False)
    prenom_infirmier = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(191), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    must_change_password = db.Column(db.Boolean, nullable=False, default=False)
    activation_token_hash = db.Column(db.String(64), nullable=True)
    activation_expires_at = db.Column(db.DateTime, nullable=True)


class Classe(db.Model):
    __tablename__ = "classe"

    id_classe = db.Column(db.Integer, primary_key=True)
    nom_classe = db.Column(db.String(50), nullable=False, unique=True)
    niveau = db.Column(db.String(50), nullable=False)
    filiere = db.Column(db.String(100), nullable=True)
    annee_scolaire = db.Column(db.String(20), nullable=False, default="2025-2026")
    eleves = db.relationship("Eleve", backref="classe_ref", lazy=True)


class Eleve(db.Model):
    __tablename__ = "eleve"

    id_eleve = db.Column(db.Integer, primary_key=True)
    nom_eleve = db.Column(db.String(100), nullable=False)
    prenom_eleve = db.Column(db.String(100), nullable=False)
    classe = db.Column(db.String(50), nullable=False)
    id_classe = db.Column(db.Integer, db.ForeignKey("classe.id_classe"), nullable=True)
    sexe = db.Column(db.String(1), nullable=False)
    date_naissance = db.Column(db.Date, nullable=False)
    antecedents = db.relationship("AntecedentMedical", backref="eleve_ref", lazy=True, cascade="all, delete-orphan")


class AntecedentMedical(db.Model):
    __tablename__ = "antecedent_medical"

    id_antecedent = db.Column(db.Integer, primary_key=True)
    id_eleve = db.Column(db.Integer, db.ForeignKey("eleve.id_eleve"), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severite = db.Column(db.Enum("Faible", "Moyenne", "Critique"), nullable=False, default="Moyenne")
    conduite_a_tenir = db.Column(db.Text, nullable=True)
    pai_signe = db.Column(db.Boolean, nullable=False, default=False)
    date_declaration = db.Column(db.Date, nullable=True)


class StockMedicament(db.Model):
    __tablename__ = "stock_medicament"

    id_medicament = db.Column(db.Integer, primary_key=True)
    nom_medicament = db.Column(db.String(150), nullable=False)
    forme = db.Column(db.String(50), nullable=False)
    quantite_stock = db.Column(db.Integer, nullable=False, default=0)
    seuil_alerte = db.Column(db.Integer, nullable=False, default=10)
    unite_mesure = db.Column(db.String(30), default="boîtes")
    date_peremption = db.Column(db.Date, nullable=True)

    @property
    def est_en_alerte(self):
        return self.quantite_stock <= self.seuil_alerte


class AuditLog(db.Model):
    __tablename__ = "audit_log"

    id_log = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Consultation(db.Model):
    __tablename__ = "consultation"

    id_consult = db.Column(db.Integer, primary_key=True)
    date_consult = db.Column(db.DateTime, nullable=False)
    motif = db.Column(db.String(255), nullable=False)
    observations = db.Column(db.Text)
    id_eleve = db.Column(db.Integer, db.ForeignKey("eleve.id_eleve"), nullable=False)
    id_medecin = db.Column(db.Integer, db.ForeignKey("medecin.id_medecin"))
    id_infirmier = db.Column(db.Integer, db.ForeignKey("infirmier.id_infirmier"))
    poids = db.Column(db.Numeric(5, 2))
    taille = db.Column(db.Numeric(5, 2))
    temperature = db.Column(db.Numeric(4, 1))
    tension = db.Column(db.String(20))
    eleve = db.relationship("Eleve", backref="consultations", lazy=True)
    prescriptions = db.relationship("Prescription", backref="consultation", lazy=True, cascade="all, delete-orphan")


class Prescription(db.Model):
    __tablename__ = "prescription"

    id_prescription = db.Column(db.Integer, primary_key=True)
    medicament = db.Column(db.String(255), nullable=False)
    dosage = db.Column(db.String(100))
    duree = db.Column(db.String(100))
    id_consult = db.Column(db.Integer, db.ForeignKey("consultation.id_consult"), nullable=False)


class Rdv(db.Model):
    __tablename__ = "rdv"

    id_rdv = db.Column(db.Integer, primary_key=True)
    id_eleve = db.Column(db.Integer, db.ForeignKey("eleve.id_eleve"), nullable=False)
    date_rdv = db.Column(db.DateTime, nullable=False)
    id_medecin = db.Column(db.Integer, db.ForeignKey("medecin.id_medecin"), nullable=False)
    statut = db.Column(db.String(20))
    eleve = db.relationship("Eleve", backref="rdvs", lazy=True)
    medecin = db.relationship("Medecin", backref="rdvs", lazy=True)
