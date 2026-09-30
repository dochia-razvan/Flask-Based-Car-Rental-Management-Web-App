from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import sqlite3
from os import path
from urllib.parse import unquote
import re

# Cream un Blueprint pentru functionalitatile de autentificare
auth = Blueprint('auth', __name__)

# Functie pentru executarea interogarilor in baza de date
def execute_query(query, params=(), fetchone=False):
    # Deschidem conexiunea la baza de date
    connection = sqlite3.connect(path.join('instance', 'database.db'))
    cursor = connection.cursor()
    # Executam interogarea SQL
    cursor.execute(query, params)
    # Extragem datele daca este necesar
    data = cursor.fetchone() if fetchone else cursor.fetchall()
    # Salvam modificarile si inchidem conexiunea
    connection.commit()
    connection.close()
    return data

# Functie pentru validarea email-urilor
def is_valid_email(email):
    # Verifica daca email-ul are un format valid utilizand regex
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email)

# Ruta pentru pagina de login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    from .tabele import User  # Importam modelul User
    errors = []  # Lista pentru erorile din formular
    errors_url = request.args.get('errors', None)  # Preluam erorile din URL daca exista
    if errors_url:
        errors.append(unquote(errors_url))  # Decodificam erorile din URL

    if request.method == 'POST':
        # Preluam valorile din formular
        email = request.form.get('email')
        password = request.form.get('password')

        # Verificam daca toate campurile sunt completate
        if not email or not password:
            errors.append('Toate campurile marcate cu * trebuie completate.')

        if not errors:
            # Cautam utilizatorul in baza de date
            user = User.query.filter_by(email=email).first()
            # Verificam daca parola este corecta
            if user and check_password_hash(user.password, password):
                # Logam utilizatorul si redirectionam catre pagina principala
                login_user(user)
                return redirect(url_for('views.home'))
            else:
                errors.append('Email-ul sau parola sunt incorecte.')

    return render_template("login.html", errors=errors, user=current_user)

# Ruta pentru logout
@auth.route('/logout')
@login_required
def logout():
    # Deconectam utilizatorul curent si redirectionam catre pagina de login
    logout_user()
    return redirect(url_for('auth.login'))

# Ruta pentru pagina de inregistrare
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    errors = []  # Lista pentru erorile din formular
    errors_url = request.args.get('errors', None)  # Preluam erorile din URL daca exista
    if errors_url:
        errors = unquote(errors_url).split('|')  # Decodificam erorile din URL

    if request.method == 'POST':
        # Preluam valorile din formular
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Cautam utilizatorul in baza de date dupa email
        user_query = "SELECT * FROM User WHERE Email = ?"
        user = execute_query(user_query, (email,), fetchone=True)

        # Verificam validitatea datelor introduse
        if user:
            errors.append('Email-ul deja exista.')
        elif len(email) < 1 or len(first_name) < 1 or len(last_name) < 1 or len(password1) < 1 or len(password2) < 1:
            errors.append('Toate campurile marcate cu * trebuie completate.')
        elif not is_valid_email(email):
            errors.append('Email-ul nu este valid.')
        elif password1 != password2:
            errors.append('Parolele nu se potrivesc.')
        else:
            # Daca datele sunt valide, criptam parola si inseram utilizatorul in baza de date
            hashed_password = generate_password_hash(password1, method='pbkdf2:sha256')
            insert_query = """
            INSERT INTO User (Email, Password, First_Name, Last_Name, Roles) 
            VALUES (?, ?, ?, ?, ?)
            """
            execute_query(insert_query, (email, hashed_password, first_name, last_name, 'client'))
            # Redirectionam catre pagina de login cu mesaj de succes
            return redirect(url_for('auth.login', success_message='Account created successfully!'))

        if errors:
            # Daca exista erori, redirectionam catre pagina de inregistrare
            return redirect(url_for('auth.sign_up', errors="|".join(errors)))

    return render_template("sign_up.html", errors=errors, user=current_user)
