from flask_login import UserMixin
from sqlalchemy.sql import func
from . import db

# Tabel User
class User(db.Model, UserMixin):
    id = db.Column("ID_User", db.Integer, primary_key=True)
    email = db.Column("Email", db.String(150), nullable=False, unique=True)
    password = db.Column("Password", db.String(500), nullable=False)
    first_name = db.Column("First_Name", db.String(150))
    last_name = db.Column("Last_Name", db.String(150))
    roles = db.Column("Roles", db.String(50), nullable=False, default='client')

# Tabel Marca
class Marca(db.Model):
    id = db.Column("ID_Marca", db.Integer, primary_key=True)
    denumire = db.Column("Denumire", db.String(50), nullable=False, unique=True)
    descriere = db.Column("Descriere", db.String(500))
    modele = db.relationship('Model', backref='marca', lazy=True)

# Tabel Model
class Model(db.Model):
    id = db.Column("ID_Model", db.Integer, primary_key=True)
    id_marca = db.Column("ID_Marca", db.Integer, db.ForeignKey('marca.ID_Marca'), nullable=False)
    denumire = db.Column("Denumire", db.String(100), nullable=False, unique=True)
    descriere = db.Column("Descriere", db.String(500))
    masini = db.relationship('Masina', backref='model', lazy=True)

# Tabel Locatie
class Locatie(db.Model):
    id = db.Column("ID_Locatie", db.Integer, primary_key=True)
    nume = db.Column("Nume_Locatie", db.String(100), nullable=False, unique=True)
    oras = db.Column("Oras", db.String(50), nullable=False)
    adresa = db.Column("Adresa", db.String(100), nullable=False)
    masini = db.relationship('Masina', backref='locatie', lazy=True)

# Tabel Masini
class Masina(db.Model):
    id = db.Column("ID_Masina", db.Integer, primary_key=True)
    id_model = db.Column("ID_Model", db.Integer, db.ForeignKey('model.ID_Model'), nullable=False)
    id_locatie = db.Column("ID_Locatie", db.Integer, db.ForeignKey('locatie.ID_Locatie'), nullable=False)
    an_fabricatie = db.Column("An_Fabricatie", db.Integer, nullable=False) 
    tarif = db.Column("Tarif", db.Numeric, nullable=False)
    imagine_url = db.Column("Imagine_URL", db.String(255))
    is_active = db.Column("IsActive", db.Boolean, nullable=False, default=True)

# Tabel Clienti
class Client(db.Model):
    id = db.Column("ID_Client", db.Integer, primary_key=True)
    email = db.Column("Email", db.String(150), nullable=False, unique=True)
    first_name = db.Column("First_Name", db.String(150))
    last_name = db.Column("Last_Name", db.String(150))
    cnp = db.Column("CNP", db.String(13), nullable=False)
    telefon = db.Column("Telefon", db.String(15), nullable=False,)
    rezervare = db.relationship('Rezervare', backref='client', uselist=False)

# Tabel Rezervari
class Rezervare(db.Model):
    id = db.Column("ID_Rezervare", db.Integer, primary_key=True)
    id_client = db.Column("ID_Client", db.Integer, db.ForeignKey('client.ID_Client'), nullable=False)
    data_inchiriere = db.Column("Data_Inchiriere", db.DateTime, default=func.now())
    data_returnare = db.Column("Data_Returnare", db.DateTime, default=func.now())
    facturi = db.relationship('Factura', backref='rezervare', uselist=False)
    masini = db.relationship('RezervariMasini', backref='rezervare', lazy=True)

# Tabel Facturi
class Factura(db.Model):
    id = db.Column("ID_Factura", db.Integer, primary_key=True)
    id_rezervare = db.Column("ID_Rezervare", db.Integer, db.ForeignKey('rezervare.ID_Rezervare'), unique=True, nullable=False)
    numar_factura = db.Column("Numar_Factura", db.String(50), nullable=False)
    data_plata = db.Column("Data_Plata", db.DateTime, default=func.now())
    data_emitere = db.Column("Data_Emitere", db.DateTime, default=func.now())
    suma_totala = db.Column("Suma_Totala", db.Numeric, nullable=False)

# Tabel de legătură RezervariMasini
class RezervariMasini(db.Model):
    id_rezervare = db.Column("ID_Rezervare", db.Integer, db.ForeignKey('rezervare.ID_Rezervare'), primary_key=True)
    id_masina = db.Column("ID_Masina", db.Integer, db.ForeignKey('masina.ID_Masina'), primary_key=True)

