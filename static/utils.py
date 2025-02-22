from flask import redirect, session, url_for

def login_required(f):
    """Decorador para verificar si el usuario está autenticado."""
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper
