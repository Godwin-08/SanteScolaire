-- Donnees de demo pour SanteScolaire
-- A utiliser apres database/schema.sql

USE gestion_hospitaliere_scolaire;

-- Nettoyage (idempotent)
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE prescription;
TRUNCATE TABLE consultation;
TRUNCATE TABLE rdv;
TRUNCATE TABLE eleve;
TRUNCATE TABLE medecin;
TRUNCATE TABLE infirmier;
TRUNCATE TABLE admin;
SET FOREIGN_KEY_CHECKS = 1;

-- Compte admin (mot de passe: admin123)
INSERT INTO admin (id_admin, nom_admin, password_hash) VALUES
  (1, 'Admin', 'scrypt:32768:8:1$8GT0FiCnSaa2U9If$bb3499f3f4e6a743159a2b9687c75725747d1ccfda2e22a3d5c4e057b877c6d5f44c08d97fddc4e4035c5a87e852bc492e04c0ca2de795b12eaaff1fcf1cacb1');

-- Personnel medical
-- Mot de passe medecin: format NOM4-ID-M (a changer a la 1ere connexion)
INSERT INTO medecin (id_medecin, nom_medecin, specialite, password_hash, must_change_password) VALUES
  (1, 'Karim Amrani', 'Generaliste', 'scrypt:32768:8:1$DpSlN2F6537eIp0s$429745b8f855665f1007e0cc448c0e45e96ff0211e3440d12c7514bd13d9e877f50c649f4bc613be266eebb0bc14403ff1ca6ea052d04d8df56293fcb19c4522', 1),
  (2, 'Samira El Fassi', 'Pediatre', 'scrypt:32768:8:1$48JfcNkhrcjWKhMj$2cc107596be0d21083c228b4bcd4b5fa8ed2a5ada1a881ae6d928504cbb0f89cce335a8c643d05a8a24911cd8ad7fc6f54c657919685ce168b5d1b2e040c88d4', 1),
  (3, 'Hicham Boussaid', 'ORL', 'scrypt:32768:8:1$LF1HRW3qu6UlQLQM$e19c618560a3e051e15bb22c5c53f17e3522b759afe4ac5106df69ebc52b0c03028a466a12c0dbbf532e16e4dee40177f24e9b2d1c6b77c8e7569c72327b78ec', 1);

-- Mot de passe infirmier: format NOM4-ID-I (a changer a la 1ere connexion)
INSERT INTO infirmier (id_infirmier, nom_infirmier, password_hash, must_change_password) VALUES
  (1, 'Youssef Berrada', 'scrypt:32768:8:1$Q88A1JtSBipPA6I2$4c546dbf4777a889ebf7c2aabb5eb184bd584aa714ced510b5ae7135b000431d92cf17c8c3d31809402fc11f68fb5df94451a46c9053842dc989d98d13756488', 1),
  (2, 'Imane Rachidi', 'scrypt:32768:8:1$EpTtW1PqYvn6uA8u$139a649c617448bdedaa5db8662703b1767e4cb77c5ab306c1d7520d2e77a8e56686286dd35f0a07dfdaa9647f461ae802b2cabb5ef8837ea9f51a820f38f6d1', 1);

-- Eleves
INSERT INTO eleve (id_eleve, nom_eleve, prenom_eleve, classe, sexe, date_naissance) VALUES
  (1, 'Alaoui', 'Nadia', '3A', 'F', '2011-04-12'),
  (2, 'Benali', 'Omar', '2B', 'M', '2012-09-23'),
  (3, 'El Idrissi', 'Sara', '1C', 'F', '2013-01-15'),
  (4, 'Zahra', 'Anas', '3B', 'M', '2011-11-05'),
  (5, 'Fassi', 'Lina', '2A', 'F', '2012-05-30'),
  (6, 'Razi', 'Younes', '1A', 'M', '2013-07-19');

-- Rendez-vous (mix: programme, annule, fait)
INSERT INTO rdv (id_rdv, id_eleve, date_rdv, id_medecin, statut) VALUES
  (1, 1, DATE_ADD(NOW(), INTERVAL 1 DAY), 1, 'programmé'),
  (2, 2, DATE_ADD(NOW(), INTERVAL 2 DAY), 2, 'programmé'),
  (3, 3, DATE_ADD(NOW(), INTERVAL 3 DAY), 3, 'programmé'),
  (4, 4, DATE_SUB(NOW(), INTERVAL 1 DAY), 1, 'fait'),
  (5, 5, DATE_SUB(NOW(), INTERVAL 2 DAY), 2, 'annule');

-- Consultations (derniers 7 jours)
INSERT INTO consultation (
  id_consult, date_consult, motif, observations, id_eleve, id_medecin, id_infirmier, poids, taille, temperature, tension
) VALUES
  (1, DATE_SUB(NOW(), INTERVAL 6 DAY), 'Fievre', 'Repos et hydratation', 1, 1, NULL, 40.5, 150.0, 38.2, '12/8'),
  (2, DATE_SUB(NOW(), INTERVAL 5 DAY), 'Toux', 'Sirop + surveillance', 2, 2, NULL, 42.0, 152.0, 37.8, '12/8'),
  (3, DATE_SUB(NOW(), INTERVAL 4 DAY), 'Maux de tete', 'Repos + hydratation', 3, 1, NULL, 38.0, 147.0, 37.1, '11/7'),
  (4, DATE_SUB(NOW(), INTERVAL 3 DAY), 'Triage', 'Triage Infirmier - Prise de constantes', 4, NULL, 1, 45.2, 155.0, 37.3, '12/8'),
  (5, DATE_SUB(NOW(), INTERVAL 2 DAY), 'Douleur ventre', 'Examens a prevoir', 5, 2, NULL, 41.3, 151.0, 37.4, '12/7'),
  (6, DATE_SUB(NOW(), INTERVAL 1 DAY), 'Allergie', 'Antihistaminique', 6, 3, NULL, 43.0, 153.0, 37.0, '12/8'),
  (7, NOW(), 'Suivi', 'Amelioration', 1, 1, NULL, 40.8, 150.0, 37.0, '12/8');

INSERT INTO prescription (id_prescription, medicament, dosage, duree, id_consult) VALUES
  (1, 'Paracetamol', '500mg', '3 jours', 1),
  (2, 'Sirop toux', '10ml', '5 jours', 2),
  (3, 'Antihistaminique', '1 cp', '7 jours', 6);
