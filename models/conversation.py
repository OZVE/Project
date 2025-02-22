# models/conversation.py
from datetime import datetime
from models import db

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    title = db.Column(db.String(255), default="Nueva conversación")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación para acceder a los mensajes de la conversación
    messages = db.relationship('ChatMessage', backref='conversation', lazy=True)
