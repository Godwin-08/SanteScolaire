"""
Context processor : injecte `bell_alerts` dans chaque template.

- Médecin  → alertes cliniques du jour (PAI, RDVs programmés, antécédents critiques)
- Admin / Infirmier → alertes pharmacie (stocks critiques)
"""

from flask import session
from app.db import mysql
from app.constants import ROLE_MEDECIN


def register_context_processors(app):
    @app.context_processor
    def inject_bell_alerts():
        if not session.get('logged_in'):
            return dict(bell_alerts=None)

        role = session.get('user_role')
        user_id = session.get('user_id')

        try:
            cur = mysql.connection.cursor()

            if role == ROLE_MEDECIN:
                # ── 1. Patients PAI / critiques avec RDV aujourd'hui ─────────────
                cur.execute("""
                    SELECT DISTINCT e.id_eleve,
                           e.nom_eleve, e.prenom_eleve,
                           a.severite,
                           IF(a.pai_signe=1, 1, 0) AS has_pai
                    FROM rdv r
                    JOIN eleve e ON r.id_eleve = e.id_eleve
                    JOIN antecedent_medical a ON e.id_eleve = a.id_eleve
                    WHERE DATE(r.date_rdv) = CURDATE()
                      AND r.id_medecin = %s
                      AND r.statut = 'programmé'
                      AND (a.pai_signe = 1 OR a.severite = 'Critique')
                    LIMIT 4
                """, (user_id,))
                pai_patients = cur.fetchall()

                # ── 2. Nombre de RDVs du jour encore programmés ──────────────────
                cur.execute("""
                    SELECT COUNT(*) as cnt
                    FROM rdv
                    WHERE DATE(date_rdv) = CURDATE()
                      AND id_medecin = %s
                      AND statut = 'programmé'
                """, (user_id,))
                row = cur.fetchone()
                rdv_programme_count = row['cnt'] if row else 0

                # ── 3. Nombre de RDVs déjà faits aujourd'hui ─────────────────────
                cur.execute("""
                    SELECT COUNT(*) as cnt
                    FROM rdv
                    WHERE DATE(date_rdv) = CURDATE()
                      AND id_medecin = %s
                      AND statut = 'fait'
                """, (user_id,))
                row = cur.fetchone()
                rdv_fait_count = row['cnt'] if row else 0

                cur.close()

                total_count = len(pai_patients) + (1 if rdv_programme_count > 0 else 0)

                return dict(bell_alerts={
                    'role': 'medecin',
                    'pai_patients': pai_patients,
                    'rdv_programme_count': rdv_programme_count,
                    'rdv_fait_count': rdv_fait_count,
                    'count': total_count,
                })

            else:
                # ── Admin / Infirmier : alertes stocks pharmacie ──────────────────
                cur.execute("""
                    SELECT id_stock, nom_medicament, quantite_stock, seuil_alerte
                    FROM stock_medicament
                    WHERE quantite_stock <= seuil_alerte
                    ORDER BY quantite_stock ASC
                    LIMIT 5
                """)
                stocks_critiques = cur.fetchall()
                cur.close()

                return dict(bell_alerts={
                    'role': role,
                    'stocks_critiques': stocks_critiques,
                    'count': len(stocks_critiques),
                })

        except Exception:
            # En cas d'erreur DB (ex: hors session / pas encore connecté), ne pas planter
            return dict(bell_alerts=None)

