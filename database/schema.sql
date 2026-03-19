-- SanteScolaire schema
-- Charset: utf8mb4 to support accents

CREATE DATABASE IF NOT EXISTS gestion_hospitaliere_scolaire
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE gestion_hospitaliere_scolaire;

CREATE TABLE IF NOT EXISTS admin (
  id_admin INT AUTO_INCREMENT PRIMARY KEY,
  nom_admin VARCHAR(100) NOT NULL,
  password_hash VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS medecin (
  id_medecin INT AUTO_INCREMENT PRIMARY KEY,
  nom_medecin VARCHAR(100) NOT NULL,
  specialite VARCHAR(100) DEFAULT NULL,
  password_hash VARCHAR(255) NOT NULL,
  must_change_password TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS infirmier (
  id_infirmier INT AUTO_INCREMENT PRIMARY KEY,
  nom_infirmier VARCHAR(100) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  must_change_password TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS eleve (
  id_eleve INT AUTO_INCREMENT PRIMARY KEY,
  nom_eleve VARCHAR(100) NOT NULL,
  prenom_eleve VARCHAR(100) NOT NULL,
  classe VARCHAR(50) NOT NULL,
  sexe ENUM('M','F') NOT NULL,
  date_naissance DATE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS consultation (
  id_consult INT AUTO_INCREMENT PRIMARY KEY,
  date_consult DATETIME NOT NULL,
  motif VARCHAR(255) NOT NULL,
  observations TEXT,
  id_eleve INT NOT NULL,
  id_medecin INT DEFAULT NULL,
  id_infirmier INT DEFAULT NULL,
  poids DECIMAL(5,2) DEFAULT NULL,
  taille DECIMAL(5,2) DEFAULT NULL,
  temperature DECIMAL(4,1) DEFAULT NULL,
  tension VARCHAR(20) DEFAULT NULL,
  CONSTRAINT fk_consultation_eleve
    FOREIGN KEY (id_eleve) REFERENCES eleve(id_eleve)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_consultation_medecin
    FOREIGN KEY (id_medecin) REFERENCES medecin(id_medecin)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_consultation_infirmier
    FOREIGN KEY (id_infirmier) REFERENCES infirmier(id_infirmier)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS prescription (
  id_prescription INT AUTO_INCREMENT PRIMARY KEY,
  medicament VARCHAR(255) NOT NULL,
  dosage VARCHAR(100) DEFAULT NULL,
  duree VARCHAR(100) DEFAULT NULL,
  id_consult INT NOT NULL,
  CONSTRAINT fk_prescription_consultation
    FOREIGN KEY (id_consult) REFERENCES consultation(id_consult)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS rdv (
  id_rdv INT AUTO_INCREMENT PRIMARY KEY,
  id_eleve INT NOT NULL,
  date_rdv DATETIME NOT NULL,
  id_medecin INT NOT NULL,
  statut VARCHAR(20) DEFAULT NULL,
  CONSTRAINT fk_rdv_eleve
    FOREIGN KEY (id_eleve) REFERENCES eleve(id_eleve)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_rdv_medecin
    FOREIGN KEY (id_medecin) REFERENCES medecin(id_medecin)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_eleve_classe ON eleve (classe);
CREATE INDEX idx_consultation_eleve ON consultation (id_eleve);
CREATE INDEX idx_consultation_medecin ON consultation (id_medecin);
CREATE INDEX idx_consultation_infirmier ON consultation (id_infirmier);
CREATE INDEX idx_rdv_eleve ON rdv (id_eleve);
CREATE INDEX idx_rdv_medecin ON rdv (id_medecin);
