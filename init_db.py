from app import app
from models import db  # Asegúrate de que `db` está definido en `models.py`

def initialize_database():
    with app.app_context():
        db.create_all()
        print("📌 Base de datos inicializada correctamente.")

if __name__ == "__main__":
    initialize_database()
