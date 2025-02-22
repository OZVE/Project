from functools import wraps
from flask import app, jsonify, redirect, session, url_for

from models.chat import ChatMessage

def login_required(f):
    """Decorador para verificar si el usuario está autenticado."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper

def get_context_messages(conversation_id, limit=10):
    """
    Recupera los últimos 'limit' mensajes de la conversación en formato para enviar a la API.
    """
    messages = ChatMessage.query.filter_by(conversation_id=conversation_id) \
                .order_by(ChatMessage.timestamp.desc()).limit(limit).all()
    # Invertir el orden para que sea cronológico
    messages = list(reversed(messages))
    # Formatear cada mensaje según el rol esperado por la API de OpenAI
    formatted = []
    for msg in messages:
        role = 'user' if msg.sender == 'user' else 'assistant'
        formatted.append({"role": role, "content": msg.message})
    return formatted
