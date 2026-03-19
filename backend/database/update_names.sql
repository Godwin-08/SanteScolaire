-- Script de migration pour separer Nom et Prenom (idempotent)
USE gestion_hospitaliere_scolaire;

-- Admin
SET @db = DATABASE();
SET @sql = (
  SELECT IF(
    EXISTS(
      SELECT 1
      FROM information_schema.columns
      WHERE table_schema = @db
        AND table_name = 'admin'
        AND column_name = 'prenom_admin'
    ),
    'SELECT 1',
    'ALTER TABLE admin ADD COLUMN prenom_admin VARCHAR(100) NOT NULL AFTER nom_admin'
  )
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Medecin
SET @sql = (
  SELECT IF(
    EXISTS(
      SELECT 1
      FROM information_schema.columns
      WHERE table_schema = @db
        AND table_name = 'medecin'
        AND column_name = 'prenom_medecin'
    ),
    'SELECT 1',
    'ALTER TABLE medecin ADD COLUMN prenom_medecin VARCHAR(100) NOT NULL AFTER nom_medecin'
  )
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Infirmier
SET @sql = (
  SELECT IF(
    EXISTS(
      SELECT 1
      FROM information_schema.columns
      WHERE table_schema = @db
        AND table_name = 'infirmier'
        AND column_name = 'prenom_infirmier'
    ),
    'SELECT 1',
    'ALTER TABLE infirmier ADD COLUMN prenom_infirmier VARCHAR(100) NOT NULL AFTER nom_infirmier'
  )
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
