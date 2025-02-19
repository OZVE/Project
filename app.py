from flask import Flask, render_template, session, request, jsonify, url_for, redirect
from flask_socketio import SocketIO, emit
from config import Config
from models.usuario import db
from routes.auth import auth_bp
import openai
import os
import re
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super_secret_key")
app.config.from_object(Config)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Inicializar base de datos
db.init_app(app)

# Registrar Blueprints
app.register_blueprint(auth_bp)

# Configurar la API de OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ ERROR: OPENAI_API_KEY no está configurada. Verifica tu archivo .env.")

client = openai.Client(api_key=api_key)

def login_required(f):
    """ Decorador para verificar si el usuario esta autenticado """
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper

@app.route('/session-check')
def session_check():
    return jsonify({"authenticated": "user_id" in session})

@app.route('/')
@login_required
def index():
    return render_template('index.html', user=session.get('user_name'))

@socketio.on('user_message')
def handle_user_message(data):
    user_input = data['message']
    print(f"📩 Mensaje recibido del usuario: {user_input}")

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en gestión de proyectos."},
                {"role": "user", "content": user_input}
            ]
        )
        ai_response = response.choices[0].message.content
        print(f"🤖 Respuesta de la IA: {ai_response}")
    except Exception as e:
        ai_response = f"❌ Error al obtener respuesta de la IA: {str(e)}"
        print(f"⚠️ Error en la API de OpenAI: {str(e)}")

    #Emitir el mensaje del usuario al chat
    emit('chat_update', {'sender': 'user', 'message': user_input}, broadcast=True)
    # Emitir la respuesta de la IA al chat
    emit('chat_update', {'sender': 'ai', 'message': ai_response}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, use_reloader=False)
