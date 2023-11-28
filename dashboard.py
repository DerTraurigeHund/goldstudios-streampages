from flask import Blueprint, render_template, redirect, url_for, session
import random
import json
import mysql.connector 
import toml
from mysql.connector import Error

#lese die Chuck_Norris.json datei
with open('Chuck_Norris.json', 'r', encoding='utf-8') as file:
    chuck_norris_data = json.load(file)

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/dashboard')
def show_dashboard():
    #suche zufällige Chuck Norris Witz aus
    test = random.choice(chuck_norris_data)['witz']
    #lese die datenbank
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
    # Überprüfe, ob der Benutzer eingeloggt ist
    if 'username' in session:
        username = session['username']
        connection = create_connection()
        cursor = connection.cursor()
        print(session['user_id'])
        # lade die uploads aus der datenbank die zur selben id gehoeren
        cursor.execute("SELECT * FROM uploads WHERE user_id=%s", (session['user_id'],))
        uploads = cursor.fetchall()

        return render_template('dashboard.html', username=username , test=test, uploads=uploads)
    else:
        # Benutzer ist nicht eingeloggt, leite ihn zur Login-Seite weiter
        return redirect(url_for('login.login_user'))
