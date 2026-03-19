from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

orm_db = SQLAlchemy()
migrate = Migrate()
