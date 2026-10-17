import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# --- CONFIGURATION SMTP ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "godwinelienougbolo@gmail.com"
SMTP_PASSWORD = "ziyi gveq biua ihkn"

def send_activation_email(recipient, name, activation_link, role):
    """Envoie le lien sécurisé d'activation du compte (valable 48h) avec le logo officiel de l'application."""
    try:
        msg_root = MIMEMultipart("related")
        msg_root["From"] = f"SanteScolaire Maroc <{SMTP_EMAIL}>"
        msg_root["To"] = recipient
        msg_root["Subject"] = "Activation de votre compte soignant - SanteScolaire"

        role_label = "Médecin" if role == "medecin" else ("Infirmier(ère)" if role == "infirmier" else "Personnel Soignant")

        # Version texte brut (fallback)
        text_body = f"""Bonjour {name},

Un compte professionnel a été créé pour vous sur la plateforme SanteScolaire ({role_label}).

Pour activer votre compte et définir votre mot de passe, cliquez sur ce lien sécurisé (valable 48 heures) :
{activation_link}

Ce lien est strictement personnel et à usage unique.
Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer ce message.

L'administration SanteScolaire Maroc
"""

        # Version HTML riche avec le logo officiel de l'application
        html_body = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Activation de compte SanteScolaire</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f6f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #2d3748;">
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f4f6f9; padding: 30px 15px;">
        <tr>
            <td align="center">
                <!-- Conteneur Principal -->
                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 560px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.06); border: 1px solid #e2e8f0;">
                    
                    <!-- En-tête avec bannière émeraude et VRAI logo de l'application -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #10ac84 0%, #0d9370 100%); padding: 36px 30px; text-align: center;">
                            <div style="margin-bottom: 12px;">
                                <img src="cid:logo_santescolaire" alt="SanteScolaire" width="64" height="64" style="width: 64px; height: 64px; border-radius: 14px; box-shadow: 0 6px 18px rgba(0,0,0,0.18); display: inline-block; vertical-align: middle;" />
                            </div>
                            <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 700; letter-spacing: -0.5px;">SanteScolaire</h1>
                            <p style="margin: 6px 0 0; color: rgba(255, 255, 255, 0.9); font-size: 13px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Santé & Médecine Scolaire</p>
                        </td>
                    </tr>

                    <!-- Corps de l'email -->
                    <tr>
                        <td style="padding: 36px 32px 24px;">
                            <h2 style="margin: 0 0 14px; font-size: 20px; font-weight: 700; color: #1a202c;">
                                Bienvenue, {name} !
                            </h2>
                            <p style="margin: 0 0 20px; font-size: 15px; line-height: 1.6; color: #4a5568;">
                                L'administration de l'établissement vient de créer votre accès professionnel sur le portail médical scolaire.
                            </p>

                            <!-- Carte Récapitulative du Profil -->
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f7fafc; border-radius: 12px; border: 1px solid #edf2f7; margin-bottom: 26px;">
                                <tr>
                                    <td style="padding: 16px 20px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td style="font-size: 13px; color: #718096; padding-bottom: 6px; font-weight: 600;">FONCTION ATTRIBUÉE</td>
                                                <td align="right" style="padding-bottom: 6px;">
                                                    <span style="background-color: #e6fffa; color: #047857; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 20px; border: 1px solid #a7f3d0;">
                                                        {role_label}
                                                    </span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size: 13px; color: #718096; font-weight: 600;">IDENTIFIANT DE CONNEXION</td>
                                                <td align="right" style="font-size: 14px; color: #2d3748; font-weight: 600;">{recipient}</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>

                            <p style="margin: 0 0 24px; font-size: 14px; line-height: 1.5; color: #4a5568;">
                                Pour finaliser votre inscription et <strong>choisir votre mot de passe personnel</strong>, veuillez cliquer sur le bouton ci-dessous :
                            </p>

                            <!-- Bouton Call To Action -->
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 28px;">
                                <tr>
                                    <td align="center">
                                        <a href="{activation_link}" target="_blank" style="display: inline-block; background-color: #10ac84; color: #ffffff; text-decoration: none; font-size: 15px; font-weight: 700; padding: 14px 34px; border-radius: 50px; box-shadow: 0 4px 14px rgba(16, 172, 132, 0.4); text-align: center;">
                                            Activer mon compte & Définir mon mot de passe &rarr;
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <!-- Notice de sécurité -->
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #fffaf0; border-left: 4px solid #dd6b20; border-radius: 6px; margin-bottom: 24px;">
                                <tr>
                                    <td style="padding: 12px 16px;">
                                        <p style="margin: 0; font-size: 12px; line-height: 1.5; color: #7c2d12;">
                                            <strong>Information de sécurité :</strong> Ce lien d'activation est <strong>valable pendant 48 heures</strong> et à usage unique. Il expire automatiquement après votre première configuration de mot de passe.
                                        </p>
                                    </td>
                                </tr>
                            </table>

                            <!-- Fallback lien texte -->
                            <p style="margin: 0; font-size: 12px; line-height: 1.5; color: #a0aec0; word-break: break-all;">
                                Si le bouton ne fonctionne pas, copiez-collez ce lien direct dans votre navigateur :<br>
                                <a href="{activation_link}" style="color: #10ac84; text-decoration: underline;">{activation_link}</a>
                            </p>
                        </td>
                    </tr>

                    <!-- Pied de page -->
                    <tr>
                        <td style="background-color: #edf2f7; padding: 20px 32px; text-align: center; border-top: 1px solid #e2e8f0;">
                            <p style="margin: 0 0 6px; font-size: 12px; color: #718096; font-weight: 500;">
                                &copy; 2026 SanteScolaire Maroc &bull; Gestion Médicale & Infirmerie Scolaire
                            </p>
                            <p style="margin: 0; font-size: 11px; color: #a0aec0;">
                                Vous recevez cet email car un compte praticien a été enregistré pour votre adresse sur le portail hospitalier scolaire.
                            </p>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

        msg_alt = MIMEMultipart("alternative")
        msg_alt.attach(MIMEText(text_body, "plain"))
        msg_alt.attach(MIMEText(html_body, "html"))
        msg_root.attach(msg_alt)

        # Attacher le logo officiel en tant qu'image CID intégrée
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'frontend', 'static', 'img', 'logo.png')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                img_data = f.read()
                img_part = MIMEImage(img_data, _subtype="png")
                img_part.add_header('Content-ID', '<logo_santescolaire>')
                img_part.add_header('Content-Disposition', 'inline', filename='logo.png')
                msg_root.attach(img_part)

        return _execute_send(msg_root)
    except Exception as e:
        print(f"Erreur préparation activation email: {e}")
        return False

def send_welcome_email(recipient, name, login_email, role):
    """Envoie les identifiants de connexion au nouvel utilisateur."""
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"SanteScolaire Maroc <{SMTP_EMAIL}>"
        msg["To"] = recipient
        msg["Subject"] = "Bienvenue - Vos identifiants SanteScolaire"

        text_body = f"""
        Bonjour {name},

        Votre compte a été créé avec succès sur le portail SanteScolaire.
        
        Voici vos informations de connexion :
        -----------------------------------------------------------
        Adresse Email : {login_email}
        Fonction : {role}
        -----------------------------------------------------------

        Vous pouvez vous connecter directement ici : http://127.0.0.1:5000/login

        Note : Pour votre sécurité, ne partagez jamais vos identifiants.
        
        Cordialement,
        L'équipe SanteScolaire
        """
        msg.attach(MIMEText(text_body, "plain"))

        return _execute_send(msg)
    except Exception as e:
        print(f"Erreur préparation welcome email: {e}")
        return False

def send_rdv_notification(medecin_id, medecin_nom, eleve_nom, date_rdv, medecin_email=None):
    """Envoie un email de notification au médecin."""
    if not medecin_email:
        # Essayer de récupérer l'email via la base si disponible
        try:
            from app.db import mysql
            cur = mysql.connection.cursor()
            cur.execute("SELECT email FROM medecin WHERE id_medecin = %s", [medecin_id])
            row = cur.fetchone()
            cur.close()
            if row:
                medecin_email = row.get('email')
        except Exception:
            pass

    if not medecin_email:
        print(f"Notification annulée : Pas d'email pour Dr. {medecin_nom} (ID: {medecin_id})")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"SanteScolaire Maroc <{SMTP_EMAIL}>"
        msg["To"] = medecin_email
        msg["Subject"] = f"Nouveau RDV Médical : {eleve_nom}"

        date_fmt = str(date_rdv).replace("T", " ")

        text_body = f"""
        Bonjour Dr. {medecin_nom},

        Un nouveau rendez-vous a été programmé dans votre agenda médical scolaire.
        
        Élève : {eleve_nom}
        Date & Heure : {date_fmt}

        Connectez-vous à l'intranet pour consulter le dossier de l'élève.
        
        Cordialement,
        L'infirmerie scolaire - SanteScolaire
        """
        msg.attach(MIMEText(text_body, "plain"))

        return _execute_send(msg)
    except Exception as e:
        print(f"Erreur préparation rdv email: {e}")
        return False

def _execute_send(msg):
    """Logique interne d'envoi SMTP (simulée si compte par défaut)."""
    if "santescolaire.ma" in SMTP_EMAIL or SMTP_PASSWORD == "votre_mot_de_passe_app":
        print("--- [SIMULATION ENVOI EMAIL] ---")
        print(f"Destinataire: {msg['To']}")
        print(f"Sujet: {msg['Subject']}")
        print("--------------------------------")
        return True

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Erreur SMTP: {e}")
        return False
