"""
Initialisation et peuplement du Référentiel Médicamenteux National
pour SanteScolaire (Base MySQL: referentiel_medicament)
"""
import sys
import os

# Ajout du path backend pour importer config si besoin
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import MySQLdb
from app.config import Config

DATASET_MEDICAMENTS = [
    # =========================================================================
    # 1. ANTALGIQUES, ANTIPYRÉTIQUES & ANTISPASMODIQUES
    # =========================================================================
    {
        "nom_commercial": "Doliprane 500 mg",
        "dci": "Paracétamol",
        "forme": "Gélule",
        "dosage_standard": "1 gélule toutes les 6h à 8h si douleur ou fièvre",
        "duree_recommandee": "3 jours (max 3g/jour)",
        "classe_therapeutique": "Antalgique / Antipyrétique",
        "statut_delivrance": "Vente libre / Prescription"
    },
    {
        "nom_commercial": "Doliprane 1000 mg",
        "dci": "Paracétamol",
        "forme": "Comprimé",
        "dosage_standard": "1 comprimé toutes les 8h (espacer de 6h min)",
        "duree_recommandee": "3 à 5 jours",
        "classe_therapeutique": "Antalgique / Antipyrétique",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Doliprane pédiatrique suspension buvable",
        "dci": "Paracétamol",
        "forme": "Suspension buvable (Sirop)",
        "dosage_standard": "1 dose-kilo avec la pipette toutes les 6 heures",
        "duree_recommandee": "3 jours",
        "classe_therapeutique": "Pédiatrie / Antalgique",
        "statut_delivrance": "Vente libre / Prescription"
    },
    {
        "nom_commercial": "Paracétamol Mylan 500 mg",
        "dci": "Paracétamol",
        "forme": "Comprimé sécable",
        "dosage_standard": "1 comprimé 3 fois par jour",
        "duree_recommandee": "3 jours",
        "classe_therapeutique": "Antalgique / Antipyrétique",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Paracétamol Biogaran 1000 mg",
        "dci": "Paracétamol",
        "forme": "Comprimé",
        "dosage_standard": "1 comprimé 3 fois par jour si fièvre > 38.5°C",
        "duree_recommandee": "3 jours",
        "classe_therapeutique": "Antalgique / Antipyrétique",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Efferalgan 500 mg effervescent",
        "dci": "Paracétamol",
        "forme": "Comprimé effervescent",
        "dosage_standard": "1 comprimé dissous dans un verre d'eau toutes les 6h",
        "duree_recommandee": "3 jours",
        "classe_therapeutique": "Antalgique / Antipyrétique",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Efferalgan 1000 mg effervescent",
        "dci": "Paracétamol",
        "forme": "Comprimé effervescent",
        "dosage_standard": "1 comprimé dissous dans l'eau 3x/jour",
        "duree_recommandee": "3 jours",
        "classe_therapeutique": "Antalgique / Antipyrétique",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Dafalgan 500 mg",
        "dci": "Paracétamol",
        "forme": "Gélule",
        "dosage_standard": "1 à 2 gélules selon le poids toutes les 6h",
        "duree_recommandee": "3 jours",
        "classe_therapeutique": "Antalgique / Antipyrétique",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Dafalgan 1000 mg",
        "dci": "Paracétamol",
        "forme": "Comprimé pelliculé",
        "dosage_standard": "1 comprimé 3 fois par jour",
        "duree_recommandee": "3 à 5 jours",
        "classe_therapeutique": "Antalgique / Antipyrétique",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Spasfon 80 mg",
        "dci": "Phloroglucinol",
        "forme": "Comprimé enrobé",
        "dosage_standard": "2 comprimés au moment des spasmes (max 6/j)",
        "duree_recommandee": "3 à 5 jours",
        "classe_therapeutique": "Antispasmodique",
        "statut_delivrance": "Vente libre / Prescription"
    },
    {
        "nom_commercial": "Spasfon Lyoc 80 mg",
        "dci": "Phloroglucinol",
        "forme": "Lyophilisat oral",
        "dosage_standard": "2 lyophilisats à laisser fondre sous la langue au moment de la crise",
        "duree_recommandee": "3 jours",
        "classe_therapeutique": "Antispasmodique",
        "statut_delivrance": "Vente libre / Prescription"
    },
    {
        "nom_commercial": "Météospasmyl",
        "dci": "Alvérine + Siméticone",
        "forme": "Capsule molle",
        "dosage_standard": "1 capsule 2 à 3 fois par jour au début des repas",
        "duree_recommandee": "7 jours",
        "classe_therapeutique": "Antispasmodique / Digestif",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Débridat 100 mg",
        "dci": "Trimébutine",
        "forme": "Comprimé",
        "dosage_standard": "1 comprimé 3 fois par jour avant les repas",
        "duree_recommandee": "7 jours",
        "classe_therapeutique": "Régulateur de motricité digestive",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Débridat suspension buvable enfant",
        "dci": "Trimébutine",
        "forme": "Granulé pour suspension buvable",
        "dosage_standard": "1 demi à 1 mesure graduée 3 fois par jour",
        "duree_recommandee": "5 jours",
        "classe_therapeutique": "Pédiatrie / Digestif",
        "statut_delivrance": "Prescription médicale"
    },

    # =========================================================================
    # 2. ANTI-INFLAMMATOIRES & CORTICOÏDES
    # =========================================================================
    {
        "nom_commercial": "Advil 400 mg",
        "dci": "Ibuprofène",
        "forme": "Comprimé enrobé",
        "dosage_standard": "1 comprimé au cours d'un repas (max 3/j)",
        "duree_recommandee": "3 jours",
        "classe_therapeutique": "Anti-inflammatoire non stéroïdien (AINS)",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Advil 200 mg",
        "dci": "Ibuprofène",
        "forme": "Comprimé",
        "dosage_standard": "1 comprimé au cours d'un repas, à renouveler si besoin après 6h",
        "duree_recommandee": "3 jours",
        "classe_therapeutique": "AINS",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "AdvilMed pédiatrique 20 mg/ml",
        "dci": "Ibuprofène",
        "forme": "Suspension buvable enfant",
        "dosage_standard": "1 graduation-kilo 3 à 4 fois par jour au cours des repas",
        "duree_recommandee": "3 jours",
        "classe_therapeutique": "Pédiatrie / AINS",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Nurofen 200 mg",
        "dci": "Ibuprofène",
        "forme": "Comprimé enrobé",
        "dosage_standard": "1 à 2 comprimés avec un grand verre d'eau",
        "duree_recommandee": "3 jours",
        "classe_therapeutique": "AINS",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Nurofen 400 mg Flash",
        "dci": "Ibuprofène",
        "forme": "Comprimé orodispersible",
        "dosage_standard": "1 comprimé au repas (espacer de 8h)",
        "duree_recommandee": "3 jours",
        "classe_therapeutique": "AINS",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Voltarène Emulgel 1%",
        "dci": "Diclofénac",
        "forme": "Gel pour application locale",
        "dosage_standard": "1 application en massage doux 2 à 3 fois par jour sur la zone douloureuse",
        "duree_recommandee": "5 jours",
        "classe_therapeutique": "Anti-inflammatoire topique",
        "statut_delivrance": "Vente libre / Prescription"
    },
    {
        "nom_commercial": "Voltarène 50 mg",
        "dci": "Diclofénac sodique",
        "forme": "Comprimé gastro-résistant",
        "dosage_standard": "1 comprimé matin et soir au milieu des repas",
        "duree_recommandee": "5 jours",
        "classe_therapeutique": "AINS",
        "statut_delivrance": "Prescription médicale (Liste II)"
    },
    {
        "nom_commercial": "Profénid 100 mg",
        "dci": "Kétoprofène",
        "forme": "Comprimé sécable",
        "dosage_standard": "1 comprimé 2 fois par jour pendant les repas",
        "duree_recommandee": "5 jours",
        "classe_therapeutique": "AINS",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Antadys 100 mg",
        "dci": "Flurbiprofène",
        "forme": "Comprimé pelliculé",
        "dosage_standard": "1 comprimé au moment des règles douloureuses (dysménorrhée)",
        "duree_recommandee": "2 à 3 jours",
        "classe_therapeutique": "AINS / Gynécologie",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Célestène 0.05% gouttes buvables",
        "dci": "Bétaméthasone",
        "forme": "Solution buvable en gouttes",
        "dosage_standard": "10 gouttes par kg le matin au petit-déjeuner",
        "duree_recommandee": "3 à 5 jours (Arrêt brutal possible si cure courte)",
        "classe_therapeutique": "Corticoïde oral pédiatrique",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Célestène 2 mg comprimé dispersible",
        "dci": "Bétaméthasone",
        "forme": "Comprimé dispersible",
        "dosage_standard": "1 comprimé dissous dans un verre d'eau le matin",
        "duree_recommandee": "3 à 5 jours",
        "classe_therapeutique": "Corticoïde oral",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Solupred 20 mg",
        "dci": "Prednisolone",
        "forme": "Comprimé orodispersible",
        "dosage_standard": "1 à 2 comprimés le matin au petit-déjeuner",
        "duree_recommandee": "5 jours",
        "classe_therapeutique": "Corticoïde oral",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Solupred 5 mg",
        "dci": "Prednisolone",
        "forme": "Comprimé orodispersible",
        "dosage_standard": "Selon prescription pédiatrique (1mg/kg/j le matin)",
        "duree_recommandee": "3 à 5 jours",
        "classe_therapeutique": "Corticoïde oral pédiatrique",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Cortancyl 20 mg",
        "dci": "Prednisone",
        "forme": "Comprimé sécable",
        "dosage_standard": "1 comprimé le matin au petit déjeuner",
        "duree_recommandee": "5 jours",
        "classe_therapeutique": "Corticoïde oral",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },

    # =========================================================================
    # 3. PNEUMOLOGIE, ASTHME & BRONCHODILATATEURS
    # =========================================================================
    {
        "nom_commercial": "Ventoline 100 µg/dose (Salbutamol)",
        "dci": "Salbutamol",
        "forme": "Aérosol doseur (Inhalateur)",
        "dosage_standard": "2 bouffées en cas de crise ou 15 min avant l'effort physique",
        "duree_recommandee": "Traitement de crise / PAI Asthme",
        "classe_therapeutique": "Bronchodilatateur d'action rapide",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Airomir 100 µg Autohaler",
        "dci": "Salbutamol",
        "forme": "Inhalateur automatique déclenché par l'inspiration",
        "dosage_standard": "1 à 2 inhalations si dyspnée ou sifflement",
        "duree_recommandee": "1 mois",
        "classe_therapeutique": "Bronchodilatateur",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Bricanyl Turbuhaler 500 µg",
        "dci": "Terbutaline",
        "forme": "Poudre pour inhalation",
        "dosage_standard": "1 inhalation en cas de gêne respiratoire (max 4/j)",
        "duree_recommandee": "1 mois",
        "classe_therapeutique": "Bronchodilatateur bêta-2 stimulant",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Bécotide 250 µg",
        "dci": "Béclométasone",
        "forme": "Suspension pour inhalation",
        "dosage_standard": "1 bouffée matin et soir, bien rincer la bouche après",
        "duree_recommandee": "Traitement de fond (3 mois)",
        "classe_therapeutique": "Corticoïde inhalé",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Flixotide 125 µg",
        "dci": "Fluticasone",
        "forme": "Aérosol doseur",
        "dosage_standard": "1 à 2 bouffées matin et soir",
        "duree_recommandee": "Traitement de fond continu",
        "classe_therapeutique": "Corticoïde inhalé",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Sérétide Diskus 100/50 µg",
        "dci": "Salmétérol + Fluticasone",
        "forme": "Poudre pour inhalation en récipient unidose",
        "dosage_standard": "1 inhalation matin et soir régulièrement",
        "duree_recommandee": "Traitement de fond asthme persistant",
        "classe_therapeutique": "Association bronchodilatateur + corticoïde",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Symbicort Turbuhaler 100/6 µg",
        "dci": "Budésonide + Formotérol",
        "forme": "Poudre pour inhalation",
        "dosage_standard": "1 inhalation matin et soir",
        "duree_recommandee": "Traitement de fond continu",
        "classe_therapeutique": "Association bronchodilatateur + corticoïde",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Singulair 5 mg (Montélukast)",
        "dci": "Montélukast",
        "forme": "Comprimé à croquer",
        "dosage_standard": "1 comprimé à croquer le soir au coucher",
        "duree_recommandee": "3 mois renouvelable",
        "classe_therapeutique": "Antagoniste des récepteurs des leucotriènes",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Singulair 4 mg granulés",
        "dci": "Montélukast",
        "forme": "Sachet de granulés",
        "dosage_standard": "1 sachet par jour le soir mélangé à une compote",
        "duree_recommandee": "Traitement pédiatrique asthme",
        "classe_therapeutique": "Pédiatrie / Pneumologie",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Chambre d'inhalation pédiatrique (AeroChamber)",
        "dci": "Dispositif médical",
        "forme": "Chambre d'inhalation avec masque enfant",
        "dosage_standard": "Utiliser pour administrer les bouffées de Ventoline/Flixotide",
        "duree_recommandee": "1 an",
        "classe_therapeutique": "Dispositif médical d'inhalation",
        "statut_delivrance": "Prescription médicale"
    },

    # =========================================================================
    # 4. ALLERGOLOGIE, ANTIHISTAMINIQUES & URGENCE ANAPHYLAXIE
    # =========================================================================
    {
        "nom_commercial": "Cétirizine 10 mg (Zyrtec)",
        "dci": "Cétirizine dichlorhydrate",
        "forme": "Comprimé pelliculé sécable",
        "dosage_standard": "1 comprimé le soir au coucher",
        "duree_recommandee": "15 à 30 jours",
        "classe_therapeutique": "Antihistaminique H1",
        "statut_delivrance": "Vente libre / Prescription"
    },
    {
        "nom_commercial": "Zyrtec pédiatrique 10 mg/ml solution buvable",
        "dci": "Cétirizine",
        "forme": "Solution buvable en gouttes",
        "dosage_standard": "5 gouttes 2 fois par jour (enfant de 2 à 6 ans)",
        "duree_recommandee": "15 jours",
        "classe_therapeutique": "Pédiatrie / Antihistaminique",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Aerius 5 mg (Desloratadine)",
        "dci": "Desloratadine",
        "forme": "Comprimé pelliculé",
        "dosage_standard": "1 comprimé une fois par jour au cours ou en dehors du repas",
        "duree_recommandee": "1 mois",
        "classe_therapeutique": "Antihistaminique H1 non sédatif",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Aerius 0.5 mg/ml sirop pédiatrique",
        "dci": "Desloratadine",
        "forme": "Sirop",
        "dosage_standard": "2.5 ml une fois par jour (2 à 5 ans) ou 5 ml (6 à 11 ans)",
        "duree_recommandee": "15 à 30 jours",
        "classe_therapeutique": "Pédiatrie / Antihistaminique",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Xyzall 5 mg (Lévocétirizine)",
        "dci": "Lévocétirizine",
        "forme": "Comprimé pelliculé",
        "dosage_standard": "1 comprimé par jour au coucher",
        "duree_recommandee": "1 mois",
        "classe_therapeutique": "Antihistaminique H1",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Bilaska 20 mg (Bilastine)",
        "dci": "Bilastine",
        "forme": "Comprimé",
        "dosage_standard": "1 comprimé par jour à jeun (1h avant ou 2h après le repas)",
        "duree_recommandee": "1 mois",
        "classe_therapeutique": "Antihistaminique H1",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Kestin 10 mg (Ebastine)",
        "dci": "Ebastine",
        "forme": "Comprimé lyophilisat",
        "dosage_standard": "1 comprimé par jour sur la langue",
        "duree_recommandee": "1 mois",
        "classe_therapeutique": "Antihistaminique H1",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Primalan 5 mg (Méquitazine)",
        "dci": "Méquitazine",
        "forme": "Comprimé sécable",
        "dosage_standard": "1 comprimé matin et soir",
        "duree_recommandee": "10 jours",
        "classe_therapeutique": "Antihistaminique",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Stylo Épinéphrine (Epipen Enfant 0.15 mg)",
        "dci": "Adrénaline (Épinéphrine)",
        "forme": "Auto-injecteur intramusculaire",
        "dosage_standard": "1 injection immédiate dans la cuisse face antéro-latérale en cas d'anaphylaxie",
        "duree_recommandee": "Urgence vitale PAI (Appel SAMU 15 obligatoire)",
        "classe_therapeutique": "Urgence vitale / Choc anaphylactique",
        "statut_delivrance": "Prescription médicale obligatoire (PAI)"
    },
    {
        "nom_commercial": "Stylo Épinéphrine (Epipen Adulte 0.30 mg)",
        "dci": "Adrénaline (Épinéphrine)",
        "forme": "Auto-injecteur intramusculaire",
        "dosage_standard": "1 injection immédiate dans la cuisse face antéro-latérale en cas d'anaphylaxie",
        "duree_recommandee": "Urgence vitale PAI (Appel SAMU 15 obligatoire)",
        "classe_therapeutique": "Urgence vitale / Choc anaphylactique",
        "statut_delivrance": "Prescription médicale obligatoire (PAI)"
    },
    {
        "nom_commercial": "Jext 150 µg auto-injecteur",
        "dci": "Adrénaline",
        "forme": "Stylo auto-injecteur",
        "dosage_standard": "1 injection IM cuisse en cas de réaction allergique sévère",
        "duree_recommandee": "Urgence PAI",
        "classe_therapeutique": "Urgence vitale / Choc anaphylactique",
        "statut_delivrance": "Prescription médicale obligatoire (PAI)"
    },
    {
        "nom_commercial": "Anapen 300 µg auto-injecteur",
        "dci": "Adrénaline",
        "forme": "Seringue pré-remplie auto-injectable",
        "dosage_standard": "1 injection IM cuisse si œdème de Quincke ou détresse respiratoire",
        "duree_recommandee": "Urgence PAI",
        "classe_therapeutique": "Urgence vitale / Choc anaphylactique",
        "statut_delivrance": "Prescription médicale obligatoire (PAI)"
    },

    # =========================================================================
    # 5. GASTRO-ENTÉROLOGIE, TRANSIT & RÉHYDRATATION
    # =========================================================================
    {
        "nom_commercial": "Smecta 3 g (Diosmectite)",
        "dci": "Diosmectite",
        "forme": "Poudre pour suspension buvable en sachet",
        "dosage_standard": "1 sachet délayé dans de l'eau 3 fois par jour",
        "duree_recommandee": "3 à 5 jours",
        "classe_therapeutique": "Adsorbant intestinal / Antidiarrhéique",
        "statut_delivrance": "Vente libre / Prescription"
    },
    {
        "nom_commercial": "Gaviscon suspension buvable en sachet",
        "dci": "Alginate de sodium + Bicarbonate de sodium",
        "forme": "Suspension buvable",
        "dosage_standard": "1 sachet après les 3 repas et éventuellement au coucher",
        "duree_recommandee": "7 jours",
        "classe_therapeutique": "Anti-reflux / Protecteur gastrique",
        "statut_delivrance": "Vente libre / Prescription"
    },
    {
        "nom_commercial": "Inexium 20 mg (Esoméprazole)",
        "dci": "Esoméprazole",
        "forme": "Comprimé gastro-résistant",
        "dosage_standard": "1 comprimé le matin à jeun 30 minutes avant le repas",
        "duree_recommandee": "14 à 28 jours",
        "classe_therapeutique": "Inhibiteur de la pompe à protons (IPP)",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Inexium 10 mg granulés pour suspension buvable",
        "dci": "Esoméprazole",
        "forme": "Sachet de granulés pédiatrique",
        "dosage_standard": "1 sachet par jour le matin mélangé à l'eau",
        "duree_recommandee": "14 jours",
        "classe_therapeutique": "Pédiatrie / IPP",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Mopral 20 mg (Oméprazole)",
        "dci": "Oméprazole",
        "forme": "Gélule gastro-résistante",
        "dosage_standard": "1 gélule le matin avec un verre d'eau",
        "duree_recommandee": "14 jours",
        "classe_therapeutique": "IPP",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Ultra-Levure 200 mg (Saccharomyces boulardii)",
        "dci": "Saccharomyces boulardii",
        "forme": "Gélule",
        "dosage_standard": "1 gélule par jour avec un verre d'eau au cours d'un repas",
        "duree_recommandee": "5 jours",
        "classe_therapeutique": "Probiotique / Flore intestinale",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Imodium 2 mg (Lopéramide)",
        "dci": "Lopéramide",
        "forme": "Gélule",
        "dosage_standard": "2 gélules d'emblée puis 1 après chaque selle liquide (max 6/j)",
        "duree_recommandee": "2 jours max",
        "classe_therapeutique": "Ralentisseur du transit intestinal",
        "statut_delivrance": "Vente libre / Prescription"
    },
    {
        "nom_commercial": "Tiorfan 100 mg (Racécadotril)",
        "dci": "Racécadotril",
        "forme": "Gélule",
        "dosage_standard": "1 gélule 3 fois par jour au début des repas",
        "duree_recommandee": "3 à 5 jours",
        "classe_therapeutique": "Antidiarrhéique antisécrétoire",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Tiorfanot 30 mg enfants",
        "dci": "Racécadotril",
        "forme": "Poudre pour suspension orale en sachet",
        "dosage_standard": "1 sachet 3 fois par jour mélangé à l'alimentation",
        "duree_recommandee": "3 à 5 jours",
        "classe_therapeutique": "Pédiatrie / Antidiarrhéique",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Soluté de Réhydratation Orale (Adiaril)",
        "dci": "SRO (Glucides + Électrolytes)",
        "forme": "Sachet pour solution buvable 200 ml",
        "dosage_standard": "Diluer 1 sachet dans 200 ml d'eau fraîche, à boire par petites gorgées",
        "duree_recommandee": "24 à 48 heures de gastro-entérite",
        "classe_therapeutique": "Réhydratation pédiatrique",
        "statut_delivrance": "Vente libre / Remboursé pédiatrie"
    },
    {
        "nom_commercial": "Forlax 10 g (Macrogol 4000)",
        "dci": "Macrogol 4000",
        "forme": "Poudre pour solution buvable en sachet",
        "dosage_standard": "1 à 2 sachets par jour le matin dissous dans l'eau",
        "duree_recommandee": "7 à 14 jours",
        "classe_therapeutique": "Laxatif osmotique",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Forlax Junior 4 g",
        "dci": "Macrogol 4000",
        "forme": "Sachet enfant",
        "dosage_standard": "1 sachet par jour le matin",
        "duree_recommandee": "7 jours",
        "classe_therapeutique": "Pédiatrie / Laxatif",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Vogalène 15 mg (Métopimazine)",
        "dci": "Métopimazine",
        "forme": "Gélule",
        "dosage_standard": "1 gélule 15 min avant les repas (max 3/j) si nausées ou vomissements",
        "duree_recommandee": "2 jours",
        "classe_therapeutique": "Antiémétique",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Vogalib 7.5 mg lyophilisat oral",
        "dci": "Métopimazine",
        "forme": "Lyophilisat oral",
        "dosage_standard": "1 lyophilisat à laisser fondre sur la langue au moment des nausées",
        "duree_recommandee": "2 jours",
        "classe_therapeutique": "Antiémétique",
        "statut_delivrance": "Vente libre"
    },

    # =========================================================================
    # 6. INFECTIOLOGIE & ANTIBIOTIQUES
    # =========================================================================
    {
        "nom_commercial": "Amoxicilline 500 mg",
        "dci": "Amoxicilline",
        "forme": "Gélule",
        "dosage_standard": "1 gélule 3 fois par jour au cours des repas",
        "duree_recommandee": "6 jours",
        "classe_therapeutique": "Antibiotique (Pénicilline A)",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Amoxicilline 1 g",
        "dci": "Amoxicilline",
        "forme": "Comprimé dispersible",
        "dosage_standard": "1 comprimé matin et soir dissous dans un verre d'eau",
        "duree_recommandee": "6 jours",
        "classe_therapeutique": "Antibiotique (Pénicilline A)",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Amoxicilline 250 mg/5 ml suspension buvable pédiatrique",
        "dci": "Amoxicilline",
        "forme": "Poudre pour suspension buvable",
        "dosage_standard": "80 mg/kg/jour en 2 ou 3 prises avec pipette graduée",
        "duree_recommandee": "6 jours",
        "classe_therapeutique": "Pédiatrie / Antibiotique",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Augmentin 1 g / 125 mg adulte",
        "dci": "Amoxicilline + Acide clavulanique",
        "forme": "Poudre pour suspension en sachet",
        "dosage_standard": "1 sachet matin et soir au début des repas",
        "duree_recommandee": "7 jours",
        "classe_therapeutique": "Antibiotique à large spectre",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Augmentin pédiatrique 100 mg/12.5 mg/ml",
        "dci": "Amoxicilline + Acide clavulanique",
        "forme": "Poudre pour suspension buvable avec pipette graduée en kg",
        "dosage_standard": "1 dose-kilo matin, midi et soir au début des repas",
        "duree_recommandee": "8 jours",
        "classe_therapeutique": "Pédiatrie / Antibiotique",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Zithromax 250 mg (Azithromycine)",
        "dci": "Azithromycine",
        "forme": "Comprimé pelliculé",
        "dosage_standard": "2 comprimés en 1 prise par jour pendant 3 jours",
        "duree_recommandee": "3 jours de traitement",
        "classe_therapeutique": "Antibiotique macrolide",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Josacine 500 mg",
        "dci": "Josamycine",
        "forme": "Comprimé dispersible",
        "dosage_standard": "1 comprimé matin et soir",
        "duree_recommandee": "6 jours",
        "classe_therapeutique": "Antibiotique macrolide",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Oroken 200 mg (Céfixime)",
        "dci": "Céfixime",
        "forme": "Comprimé pelliculé",
        "dosage_standard": "1 comprimé 2 fois par jour",
        "duree_recommandee": "5 jours",
        "classe_therapeutique": "Céphalosporine de 3e génération",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Pyostacine 500 mg (Pristinamycine)",
        "dci": "Pristinamycine",
        "forme": "Comprimé pelliculé",
        "dosage_standard": "2 comprimés matin et soir au milieu des repas",
        "duree_recommandee": "7 jours",
        "classe_therapeutique": "Antibiotique synergistine",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Ciflox 500 mg (Ciprofloxacine)",
        "dci": "Ciprofloxacine",
        "forme": "Comprimé sécable",
        "dosage_standard": "1 comprimé 2 fois par jour",
        "duree_recommandee": "5 jours",
        "classe_therapeutique": "Fluoroquinolone",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Monuril 3 g (Fosfomycine)",
        "dci": "Fosfomycine trométamol",
        "forme": "Granulés pour solution buvable en sachet unidose",
        "dosage_standard": "1 sachet unique le soir au coucher après vidange vésicale",
        "duree_recommandee": "Prise unique (Cystite aiguë simple)",
        "classe_therapeutique": "Antibactérien urinaire",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },

    # =========================================================================
    # 7. ORL, RHINOLOGIE & TOUX
    # =========================================================================
    {
        "nom_commercial": "Sérum Physiologique dosettes stériles 5 ml",
        "dci": "Chlorure de sodium 0.9%",
        "forme": "Dosettes unidoses",
        "dosage_standard": "Lavage nasal 2 à 4 fois par jour dans chaque narine",
        "duree_recommandee": "7 jours",
        "classe_therapeutique": "Hygiène nasale & oculaire",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Rhinotrophyl spray nasal",
        "dci": "Acide ténoïque",
        "forme": "Solution pour pulvérisation nasale",
        "dosage_standard": "1 pulvérisation dans chaque narine 3 à 4 fois par jour",
        "duree_recommandee": "5 jours",
        "classe_therapeutique": "Antiseptique local ORL",
        "statut_delivrance": "Vente libre / Prescription"
    },
    {
        "nom_commercial": "Pivalone 1% suspension nasale",
        "dci": "Tixocortol pivalate",
        "forme": "Spray nasal",
        "dosage_standard": "1 à 2 pulvérisations dans chaque narine 3 fois par jour",
        "duree_recommandee": "5 jours",
        "classe_therapeutique": "Corticoïde local nasal",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Hexaspray collutoire",
        "dci": "Biclotymol",
        "forme": "Collutoire en flacon pressurisé",
        "dosage_standard": "2 pulvérisations au fond de la gorge 3 fois par jour",
        "duree_recommandee": "5 jours",
        "classe_therapeutique": "Antiseptique de la gorge",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Lysopaïne comprimés à sucer",
        "dci": "Cétylpyridinium + Lysozyme",
        "forme": "Comprimé à sucer",
        "dosage_standard": "3 à 6 comprimés à sucer par jour répartis régulièrement",
        "duree_recommandee": "5 jours",
        "classe_therapeutique": "Maux de gorge peu intenses",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Strepsils Miel Citron",
        "dci": "Amylmétacrésol + Alcool dichlorobenzylique",
        "forme": "Pastille à sucer",
        "dosage_standard": "1 pastille à sucer lentement 3 à 4 fois par jour",
        "duree_recommandee": "3 jours",
        "classe_therapeutique": "Pastilles antiseptiques",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Maxilase sirop maux de gorge",
        "dci": "Alpha-amylase",
        "forme": "Sirop",
        "dosage_standard": "1 cuillère à soupe (15 ml) 3 fois par jour au cours des repas",
        "duree_recommandee": "5 jours",
        "classe_therapeutique": "Anti-inflammatoire enzymatique ORL",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Exomuc 200 mg (Acétylcystéine)",
        "dci": "Acétylcystéine",
        "forme": "Granulés pour solution buvable en sachet",
        "dosage_standard": "1 sachet dissous dans l'eau 3 fois par jour (avant 18h)",
        "duree_recommandee": "5 jours",
        "classe_therapeutique": "Fluidifiant bronchique (Toux grasse)",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Toplexil sirop toux sèche",
        "dci": "Oxomémazine",
        "forme": "Sirop",
        "dosage_standard": "10 ml 2 à 3 fois par jour de préférence le soir (peut endormir)",
        "duree_recommandee": "3 à 4 jours max",
        "classe_therapeutique": "Antitussif antihistaminique",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Hélicidine 10% sirop sans sucre",
        "dci": "Mucine d'hélis",
        "forme": "Sirop",
        "dosage_standard": "2 cuillères à café 3 fois par jour",
        "duree_recommandee": "5 jours",
        "classe_therapeutique": "Antitussif d'action périphérique",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Otipax gouttes auriculaires",
        "dci": "Phénazone + Lidocaïne",
        "forme": "Gouttes auriculaires",
        "dosage_standard": "4 gouttes tièdes dans le conduit auditif 2 à 3 fois par jour si tympan fermé",
        "duree_recommandee": "3 à 5 jours",
        "classe_therapeutique": "Antalgique local auriculaire",
        "statut_delivrance": "Vente libre / Prescription"
    },
    {
        "nom_commercial": "Polydexa gouttes auriculaires",
        "dci": "Néomycine + Polymyxine B + Dexaméthasone",
        "forme": "Gouttes auriculaires",
        "dosage_standard": "1 à 5 gouttes dans l'oreille atteinte matin et soir",
        "duree_recommandee": "7 jours",
        "classe_therapeutique": "Antibiotique + corticoïde auriculaire",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },

    # =========================================================================
    # 8. OPHTALMOLOGIE
    # =========================================================================
    {
        "nom_commercial": "Collyre antiseptique Désomédine 0.1%",
        "dci": "Hexamidine di-isétionate",
        "forme": "Flacon compte-gouttes 10 ml",
        "dosage_standard": "1 goutte dans chaque œil 4 à 6 fois par jour",
        "duree_recommandee": "6 jours",
        "classe_therapeutique": "Antiseptique oculaire",
        "statut_delivrance": "Vente libre / Prescription"
    },
    {
        "nom_commercial": "Dacudoses solution pour lavage ophtalmique",
        "dci": "Acide borique + Borax",
        "forme": "Récipient unidose 10 ml",
        "dosage_standard": "Lavage oculaire abondant 1 à 3 fois par jour",
        "duree_recommandee": "Ponctuel / 3 jours",
        "classe_therapeutique": "Lavage oculaire antiseptique léger",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Zaditen 0.25 mg/ml collyre",
        "dci": "Kétotifène",
        "forme": "Unidoses",
        "dosage_standard": "1 goutte dans le cul-de-sac conjonctival 2 fois par jour",
        "duree_recommandee": "15 jours",
        "classe_therapeutique": "Antiallergique oculaire",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Tobrex 0.3% collyre (Tobramycine)",
        "dci": "Tobramycine",
        "forme": "Flacon compte-gouttes",
        "dosage_standard": "1 goutte dans l'œil infecté 3 à 4 fois par jour",
        "duree_recommandee": "5 à 7 jours",
        "classe_therapeutique": "Antibiotique ophtalmique",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Tobradex collyre suspension",
        "dci": "Tobramycine + Dexaméthasone",
        "forme": "Flacon compte-gouttes",
        "dosage_standard": "1 goutte 3 à 4 fois par jour",
        "duree_recommandee": "5 jours",
        "classe_therapeutique": "Association antibiotique + anti-inflammatoire oculaire",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },

    # =========================================================================
    # 9. DERMATOLOGIE, ANTISEPTIQUES & TRAUMATOLOGIE SCOLAIRE
    # =========================================================================
    {
        "nom_commercial": "Bétadine Dermique 10%",
        "dci": "Povidone iodée",
        "forme": "Flacon solution cutanée",
        "dosage_standard": "Application locale pure ou diluée sur plaie nettoyée",
        "duree_recommandee": "5 jours",
        "classe_therapeutique": "Antiseptique local iodé",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Biseptine solution cutanée spray",
        "dci": "Chlorhexidine + Chlorure de benzalkonium",
        "forme": "Spray pulvérisateur cutané",
        "dosage_standard": "1 à 2 pulvérisations locales sur la lésion",
        "duree_recommandee": "3 à 5 jours",
        "classe_therapeutique": "Antiseptique incolore sans alcool",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Biafine émulsion pour application cutanée",
        "dci": "Trolamine",
        "forme": "Tube 186 g",
        "dosage_standard": "Appliquer en couche épaisse 2 à 4 fois par jour sur brûlure superficielle",
        "duree_recommandee": "5 jours",
        "classe_therapeutique": "Protecteur cutané / Brûlures 1er degré",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Cicalfate+ Crème réparatrice protectrice",
        "dci": "Cuivre + Zinc + Eau thermale d'Avène",
        "forme": "Tube crème",
        "dosage_standard": "Appliquer 2 fois par jour sur peau propre et sèche",
        "duree_recommandee": "7 jours",
        "classe_therapeutique": "Dermatologie réparatrice / Irritations",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Fucidine 2% crème (Acide fusidique)",
        "dci": "Acide fusidique",
        "forme": "Tube 15 g crème",
        "dosage_standard": "Application 2 fois par jour sur impétigo ou lésion surinfectée",
        "duree_recommandee": "7 jours",
        "classe_therapeutique": "Antibiotique topique cutané",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Diprosone 0.05% crème",
        "dci": "Bétaméthasone",
        "forme": "Tube crème",
        "dosage_standard": "1 application par jour en couche mince sur l'eczéma (éviter le visage)",
        "duree_recommandee": "5 à 7 jours",
        "classe_therapeutique": "Dermocorticoïde d'activité forte",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Locoid 0.1% crème",
        "dci": "Hydrocortisone butyrate",
        "forme": "Tube crème",
        "dosage_standard": "1 application par jour en massage léger",
        "duree_recommandee": "7 jours",
        "classe_therapeutique": "Dermocorticoïde d'activité modérée",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Arnica Montana Gel",
        "dci": "Extrait d'Arnica",
        "forme": "Gel topique",
        "dosage_standard": "Application immédiate après contusion/bosse, répéter 2 à 3 fois par jour",
        "duree_recommandee": "3 jours",
        "classe_therapeutique": "Traumatologie / Ecchymoses",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Econazole 1% crème (Pévaryl)",
        "dci": "Econazole nitrate",
        "forme": "Tube crème",
        "dosage_standard": "Application matin et soir après toilette de la mycose",
        "duree_recommandee": "14 à 21 jours",
        "classe_therapeutique": "Antifongique topique",
        "statut_delivrance": "Vente libre / Prescription"
    },
    {
        "nom_commercial": "Pansements adhésifs stériles étanches",
        "dci": "Dispositif médical de pansement",
        "forme": "Boîte de pansements assortis",
        "dosage_standard": "Renouveler après chaque lavage ou une fois par jour",
        "duree_recommandee": "Soins courants",
        "classe_therapeutique": "Dispositif médical",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Bandes extensibles Velpeau 3m x 7cm",
        "dci": "Bande de contention",
        "forme": "Rouleau sous blister",
        "dosage_standard": "Maintien de compresse ou soutien articulaire d'entorse légère",
        "duree_recommandee": "7 jours",
        "classe_therapeutique": "Contention & Pansements",
        "statut_delivrance": "Vente libre"
    },

    # =========================================================================
    # 10. ENDOCRINOLOGIE, DIABÈTE & URGENCES MÉTABOLIQUES
    # =========================================================================
    {
        "nom_commercial": "Glucagen HypoKit 1 mg",
        "dci": "Glucagon",
        "forme": "Poudre et solvant pour solution injectable",
        "dosage_standard": "1 injection sous-cutanée ou intramusculaire immédiate si malaise hypoglycémique sévère",
        "duree_recommandee": "Urgence PAI Diabète (SAMU 15)",
        "classe_therapeutique": "Urgence vitale / Hypoglycémie",
        "statut_delivrance": "Prescription médicale obligatoire (PAI)"
    },
    {
        "nom_commercial": "Insuline NovoRapid FlexPen 100 U/ml",
        "dci": "Insuline asparte",
        "forme": "Stylo prérempli pour injection sous-cutanée",
        "dosage_standard": "Selon protocole PAI diabète de l'enfant (avant le repas)",
        "duree_recommandee": "Traitement continu",
        "classe_therapeutique": "Insuline rapide",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Insuline Lantus SoloStar 100 U/ml",
        "dci": "Insuline glargine",
        "forme": "Stylo prérempli",
        "dosage_standard": "1 injection sous-cutanée par jour à heure fixe",
        "duree_recommandee": "Traitement de fond diabète type 1",
        "classe_therapeutique": "Insuline basale lente",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Lecteur Glycémie & Capteur Freestyle Libre 2",
        "dci": "Capteur de glucose interstitiel",
        "forme": "Capteur à coller sur le bras",
        "dosage_standard": "Scan continu du taux de sucre de l'élève en classe",
        "duree_recommandee": "14 jours par capteur",
        "classe_therapeutique": "Dispositif médical Diabétologie",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Levothyrox 50 µg",
        "dci": "Lévothyroxine sodique",
        "forme": "Comprimé sécable",
        "dosage_standard": "1 comprimé par jour le matin à jeun 30 min avant le petit-déjeuner",
        "duree_recommandee": "Traitement de substitution thyroïdienne à vie",
        "classe_therapeutique": "Hormone thyroïdienne",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Levothyrox 25 µg",
        "dci": "Lévothyroxine sodique",
        "forme": "Comprimé sécable",
        "dosage_standard": "1 comprimé le matin à jeun",
        "duree_recommandee": "Traitement au long cours",
        "classe_therapeutique": "Hormone thyroïdienne",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Levothyrox 75 µg",
        "dci": "Lévothyroxine",
        "forme": "Comprimé",
        "dosage_standard": "1 comprimé le matin à jeun",
        "duree_recommandee": "Traitement au long cours",
        "classe_therapeutique": "Hormone thyroïdienne",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Metformine 500 mg",
        "dci": "Metformine chlorhydrate",
        "forme": "Comprimé pelliculé",
        "dosage_standard": "1 comprimé au cours des repas",
        "duree_recommandee": "Traitement continu",
        "classe_therapeutique": "Antidiabétique oral",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },

    # =========================================================================
    # 11. NEUROLOGIE, PÉDO-PSYCHIATRIE & TDAH
    # =========================================================================
    {
        "nom_commercial": "Ritaline 10 mg (Méthylphénidate)",
        "dci": "Méthylphénidate chlorhydrate",
        "forme": "Comprimé sécable",
        "dosage_standard": "1 comprimé le matin au petit-déjeuner (prise scolaire selon PAI)",
        "duree_recommandee": "Ordonnance sécurisée (max 28 jours)",
        "classe_therapeutique": "Psychostimulant / TDAH",
        "statut_delivrance": "Stupéfiant - Prescription restreinte spécialiste"
    },
    {
        "nom_commercial": "Quasym 20 mg LP",
        "dci": "Méthylphénidate",
        "forme": "Gélule à libération modifiée",
        "dosage_standard": "1 gélule le matin avant l'école",
        "duree_recommandee": "28 jours",
        "classe_therapeutique": "TDAH pédiatrique",
        "statut_delivrance": "Stupéfiant - Prescription sécurisée"
    },
    {
        "nom_commercial": "Concerta LP 18 mg",
        "dci": "Méthylphénidate",
        "forme": "Comprimé à libération prolongée",
        "dosage_standard": "1 comprimé le matin avalé entier sans croquer",
        "duree_recommandee": "28 jours",
        "classe_therapeutique": "TDAH pédiatrique",
        "statut_delivrance": "Stupéfiant - Prescription sécurisée"
    },
    {
        "nom_commercial": "Dépakine 500 mg Chrono",
        "dci": "Valproate de sodium",
        "forme": "Comprimé pelliculé sécable LP",
        "dosage_standard": "1 comprimé matin et soir",
        "duree_recommandee": "Traitement anti-épileptique continu",
        "classe_therapeutique": "Anti-épileptique / Neurologie",
        "statut_delivrance": "Prescription médicale obligatoire (Protocole strict)"
    },
    {
        "nom_commercial": "Dépakine sirop 200 mg/ml enfant",
        "dci": "Valproate de sodium",
        "forme": "Solution buvable avec pipette",
        "dosage_standard": "Selon posologie neurologue au cours des repas",
        "duree_recommandee": "Traitement continu",
        "classe_therapeutique": "Pédiatrie / Anti-épileptique",
        "statut_delivrance": "Prescription médicale obligatoire"
    },
    {
        "nom_commercial": "Keppra 500 mg (Lévétiracétam)",
        "dci": "Lévétiracétam",
        "forme": "Comprimé pelliculé sécable",
        "dosage_standard": "1 comprimé 2 fois par jour",
        "duree_recommandee": "Traitement anti-épileptique continu",
        "classe_therapeutique": "Anti-épileptique",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Buccolam 5 mg solution buccale",
        "dci": "Midazolam",
        "forme": "Seringue pré-remplie pour administration buccale",
        "dosage_standard": "1 dose dans l'espace situé entre la joue et la gencive si crise d'épilepsie > 5 min",
        "duree_recommandee": "Urgence PAI Épilepsie",
        "classe_therapeutique": "Urgence neurologique / Anticonvulsivant",
        "statut_delivrance": "Prescription médicale obligatoire (PAI)"
    },

    # =========================================================================
    # 12. VITAMINES, SUPPLÉMENTATION & HÉMATOLOGIE
    # =========================================================================
    {
        "nom_commercial": "Uvédose 100 000 UI ampoule buvable",
        "dci": "Cholécalciférol (Vitamine D3)",
        "forme": "Ampoule buvable 2 ml",
        "dosage_standard": "1 ampoule à boire en prise unique avec un verre de lait",
        "duree_recommandee": "Renouveler après 3 mois en hiver",
        "classe_therapeutique": "Vitamine D",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "ZymaD 10 000 UI/ml gouttes",
        "dci": "Cholécalciférol (Vitamine D3)",
        "forme": "Flacon compte-gouttes",
        "dosage_standard": "2 à 4 gouttes par jour dans une petite cuillère",
        "duree_recommandee": "Saison automne-hiver",
        "classe_therapeutique": "Vitamine D pédiatrique",
        "statut_delivrance": "Vente libre / Prescription"
    },
    {
        "nom_commercial": "Tardyferon 80 mg",
        "dci": "Sulfate ferreux",
        "forme": "Comprimé enrobé",
        "dosage_standard": "1 comprimé par jour avant le repas ou pendant si intolérance",
        "duree_recommandee": "3 mois (Anémie ferriprive)",
        "classe_therapeutique": "Antianémique / Fer",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Tardyferon B9",
        "dci": "Fer + Acide folique",
        "forme": "Comprimé",
        "dosage_standard": "1 comprimé par jour avec un verre d'eau",
        "duree_recommandee": "3 mois",
        "classe_therapeutique": "Antianémique / Fer + B9",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Spéciafoldine 5 mg (Acide folique)",
        "dci": "Acide folique (Vitamine B9)",
        "forme": "Comprimé",
        "dosage_standard": "1 comprimé par jour",
        "duree_recommandee": "1 mois",
        "classe_therapeutique": "Supplémentation B9",
        "statut_delivrance": "Prescription médicale"
    },
    {
        "nom_commercial": "Magné B6 comprimés",
        "dci": "Magnésium + Pyridoxine",
        "forme": "Comprimé enrobé",
        "dosage_standard": "1 à 2 comprimés 2 fois par jour au cours des repas",
        "duree_recommandee": "1 mois (Fatigue passagère / Nervosité)",
        "classe_therapeutique": "Oligo-élément / Magnésium",
        "statut_delivrance": "Vente libre"
    },
    {
        "nom_commercial": "Calcium Vitamine D3 Biogaran 500 mg / 400 UI",
        "dci": "Carbonate de calcium + Cholécalciférol",
        "forme": "Comprimé à sucer ou à croquer",
        "dosage_standard": "1 comprimé 2 fois par jour",
        "duree_recommandee": "3 mois",
        "classe_therapeutique": "Supplémentation osseuse",
        "statut_delivrance": "Prescription médicale"
    },

    # =========================================================================
    # 13. VACCINS & PRÉVENTION SCOLAIRE
    # =========================================================================
    {
        "nom_commercial": "Revaxis vaccin injectable (DT Polio)",
        "dci": "Vaccin diphtérique, tétanique et poliomyélitique",
        "forme": "Seringue préremplie injectable 0.5 ml",
        "dosage_standard": "1 dose de rappel à 6 ans et entre 11 et 13 ans",
        "duree_recommandee": "Rappel obligatoire calendrier vaccinal",
        "classe_therapeutique": "Vaccin obligatoire",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Boostrixtetra vaccin (DTCaP)",
        "dci": "Vaccin diphtérie, tétanos, coqueluche et polio",
        "forme": "Seringue préremplie",
        "dosage_standard": "1 dose intramusculaire de rappel à 11-13 ans",
        "duree_recommandee": "Calendrier vaccinal scolaire",
        "classe_therapeutique": "Vaccin",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Gardasil 9 vaccin HPV",
        "dci": "Vaccin Papillomavirus humain 9-valent",
        "forme": "Seringue préremplie 0.5 ml",
        "dosage_standard": "Schéma 2 doses à 6 mois d'intervalle (filles et garçons 11-14 ans)",
        "duree_recommandee": "Campagne vaccinale nationale en milieu scolaire",
        "classe_therapeutique": "Vaccin préventif anticancéreux",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Bexsero vaccin Méningite B",
        "dci": "Vaccin méningococcique groupe B",
        "forme": "Seringue préremplie suspension injectable",
        "dosage_standard": "1 injection intramusculaire",
        "duree_recommandee": "Selon recommandations pédiatriques",
        "classe_therapeutique": "Vaccin méningocoque",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    },
    {
        "nom_commercial": "Priorix vaccin ROR",
        "dci": "Vaccin Rougeole, Oreillons, Rubéole",
        "forme": "Poudre et solvant pour injection",
        "dosage_standard": "1 dose sous-cutanée ou IM (rattrapage si carnet incomplet)",
        "duree_recommandee": "Vaccination obligatoire",
        "classe_therapeutique": "Vaccin pédiatrique ROR",
        "statut_delivrance": "Prescription médicale obligatoire (Liste I)"
    }
]


def init_database():
    """Initialise la table referentiel_medicament et insère le dataset."""
    cfg = Config()
    db = MySQLdb.connect(
        host=cfg.MYSQL_HOST,
        user=cfg.MYSQL_USER,
        passwd=cfg.MYSQL_PASSWORD,
        db=cfg.MYSQL_DB,
        charset='utf8mb4'
    )
    cur = db.cursor()

    print("[1/3] Création de la table 'referentiel_medicament'...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS referentiel_medicament (
            id_ref INT AUTO_INCREMENT PRIMARY KEY,
            nom_commercial VARCHAR(255) NOT NULL,
            dci VARCHAR(255) DEFAULT NULL,
            forme VARCHAR(100) DEFAULT NULL,
            dosage_standard VARCHAR(255) DEFAULT NULL,
            duree_recommandee VARCHAR(150) DEFAULT NULL,
            classe_therapeutique VARCHAR(150) DEFAULT NULL,
            statut_delivrance VARCHAR(150) DEFAULT 'Prescription médicale',
            INDEX idx_nom (nom_commercial),
            INDEX idx_dci (dci),
            INDEX idx_classe (classe_therapeutique)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    print(f"[2/3] Insertion / Synchronisation des {len(DATASET_MEDICAMENTS)} spécialités pharmaceutiques...")
    cur.execute("SELECT COUNT(*) FROM referentiel_medicament")
    count_existing = cur.fetchone()[0]

    nb_insere = 0
    for med in DATASET_MEDICAMENTS:
        # Vérifier si existe déjà par nom_commercial
        cur.execute("SELECT id_ref FROM referentiel_medicament WHERE nom_commercial = %s", [med["nom_commercial"]])
        existing = cur.fetchone()
        if not existing:
            cur.execute("""
                INSERT INTO referentiel_medicament 
                (nom_commercial, dci, forme, dosage_standard, duree_recommandee, classe_therapeutique, statut_delivrance)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                med["nom_commercial"],
                med["dci"],
                med["forme"],
                med["dosage_standard"],
                med["duree_recommandee"],
                med["classe_therapeutique"],
                med["statut_delivrance"]
            ))
            nb_insere += 1
        else:
            # Mettre à jour les dosages standards et métadonnées
            cur.execute("""
                UPDATE referentiel_medicament
                SET dci=%s, forme=%s, dosage_standard=%s, duree_recommandee=%s,
                    classe_therapeutique=%s, statut_delivrance=%s
                WHERE id_ref=%s
            """, (
                med["dci"],
                med["forme"],
                med["dosage_standard"],
                med["duree_recommandee"],
                med["classe_therapeutique"],
                med["statut_delivrance"],
                existing[0]
            ))

    db.commit()
    cur.execute("SELECT COUNT(*) FROM referentiel_medicament")
    total_total = cur.fetchone()[0]
    cur.close()
    db.close()
    print(f"[3/3] SUCCÈS ! {nb_insere} nouvelles références ajoutées. Total dans la base : {total_total} médicaments.")


if __name__ == "__main__":
    init_database()
