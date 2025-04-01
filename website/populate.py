import sqlite3
from os import path

# Setam calea catre baza de date
DB_PATH = path.join('instance', 'database.db')

# Functie generica pentru executarea interogarilor SQL
def execute_query(query, params=()):
    try:
        # Se deschide conexiunea cu baza de date
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        # Executam interogarea SQL cu parametri optionali
        cursor.execute(query, params)
        # Commit pentru a salva modificarile
        connection.commit()
    except sqlite3.Error as e:
        # Prindem erorile si le afisam
        print(f"Error: {e}")
    finally:
        # Inchidem conexiunea indiferent de rezultat
        connection.close()

# Functie pentru popularea tabelelor Marca si Model in baza de date
def populate_marca_and_model():
    # Lista cu date pentru tabela Marca
    marcas = [
        ('Audi', 'High-quality German automotive manufacturer.'),
        ('BMW', 'Bayerische Motoren Werke AG, known for luxury vehicles.'),
        ('Dacia', 'Romanian car manufacturer known for affordability.'),
        ('Ford', 'Global automotive company based in the USA.'),
        ('Toyota', 'Japanese manufacturer known for reliability.'),
        ('Mercedes-Benz', 'Luxury German automaker.'),
        ('Volkswagen', 'German automotive giant known for versatility.'),
        ('Hyundai', 'South Korean car manufacturer.'),
        ('Tesla', 'Electric vehicle manufacturer from the USA.'),
        ('Honda', 'Japanese automaker known for innovation.')
    ]

    # Interogare SQL pentru inserarea datelor in tabela Marca
    insert_marca_query = "INSERT INTO Marca (Denumire, Descriere) VALUES (?, ?)"
    for marca in marcas:
        execute_query(insert_marca_query, marca)

    # Extragem datele din tabela Marca pentru a obtine ID-urile
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("SELECT ID_Marca, Denumire FROM Marca")
    marca_data = cursor.fetchall()
    connection.close()

    # Dictionar cu datele despre modele pentru fiecare marca
    models = {
        'Audi': [
            ('A3', 'Compact executive car.'),
            ('A4', 'Luxury sedan.'),
            ('Q5', 'Luxury compact SUV.'),
            ('Q7', 'Mid-size luxury SUV.'),
            ('R8', 'Sports car.'),
            ('A6', 'Executive sedan.'),
            ('TT', 'Compact sports car.'),
            ('Q3', 'Compact luxury SUV.'),
            ('e-tron', 'Electric SUV.'),
            ('A8', 'Flagship luxury sedan.')
        ],
        'BMW': [
            ('3 Series', 'Compact executive car.'),
            ('5 Series', 'Mid-size executive car.'),
            ('X1', 'Compact SUV.'),
            ('X5', 'Luxury mid-size SUV.'),
            ('i8', 'Plug-in hybrid sports car.'),
            ('7 Series', 'Luxury sedan.'),
            ('X3', 'Compact luxury SUV.'),
            ('Z4', 'Convertible sports car.'),
            ('i3', 'Electric compact car.'),
            ('X7', 'Full-size luxury SUV.')
        ],
        'Dacia': [
            ('Duster', 'Compact SUV.'),
            ('Logan', 'Affordable sedan.'),
            ('Sandero', 'Affordable hatchback.'),
            ('Spring', 'Electric city car.'),
            ('Dokker', 'Compact MPV.'),
            ('Lodgy', 'Affordable family car.'),
            ('Pick-Up', 'Utility vehicle.'),
            ('1310', 'Classic sedan.'),
            ('1300', 'Vintage sedan.'),
            ('Nova', 'First modern Dacia car.')
        ],
        'Ford': [
            ('Focus', 'Compact car.'),
            ('Fiesta', 'Small hatchback.'),
            ('Mustang', 'Sports car.'),
            ('Explorer', 'Mid-size SUV.'),
            ('Escape', 'Compact SUV.'),
            ('Edge', 'Mid-size crossover.'),
            ('Ranger', 'Pickup truck.'),
            ('Transit', 'Commercial van.'),
            ('Fusion', 'Mid-size sedan.'),
            ('Bronco', 'Off-road SUV.')
        ],
        'Toyota': [
            ('Corolla', 'Compact sedan.'),
            ('Camry', 'Mid-size sedan.'),
            ('RAV4', 'Compact SUV.'),
            ('Highlander', 'Mid-size SUV.'),
            ('Prius', 'Hybrid electric car.'),
            ('Tacoma', 'Mid-size pickup truck.'),
            ('Tundra', 'Full-size pickup truck.'),
            ('C-HR', 'Subcompact SUV.'),
            ('Supra', 'Sports car.'),
            ('Yaris', 'Subcompact car.')
        ],
        'Mercedes-Benz': [
            ('A-Class', 'Compact luxury car.'),
            ('C-Class', 'Luxury sedan.'),
            ('E-Class', 'Executive car.'),
            ('S-Class', 'Flagship luxury sedan.'),
            ('GLA', 'Compact luxury SUV.'),
            ('GLC', 'Mid-size luxury SUV.'),
            ('GLE', 'Luxury SUV.'),
            ('GLS', 'Full-size luxury SUV.'),
            ('AMG GT', 'High-performance sports car.'),
            ('V-Class', 'Luxury van.')
        ],
        'Volkswagen': [
            ('Golf', 'Compact car.'),
            ('Passat', 'Mid-size sedan.'),
            ('Tiguan', 'Compact SUV.'),
            ('Atlas', 'Mid-size SUV.'),
            ('ID.4', 'Electric SUV.'),
            ('Jetta', 'Compact sedan.'),
            ('Polo', 'Subcompact car.'),
            ('Beetle', 'Iconic compact car.'),
            ('Arteon', 'Luxury fastback.'),
            ('Touareg', 'Luxury SUV.')
        ],
        'Hyundai': [
            ('Elantra', 'Compact sedan.'),
            ('Sonata', 'Mid-size sedan.'),
            ('Tucson', 'Compact SUV.'),
            ('Santa Fe', 'Mid-size SUV.'),
            ('Palisade', 'Full-size SUV.'),
            ('Kona', 'Subcompact SUV.'),
            ('Ioniq', 'Hybrid/electric car.'),
            ('Venue', 'Subcompact SUV.'),
            ('Accent', 'Affordable sedan.'),
            ('Nexo', 'Hydrogen-powered SUV.')
        ],
        'Tesla': [
            ('Model S', 'Luxury electric sedan.'),
            ('Model 3', 'Affordable electric sedan.'),
            ('Model X', 'Electric SUV.'),
            ('Model Y', 'Compact electric SUV.'),
            ('Cybertruck', 'Electric pickup truck.'),
            ('Roadster', 'High-performance electric sports car.'),
            ('Semi', 'Electric truck.'),
            ('Model 2', 'Compact electric car (concept).'),
            ('Model P', 'Electric performance car (concept).'),
            ('PowerTruck', 'Heavy-duty electric truck.')
        ],
        'Honda': [
            ('Civic', 'Compact sedan.'),
            ('Accord', 'Mid-size sedan.'),
            ('CR-V', 'Compact SUV.'),
            ('Pilot', 'Mid-size SUV.'),
            ('Fit', 'Subcompact car.'),
            ('Odyssey', 'Minivan.'),
            ('Ridgeline', 'Pickup truck.'),
            ('Insight', 'Hybrid sedan.'),
            ('HR-V', 'Subcompact SUV.'),
            ('NSX', 'Sports car.')
        ]
    }

    # Interogare SQL pentru inserarea datelor in tabela Model
    insert_model_query = "INSERT INTO Model (ID_Marca, Denumire, Descriere) VALUES (?, ?, ?)"
    for marca_id, marca_name in marca_data:
        for model in models.get(marca_name, []):
            execute_query(insert_model_query, (marca_id, *model))

# Functie pentru popularea tabelei Locatie in baza de date
def populate_locatii():
    # Lista cu locatii pentru a fi adaugate in tabela Locatie
    locatii = [
        ('CarGET Sector 1', 'Bucuresti Sector 1', 'Str. Ion Mihalache 15, Bucuresti Sector 1'),
        ('CarGET Sector 2', 'Bucuresti Sector 2', 'Calea Floreasca 72, Bucuresti Sector 2'),
        # Alte locatii...
    ]

    # Interogare SQL pentru inserarea locatiilor
    insert_locatii_query = "INSERT INTO Locatie (Nume_Locatie, Oras, Adresa) VALUES (?, ?, ?)"
    for locatie in locatii:
        execute_query(insert_locatii_query, locatie)

# Executam functiile pentru popularea tabelelor daca scriptul este rulat direct
if __name__ == "__main__":
    populate_marca_and_model()
    print("Populated Marca and Model tables successfully.")

    populate_locatii()
    print("Populated Locatii table successfully.")