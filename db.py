from flask_mysqldb import MySQL

# Instance globale de MySQL pour être importée dans les blueprints
# Cela permet d'éviter les importations circulaires et de partager la connexion DB
mysql = MySQL()