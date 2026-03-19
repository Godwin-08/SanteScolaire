import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.utils import get_emails


def send_rdv_notification(medecin_id, medecin_nom, eleve_nom, date_rdv):
    """Envoie un email de notification au médecin."""
    emails = get_emails()
    medecin_email = emails.get(str(medecin_id))

    if not medecin_email:
        print(
            f"Notification annulée : Pas d'email pour Dr. {medecin_nom} (ID: {medecin_id})"
        )
        return False

    # --- CONFIGURATION SMTP (À ADAPTER) ---
    # Exemple pour Gmail (nécessite un mot de passe d'application si 2FA activé)
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_EMAIL = "votre_email@gmail.com"
    SMTP_PASSWORD = "votre_mot_de_passe_app"

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_EMAIL
        msg["To"] = medecin_email
        msg["Subject"] = f"Nouveau RDV : {eleve_nom}"

        # Formatage de la date (suppression du T)
        date_fmt = str(date_rdv).replace("T", " ")

        body = f"""
        Bonjour Dr. {medecin_nom},

        Un nouveau rendez-vous a été programmé dans votre agenda.
        
        Patient : {eleve_nom}
        Date : {date_fmt}

        Connectez-vous à l'intranet pour voir les détails.
        
        Cordialement,
        L'équipe SanteScolaire
        """
        msg.attach(MIMEText(body, "plain"))

        # Simulation (pour éviter les erreurs tant que vous n'avez pas mis vos vrais identifiants)
        if SMTP_EMAIL == "votre_email@gmail.com":
            print("--- [SIMULATION EMAIL] ---")
            print(f"À: {medecin_email}")
            print(f"Sujet: {msg['Subject']}")
            print(f"Corps: \n{body}")
            print("--------------------------")
            return True

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False
