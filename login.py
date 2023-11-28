from flask import Blueprint, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
from hashlib import sha256
from dashboard import dashboard  # Importiere das Dashboard-Blueprint
import toml

login = Blueprint('login', __name__)

#lade die Konfigurationsdatei
config = toml.load('conf.toml')

# Verbindungsdaten zur MySQL-Datenbank (Du kannst diese Informationen auch aus main.py importieren)
DB_HOST = config['mysql']['host']
DB_USER = config['mysql']['user']
DB_PASSWORD = config['mysql']['password']
DB_NAME =  config['mysql']['db']

# Funktion zur Verbindungsherstellung mit der Datenbank
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        print("Verbindung zur MySQL-Datenbank hergestellt")
    except Error as e:
        print(f"Fehler bei der Verbindung zur MySQL-Datenbank: {e}")

    return connection

@login.route('/login', methods=['GET', 'POST'])
def login_user():
    error_message = None  # Hinzugefügt: Variable für Fehlermeldung

    #überprüfe ob der Benutzer eingeloggt ist
    if 'username' in session:
        return redirect(url_for('dashboard.show_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = create_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and sha256(password.encode('utf-8')).hexdigest() == user[2]:  # Annahme: Passwort ist in der dritten Spalte der Tabelle
            # Setze den Benutzernamen und den Rang in der Sitzung
            session['username'] = username
            session['rank'] = user[3]  # Annahme: Der Rang befindet sich in der vierten Spalte der Tabelle
            session['user_id'] = user[0]

            connection.close()

            # Leite den Benutzer zum Dashboard weiter
            return redirect(url_for('dashboard.show_dashboard'))
        else:
            connection.close()
            error_message = 'Ungültige Anmeldedaten'  # Hinzugefügt: Fehlermeldung setzen

    return render_template('login.html', error_message=error_message)  # Hinzugefügt: Fehlermeldung an das Template übergeben
