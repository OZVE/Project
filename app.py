from flask import Flask, render_template, session, request, jsonify, url_for, redirect
from flask_socketio import SocketIO, emit
from config import Config
from models import db
from routes.auth import auth_bp
from models.chat import ChatMessage
import openai
import os
import re
from dotenv import load_dotenv
from static.utils import get_context_messages, login_required

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.getenv("SECRET_KEY", "super_secret_key")


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

@app.route('/conversations', endpoint='lista_conversaciones')
@login_required
def conversations():
    from models.conversation import Conversation
    convs = Conversation.query.filter_by(user_id=session.get('user_id')).order_by(Conversation.created_at.desc()).all()
    return render_template('conversations.html', conversations=convs)

@app.route('/new-conversation')
@login_required
def new_conversation():
    from models.conversation import Conversation
    # Crear una nueva conversación con título por defecto
    conv = Conversation(user_id=session.get('user_id'), title="Nueva Conversación")
    db.session.add(conv)
    db.session.commit()
    return redirect(url_for('chat', conversation_id=conv.id))


@app.route('/chat/<int:conversation_id>')
@login_required
def chat(conversation_id):
    from models.conversation import Conversation
    conv = Conversation.query.filter_by(id=conversation_id, user_id=session.get('user_id')).first_or_404()
    messages = conv.messages  # O una consulta ordenada
    return render_template('chat.html', conversation=conv, messages=messages)

@app.route('/conversations')
@login_required
def conversations():
    from models.conversation import Conversation
    convs = Conversation.query.filter_by(user_id=session.get('user_id')).order_by(Conversation.created_at.desc()).all()
    return render_template('conversations.html', conversations=convs)


@app.route('/', endpoint='index')
@login_required
def index():
    return render_template('index.html', user=session.get('user_name'))

@socketio.on('user_message')
def handle_user_message(data):
    user_input = data['message']
    conversation_id = data.get('conversation_id')
    print(f"📩 Mensaje recibido del usuario: {user_input} en conversación: {conversation_id}")

    
    
    # Guardar el mensaje del usuario
    if 'user_id' in session and conversation_id:
        user_message = ChatMessage(
            conversation_id=conversation_id,
            user_id=session['user_id'],
            sender='user',
            message=user_input
        )
        db.session.add(user_message)
        db.session.commit()

    try:

        context_messages = get_context_messages(conversation_id)

        messages_payload = [
            {"role": "system", "content": "Eres un asistente experto en gestión de proyectos."}
        ] + context_messages + [{"role": "user", "content": user_input}]

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages_payload
        )
        
        ai_response = response.choices[0].message.content
        print(f"🤖 Respuesta de la IA: {ai_response}")
    except Exception as e:
        ai_response = f"❌ Error al obtener respuesta de la IA: {str(e)}"
        print(f"⚠️ Error en la API de OpenAI: {str(e)}")
    
    # Guardar la respuesta de la IA
    if 'user_id' in session and conversation_id:
        ai_message = ChatMessage(
            conversation_id=conversation_id,
            user_id=session['user_id'],
            sender='ai',
            message=ai_response
        )
        db.session.add(ai_message)
        db.session.commit()



    emit('chat_update', {
    'conversation_id': conversation_id,
     'messages': [
        {'sender': 'user', 'message': user_input},
        {'sender': 'ai', 'message': ai_response}
        ]
    }, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True, use_reloader=False)
