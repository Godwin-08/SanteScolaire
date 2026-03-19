import json
import os

EMAILS_FILE = "medecin_emails.json"


def get_emails():
    """Charge les emails depuis le fichier JSON."""
    if not os.path.exists(EMAILS_FILE):
        return {}
    try:
        with open(EMAILS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_emails_data(emails):
    """Sauvegarde les emails dans le fichier JSON."""
    with open(EMAILS_FILE, "w") as f:
        json.dump(emails, f)
