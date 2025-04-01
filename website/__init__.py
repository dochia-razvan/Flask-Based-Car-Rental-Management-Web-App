from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_login import current_user
from sqlalchemy import inspect
from os import path
import sqlite3
from datetime import datetime
from flask.json import dumps 

# Initializam obiectul SQLAlchemy pentru gestionarea bazei de date
db = SQLAlchemy()
DB_NAME = "database.db"  # Numele fisierului bazei de date

# Functie pentru executarea interogarilor SQL
def execute_query(query, params=(), fetchone=False):
    # Deschidem o conexiune catre baza de date
    connection = sqlite3.connect(path.join('instance', DB_NAME))
    cursor = connection.cursor()
    # Executam interogarea si obtinem rezultatele
    cursor.execute(query, params)
    data = cursor.fetchone() if fetchone else cursor.fetchall()
    connection.commit()  # Salvam modificarile in baza de date
    connection.close()  # Inchidem conexiunea
    return data

# Functie pentru crearea aplicatiei Flask
def create_app():
    app = Flask(__name__)  # Cream aplicatia Flask
    app.config['SECRET_KEY'] = 'dwaftrzsdgrdsytawdasfwqedawdfsfzfwafazsdfas'  # Cheie secreta pentru securitate
    # Configuram baza de date SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{path.join(app.instance_path, DB_NAME)}'
    db.init_app(app)  # Initializam SQLAlchemy cu aplicatia Flask

    # Importam si inregistram Blueprints
    from .views import views
    from .auth import auth
    from . import tabele  # Importam tabelele definite

    app.register_blueprint(views, url_prefix='/')  # Blueprint pentru functionalitatile principale
    app.register_blueprint(auth, url_prefix='/')  # Blueprint pentru autentificare

    # Cream tabelele in baza de date, daca nu exista
    with app.app_context():
        db.create_all()  # Creeaza toate tabelele definite
        inspector = inspect(db.engine)  # Inspecteaza structura bazei de date

    # Configuram managerul de autentificare
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Pagina implicita pentru login
    login_manager.init_app(app)  # Asociem managerul cu aplicatia Flask

    # Functie pentru incarcarea utilizatorului curent in sesiune
    @login_manager.user_loader
    def load_user(user_id):
        return tabele.User.query.get(int(user_id))  # Incarca utilizatorul pe baza ID-ului

    # Injecteaza obiectul utilizatorului curent in toate sabloanele
    @app.context_processor
    def inject_user():
        return dict(user=current_user)

    # Injecteaza variabile globale in toate sabloanele
    @app.context_processor
    def inject_globals():
        return dict(user=current_user, datetime=datetime)

    # Adaugam functii utile pentru sabloane Jinja2
    app.jinja_env.globals.update(enumerate=enumerate)  # Permite utilizarea `enumerate` in sabloane
    app.jinja_env.filters['tojson'] = dumps  # Permite conversia la JSON in sabloane

    return app  # Returnam aplicatia Flask configurata