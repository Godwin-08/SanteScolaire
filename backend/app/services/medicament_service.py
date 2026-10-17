"""
Service de référentiel médical et de vérification des stocks scolaires.
Gère le catalogue complet des spécialités pharmaceutiques (table referentiel_medicament),
la recherche autocomplétée AJAX et la corrélation en temps réel avec le stock de l'infirmerie.
"""

def verifier_disponibilite_ecole(nom_medicament, cur):
    """
    Vérifie si un médicament prescrit existe dans le stock de la pharmacie scolaire
    de l'établissement et s'il est en quantité suffisante (> 0).
    Retourne un dictionnaire avec le statut, la quantité disponible et le lieu.
    """
    if not nom_medicament or not str(nom_medicament).strip():
        return {"disponible": False, "raison": "Non spécifié"}

    terme = str(nom_medicament).strip().lower()

    # Recherche dans la table stock_medicament
    cur.execute("""
        SELECT nom_medicament, quantite_stock, seuil_alerte, unite_mesure, forme
        FROM stock_medicament
        WHERE quantite_stock > 0
    """)
    stocks = cur.fetchall()

    for s in stocks:
        stock_nom = s['nom_medicament'].lower()
        # Correspondance exacte ou partielle (ex: 'Ventoline' dans 'Ventoline 100µg (Salbutamol)')
        mots_cle = [w for w in terme.split() if len(w) > 3]
        match = (
            any(w in stock_nom for w in mots_cle) or 
            (stock_nom in terme) or 
            (terme in stock_nom)
        )
        if match:
            return {
                "disponible": True,
                "quantite": s['quantite_stock'],
                "seuil_alerte": s.get('seuil_alerte') or 5,
                "unite": s.get('unite_mesure') or 'unités',
                "forme": s.get('forme') or '',
                "nom_stock": s['nom_medicament'],
                "lieu": "Infirmerie scolaire (Délivré sur place)"
            }

    return {
        "disponible": False,
        "quantite": 0,
        "lieu": "Pharmacie d'officine externe (À la charge des parents)"
    }


def rechercher_medicaments(query, cur, limit=20):
    """
    Recherche en temps réel dans le référentiel des médicaments (DCI, nom de spécialité, classe).
    Croise chaque résultat avec le stock de l'infirmerie scolaire.
    """
    if not query or len(query.strip()) < 1:
        # Si vide, on propose les médicaments fréquents et ceux du stock
        cur.execute("""
            SELECT id_ref, nom_commercial, dci, forme, dosage_standard, duree_recommandee, classe_therapeutique, statut_delivrance
            FROM referentiel_medicament
            ORDER BY nom_commercial ASC
            LIMIT %s
        """, [limit])
        rows = cur.fetchall()
    else:
        q = f"%{query.strip()}%"
        cur.execute("""
            SELECT id_ref, nom_commercial, dci, forme, dosage_standard, duree_recommandee, classe_therapeutique, statut_delivrance
            FROM referentiel_medicament
            WHERE nom_commercial LIKE %s 
               OR dci LIKE %s 
               OR classe_therapeutique LIKE %s
            ORDER BY 
                CASE 
                    WHEN nom_commercial LIKE %s THEN 1
                    WHEN dci LIKE %s THEN 2
                    ELSE 3
                END,
                nom_commercial ASC
            LIMIT %s
        """, [q, q, q, f"{query.strip()}%", f"{query.strip()}%", limit])
        rows = cur.fetchall()

    resultats = []
    for r in rows:
        dispo = verifier_disponibilite_ecole(r['nom_commercial'], cur)
        if not dispo.get('disponible') and r.get('dci'):
            # Vérifier aussi par la DCI si dispo
            dispo_dci = verifier_disponibilite_ecole(r['dci'], cur)
            if dispo_dci.get('disponible'):
                dispo = dispo_dci

        est_dispo = dispo.get('disponible', False)
        resultats.append({
            "id_ref": r['id_ref'],
            "nom": r['nom_commercial'],
            "dci": r.get('dci') or '',
            "forme": r.get('forme') or '',
            "dosage": r.get('dosage_standard') or '',
            "duree": r.get('duree_recommandee') or '',
            "classe": r.get('classe_therapeutique') or '',
            "statut_delivrance": r.get('statut_delivrance') or 'Prescription médicale',
            "en_stock_ecole": est_dispo,
            "stock_quantite": dispo.get('quantite', 0),
            "stock_unite": dispo.get('unite', 'unités'),
            "stock_lieu": dispo.get('lieu', "Pharmacie d'officine"),
            "stock_badge_html": "🏫 Disponible à l'infirmerie" if est_dispo else "🏪 Pharmacie d'officine"
        })

    return resultats
