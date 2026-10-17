-- ========================================================
-- Données de démonstration réalistes pour SanteScolaire (Maroc)
-- Charset: utf8mb4
-- ========================================================

USE gestion_hospitaliere_scolaire;

-- 1. Nettoyage ordonné des données existantes
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE prescription;
TRUNCATE TABLE consultation;
TRUNCATE TABLE rdv;
TRUNCATE TABLE eleve;
TRUNCATE TABLE medecin;
TRUNCATE TABLE infirmier;
TRUNCATE TABLE admin;
SET FOREIGN_KEY_CHECKS = 1;

-- 2. Compte Administrateur
-- Mot de passe : admin123
INSERT INTO admin (id_admin, nom_admin, prenom_admin, email, password_hash) VALUES
  (1, 'El Idrissi', 'Yassine', 'admin@santescolaire.ma', 'scrypt:32768:8:1$iPQipRAWkIlC20ZB$c0d06e705e590211b649ed2f807d01658c455c2d804e5118ac5054c506fd633ef25d224d157801b945637f44e616515a4391f6c2922da7292d56978911b41b3e');

-- 3. Médecins scolaires
-- Mots de passe : Pass1234!
INSERT INTO medecin (id_medecin, nom_medecin, prenom_medecin, email, specialite, password_hash, must_change_password) VALUES
  (1, 'Amrani', 'Karim', 'dr.amrani@santescolaire.ma', 'Médecine Générale', 'scrypt:32768:8:1$2lBZ7tkwhCVXBsRc$72bcbe1da8c38ac6aac7a30b0ffbfe728432abce9ddf1941dbbbafdf994e80ddf7f1bc10d87df0b2aabbfc4d802e48c5f7176070a9f0783b408f68db598fdf89', 0),
  (2, 'El Fassi', 'Samira', 'dr.elfassi@santescolaire.ma', 'Pédiatrie', 'scrypt:32768:8:1$2lBZ7tkwhCVXBsRc$72bcbe1da8c38ac6aac7a30b0ffbfe728432abce9ddf1941dbbbafdf994e80ddf7f1bc10d87df0b2aabbfc4d802e48c5f7176070a9f0783b408f68db598fdf89', 0),
  (3, 'Bennani', 'Mehdi', 'dr.bennani@santescolaire.ma', 'Pédopsychiatrie', 'scrypt:32768:8:1$2lBZ7tkwhCVXBsRc$72bcbe1da8c38ac6aac7a30b0ffbfe728432abce9ddf1941dbbbafdf994e80ddf7f1bc10d87df0b2aabbfc4d802e48c5f7176070a9f0783b408f68db598fdf89', 0),
  (4, 'Boussaid', 'Hicham', 'dr.boussaid@santescolaire.ma', 'ORL & Allergologie', 'scrypt:32768:8:1$2lBZ7tkwhCVXBsRc$72bcbe1da8c38ac6aac7a30b0ffbfe728432abce9ddf1941dbbbafdf994e80ddf7f1bc10d87df0b2aabbfc4d802e48c5f7176070a9f0783b408f68db598fdf89', 0);

-- 4. Infirmiers scolaires
-- Mots de passe : Pass1234!
INSERT INTO infirmier (id_infirmier, nom_infirmier, prenom_infirmier, email, password_hash, must_change_password) VALUES
  (1, 'Berrada', 'Youssef', 'inf.berrada@santescolaire.ma', 'scrypt:32768:8:1$2lBZ7tkwhCVXBsRc$72bcbe1da8c38ac6aac7a30b0ffbfe728432abce9ddf1941dbbbafdf994e80ddf7f1bc10d87df0b2aabbfc4d802e48c5f7176070a9f0783b408f68db598fdf89', 0),
  (2, 'Rachidi', 'Imane', 'inf.rachidi@santescolaire.ma', 'scrypt:32768:8:1$2lBZ7tkwhCVXBsRc$72bcbe1da8c38ac6aac7a30b0ffbfe728432abce9ddf1941dbbbafdf994e80ddf7f1bc10d87df0b2aabbfc4d802e48c5f7176070a9f0783b408f68db598fdf89', 0),
  (3, 'Tazi', 'Kenza', 'inf.tazi@santescolaire.ma', 'scrypt:32768:8:1$2lBZ7tkwhCVXBsRc$72bcbe1da8c38ac6aac7a30b0ffbfe728432abce9ddf1941dbbbafdf994e80ddf7f1bc10d87df0b2aabbfc4d802e48c5f7176070a9f0783b408f68db598fdf89', 0);

-- 5. Élèves (30 profils variés répartis sur le Collège et le Lycée)
INSERT INTO eleve (id_eleve, nom_eleve, prenom_eleve, classe, sexe, date_naissance) VALUES
  (1, 'Alaoui', 'Nadia', '1AC-1', 'F', '2013-04-12'),
  (2, 'Benali', 'Omar', '1AC-1', 'M', '2013-09-23'),
  (3, 'El Idrissi', 'Sara', '1AC-2', 'F', '2013-01-15'),
  (4, 'Zahra', 'Anas', '2AC-1', 'M', '2012-11-05'),
  (5, 'Fassi', 'Lina', '2AC-1', 'F', '2012-05-30'),
  (6, 'Razi', 'Younes', '2AC-2', 'M', '2012-07-19'),
  (7, 'Alami', 'Mehdi', '3AC-1', 'M', '2011-03-08'),
  (8, 'Berrada', 'Salma', '3AC-1', 'F', '2011-08-22'),
  (9, 'Chraibi', 'Hamza', '3AC-2', 'M', '2011-12-14'),
  (10, 'Kabbaj', 'Hiba', '3AC-2', 'F', '2011-02-17'),
  (11, 'Mansouri', 'Yassine', 'TCS-1', 'M', '2010-06-25'),
  (12, 'Amrani', 'Kenza', 'TCS-1', 'F', '2010-10-03'),
  (13, 'Tazi', 'Amine', 'TCS-2', 'M', '2010-01-29'),
  (14, 'Slaoui', 'Malak', 'TCS-2', 'F', '2010-04-18'),
  (15, 'Bennouna', 'Adam', '1BAC-SM', 'M', '2009-09-11'),
  (16, 'Filali', 'Rania', '1BAC-SM', 'F', '2009-11-07'),
  (17, 'Bouziane', 'Saad', '1BAC-SE', 'M', '2009-03-16'),
  (18, 'Zaki', 'Yasmine', '1BAC-SE', 'F', '2009-08-05'),
  (19, 'El Harti', 'Rayan', '1BAC-SE', 'M', '2009-12-28'),
  (20, 'Benjelloun', 'Nour', '2BAC-PC', 'F', '2008-05-14'),
  (21, 'Bennis', 'Walid', '2BAC-PC', 'M', '2008-02-20'),
  (22, 'Chaoui', 'Ines', '2BAC-PC', 'F', '2008-07-09'),
  (23, 'Jamai', 'Reda', '2BAC-SVT', 'M', '2008-10-31'),
  (24, 'Mezouar', 'Aya', '2BAC-SVT', 'F', '2008-01-24'),
  (25, 'Touhami', 'Karim', '2BAC-SM', 'M', '2008-04-03'),
  (26, 'Belkacem', 'Rim', '2BAC-SM', 'F', '2008-09-19'),
  (27, 'Naciri', 'Zakaria', '1AC-2', 'M', '2013-06-11'),
  (28, 'Daoudi', 'Imane', '2AC-2', 'F', '2012-10-02'),
  (29, 'Tahiri', 'Marouane', '3AC-1', 'M', '2011-05-15'),
  (30, 'Kadiri', 'Chaimaa', 'TCS-1', 'F', '2010-08-27');

-- 6. Consultations médicales réalistes (étalées dans le temps)
INSERT INTO consultation (id_consult, date_consult, motif, observations, id_eleve, id_medecin, id_infirmier, poids, taille, temperature, tension) VALUES
  (1, DATE_SUB(NOW(), INTERVAL 28 DAY), 'Bilan médical d entrée', 'Examen général normal. Bonne croissance staturo-pondérale.', 1, 1, NULL, 39.5, 148.0, 37.0, '11/7'),
  (2, DATE_SUB(NOW(), INTERVAL 26 DAY), 'Entorse cheville droite en EPS', 'Gonflement malléolaire externe, pas de craquement audible. Cryothérapie et bandage.', 2, NULL, 1, 45.0, 154.0, 36.8, '12/8'),
  (3, DATE_SUB(NOW(), INTERVAL 25 DAY), 'Contrôle entorse cheville', 'Amélioration, appui possible sans douleur vive. Dispense EPS de 10 jours accordée.', 2, 1, NULL, 45.0, 154.0, 36.9, '12/8'),
  (4, DATE_SUB(NOW(), INTERVAL 23 DAY), 'Céphalées et fatigue oculaire', 'Baisse d acuité visuelle suspectée au tableau. Consultation ophtalmologique conseillée.', 3, 2, NULL, 37.5, 145.0, 37.1, '11/7'),
  (5, DATE_SUB(NOW(), INTERVAL 21 DAY), 'Crise d asthme aiguë', 'Dyspnée expiratoire sifflante post-effort. Traitement par bronchodilatateur en spray.', 4, 1, NULL, 48.0, 158.0, 37.2, '12/8'),
  (6, DATE_SUB(NOW(), INTERVAL 20 DAY), 'Plaie arcade sourcilière', 'Chute dans la cour. Plaie superficielle désinfectée et rapprochée par sutures adhésives.', 5, NULL, 2, 42.0, 152.0, 36.7, '11/7'),
  (7, DATE_SUB(NOW(), INTERVAL 18 DAY), 'Douleurs abdominales aiguës', 'Douleurs péri-ombilicales sans défense ni fièvre. Spasmes digestifs liés au stress.', 6, 2, NULL, 46.5, 156.0, 37.0, '12/7'),
  (8, DATE_SUB(NOW(), INTERVAL 16 DAY), 'Rhinite allergique sévère', 'Éternuements en salves, prurit nasal et conjonctivite saisonnière printanière.', 7, 4, NULL, 52.0, 163.0, 36.9, '12/8'),
  (9, DATE_SUB(NOW(), INTERVAL 15 DAY), 'Malaise vagal en classe', 'Hypoglycémie matinale (absence de petit-déjeuner). Repos et collation sucrée.', 8, NULL, 1, 44.0, 155.0, 36.6, '10/6'),
  (10, DATE_SUB(NOW(), INTERVAL 13 DAY), 'Fièvre 38.8 et mal de gorge', 'Angine érythémato-pultacée, adénopathies sous-maxillaires sensibles. Traitement antibiotique.', 9, 1, NULL, 50.0, 161.0, 38.8, '12/8'),
  (11, DATE_SUB(NOW(), INTERVAL 12 DAY), 'Épistaxis spontané', 'Saignement de nez antérieur jugulé par compression bidigitale et mèche hémostatique.', 10, NULL, 3, 43.5, 153.0, 37.0, '11/7'),
  (12, DATE_SUB(NOW(), INTERVAL 10 DAY), 'Gastro-entérite aiguë', 'Nausées, vomissements et crampes abdominales. Hydratation orale préconisée.', 11, 2, NULL, 58.0, 170.0, 37.8, '11/7'),
  (13, DATE_SUB(NOW(), INTERVAL 9 DAY), 'Bilan de santé systématique', 'Acuité visuelle 10/10, audition normale, colonne vertébrale sans scoliose.', 12, 1, NULL, 51.0, 162.0, 36.8, '12/8'),
  (14, DATE_SUB(NOW(), INTERVAL 8 DAY), 'Traumatisme du poignet', 'Chute au basketball. Pas de fracture évidente, contusion simple.', 13, NULL, 2, 60.5, 172.0, 36.7, '12/8'),
  (15, DATE_SUB(NOW(), INTERVAL 7 DAY), 'Crise d angoisse / tachycardie', 'Stress avant les examens continus. Écoute active et relaxation, pouls régulier.', 14, 3, NULL, 47.0, 159.0, 37.0, '13/8'),
  (16, DATE_SUB(NOW(), INTERVAL 6 DAY), 'Lombalgie aiguë', 'Douleur lombaire musculaire suite à port de sac à dos trop lourd.', 15, 1, NULL, 64.0, 176.0, 36.8, '12/8'),
  (17, DATE_SUB(NOW(), INTERVAL 5 DAY), 'Dermatite atopique eczéma', 'Plaies de grattage aux plis des coudes. Application de crème émolliente et dermocorticoïde.', 16, 4, NULL, 49.0, 160.0, 36.9, '11/7'),
  (18, DATE_SUB(NOW(), INTERVAL 4 DAY), 'Brûlure chimique légère en TP', 'Projection acide dilué sur avant-bras. Lavage abondant à l eau 15 min, pansement gras.', 17, NULL, 1, 62.0, 174.0, 36.7, '12/8'),
  (19, DATE_SUB(NOW(), INTERVAL 3 DAY), 'Insomnie et asthénie chronique', 'Baisse de concentration en cours. Conseils d hygiène du sommeil et suivi psychologique.', 18, 3, NULL, 48.5, 161.0, 36.8, '11/7'),
  (20, DATE_SUB(NOW(), INTERVAL 2 DAY), 'Toux sèche quinteuse', 'Trachéite aiguë saisonnière sans râles pulmonaires. Sirop antitussif et miel.', 19, 1, NULL, 63.0, 175.0, 37.4, '12/8'),
  (21, DATE_SUB(NOW(), INTERVAL 1 DAY), 'Dysphagie et fièvre 38.2', 'Pharyngite aiguë. Antipyrétique et pastilles antiseptiques.', 20, 2, NULL, 53.0, 164.0, 38.2, '12/8'),
  (22, DATE_SUB(NOW(), INTERVAL 1 DAY), 'Piqûre d insecte œdématiée', 'Réaction locale au niveau de la cheville, pas de signe d anaphylaxie.', 21, NULL, 2, 67.0, 178.0, 36.9, '12/8'),
  (23, NOW(), 'Contrôle respiratoire post-asthme', 'Auscultation claire, bon débit expiratoire de pointe (Peak Flow).', 4, 1, NULL, 48.2, 158.0, 36.8, '12/8'),
  (24, NOW(), 'Céphalées pulsatiles', 'Suspicion de migraine ophtalmique, repos en salle d infirmerie dans l obscurité.', 22, NULL, 3, 52.0, 163.0, 37.0, '11/7'),
  (25, NOW(), 'Douleurs dentaires vives', 'Caries molaires avec inflammation gingivale. Orientation urgente vers un dentiste.', 23, 1, NULL, 65.0, 177.0, 37.2, '12/8');

-- 7. Prescriptions médicales
INSERT INTO prescription (id_prescription, id_consult, medicament, dosage, duree) VALUES
  (1, 2, 'Pommade anti-inflammatoire Arnica gel', '2 applications par jour', '5 jours'),
  (2, 3, 'Paracétamol 500mg', '1 comprimé toutes les 8 heures si douleur', '4 jours'),
  (3, 4, 'Collyre apaisant lubrifiant', '1 goutte dans chaque œil 3x/jour', '7 jours'),
  (4, 5, 'Salbutamol (Ventoline) 100 µg', '2 bouffées à répéter si crise + avant EPS', '1 mois'),
  (5, 7, 'Spasfon Lyoc 80mg', '2 lyophilisats en cas de spasmes', '3 jours'),
  (6, 8, 'Cétirizine 10mg (Antihistaminique)', '1 comprimé le soir au coucher', '15 jours'),
  (7, 8, 'Spray nasal de corticoïde', '1 pulvérisation par narine le matin', '10 jours'),
  (8, 10, 'Amoxicilline 500mg', '1 gélule 3 fois par jour', '6 jours'),
  (9, 10, 'Paracétamol 1000mg', '1 comprimé toutes les 6 heures en cas de fièvre', '3 jours'),
  (10, 12, 'Smecta (Diosmectite)', '1 sachet dans l eau 3 fois par jour', '4 jours'),
  (11, 12, 'Sérum de réhydratation orale', 'À boire par petites gorgées régulièrement', '2 jours'),
  (12, 14, 'Paracétamol 500mg', '1 comprimé si douleur persistante', '3 jours'),
  (13, 15, 'Magnésium B6 marin', '1 comprimé matin et midi aux repas', '1 mois'),
  (14, 16, 'Ibuprofène 400mg', '1 comprimé 2 fois par jour après repas', '5 jours'),
  (15, 17, 'Hydrocortisone crème 1%', '1 application le soir sur les lésions', '5 jours'),
  (16, 17, 'Baume émollient relipidant', 'Application biquotidienne sur peau sèche', 'En continu'),
  (17, 18, 'Biafine émulsion', 'Application en couche épaisse 3 fois par jour', '5 jours'),
  (18, 20, 'Sirop Hélicidine antitussif', '1 cuillère à soupe 3 fois par jour', '5 jours'),
  (19, 21, 'Paracétamol 500mg', '1 sachet toutes les 6 heures', '3 jours'),
  (20, 21, 'Pastilles pour la gorge à la propolis', '4 à 6 pastilles par jour à sucer', '4 jours'),
  (21, 22, 'Crème apaisante antihistaminique', '1 application sur la piqûre 2x/jour', '3 jours'),
  (22, 25, 'Paracétamol 1000mg', '1 comprimé en attendant le RDV dentiste', '24 heures');

-- 8. Rendez-vous médicaux (Historique + À venir pour un agenda vivant)
INSERT INTO rdv (id_rdv, id_eleve, date_rdv, id_medecin, statut) VALUES
  -- RDV passés réalisés
  (1, 1, DATE_SUB(NOW(), INTERVAL 28 DAY), 1, 'fait'),
  (2, 2, DATE_SUB(NOW(), INTERVAL 25 DAY), 1, 'fait'),
  (3, 4, DATE_SUB(NOW(), INTERVAL 21 DAY), 1, 'fait'),
  (4, 7, DATE_SUB(NOW(), INTERVAL 16 DAY), 4, 'fait'),
  (5, 9, DATE_SUB(NOW(), INTERVAL 13 DAY), 1, 'fait'),
  (6, 11, DATE_SUB(NOW(), INTERVAL 10 DAY), 2, 'fait'),
  (7, 14, DATE_SUB(NOW(), INTERVAL 7 DAY), 3, 'fait'),
  (8, 16, DATE_SUB(NOW(), INTERVAL 5 DAY), 4, 'fait'),
  -- RDV annulés
  (9, 5, DATE_SUB(NOW(), INTERVAL 14 DAY), 2, 'annule'),
  (10, 8, DATE_SUB(NOW(), INTERVAL 4 DAY), 3, 'annule'),
  -- RDV programmés pour les prochains jours
  (11, 3, DATE_ADD(NOW(), INTERVAL 1 DAY), 2, 'programmé'),
  (12, 10, DATE_ADD(NOW(), INTERVAL 2 DAY), 1, 'programmé'),
  (13, 15, DATE_ADD(NOW(), INTERVAL 3 DAY), 1, 'programmé'),
  (14, 18, DATE_ADD(NOW(), INTERVAL 4 DAY), 3, 'programmé'),
  (15, 20, DATE_ADD(NOW(), INTERVAL 5 DAY), 2, 'programmé'),
  (16, 22, DATE_ADD(NOW(), INTERVAL 6 DAY), 4, 'programmé'),
  (17, 24, DATE_ADD(NOW(), INTERVAL 7 DAY), 1, 'programmé');
