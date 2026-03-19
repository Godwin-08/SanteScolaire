import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.constants import ROLE_MEDECIN
from app.utils import get_emails

# --- CONFIGURATION SMTP ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "votre_compte@gmail.com"  # À REMPLACER
SMTP_PASSWORD = "votre_mot_de_passe_app" # À REMPLACER

def send_welcome_email(recipient, name, user_id, role):
    """Envoie les identifiants de connexion au nouvel utilisateur."""
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"SanteScolaire <{SMTP_EMAIL}>"
        msg["To"] = recipient
        msg["Subject"] = "Bienvenue - Vos identifiants SanteScolaire"

        text_body = f"""
        Bonjour {name},

        Votre compte a été créé avec succès.
        
        Voici vos informations de connexion :
        -----------------------------------------------------------
        Identifiant professionnel : {user_id}
        Rôle : {role}
        -----------------------------------------------------------

        Vous pouvez vous connecter ici : http://127.0.0.1:5000/login

        Note : Pour votre sécurité, ne partagez pas ces informations.
        
        Cordialement,
        L'équipe SanteScolaire
        """
        msg.attach(MIMEText(text_body, "plain"))

        return _execute_send(msg)
    except Exception as e:
        print(f"Erreur préparation welcome email: {e}")
        return False

def send_rdv_notification(medecin_id, medecin_nom, eleve_nom, date_rdv):
    """Envoie un email de notification au médecin."""
    emails = get_emails()
    key = f"{ROLE_MEDECIN}_{medecin_id}"
    medecin_email = emails.get(key) or emails.get(str(medecin_id))

    if not medecin_email:
        print(
            f"Notification annulée : Pas d'email pour Dr. {medecin_nom} (ID: {medecin_id})"
        )
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"SanteScolaire <{SMTP_EMAIL}>"
        msg["To"] = medecin_email
        msg["Subject"] = f"Nouveau RDV : {eleve_nom}"

        # Formatage de la date (suppression du T)
        date_fmt = str(date_rdv).replace("T", " ")

        text_body = f"""
        Bonjour Dr. {medecin_nom},

        Un nouveau rendez-vous a été programmé dans votre agenda.
        
        Patient : {eleve_nom}
        Date : {date_fmt}

        Connectez-vous à l'intranet pour voir les détails.
        
        Cordialement,
        L'équipe SanteScolaire
        """
        msg.attach(MIMEText(text_body, "plain"))

        return _execute_send(msg)
    except Exception as e:
        print(f"Erreur préparation rdv email: {e}")
        return False

def _execute_send(msg):
    """Logique interne d'envoi SMTP."""
    if SMTP_EMAIL == "votre_compte@gmail.com":
        print("--- [SIMULATION GMAIL] ---")
        print(f"Destinataire: {msg['To']}")
        print(f"Sujet: {msg['Subject']}")
        print("--------------------------")
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
