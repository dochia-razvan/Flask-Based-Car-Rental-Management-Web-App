# Importam functia create_app din pachetul website
from website import create_app

# Cream o instanta a aplicatiei Flask folosind functia create_app
app = create_app()

# Punctul de intrare principal al aplicatiei
if __name__ == '__main__':
    # Pornim serverul Flask in modul debug
    # Modul debug permite identificarea si remedierea erorilor in timpul dezvoltarii
    app.run(debug=True)
