# models/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importar modelos para que se registren
from models.usuario import Usuario
from models.chat import ChatMessage
from models.conversation import Conversation
