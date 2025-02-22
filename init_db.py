# init_db.py
from app import app, db  # Asegúrate de importar 'db' desde app.py

with app.app_context():
    db.create_all()
    print("Base de datos inicializada correctamente.")
