import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    def __init__(self):
        self.SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

        self.MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
        self.MYSQL_USER = os.environ.get("MYSQL_USER", "root")
        self.MYSQL_PASSWORD = os.environ.get("DB_PASSWORD")
        self.MYSQL_DB = os.environ.get("MYSQL_DB", "gestion_hospitaliere_scolaire")
        self.MYSQL_CURSORCLASS = "DictCursor"

        password = "" if self.MYSQL_PASSWORD is None else quote_plus(self.MYSQL_PASSWORD)
        self.SQLALCHEMY_DATABASE_URI = (
            f"mysql+mysqldb://{self.MYSQL_USER}:{password}@{self.MYSQL_HOST}/{self.MYSQL_DB}"
        )
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
