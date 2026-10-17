"""
==============================================================================
Service des Statistiques & Indicateurs Clés (KPI) — SantéScolaire
==============================================================================
Ce module centralise l'ensemble des calculs statistiques, agrégations
et métriques de décision médicale (inspiré de l'architecture GTM) :
1. KPIs Globaux d'Établissement (Taux de couverture médicale, assiduité aux RDV, flux)
2. KPIs Personnalisés pour le Médecin connecté (Consultations, patientèle, assiduité)
3. KPIs Personnalisés pour l'Infirmerie (Flux quotidien, urgences, pharmacie)
4. Tendance & Évolution Mensuelle (Dynamique comparative mois M vs M-1)
5. Répartition Épidémiologique des Pathologies par Cycle (Collège vs Lycée)
"""

from datetime import datetime, date, timedelta
from sqlalchemy import func, extract
from app.extensions import orm_db as db
from app.models import (
    Eleve, Classe, Consultation, Prescription, Rdv, 
    Medecin, Infirmier, Specialite, StockMedicament, AntecedentMedical
)

def get_kpi_globaux():
    """
    Calcule les indicateurs clés globaux pour le pilotage médico-scolaire.
    """
    today = date.today()
    debut_annee_scolaire = date(today.year if today.month >= 9 else today.year - 1, 9, 1)

    total_eleves = Eleve.query.count()
    
    # 1. Taux de couverture médicale (% d'élèves ayant eu au moins 1 consultation cette année)
    eleves_consultes_cette_annee = (
        db.session.query(func.count(func.distinct(Consultation.id_eleve)))
        .filter(Consultation.date_consult >= debut_annee_scolaire)
        .scalar() or 0
    )
    taux_couverture = (
        round((eleves_consultes_cette_annee / total_eleves * 100), 1) 
        if total_eleves > 0 else 0
    )

    # 2. Taux d'assiduité aux rendez-vous (% honorés)
    total_rdv = Rdv.query.count()
    rdv_faits = Rdv.query.filter(func.lower(Rdv.statut) == 'fait').count()
    rdv_annules = Rdv.query.filter(func.lower(Rdv.statut) == 'annulé').count()
    taux_assiduite = (
        round((rdv_faits / (total_rdv - rdv_annules) * 100), 1)
        if (total_rdv - rdv_annules) > 0 else 100.0
    )

    # 3. Total consultations & Suivis PAI
    total_consultations = Consultation.query.count()
    eleves_pai_critiques = (
        db.session.query(func.count(func.distinct(AntecedentMedical.id_eleve)))
        .filter((AntecedentMedical.pai_signe == True) | (AntecedentMedical.severite == 'Critique'))
        .scalar() or 0
    )

    # 4. Médicaments sous seuil d'alerte
    stocks_en_alerte = StockMedicament.query.filter(
        StockMedicament.quantite_stock <= StockMedicament.seuil_alerte
    ).count()

    return {
        "total_eleves": total_eleves,
        "eleves_consultes": eleves_consultes_cette_annee,
        "taux_couverture": taux_couverture,
        "total_consultations": total_consultations,
        "total_rdv": total_rdv,
        "taux_assiduite": taux_assiduite,
        "eleves_pai_critiques": eleves_pai_critiques,
        "stocks_en_alerte": stocks_en_alerte
    }


def get_kpi_medecin(medecin_id):
    """
    Calcule les indicateurs individualisés pour le médecin connecté.
    (Inspiré de dashboard_formateur dans GTM)
    """
    today = date.today()
    debut_mois = date(today.year, today.month, 1)

    # 1. Consultations totales et ce mois-ci
    total_consultations = Consultation.query.filter_by(id_medecin=medecin_id).count()
    consultations_ce_mois = Consultation.query.filter(
        Consultation.id_medecin == medecin_id,
        Consultation.date_consult >= debut_mois
    ).count()

    # 2. Patients distincts suivis
    patients_distincts = (
        db.session.query(func.count(func.distinct(Consultation.id_eleve)))
        .filter(Consultation.id_medecin == medecin_id)
        .scalar() or 0
    )

    # 3. Rendez-vous à venir du médecin
    rdv_a_venir = Rdv.query.filter(
        Rdv.id_medecin == medecin_id,
        Rdv.date_rdv >= datetime.now(),
        func.coalesce(func.lower(Rdv.statut), 'programmé') == 'programmé'
    ).count()

    # 4. Taux d'assiduité spécifique à ce médecin
    total_rdv_med = Rdv.query.filter_by(id_medecin=medecin_id).count()
    rdv_faits_med = Rdv.query.filter(
        Rdv.id_medecin == medecin_id,
        func.lower(Rdv.statut) == 'fait'
    ).count()
    taux_assiduite_med = (
        round((rdv_faits_med / total_rdv_med * 100), 1)
        if total_rdv_med > 0 else 100.0
    )

    # 5. Consultations d'aujourd'hui (file d'attente active)
    debut_jour = datetime.combine(today, datetime.min.time())
    fin_jour = datetime.combine(today, datetime.max.time())
    
    rdvs_aujourdhui = (
        db.session.query(Rdv, Eleve)
        .join(Eleve, Rdv.id_eleve == Eleve.id_eleve)
        .filter(
            Rdv.id_medecin == medecin_id,
            Rdv.date_rdv >= debut_jour,
            Rdv.date_rdv <= fin_jour
        )
        .order_by(Rdv.date_rdv.asc())
        .all()
    )

    visites_du_jour = []
    for r, e in rdvs_aujourdhui:
        # Recherche si l'élève a un PAI ou antécédent critique
        a_pai = any(a.pai_signe or a.severite == 'Critique' for a in e.antecedents)
        visites_du_jour.append({
            "id_rdv": r.id_rdv,
            "heure": r.date_rdv.strftime("%H:%M"),
            "eleve_id": e.id_eleve,
            "eleve_nom": f"{e.prenom_eleve} {e.nom_eleve}",
            "classe": e.classe,
            "statut": r.statut or "Programmé",
            "a_pai": a_pai
        })

    return {
        "total_consultations": total_consultations,
        "consultations_ce_mois": consultations_ce_mois,
        "patients_distincts": patients_distincts,
        "rdv_a_venir": rdv_a_venir,
        "taux_assiduite": taux_assiduite_med,
        "visites_du_jour": visites_du_jour
    }


def get_kpi_infirmier(infirmier_id=None):
    """
    Calcule les indicateurs opérationnels pour l'infirmerie et la gestion des soins quotidiens.
    """
    today = date.today()
    debut_jour = datetime.combine(today, datetime.min.time())
    fin_jour = datetime.combine(today, datetime.max.time())

    # 1. Passages du jour à l'infirmerie
    passages_aujourdhui = Consultation.query.filter(
        Consultation.date_consult >= debut_jour,
        Consultation.date_consult <= fin_jour
    ).count()

    # 2. Total soins infirmiers cette semaine
    debut_semaine = datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time())
    passages_semaine = Consultation.query.filter(
        Consultation.date_consult >= debut_semaine
    ).count()

    # 3. Urgences / Alertes de stock
    medicaments_critiques = StockMedicament.query.filter(
        StockMedicament.quantite_stock <= StockMedicament.seuil_alerte
    ).all()

    stocks_alertes_data = [
        {
            "id": m.id_medicament,
            "nom": m.nom_medicament,
            "forme": m.forme,
            "quantite": m.quantite_stock,
            "seuil": m.seuil_alerte,
            "unite": m.unite_mesure
        }
        for m in medicaments_critiques
    ]

    return {
        "passages_aujourdhui": passages_aujourdhui,
        "passages_semaine": passages_semaine,
        "nb_stocks_critiques": len(stocks_alertes_data),
        "stocks_critiques": stocks_alertes_data
    }


def get_tendance_mensuelle_consultations():
    """
    Compare l'afflux des consultations sur le mois M vs le mois M-1
    pour dégager la tendance globale (hausse/baisse en %).
    (Calqué sur _tendance_globale dans GTM)
    """
    today = date.today()
    premier_jour_m = date(today.year, today.month, 1)
    
    # Mois précédent
    if today.month == 1:
        premier_jour_m_prev = date(today.year - 1, 12, 1)
    else:
        premier_jour_m_prev = date(today.year, today.month - 1, 1)

    nb_m = Consultation.query.filter(Consultation.date_consult >= premier_jour_m).count()
    nb_m_prev = Consultation.query.filter(
        Consultation.date_consult >= premier_jour_m_prev,
        Consultation.date_consult < premier_jour_m
    ).count()

    if nb_m_prev == 0:
        variation = 0
    else:
        variation = round(((nb_m - nb_m_prev) / nb_m_prev) * 100)

    direction = "hausse" if variation > 0 else ("baisse" if variation < 0 else "stable")

    return {
        "mois_actuel": nb_m,
        "mois_precedent": nb_m_prev,
        "variation_pct": abs(variation),
        "direction": direction,
        "message": (
            f"Les passages à l'infirmerie sont en {direction} de {abs(variation)}% "
            f"par rapport au mois précédent."
        ) if variation != 0 else "Fréquentation stable par rapport au mois précédent."
    }


def get_repartition_pathologies_par_cycle():
    """
    Répartit les motifs de consultation selon le cycle scolaire :
    - Collège : 1AC, 2AC, 3AC
    - Lycée : TCS, 1BAC, 2BAC
    """
    consultations = (
        db.session.query(Consultation.motif, Eleve.classe)
        .join(Eleve, Consultation.id_eleve == Eleve.id_eleve)
        .all()
    )

    college_motifs = {}
    lycee_motifs = {}

    for motif, classe in consultations:
        m = (motif or "Autre").strip()
        cl = (classe or "").upper()
        if any(cl.startswith(prefix) for prefix in ["1AC", "2AC", "3AC"]):
            college_motifs[m] = college_motifs.get(m, 0) + 1
        else:
            lycee_motifs[m] = lycee_motifs.get(m, 0) + 1

    return {
        "college": sorted(college_motifs.items(), key=lambda x: x[1], reverse=True)[:5],
        "lycee": sorted(lycee_motifs.items(), key=lambda x: x[1], reverse=True)[:5]
    }

