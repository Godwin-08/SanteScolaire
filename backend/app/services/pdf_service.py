"""
Service de génération de documents PDF officiels pour SanteScolaire.
Utilise ReportLab pour générer des documents vectoriels nets, conformes aux normes médicales.
"""
import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

PRIMARY = colors.HexColor('#10ac84')     # Vert Émeraude SanteScolaire
PRIMARY_DARK = colors.HexColor('#0d8a6a')
PRIMARY_LIGHT = colors.HexColor('#e8f8f5')
SECONDARY = colors.HexColor('#2563eb')   # Bleu Médical
TEXT_DARK = colors.HexColor('#0f172a')   # Noir Ardoise
TEXT_MUTED = colors.HexColor('#64748b')  # Gris Moyen
BG_LIGHT = colors.HexColor('#f8fafc')    # Gris Très Clair
BORDER_COLOR = colors.HexColor('#cbd5e1')# Bordure
RED_DANGER = colors.HexColor('#dc2626')  # Rouge Alerte PAI
RED_LIGHT = colors.HexColor('#fee2e2')   # Fond Rouge PAI


def _get_logo_path():
    """Localise le logo officiel de l'application."""
    base_dirs = [
        os.path.join(os.path.dirname(__file__), '..', '..', '..', 'frontend', 'static', 'img', 'logo.png'),
        os.path.join(os.path.dirname(__file__), '..', 'static', 'img', 'logo.png'),
        'frontend/static/img/logo.png',
        'static/img/logo.png'
    ]
    for p in base_dirs:
        abs_p = os.path.abspath(p)
        if os.path.exists(abs_p):
            return abs_p
    return None


def generate_ordonnance_pdf(consultation, prescriptions, medecin=None):
    """
    Génère le PDF officiel d'une ordonnance médicale A4.
    Retourne un buffer BytesIO prêt à être streamé par Flask.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )

    styles = getSampleStyleSheet()
    
    # Styles personnalisés
    style_med_nom = ParagraphStyle(
        'MedNom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=TEXT_DARK
    )
    style_med_spe = ParagraphStyle(
        'MedSpe',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=PRIMARY
    )
    style_med_info = ParagraphStyle(
        'MedInfo',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=TEXT_MUTED
    )
    style_app_brand = ParagraphStyle(
        'AppBrand',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=16,
        alignment=TA_RIGHT,
        textColor=TEXT_DARK
    )
    style_doc_date = ParagraphStyle(
        'DocDate',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        alignment=TA_RIGHT,
        textColor=TEXT_MUTED
    )
    style_patient_name = ParagraphStyle(
        'PatientName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=TEXT_DARK
    )
    style_patient_sub = ParagraphStyle(
        'PatientSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=TEXT_MUTED
    )
    style_section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=PRIMARY_DARK,
        textTransform='uppercase'
    )
    style_rx_name = ParagraphStyle(
        'RxName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=TEXT_DARK
    )
    style_rx_poso = ParagraphStyle(
        'RxPoso',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1e293b')
    )
    style_rx_tag_ecole = ParagraphStyle(
        'RxTagEcole',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9,
        alignment=TA_RIGHT,
        textColor=colors.HexColor('#047857')
    )
    style_rx_tag_pharma = ParagraphStyle(
        'RxTagPharma',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9,
        alignment=TA_RIGHT,
        textColor=colors.HexColor('#1d4ed8')
    )
    style_signature_title = ParagraphStyle(
        'SigTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=TEXT_DARK
    )
    style_signature_sub = ParagraphStyle(
        'SigSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        alignment=TA_CENTER,
        textColor=TEXT_MUTED
    )
    style_legal_notice = ParagraphStyle(
        'LegalNotice',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9.5,
        textColor=TEXT_MUTED
    )

    story = []

    # 1. EN-TÊTE MÉDICAL + LOGO OFFICIEL
    med_prenom = (medecin.get('prenom_medecin') if medecin else consultation.get('prenom_medecin')) or ''
    med_nom = (medecin.get('nom_medecin') if medecin else consultation.get('nom_medecin')) or 'Médecin Scolaire'
    specialite = (medecin.get('nom_specialite') if medecin else consultation.get('specialite')) or 'Médecine Scolaire & Pédiatrie'
    
    med_info_cell = [
        Paragraph(f"Dr. {med_prenom} {med_nom}".strip(), style_med_nom),
        Spacer(1, 1 * mm),
        Paragraph(specialite.upper(), style_med_spe),
        Spacer(1, 1 * mm),
        Paragraph("Pôle Médical & Prévention Scolaire &middot; Santé Scolaire", style_med_info),
        Paragraph("N° d'Inscription Ordre National : <b>45892-MED</b>", style_med_info),
    ]

    date_str = consultation.get('date_consult')
    if isinstance(date_str, datetime):
        date_str = date_str.strftime('%d/%m/%Y')
    elif not date_str:
        date_str = datetime.now().strftime('%d/%m/%Y')

    ref_str = f"REF : ORD-{consultation.get('id_consult', '00')}-{consultation.get('id_eleve', '00')}"

    logo_path = _get_logo_path()
    brand_items = []
    if logo_path:
        img = RLImage(logo_path, width=28 * mm, height=28 * mm)
        brand_items.append(img)
    brand_items.append(Paragraph("<b>Sante<font color='#10ac84'>Scolaire</font></b>", style_app_brand))
    brand_items.append(Spacer(1, 1 * mm))
    brand_items.append(Paragraph(f"Délivré le : <b>{date_str}</b>", style_doc_date))
    brand_items.append(Paragraph(f"<b>{ref_str}</b>", style_doc_date))

    header_table = Table([[med_info_cell, brand_items]], colWidths=[10.5 * cm, 7.0 * cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 3 * mm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=8, spaceBefore=4))

    # 2. ENCART PATIENT / ÉLÈVE
    nom_el = f"{consultation.get('nom_eleve', '')} {consultation.get('prenom_eleve', '')}".strip()
    classe_el = consultation.get('classe', 'Non assignée')
    sexe_el = "Masculin" if consultation.get('sexe') == 'M' else ("Féminin" if consultation.get('sexe') == 'F' else "")
    dob_el = consultation.get('date_naissance', '')
    if isinstance(dob_el, datetime):
        dob_el = dob_el.strftime('%d/%m/%Y')

    poids = consultation.get('poids')
    taille = consultation.get('taille')
    biometrie = []
    if poids:
        biometrie.append(f"Poids : <b>{poids} kg</b>")
    if taille:
        biometrie.append(f"Taille : <b>{taille} cm</b>")
    bio_str = " &middot; ".join(biometrie) if biometrie else "Biométrie : Non renseignée"

    patient_cell = [
        Paragraph("<font size='7' color='#64748b'><b>PATIENT(E) / ÉLÈVE :</b></font>", style_patient_sub),
        Paragraph(nom_el, style_patient_name),
        Paragraph(f"Classe : <b>{classe_el}</b> &middot; Né(e) le : <b>{dob_el}</b> &middot; Sexe : {sexe_el}", style_patient_sub),
        Paragraph(f"{bio_str} &middot; Dossier ID : #{consultation.get('id_eleve')}", style_patient_sub)
    ]
    badge_cell = [
        Paragraph("<para align='right'><font size='7.5' color='#0f172a'><b>SECRET MÉDICAL</b></font><br/><font size='7' color='#64748b'>Usage Thérapeutique Strict</font></para>", styles['Normal'])
    ]

    patient_table = Table([[patient_cell, badge_cell]], colWidths=[13.5 * cm, 4.0 * cm])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.75, BORDER_COLOR),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 4 * mm))

    # 3. TITRE PRESCRIPTIONS
    story.append(Paragraph("<b>PRESCRIPTIONS MÉDICALES :</b>", style_section_title))
    story.append(Spacer(1, 2 * mm))

    # 4. LISTE DES MÉDICAMENTS (TABLEAU STYLISÉ)
    table_data = []
    for idx, p in enumerate(prescriptions, 1):
        est_ecole = p.get('dispo_ecole', False)
        tag = (Paragraph("[Délivré à l'infirmerie]", style_rx_tag_ecole) if est_ecole 
               else Paragraph("[Pharmacie d'officine]", style_rx_tag_pharma))

        rx_block = [
            Paragraph(f"<b>{idx}. {p.get('medicament')}</b>", style_rx_name),
            Spacer(1, 0.8 * mm),
            Paragraph(f"&bull; <b>Posologie :</b> {p.get('dosage')} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Durée :</b> {p.get('duree')}", style_rx_poso)
        ]
        table_data.append([rx_block, tag])

    if not table_data:
        table_data.append([Paragraph("<i>Aucun médicament prescrit lors de cette consultation.</i>", style_rx_poso), ""])

    rx_table = Table(table_data, colWidths=[13.5 * cm, 4.0 * cm])
    rx_style = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]
    rx_table.setStyle(TableStyle(rx_style))
    story.append(rx_table)
    story.append(Spacer(1, 4 * mm))

    # 5. CONTEXTE CLINIQUE / OBSERVATIONS (SI PRÉSENT)
    motif = consultation.get('motif')
    if motif:
        obs_table = Table([[
            Paragraph(f"<b>Indication / Contexte :</b> {motif}", style_patient_sub)
        ]], colWidths=[17.5 * cm])
        obs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(obs_table)
        story.append(Spacer(1, 4 * mm))

    # 6. MENTIONS LÉGALES & CADRE DE SIGNATURE / CACHET
    legal_text = (
        "<b>Conditions de validité légale :</b><br/>"
        "&bull; Ordonnance valable <b>3 mois</b> à compter de sa date de prescription.<br/>"
        "&bull; Délivrance nominative strictement réservée au patient désigné ci-dessus.<br/>"
        "&bull; Ne pas renouveler sans avis médical express.<br/>"
        "&bull; En cas de réaction indésirable, contacter immédiatement le pôle médical scolaire."
    )
    legal_cell = [
        Paragraph(legal_text, style_legal_notice),
        Spacer(1, 2 * mm),
        Paragraph("<font size='6.5' color='#94a3b8'>Système d'Information Médicale &middot; SanteScolaire</font>", style_legal_notice)
    ]

    signature_cell = [
        Paragraph("<b>SIGNATURE & CACHET DU PRATICIEN</b>", style_signature_title),
        Paragraph(f"Dr. {med_prenom} {med_nom}", style_signature_sub),
        Spacer(1, 15 * mm),
        Paragraph("<font size='6.5' color='#94a3b8'>[ Emplacement réservé cachet & visa ]</font>", style_signature_sub)
    ]

    bottom_table = Table([[legal_cell, signature_cell]], colWidths=[10.5 * cm, 7.0 * cm])
    bottom_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (1, 0), (1, 0), 1, colors.HexColor('#94a3b8')),
        ('BACKGROUND', (1, 0), (1, 0), colors.white),
        ('LINEBEFORE', (1, 0), (1, 0), 1, colors.HexColor('#94a3b8')),
        ('TOPPADDING', (1, 0), (1, 0), 8),
        ('BOTTOMPADDING', (1, 0), (1, 0), 8),
        ('LEFTPADDING', (1, 0), (1, 0), 8),
        ('RIGHTPADDING', (1, 0), (1, 0), 8),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#cbd5e1')),
    ]))
    story.append(bottom_table)

    # Construction du document
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_fiche_pai_pdf(eleve, antecedents, medecin_referent=None):
    """
    Génère la Fiche d'Urgence PAI (Protocole d'Accueil Individualisé) au format PDF A4.
    Destinée aux enseignants, surveillants et personnels scolaires en cas d'urgence.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.6 * cm,
        rightMargin=1.6 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.4 * cm
    )

    styles = getSampleStyleSheet()

    style_header_title = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=RED_DANGER
    )
    style_header_sub = ParagraphStyle(
        'HeaderSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=TEXT_DARK
    )
    style_alert_badge = ParagraphStyle(
        'AlertBadge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        alignment=TA_CENTER,
        textColor=colors.white
    )
    style_sec_header = ParagraphStyle(
        'SecHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=TEXT_DARK
    )
    style_sec_desc = ParagraphStyle(
        'SecDesc',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=TEXT_DARK
    )
    style_emergency_box = ParagraphStyle(
        'EmergBox',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=RED_DANGER
    )

    story = []

    # 1. EN-TÊTE D'URGENCE ROUGE
    logo_path = _get_logo_path()
    header_left = []
    if logo_path:
        header_left.append(RLImage(logo_path, width=22 * mm, height=22 * mm))
    
    header_center = [
        Paragraph("FICHE D'URGENCE &middot; PROTOCOLE D'ACCUEIL INDIVIDUALISÉ", style_header_title),
        Spacer(1, 1 * mm),
        Paragraph("Document officiel à destination de l'équipe pédagogique et des surveillants", style_header_sub),
        Paragraph("<font size='7.5' color='#64748b'>Édité sous la responsabilité du Pôle Médical Scolaire &middot; Application Immédiate</font>", styles['Normal'])
    ]

    header_right = [
        Paragraph("<b>URGENCE</b><br/><font size='7.5'>PRIORITÉ ABSOLUE</font>", style_alert_badge)
    ]

    header_table = Table([[header_left, header_center, header_right]], colWidths=[2.8 * cm, 12.0 * cm, 3.0 * cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (2, 0), (2, 0), RED_DANGER),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
        ('TOPPADDING', (2, 0), (2, 0), 6),
        ('BOTTOMPADDING', (2, 0), (2, 0), 6),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 3 * mm))
    story.append(HRFlowable(width="100%", thickness=2, color=RED_DANGER, spaceAfter=8, spaceBefore=2))

    # 2. IDENTITÉ DE L'ÉLÈVE
    nom_el = f"{eleve.get('nom_eleve', '')} {eleve.get('prenom_eleve', '')}".strip()
    classe_el = eleve.get('classe', 'Non assignée')
    dob_el = eleve.get('date_naissance', '')
    if isinstance(dob_el, datetime):
        dob_el = dob_el.strftime('%d/%m/%Y')

    id_cell = [
        Paragraph(f"Élève : <b><font size='13'>{nom_el}</font></b>", styles['Normal']),
        Paragraph(f"Classe : <b>{classe_el}</b> &nbsp;&nbsp;|&nbsp;&nbsp; Date de naissance : <b>{dob_el}</b> &nbsp;&nbsp;|&nbsp;&nbsp; ID : #{eleve.get('id_eleve')}", styles['Normal']),
    ]
    ref_med_nom = f"Dr. {medecin_referent.get('nom_medecin')}" if medecin_referent else "Médecin Scolaire Référent"
    contact_cell = [
        Paragraph(f"<b>Médecin référent :</b> {ref_med_nom}", styles['Normal']),
        Paragraph("<b>Infirmerie :</b> Poste interne 104 / Urgences", styles['Normal']),
    ]

    id_table = Table([[id_cell, contact_cell]], colWidths=[11.0 * cm, 6.8 * cm])
    id_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(id_table)
    story.append(Spacer(1, 4 * mm))

    # 3. LISTE DES PATHOLOGIES / ALLERGIES ET PROTOCOLES D'ACTION
    pai_items = [a for a in antecedents if a.get('pai_signe') or a.get('severite') == 'Critique']
    if not pai_items:
        pai_items = antecedents  # Fallback si aucun explicitement marqué critique

    story.append(Paragraph("<b>PATHOLOGIES & CONDUITE À TENIR EN CAS DE CRISE :</b>", style_sec_header))
    story.append(Spacer(1, 2 * mm))

    for a in pai_items:
        sev = a.get('severite', 'Importante')
        type_ant = a.get('type', 'Pathologie')
        desc = a.get('description', '')
        action = a.get('conduite_a_tenir', 'Alerter immédiatement les secours et l\'infirmerie.')

        item_data = [
            [
                Paragraph(f"<b><font size='11'>{type_ant}</font></b> &nbsp;&nbsp;&bull;&nbsp;&nbsp; Gravité : <font color='#dc2626'><b>{sev.upper()}</b></font>", style_sec_header)
            ],
            [
                Paragraph(f"<b>Symptômes & Description :</b> {desc}", style_sec_desc)
            ],
            [
                Paragraph(f"<b>CONDUITE D'URGENCE IMMÉDIATE :</b><br/>{action}", style_emergency_box)
            ]
        ]
        item_table = Table(item_data, colWidths=[17.8 * cm])
        item_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fef2f2')),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#fee2e2')),
            ('BOX', (0, 0), (-1, -1), 1, RED_DANGER),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor('#fca5a5')),
            ('LINEBELOW', (0, 1), (-1, 1), 0.5, colors.HexColor('#fca5a5')),
        ]))
        story.append(item_table)
        story.append(Spacer(1, 3 * mm))

    # 4. NUMÉROS D'URGENCE RAPIDES
    story.append(Spacer(1, 2 * mm))
    num_data = [
        [
            Paragraph("<b>SAMU : 15</b>", ParagraphStyle('Num1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, textColor=RED_DANGER, alignment=TA_CENTER)),
            Paragraph("<b>POMPIERS : 18</b>", ParagraphStyle('Num2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, textColor=RED_DANGER, alignment=TA_CENTER)),
            Paragraph("<b>NUMÉRO UNIQUE : 112</b>", ParagraphStyle('Num3', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, textColor=RED_DANGER, alignment=TA_CENTER)),
            Paragraph("<b>INFIRMERIE ÉCOLE : 104</b>", ParagraphStyle('Num4', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, textColor=PRIMARY_DARK, alignment=TA_CENTER)),
        ]
    ]
    num_table = Table(num_data, colWidths=[4.4 * cm, 4.4 * cm, 4.4 * cm, 4.6 * cm])
    num_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(num_table)
    story.append(Spacer(1, 4 * mm))

    # 5. CADRE SIGNATURES (MÉDECIN + CHEF D'ÉTABLISSEMENT + PARENTS)
    sig_data = [
        [
            Paragraph("<b>Le Médecin Scolaire</b><br/><br/><font size='7' color='#94a3b8'>Visa & Cachet</font>", ParagraphStyle('s1', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8)),
            Paragraph("<b>Le Chef d'Établissement</b><br/><br/><font size='7' color='#94a3b8'>Signature & Cachet</font>", ParagraphStyle('s2', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8)),
            Paragraph("<b>Les Représentants Légaux</b><br/><br/><font size='7' color='#94a3b8'>Lu et approuvé</font>", ParagraphStyle('s3', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8)),
        ]
    ]
    sig_table = Table(sig_data, colWidths=[5.9 * cm, 5.9 * cm, 6.0 * cm])
    sig_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.75, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 18),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(sig_table)

    doc.build(story)
    buffer.seek(0)
    return buffer

