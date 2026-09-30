from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import sqlite3
from os import path
from datetime import datetime
from urllib.parse import unquote
import re
from datetime import datetime
import json

# Defineste un blueprint Flask numit 'views' pentru organizarea rutelor aplicatiei
views = Blueprint('views', __name__)

# Specifica folderul unde vor fi incarcate fisierele (imagini)
UPLOAD_FOLDER = '/website/static/uploads/'

# Defineste extensiile permise pentru incarcarea fisierelor
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Calea implicita pentru imaginea care va fi utilizata daca nu exista o imagine specificata
DEFAULT_IMAGE_PATH = 'static/photos/default.png'

# Functie pentru executarea interogarilor SQL
def execute_query(query, params=(), fetchone=False):
    # Se conecteaza la baza de date
    connection = sqlite3.connect(path.join('instance', 'database.db'))
    cursor = connection.cursor()
    # Executa interogarea cu parametrii specificati
    cursor.execute(query, params)
    # Returneaza un singur rezultat sau toate rezultatele, in functie de argument
    data = cursor.fetchone() if fetchone else cursor.fetchall()
    # Salveaza modificarile in baza de date si inchide conexiunea
    connection.commit()
    connection.close()
    return data

# Verifica daca un email este valid
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# Verifica daca un numar de telefon este valid
def is_valid_phone(phone):
    phone_regex = r'^\+?[0-9]+$'
    return re.match(phone_regex, phone) is not None

# Functie pentru obtinerea URL-ului unei imagini
def get_image_url(image_path):
    # Daca nu exista o cale pentru imagine sau este goala, se returneaza calea implicita
    if not image_path or image_path.strip() == "":
        return "/static/photos/default.png"

    # Daca calea incepe cu "website/", elimina prefixul pentru a obtine calea relativa
    if image_path.startswith("website/"):
        relative_path = image_path.replace("website/", "")
    else:
        relative_path = image_path

    # Creeaza caile complete pentru folderul de upload si folderul de imagini implicite
    uploads_path = os.path.join("website/static/uploads", os.path.basename(relative_path))
    photos_path = os.path.join("website/static/photos", os.path.basename(relative_path))

    # Verifica daca fisierul exista in folderul de upload
    if os.path.exists(uploads_path):
        return f"/static/uploads/{os.path.basename(relative_path)}"
    # Verifica daca fisierul exista in folderul de imagini implicite
    elif os.path.exists(photos_path):
        return f"/static/photos/{os.path.basename(relative_path)}"
    # Daca fisierul nu exista in niciunul dintre foldere, returneaza calea implicita
    else:
        return "/static/photos/default.png"

# Ruta pentru obtinerea detaliilor unei masini in functie de ID-ul acesteia
@views.route('/get-car-details/<int:masina_id>', methods=['GET'])
def get_car_details(masina_id):
    # Interogare SQL pentru detaliile masinii
    query = """
        SELECT Tarif, ID_Locatie, Imagine_URL
        FROM Masina
        WHERE ID_Masina = ?
    """
    masina = execute_query(query, (masina_id,), fetchone=True)

    # Daca masina exista, returneaza detaliile acesteia
    if masina:
        return {
            "tarif": masina[0],
            "id_locatie": masina[1],
            "imagine_url": get_image_url(masina[2])
        }, 200
    # Daca masina nu exista, returneaza un mesaj de eroare si codul 404
    else:
        return {"error": "Mașina nu a fost găsită."}, 404

# Functie pentru verificarea extensiilor permise ale fisierelor incarcate
def allowed_file(filename):
    # Verifica daca fisierul are o extensie si daca aceasta este permisa
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta pentru modificarea datelor despre masini, disponibila doar pentru utilizatorii logati
@views.route('/modificare-date-masini', methods=['GET', 'POST'])
@login_required
def modificare_date_masini():
    # Verifica daca utilizatorul are rolul de 'angajat'; daca nu, il redirectioneaza la pagina principala
    if current_user.roles != 'angajat':
        return render_template("home.html", user=current_user)

    # Initializeaza listele pentru erori si mesajele de succes
    errors = []
    success_message = request.args.get('success_message', None)
    errors_url = request.args.get('errors', None)

    # Decodifica eventualele erori primite prin URL
    if errors_url:
        errors = unquote(errors_url).split('|')

    # Daca metoda HTTP este POST, se incearca salvarea noilor date
    if request.method == 'POST':
        # Preia valorile introduse de utilizator din formular
        id_marca = request.form.get('id_marca', type=int)
        id_model = request.form.get('id_model')
        id_locatie = request.form.get('id_locatie')
        tarif = request.form.get('tarif')
        an_fabricatie = request.form.get('an_fabricatie')
        imagine = request.files.get('imagine')

        # Verifica daca toate campurile obligatorii sunt completate
        if not id_model or not id_locatie or not tarif or not an_fabricatie:
            errors.append("Toate câmpurile marcate cu * trebuie completate.")

        # Valideaza tariful
        if tarif:
            try:
                tarif = float(tarif)
                # Verifica daca tariful este cel putin 20 RON
                if tarif < 20:
                    errors.append("Tariful trebuie să fie cel puțin 20 RON.")
            except ValueError:
                # Adauga o eroare daca tariful nu este un numar valid
                errors.append("Tariful trebuie să fie un număr valid.")

        # Valideaza anul de fabricatie
        if an_fabricatie:
            try:
                an_fabricatie = int(an_fabricatie)
                current_year = datetime.now().year
                # Verifica daca anul este intre 1990 si anul curent
                if an_fabricatie < 1990 or an_fabricatie > current_year:
                    errors.append(f"Anul de fabricație trebuie să fie între 1990 și {current_year}.")
            except ValueError:
                # Adauga o eroare daca anul de fabricatie nu este un numar valid
                errors.append("Anul de fabricație trebuie să fie un număr valid.")

        # Daca exista erori, redirectioneaza inapoi la pagina cu erorile incluse in URL
        if errors:
            return redirect(url_for('views.modificare_date_masini', errors="|".join(errors)))

        # Daca nu exista imagine incarcata, foloseste imaginea implicita
        imagine_url = DEFAULT_IMAGE_PATH
        if imagine and allowed_file(imagine.filename):
            # Salveaza imaginea incarcata in folderul de upload
            filename = secure_filename(imagine.filename)
            filepath = os.path.join("website/static/uploads", filename)
            imagine.save(filepath)
            # Converteste calea pentru utilizare in aplicatie
            imagine_url = filepath.replace("website/", "")

        # Interogare SQL pentru a adauga o masina in baza de date
        insert_query = """
        INSERT INTO Masina (ID_Model, ID_Locatie, Tarif, An_Fabricatie, Imagine_URL, IsActive)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        execute_query(insert_query, (id_model, id_locatie, tarif, an_fabricatie, imagine_url, True))

        # Preia datele despre marca si model pentru mesajul de succes
        marca = next(m for m in execute_query("SELECT * FROM Marca") if m[0] == int(id_marca))
        model = next(m for m in execute_query("SELECT * FROM Model") if m[0] == int(id_model))
        success_message = f"Mașina {marca[1]} {model[2]} {an_fabricatie} a fost adăugată cu succes!"

        # Redirectioneaza cu un mesaj de succes
        return redirect(url_for('views.modificare_date_masini', success_message=success_message))

    # Interogare SQL pentru a obtine lista masinilor existente
    masini_query = """
    SELECT 
        m.ID_Masina,
        ma.Denumire AS Marca,
        mo.Denumire AS Model,
        m.An_Fabricatie,
        l.Nume_Locatie,
        m.Tarif,
        m.Imagine_URL
    FROM 
        Masina m
    JOIN Model mo ON m.ID_Model = mo.ID_Model
    JOIN Marca ma ON mo.ID_Marca = ma.ID_Marca
    JOIN Locatie l ON m.ID_Locatie = l.ID_Locatie
    """
    masini = execute_query(masini_query)

    # Interogari pentru a obtine listele pentru dropdown-uri (marci, modele, locatii)
    marci_query = "SELECT * FROM Marca"
    marci = execute_query(marci_query)

    modele_query = "SELECT * FROM Model"
    modele = execute_query(modele_query)

    locatii_query = "SELECT * FROM Locatie"
    locatii = execute_query(locatii_query)

    # Returneaza template-ul pentru modificarea masinilor, cu toate datele necesare
    return render_template(
        "modificare_date_masini.html",
        user=current_user,
        masini=masini,
        marci=marci,
        modele=modele,
        locatii=locatii,
        selected_marca=id_marca if 'id_marca' in locals() else None,
        errors=errors,
        success_message=success_message,
    )

# Ruta pentru actualizarea informatiilor despre o masina, disponibila doar pentru utilizatorii logati
@views.route('/update-car', methods=['POST'])
@login_required
def update_car():
    # Verifica daca utilizatorul are rolul de 'angajat'; daca nu, il redirectioneaza la pagina principala
    if current_user.roles != 'angajat':
        return redirect(url_for('views.home'))

    # Preia datele transmise prin formular
    id_masina = request.form.get('id_masina')
    tarif = request.form.get('tarif')
    id_locatie = request.form.get('id_locatie')
    imagine = request.files.get('imagine')

    # Initializeaza o lista pentru erori
    errors = []

    # Verifica daca toate campurile obligatorii sunt completate
    if not id_masina or not tarif or not id_locatie:
        errors.append("Toate câmpurile marcate cu * trebuie completate.")
    else:
        try:
            # Verifica daca tariful este un numar valid si mai mare sau egal cu 20
            tarif = float(tarif)
            if tarif < 20:
                errors.append("Tariful trebuie să fie cel puțin 20 RON.")
        except ValueError:
            # Adauga o eroare daca tariful nu este un numar valid
            errors.append("Tariful trebuie să fie un număr valid.")

    # Daca exista erori, redirectioneaza inapoi la pagina de modificare cu erorile incluse in URL
    if errors:
        return redirect(url_for('views.modificare_date_masini', errors="|".join(errors)))

    # Preia URL-ul imaginii existente din baza de date pentru masina specificata
    masina = execute_query("SELECT Imagine_URL FROM Masina WHERE ID_Masina = ?", (id_masina,), fetchone=True)
    imagine_url = masina[0] if masina else DEFAULT_IMAGE_PATH  # Daca nu exista, se foloseste imaginea implicita

    # Daca exista o imagine noua incarcata, o salveaza in directorul de upload si actualizeaza URL-ul
    if imagine and allowed_file(imagine.filename):
        filename = secure_filename(imagine.filename)
        filepath = os.path.join("website/static/uploads", filename)
        imagine.save(filepath)
        imagine_url = filepath.replace("website/", "")  # Converteste calea pentru utilizare in aplicatie

    # Interogare SQL pentru actualizarea informatiilor despre masina
    update_query = """
        UPDATE Masina
        SET Tarif = ?, ID_Locatie = ?, Imagine_URL = ?
        WHERE ID_Masina = ?
    """
    execute_query(update_query, (tarif, id_locatie, imagine_url, id_masina))

    # Mesaj de succes pentru actualizarea datelor masinii
    success_message = "Datele mașinii au fost actualizate cu succes!"
    return redirect(url_for('views.modificare_date_masini', success_message=success_message))

# Ruta pentru obtinerea modelelor asociate unei marci specifice
@views.route('/get-models/<int:marca_id>', methods=['GET'])
def get_models(marca_id):
    # Interogare SQL pentru a obtine toate modelele asociate marcii primite ca parametru
    modele_query = "SELECT * FROM Model WHERE ID_Marca = ?"
    modele = execute_query(modele_query, (marca_id,))
    
    # Returneaza modelele sub forma de JSON, incluzand ID-ul si denumirea fiecarui model
    return {"modele": [{"id": m[0], "denumire": m[2]} for m in modele]}

# Ruta pentru rezervarea masinii
@views.route('/rezerva-masina', methods=['GET'])
def rezerva_masina():
    # Determina daca este activ modul de editare
    edit_mode = request.args.get('edit_mode', 'false') == 'true'

    # Preia starea de sortare (active/inactive/all)
    sort_status = request.args.get('sort_status', 'all')

    # Preia parametrii de filtrare trimisi prin URL
    oras = request.args.get('oras')
    marca_id = request.args.get('marca_id')
    model_id = request.args.get('model_id')
    an_fabricatie = request.args.get('an_fabricatie')
    tarif_maxim = request.args.get('tarif_maxim')
    data_inchiriere = request.args.get('data_inchiriere')
    data_returnare = request.args.get('data_returnare')

    # Construieste interogarea SQL de baza pentru selectarea masinilor
    query = """
    SELECT 
        m.ID_Masina,
        mo.Denumire AS Model,
        ma.Denumire AS Marca,
        m.An_Fabricatie,
        m.Tarif,
        l.Nume_Locatie,
        l.Adresa,
        m.Imagine_URL,
        m.IsActive
    FROM 
        Masina m
    JOIN 
        Model mo ON m.ID_Model = mo.ID_Model
    JOIN 
        Marca ma ON mo.ID_Marca = ma.ID_Marca
    JOIN 
        Locatie l ON m.ID_Locatie = l.ID_Locatie
    WHERE 1=1
    """
    # Lista de parametri pentru query-ul parametrizat
    params = []

    # Adauga conditii pentru filtrarea masinilor in functie de starea de activare
    if edit_mode:
        if sort_status == 'active':
            query += " AND m.IsActive = 1"
        elif sort_status == 'inactive':
            query += " AND m.IsActive = 0"
    else:
        query += " AND m.IsActive = 1"

    # Adauga conditii suplimentare de filtrare in functie de parametrii trimisi
    if oras:
        query += " AND l.Oras = ?"
        params.append(oras)
    if marca_id:
        query += " AND ma.ID_Marca = ?"
        params.append(marca_id)
    if model_id:
        query += " AND mo.ID_Model = ?"
        params.append(model_id)
    if an_fabricatie:
        query += " AND m.An_Fabricatie = ?"
        params.append(an_fabricatie)
    if tarif_maxim:
        query += " AND m.Tarif <= ?"
        params.append(float(tarif_maxim))

    # Verifica daca s-au specificat perioade de inchiriere si adauga filtrarea corespunzatoare
    if data_inchiriere and data_returnare:
        query += """
        AND NOT EXISTS (
            SELECT 1 
            FROM rezervari_masini rm
            WHERE rm.ID_Masina = m.ID_Masina 
              AND rm.ID_Rezervare IN (
                  SELECT r.ID_Rezervare
                  FROM rezervare r
                  WHERE NOT (r.Data_Returnare <= ? OR r.Data_Inchiriere >= ?)
              )
        )
        """
        params.append(data_inchiriere)
        params.append(data_returnare)

    # Executa query-ul pentru obtinerea masinilor filtrate
    masini = execute_query(query, params)

    # Transformarea rezultatelor in format JSON pentru a fi utilizate in frontend
    masini_data = [
        {
            "ID_Masina": m[0],
            "Model": m[1],
            "Marca": m[2],
            "An_Fabricatie": m[3],
            "Tarif": m[4],
            "Nume_Locatie": m[5],
            "Adresa": m[6],
            "Imagine_URL": get_image_url(m[7]),  # Converteste URL-ul imaginii pentru afisare
            "IsActive": "Da" if m[8] else "Nu"  # Marcheaza masinile active/inactive
        }
        for m in masini
    ]

    # Daca cererea solicita format JSON, returneaza rezultatele in acest format
    if request.headers.get('Accept') == 'application/json':
        return {"masini": masini_data}, 200

    # Interogare pentru obtinerea listelor de marci si orase pentru utilizarea in dropdown-uri
    marci_query = "SELECT * FROM Marca"
    marci = execute_query(marci_query)

    orase_query = "SELECT DISTINCT Oras FROM Locatie"
    orase = [row[0] for row in execute_query(orase_query)]

    # Returneaza pagina HTML pentru rezervare, populata cu datele filtrate si optiunile necesare
    return render_template(
        "rezerva_masina.html",
        masini=masini_data,  # Masinile obtinute dupa filtrare
        marci=marci,  # Lista de marci pentru dropdown
        orase=orase,  # Lista de orase pentru dropdown
        success_message=request.args.get('success_message', None),  # Mesaj de succes (daca exista)
        edit_mode=edit_mode,  # Indica daca este activ modul de editare
        sort_status=sort_status,  # Starea de sortare (active/inactive/all)
        user=current_user  # Informatiile despre utilizatorul curent
    )

@views.route('/rezervare', methods=['GET'])
def rezervare():
    # Verificam daca utilizatorul este autentificat
    if not current_user.is_authenticated:
        # Daca nu, il redirectionam catre pagina de login cu un mesaj de eroare
        return redirect(url_for('auth.login', errors='Trebuie să fii logat ca să faci o rezervare!'))

    # Preluam lista de ID-uri ale masinilor selectate din parametrii requestului
    masini_ids = request.args.getlist('masini_ids')
    if not masini_ids:
        # Daca nu exista masini selectate, afisam un mesaj de eroare si redirectionam utilizatorul
        flash("Nu ai selectat nicio mașină pentru rezervare.", category="error")
        return redirect(url_for('views.rezerva_masina'))
    
    # Construim query-ul pentru a selecta detaliile masinilor selectate
    query = """
    SELECT 
        m.ID_Masina, 
        mo.Denumire AS Model, 
        ma.Denumire AS Marca, 
        m.An_Fabricatie, 
        m.Tarif, 
        l.Nume_Locatie, 
        l.Adresa 
    FROM 
        Masina m
    JOIN 
        Model mo ON m.ID_Model = mo.ID_Model
    JOIN 
        Marca ma ON mo.ID_Marca = ma.ID_Marca
    JOIN 
        Locatie l ON m.ID_Locatie = l.ID_Locatie
    WHERE 
        m.ID_Masina IN ({}) AND m.IsActive = 1
    """.format(",".join("?" * len(masini_ids)))  # Cream un placeholder pentru fiecare ID

    # Executam query-ul folosind ID-urile masinilor
    masini = execute_query(query, tuple(masini_ids))
    # Transformam rezultatele intr-o structura de date pentru a fi folosite in template
    masini_data = [
        {
            "ID_Masina": m[0],  # ID-ul masinii
            "Model": m[1],      # Modelul masinii
            "Marca": m[2],      # Marca masinii
            "An_Fabricatie": m[3],  # Anul de fabricatie al masinii
            "Tarif": m[4],      # Tariful masinii
            "Nume_Locatie": m[5],   # Locatia masinii
            "Adresa": m[6]      # Adresa locatiei
        }
        for m in masini  # Iteram prin fiecare masina returnata de query
    ]

    # Preluam un mesaj de succes din parametrii requestului, daca exista
    success_message = request.args.get('success_message', None)

    # Randam template-ul rezervare.html, trimitand detaliile masinilor si alte date necesare
    return render_template("rezervare.html", masini=masini_data, datetime=datetime, success_message=success_message)

@views.route('/confirmare-rezervare', methods=['POST'])
def confirmare_rezervare():
    # Verificam daca utilizatorul este autentificat
    if not current_user.is_authenticated:
        # Daca nu este autentificat, redirectionam catre pagina de login cu un mesaj de eroare
        return redirect(url_for('auth.login', errors='Trebuie sa fii logat ca sa faci o rezervare!'))

    # Preluam datele din formular
    data_inchiriere = request.form.get('data_inchiriere')
    data_returnare = request.form.get('data_returnare')
    email = request.form.get('email')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    cnp = request.form.get('cnp')
    telefon = request.form.get('telefon')
    masini_ids = request.form.getlist('masini_ids')  # Lista ID-urilor masinilor selectate

    # Initializam o lista pentru erori
    errors = []

    # Validam completarea tuturor campurilor obligatorii
    if not data_inchiriere or not data_returnare or not email or not first_name or not last_name or not cnp or not telefon:
        errors.append("Toate câmpurile marcate cu * trebuie completate.")

    # Validam CNP-ul
    if len(cnp) != 13 or not cnp.isdigit():
        errors.append("CNP-ul trebuie să conțină 13 caractere numerice.")

    # Validam numarul de telefon
    if not is_valid_phone(telefon):
        errors.append("Telefonul trebuie să conțină doar cifre.")

    # Validam adresa de email
    if not is_valid_email(email):
        errors.append("Adresa de email nu este validă.")

    # Validam datele de inchiriere si returnare
    if data_inchiriere and data_returnare:
        try:
            inchiriere_date = datetime.strptime(data_inchiriere, "%Y-%m-%d").date()
            returnare_date = datetime.strptime(data_returnare, "%Y-%m-%d").date()
            today = datetime.now().date()

            # Verificam daca data de inchiriere este in trecut
            if inchiriere_date < today:
                errors.append("Data de închiriere nu poate fi mai veche decât ziua curentă.")

            # Verificam daca data de returnare este corecta
            if returnare_date <= inchiriere_date:
                errors.append("Data de returnare trebuie să fie cel puțin o zi după data de închiriere.")
        except ValueError:
            errors.append("Datele selectate nu sunt valide.")

    # Verificam disponibilitatea fiecarei masini selectate
    for masina_id in masini_ids:
        disponibilitate_query = """
        SELECT COUNT(*) 
        FROM rezervari_masini 
        WHERE ID_Masina = ? 
        AND ID_Rezervare IN (
            SELECT ID_Rezervare 
            FROM rezervare 
            WHERE NOT (
                Data_Returnare <= ? OR Data_Inchiriere >= ?
            )
        ) 
        AND ID_Masina IN (
            SELECT ID_Masina 
            FROM masina 
            WHERE IsActive = 1
        );
        """
        masina_ocupata = execute_query(disponibilitate_query, (masina_id, data_inchiriere, data_returnare), fetchone=True)[0]
        if masina_ocupata > 0:
            # Adaugam eroare daca masina nu este disponibila
            errors.append(f"Mașina {masina_id} nu este disponibilă în perioada selectată.")

    # Daca exista erori, randam din nou pagina de rezervare cu mesajele de eroare
    if errors:
        masini = [
            execute_query("""
                SELECT m.ID_Masina, mo.Denumire AS Model, ma.Denumire AS Marca, m.An_Fabricatie,
                    m.Tarif, l.Nume_Locatie, l.Adresa
                FROM Masina m
                JOIN Model mo ON m.ID_Model = mo.ID_Model
                JOIN Marca ma ON mo.ID_Marca = ma.ID_Marca
                JOIN Locatie l ON m.ID_Locatie = l.ID_Locatie
                WHERE m.ID_Masina = ?
            """, (masina_id,), fetchone=True)
            for masina_id in masini_ids
        ]
        masini_data = [
            {
                "ID_Masina": masina[0],
                "Model": masina[1],
                "Marca": masina[2],
                "An_Fabricatie": masina[3],
                "Tarif": masina[4],
                "Nume_Locatie": masina[5],
                "Adresa": masina[6]
            }
            for masina in masini
        ]
        return render_template(
            "rezervare.html",
            masini=masini_data,
            errors=errors,
            user=current_user,
            data_inchiriere=data_inchiriere,
            data_returnare=data_returnare,
            email=email,
            first_name=first_name,
            last_name=last_name,
            cnp=cnp,
            telefon=telefon
        )

    # Calculam numarul de zile de inchiriere
    days = (returnare_date - inchiriere_date).days

    # Calculam costul total al rezervarii
    total_plata = sum([
        execute_query("SELECT Tarif FROM Masina WHERE ID_Masina = ?", (masina_id,), fetchone=True)[0] * days
        for masina_id in masini_ids
    ])

    # Verificam daca clientul exista deja in baza de date
    client_query = execute_query("SELECT ID_Client FROM Client WHERE Email = ?", (email,), fetchone=True)
    if client_query:
        # Daca exista, actualizam datele clientului
        client_id = client_query[0]
        execute_query("""
            UPDATE Client SET First_Name = ?, Last_Name = ?, CNP = ?, Telefon = ? WHERE Email = ?
        """, (first_name, last_name, cnp, telefon, email))
    else:
        # Daca nu exista, il adaugam in baza de date
        execute_query("""
            INSERT INTO Client (Email, First_Name, Last_Name, CNP, Telefon)
            VALUES (?, ?, ?, ?, ?)
        """, (email, first_name, last_name, cnp, telefon))
        client_id = execute_query("SELECT ID_Client FROM Client WHERE Email = ?", (email,), fetchone=True)[0]

    # Adaugam rezervarea in baza de date
    execute_query("""
        INSERT INTO Rezervare (ID_Client, Data_Inchiriere, Data_Returnare)
        VALUES (?, ?, ?)
    """, (client_id, data_inchiriere, data_returnare))
    rezervare_id = execute_query("""
        SELECT ID_Rezervare FROM Rezervare WHERE ID_Client = ? AND Data_Inchiriere = ? AND Data_Returnare = ?
    """, (client_id, data_inchiriere, data_returnare), fetchone=True)[0]

    # Asociem masinile selectate cu rezervarea creata
    for masina_id in masini_ids:
        execute_query("""
            INSERT INTO rezervari_masini (ID_Rezervare, ID_Masina)
            VALUES (?, ?)
        """, (rezervare_id, masina_id))

    # Determinam numarul de factura al clientului
    numar_facturi_client = execute_query("""
        SELECT COUNT(*)
        FROM Factura 
        WHERE ID_Rezervare IN (
            SELECT ID_Rezervare 
            FROM Rezervare 
            WHERE ID_Client = ?
        );
    """, (client_id,), fetchone=True)[0]

    # Incrementam numarul facturii pentru client
    numar_factura = numar_facturi_client + 1

    # Adaugam factura in baza de date
    execute_query("""
        INSERT INTO Factura (ID_Rezervare, Numar_Factura, Data_Plata, Data_Emitere, Suma_Totala)
        VALUES (?, ?, ?, ?, ?)
    """, (rezervare_id, numar_factura, datetime.now(), datetime.now(), total_plata))

    # Redirectionam utilizatorul cu un mesaj de succes
    success_message = "Rezervarea și factura au fost realizate cu succes!"
    return redirect(url_for('views.rezerva_masina', success_message=success_message))

@views.route('/toggle-edit-mode', methods=['POST'])
@login_required
def toggle_edit_mode():
    # Verificam daca utilizatorul curent are rolul de "angajat"
    if current_user.roles != 'angajat':
        # Daca nu, afisam un mesaj de eroare si redirectionam utilizatorul
        flash("Nu ai permisiunea să editezi.", category="error")
        return redirect(url_for('views.rezerva_masina'))

    # Preluam starea curenta a modului de editare din formular
    edit_mode = request.form.get('edit_mode') == 'true'

    # Returnam starea opusa a modului de editare pentru a comuta intre moduri
    return {"edit_mode": not edit_mode}

@views.route('/delete-masina/<int:masina_id>', methods=['POST'])
@login_required
def delete_masina(masina_id):
    # Verificam daca utilizatorul curent are rolul de "angajat"
    if current_user.roles != 'angajat':
        # Daca nu, returnam un mesaj de eroare cu codul 403 (acces interzis)
        return {"error": "Permisiune refuzată"}, 403

    try:
        # Actualizam statusul masinii in baza de date, marcand-o ca inactiva
        execute_query("UPDATE Masina SET IsActive = 0 WHERE ID_Masina = ?", (masina_id,))
        # Returnam un mesaj de succes daca operatiunea a fost realizata cu succes
        return {"message": "Mașina a fost dezactivată cu succes!"}, 200
    except Exception as e:
        # In caz de eroare, returnam mesajul erorii
        return {"error": str(e)}, 500

@views.route('/activate-masina/<int:masina_id>', methods=['POST'])
@login_required
def activate_masina(masina_id):
    # Verificam daca utilizatorul curent are rolul de "angajat"
    if current_user.roles != 'angajat':
        # Daca nu, returnam un mesaj de eroare cu codul 403 (acces interzis)
        return {"error": "Permisiune refuzată"}, 403

    try:
        # Actualizam statusul masinii in baza de date, marcand-o ca activa
        execute_query("UPDATE Masina SET IsActive = 1 WHERE ID_Masina = ?", (masina_id,))
        # Returnam un mesaj de succes daca operatiunea a fost realizata cu succes
        return {"message": "Mașina a fost reactivată cu succes!"}, 200
    except Exception as e:
        # In caz de eroare, returnam mesajul erorii
        return {"error": str(e)}, 500

@views.route('/realdelete-masina', methods=['POST'])
@login_required
def delete_car():
    # Verifica daca utilizatorul curent are rolul de "angajat"
    if current_user.roles != 'angajat':
        # Returneaza un mesaj de eroare daca utilizatorul nu are permisiunea
        return {"error": "Nu ai permisiunea să ștergi mașini!"}, 403

    # Preia datele din request-ul JSON
    data = request.get_json()
    id_masina = data.get('id_masina')

    # Verifica daca ID-ul masinii a fost specificat
    if not id_masina:
        return {"error": "ID-ul mașinii nu este specificat!"}, 400

    # Verifica daca masina exista in baza de date
    masina = execute_query("SELECT IsActive FROM Masina WHERE ID_Masina = ?", (id_masina,), fetchone=True)
    if not masina:
        return {"error": "Mașina nu există!"}, 404

    try:
        # Sterge toate inregistrarile din tabelul rezervari_masini pentru aceasta masina
        execute_query("DELETE FROM rezervari_masini WHERE ID_Masina = ?", (id_masina,))

        # Sterge toate facturile asociate rezervarilor acestei masini
        execute_query("""
            DELETE FROM Factura 
            WHERE ID_Rezervare IN (
                SELECT ID_Rezervare FROM Rezervare WHERE ID_Rezervare IN (
                    SELECT ID_Rezervare FROM rezervari_masini WHERE ID_Masina = ?
                )
            )
        """, (id_masina,))

        # Sterge rezervarile care nu mai au masini asociate
        execute_query("""
            DELETE FROM Rezervare 
            WHERE ID_Rezervare NOT IN (SELECT DISTINCT ID_Rezervare FROM rezervari_masini)
        """)

        # Sterge masina din tabelul Masina
        execute_query("DELETE FROM Masina WHERE ID_Masina = ?", (id_masina,))

        # Returneaza un mesaj de succes
        return {"message": "Mașina a fost ștearsă cu succes!"}, 200
    except Exception as e:
        # In caz de eroare, returneaza mesajul erorii
        return {"error": f"Eroare la ștergerea mașinii: {str(e)}"}, 500

@views.route('/', methods=['GET'])
def home():
    # Creeaza un query pentru a prelua cele mai populare masini (top 5 dupa numarul de rezervari)
    query_vandute = """
    SELECT 
        m.ID_Masina,
        mo.Denumire AS Model,
        ma.Denumire AS Marca,
        m.An_Fabricatie,
        m.Tarif,
        l.Nume_Locatie,
        m.Imagine_URL,
        COUNT(rm.ID_Masina) AS RezervariTotale
    FROM Masina m
    JOIN Model mo ON m.ID_Model = mo.ID_Model
    JOIN Marca ma ON mo.ID_Marca = ma.ID_Marca
    JOIN Locatie l ON m.ID_Locatie = l.ID_Locatie
    LEFT JOIN rezervari_masini rm ON m.ID_Masina = rm.ID_Masina
    WHERE m.IsActive = 1
    GROUP BY 
        m.ID_Masina, mo.Denumire, ma.Denumire, m.An_Fabricatie, m.Tarif, l.Nume_Locatie, m.Imagine_URL
    ORDER BY RezervariTotale DESC
    LIMIT 5;
    """
    # Executa query-ul pentru cele mai populare masini
    masini_populare = execute_query(query_vandute)

    # Creeaza un query pentru a prelua cele mai ieftine masini (top 5 dupa tarif)
    query_ieftine = """
    SELECT 
        m.ID_Masina,
        mo.Denumire AS Model,
        ma.Denumire AS Marca,
        m.An_Fabricatie,
        m.Tarif,
        l.Nume_Locatie,
        m.Imagine_URL
    FROM Masina m
    JOIN Model mo ON m.ID_Model = mo.ID_Model
    JOIN Marca ma ON mo.ID_Marca = ma.ID_Marca
    JOIN Locatie l ON m.ID_Locatie = l.ID_Locatie
    WHERE m.IsActive = 1
    ORDER BY m.Tarif ASC
    LIMIT 5;
    """
    # Executa query-ul pentru cele mai ieftine masini
    masini_ieftine = execute_query(query_ieftine)

    # Formateaza datele masinilor populare pentru a fi trimise catre template
    masini_populare_data = [
        {
            "ID_Masina": m[0],
            "Model": m[1],
            "Marca": m[2],
            "An_Fabricatie": m[3],
            "Tarif": m[4],
            "Nume_Locatie": m[5],
            "Imagine_URL": get_image_url(m[6]),
            "RezervariTotale": m[7],
        }
        for m in masini_populare
    ]

    # Formateaza datele masinilor ieftine pentru a fi trimise catre template
    masini_ieftine_data = [
        {
            "ID_Masina": m[0],
            "Model": m[1],
            "Marca": m[2],
            "An_Fabricatie": m[3],
            "Tarif": m[4],
            "Nume_Locatie": m[5],
            "Imagine_URL": get_image_url(m[6]),
        }
        for m in masini_ieftine
    ]

    # Returneaza pagina principala cu datele masinilor populare si ieftine
    return render_template(
        "home.html",
        user=current_user,
        masini_populare=masini_populare_data,
        masini_ieftine=masini_ieftine_data,
    )


@views.route('/rezervarile-mele', methods=['GET'])
@login_required  # Asigura ca doar utilizatorii autentificati pot accesa aceasta ruta
def rezervarile_mele():
    # Interogare pentru a obtine ID-ul clientului pe baza adresei de email a utilizatorului curent
    client_query = "SELECT ID_Client FROM Client WHERE Email = ?"
    client = execute_query(client_query, (current_user.email,), fetchone=True)

    # Daca clientul nu exista in baza de date, se returneaza o pagina fara rezervari
    if not client:
        return render_template("rezervarile_mele.html", rezervari={}, user=current_user)

    # Extrage ID-ul clientului din rezultatul interogarii
    id_client = client[0]

    # Interogare pentru a obtine toate rezervarile clientului impreuna cu detalii despre facturi si masini
    rezervari_query = """
    SELECT 
        r.ID_Rezervare,
        r.Data_Inchiriere, 
        r.Data_Returnare,
        f.Numar_Factura,
        f.Data_Plata,
        f.Data_Emitere,
        f.Suma_Totala,
        mo.Denumire AS Model,
        ma.Denumire AS Marca,
        m.An_Fabricatie,
        m.Tarif,
        l.Nume_Locatie,
        l.Adresa
    FROM 
        Rezervare r
    JOIN 
        Factura f ON r.ID_Rezervare = f.ID_Rezervare
    JOIN 
        rezervari_masini rm ON r.ID_Rezervare = rm.ID_Rezervare
    JOIN 
        Masina m ON rm.ID_Masina = m.ID_Masina
    JOIN 
        Model mo ON m.ID_Model = mo.ID_Model
    JOIN 
        Marca ma ON mo.ID_Marca = ma.ID_Marca
    JOIN 
        Locatie l ON m.ID_Locatie = l.ID_Locatie
    WHERE 
        r.ID_Client = ?
    ORDER BY 
        r.Data_Inchiriere DESC
    """
    rezervari_raw = execute_query(rezervari_query, (id_client,))

    today = datetime.now().date()  # Obtine data curenta
    rezervari = {}  # Dicționar pentru organizarea datelor rezervarilor
    for row in rezervari_raw:
        rezervare_id = row[0]  # ID-ul rezervarii curente
        data_inchiriere = datetime.strptime(row[1], "%Y-%m-%d").date()  # Converteste data din string in obiect de tip data
        # Daca rezervarea curenta nu este in dicționar, adauga detaliile principale
        if rezervare_id not in rezervari:
            rezervari[rezervare_id] = {
                "Data_Inchiriere": row[1],
                "Data_Returnare": row[2],
                "Factura": {
                    "Numar_Factura": row[3],
                    "Data_Plata": row[4],
                    "Data_Emitere": row[5],
                    "Suma_Totala": row[6],
                },
                "Masini": [],  # Lista goala pentru masinile asociate acestei rezervari
                "Can_Cancel": data_inchiriere > today,  # Determina daca rezervarea poate fi anulata (inca nu a inceput)
            }
        # Adauga detalii despre masina la lista de masini asociate rezervarii
        rezervari[rezervare_id]["Masini"].append({
            "Model": row[7],
            "Marca": row[8],
            "An_Fabricatie": row[9],
            "Tarif": row[10],
            "Nume_Locatie": row[11],
            "Adresa": row[12]
        })

    # Returneaza pagina cu rezervarile clientului, incluzand datele prelucrate
    return render_template("rezervarile_mele.html", rezervari=rezervari, user=current_user)

@views.route('/total-rezervari', methods=['GET'])
@login_required  # Asigura ca doar utilizatorii autentificati pot accesa aceasta ruta
def total_rezervari():
    if current_user.roles != 'angajat':  # Verifica daca utilizatorul are rolul de "angajat"
        return redirect(url_for('views.home'))  # Redirectioneaza utilizatorii fara permisiuni catre pagina principala

    # Preia filtrele de cautare din request
    email = request.args.get('email', '').strip()
    data_inchiriere = request.args.get('data_inchiriere', '')
    data_returnare = request.args.get('data_returnare', '')
    masina_id = request.args.get('masina', '')

    # Construim query-ul pentru a extrage rezervarile cu detalii suplimentare despre clienti, masini si facturi
    query = """
    SELECT 
        r.ID_Rezervare, r.Data_Inchiriere, r.Data_Returnare,
        c.First_Name AS Nume_Client, c.Last_Name AS Prenume_Client, c.CNP AS CNP_Client, c.Email AS Email_Client, c.Telefon AS Telefon_Client,
        m.ID_Masina, mo.Denumire AS Model, ma.Denumire AS Marca, m.An_Fabricatie, m.Tarif,
        l.Nume_Locatie, l.Adresa AS Adresa_Locatie,
        f.Numar_Factura, f.Data_Plata, f.Data_Emitere, f.Suma_Totala
    FROM 
        Rezervare r
    JOIN 
        Client c ON r.ID_Client = c.ID_Client
    JOIN 
        rezervari_masini rm ON r.ID_Rezervare = rm.ID_Rezervare
    JOIN 
        Masina m ON rm.ID_Masina = m.ID_Masina
    JOIN 
        Model mo ON m.ID_Model = mo.ID_Model
    JOIN 
        Marca ma ON mo.ID_Marca = ma.ID_Marca
    JOIN 
        Locatie l ON m.ID_Locatie = l.ID_Locatie
    JOIN 
        Factura f ON r.ID_Rezervare = f.ID_Rezervare
    WHERE 1=1
    """
    params = []  # Lista pentru parametrii query-ului

    # Adaugam filtrele de cautare daca sunt specificate
    if email:
        query += " AND c.Email LIKE ?"
        params.append(f"%{email}%")
    if data_inchiriere:
        query += " AND r.Data_Inchiriere >= ?"
        params.append(data_inchiriere)
    if data_returnare:
        query += " AND r.Data_Returnare <= ?"
        params.append(data_returnare)
    if masina_id:
        query += """
        AND r.ID_Rezervare IN (
            SELECT DISTINCT rm.ID_Rezervare
            FROM rezervari_masini rm
            WHERE rm.ID_Masina = ?
        )
        """
        params.append(masina_id)

    # Adaugam sortare dupa data inchirierii in ordine descrescatoare
    query += " ORDER BY r.Data_Inchiriere DESC"
    rezervari = execute_query(query, params)  # Executam query-ul cu parametrii specificati

    # Interogare pentru a prelua toate masinile disponibile
    masini_query = """
    SELECT 
        m.ID_Masina, ma.Denumire AS Marca, mo.Denumire AS Model, m.An_Fabricatie
    FROM 
        Masina m
    JOIN 
        Model mo ON m.ID_Model = mo.ID_Model
    JOIN 
        Marca ma ON mo.ID_Marca = ma.ID_Marca
    """
    masini = execute_query(masini_query)

    # Organizarea datelor despre rezervari intr-un format structurat
    rezervari_data = {}
    for row in rezervari:
        rezervare_id = row[0]
        if rezervare_id not in rezervari_data:
            rezervari_data[rezervare_id] = {
                "Data_Inchiriere": row[1],
                "Data_Returnare": row[2],
                "Client": {
                    "Nume": row[3],
                    "Prenume": row[4],
                    "CNP": row[5],
                    "Email": row[6],
                    "Telefon": row[7],
                },
                "Masini": [],  # Lista de masini asociate rezervarii
                "Factura": {
                    "Numar_Factura": row[15],
                    "Data_Plata": row[16],
                    "Data_Emitere": row[17],
                    "Suma_Totala": row[18],
                }
            }
        # Adaugam detalii despre masina in lista de masini asociate rezervarii
        rezervari_data[rezervare_id]["Masini"].append({
            "ID_Masina": row[8],
            "Model": row[9],
            "Marca": row[10],
            "An_Fabricatie": row[11],
            "Tarif": row[12],
            "Nume_Locatie": row[13],
            "Adresa": row[14],
        })

    # Returnam pagina cu toate rezervarile si detalii despre masini
    return render_template(
        "total_rezervari.html",
        rezervari=rezervari_data,
        masini=masini,
        user=current_user,
        str=str
    )

@views.route('/delete-rezervare/<int:rezervare_id>', methods=['POST'])
@login_required  # Asigura ca doar utilizatorii autentificati pot accesa aceasta ruta
def delete_rezervare(rezervare_id):
    if current_user.roles != 'angajat':  # Verifica daca utilizatorul are permisiuni de "angajat"
        return {"error": "Nu ai permisiunea să ștergi rezervări!"}, 403

    try:
        # Sterge factura asociata rezervarii
        execute_query("DELETE FROM Factura WHERE ID_Rezervare = ?", (rezervare_id,))

        # Obtinem ID-ul clientului asociat rezervarii pentru verificari ulterioare
        client_id = execute_query(
            "SELECT ID_Client FROM Rezervare WHERE ID_Rezervare = ?", (rezervare_id,), fetchone=True
        )[0]

        # Stergem legaturile rezervarii cu masinile si rezervarea in sine
        execute_query("DELETE FROM rezervari_masini WHERE ID_Rezervare = ?", (rezervare_id,))
        execute_query("DELETE FROM Rezervare WHERE ID_Rezervare = ?", (rezervare_id,))

        # Verificam daca clientul mai are alte rezervari
        rezervari_client = execute_query(
            "SELECT COUNT(*) FROM Rezervare WHERE ID_Client = ?", (client_id,), fetchone=True
        )[0]

        # Daca clientul nu mai are alte rezervari, il stergem din baza de date
        if rezervari_client == 0:
            execute_query("DELETE FROM Client WHERE ID_Client = ?", (client_id,))

        return {"message": "Rezervarea a fost ștearsă cu succes!"}, 200  # Mesaj de succes

    except Exception as e:  # Tratam orice eroare care apare
        return {"error": f"Eroare la ștergerea rezervării: {str(e)}"}, 500