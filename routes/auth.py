from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.usuario import db, Usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Maneja el registro de usuarios"""
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']

        if Usuario.query.filter_by(email=email).first():
            flash("El correo ya está registrado", "error")
            return redirect(url_for('auth.signup'))

        nuevo_usuario = Usuario(nombre=nombre, email=email)
        nuevo_usuario.set_password(password)

        db.session.add(nuevo_usuario)
        db.session.commit()

        flash("Registro exitoso. Inicia sesión.", "success")
        return redirect(url_for('auth.login'))

    return render_template('signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja el inicio de sesión"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.check_password(password):
            session['user_id'] = usuario.id
            session['user_name'] = usuario.nombre
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for('index'))  # 🔥 Asegúrate de que 'index' es el nombre de la función en app.py
        
        flash("Correo o contraseña incorrectos", "error")

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Cierra la sesión del usuario"""
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for('index'))  # 🔥 Corregido (antes usaba 'index.html', lo cual es incorrecto en Flask)
