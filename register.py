from flask import Blueprint, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
import hashlib
from dashboard import dashboard  # Importiere das Dashboard-Blueprint
import toml

register = Blueprint('register', __name__)

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

# Funktion zur Verschlüsselung des Passworts mit SHA-256
def hash_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    return sha256.hexdigest()

@register.route('/register', methods=['GET', 'POST'])
def register_user():
    #überprüfe ob der Benutzer eingeloggt ist
    if 'username' in session:
        return redirect(url_for('dashboard.show_dashboard'))
    
    # wenn die tabelle user nicht existiert, erstelle eine
    # Überprüfe, ob die Tabelle "user" existiert, andernfalls erstelle sie
    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255), rank VARCHAR(255), email VARCHAR(255))")
        connection.commit()
    except Error as e:
        print(f"Fehler bei der Verbindung zur MySQL-Datenbank: {e}")
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['e-mail']

        # Setze den Standardrang auf 'Starter'
        default_rank = 'Starter'

        connection = create_connection()
        cursor = connection.cursor()

        try:
            # Füge den Benutzer mit Standardrang zur Datenbank hinzu
            cursor.execute("INSERT INTO users (username, password, rank, email) VALUES (%s, %s, %s, %s)", (username, hash_password(password), default_rank, email))
            connection.commit()
            connection = create_connection()
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()

            # Setze den Benutzernamen in der Sitzung
            session['username'] = username
            session['rank'] = default_rank
            session['user_id'] = user[0]


            # Leite den Benutzer zum Dashboard weiter
            return redirect(url_for('dashboard.show_dashboard'))
        except Error as e:
            return 'Benutzername bereits vergeben oder E-Mail bereits vergeben'

    return render_template('register.html')
