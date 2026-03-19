from app.extensions import orm_db as db


class Admin(db.Model):
    __tablename__ = "admin"

    id_admin = db.Column(db.Integer, primary_key=True)
    nom_admin = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


class Medecin(db.Model):
    __tablename__ = "medecin"

    id_medecin = db.Column(db.Integer, primary_key=True)
    nom_medecin = db.Column(db.String(100), nullable=False)
    specialite = db.Column(db.String(100))
    password_hash = db.Column(db.String(255), nullable=False)
    must_change_password = db.Column(db.Boolean, nullable=False, default=True)


class Infirmier(db.Model):
    __tablename__ = "infirmier"

    id_infirmier = db.Column(db.Integer, primary_key=True)
    nom_infirmier = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    must_change_password = db.Column(db.Boolean, nullable=False, default=True)


class Eleve(db.Model):
    __tablename__ = "eleve"

    id_eleve = db.Column(db.Integer, primary_key=True)
    nom_eleve = db.Column(db.String(100), nullable=False)
    prenom_eleve = db.Column(db.String(100), nullable=False)
    classe = db.Column(db.String(50), nullable=False)
    sexe = db.Column(db.String(1), nullable=False)
    date_naissance = db.Column(db.Date, nullable=False)


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
