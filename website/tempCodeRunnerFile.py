import sqlite3
from os import path

# Database connection
DB_PATH = path.join('instance', 'database.db')

def execute_query(query, params=()):
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute(query, params)
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        connection.close()

def populate_marca_and_model():
    # Marca data
    marcas = [
        ('Audi', 'High-quality German automotive manufacturer.'),
        ('BMW', 'Bayerische Motoren Werke AG, known for luxury vehicles.'),
        ('Dacia', 'Romanian car manufacturer known for affordability.')
    ]

    # Insert Marca data
    insert_marca_query = "INSERT INTO Marca (Denumire, Descriere) VALUES (?, ?)"
    for marca in marcas:
        execute_query(insert_marca_query, marca)

    # Fetch Marca IDs
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("SELECT ID_Marca, Denumire FROM Marca")
    marca_data = cursor.fetchall()
    connection.close()

    # Model data
    models = {
        'Audi': [
            ('A3', 'Compact executive car.'),
            ('A4', 'Luxury sedan.'),
            ('Q5', 'Luxury compact SUV.'),
            ('Q7', 'Mid-size luxury SUV.'),
            ('R8', 'Sports car.')
        ],
        'BMW': [
            ('3 Series', 'Compact executive car.'),
            ('5 Series', 'Mid-size executive car.'),
            ('X1', 'Compact SUV.'),
            ('X5', 'Luxury mid-size SUV.'),
            ('i8', 'Plug-in hybrid sports car.')
        ],
        'Dacia': [
            ('Duster', 'Compact SUV.'),
            ('Logan', 'Affordable sedan.'),
            ('Sandero', 'Affordable hatchback.'),
            ('Spring', 'Electric city car.'),
            ('Dokker', 'Compact MPV.')
        ]
    }

    # Insert Model data
    insert_model_query = "INSERT INTO Model (ID_Marca, Denumire, Descriere) VALUES (?, ?, ?)"
    for marca_id, marca_name in marca_data:
        for model in models.get(marca_name, []):
            execute_query(insert_model_query, (marca_id, *model))

def populate_locatii():
    # Locatie data
    locatii = [
        ('CarGET Sector 1', 'Bucuresti Sector 1', 'Str. Ion Mihalache 15, Bucuresti Sector 1'),
        ('CarGET Sector 2', 'Bucuresti Sector 2', 'Calea Floreasca 72, Bucuresti Sector 2'),
        ('CarGET Sector 3', 'Bucuresti Sector 3', 'Bd. Nicolae Grigorescu 12, Bucuresti Sector 3'),
        ('CarGET Timișoara', 'Timișoara', 'Str. Alba Iulia 18, Timișoara'),
        ('CarGET Constanța', 'Constanța', 'Bd. Tomis 25, Constanța')
    ]

    # Insert Locatii data
    insert_locatii_query = "INSERT INTO Locatie (Nume_Locatie, Oras, Adresa) VALUES (?, ?, ?)"
    for locatie in locatii:
        execute_query(insert_locatii_query, locatie)

# Run the function
if __name__ == "__main__":
    populate_marca_and_model()
    print("Populated Marca and Model tables successfully.")

    populate_locatii()
    print("Populated Locatii table successfully.")
