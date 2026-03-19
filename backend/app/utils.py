import json
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EMAILS_FILE = os.path.join(BASE_DIR, "medecin_emails.json")


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
