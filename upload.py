from flask import Blueprint, render_template, request, session, redirect, url_for
import os
import toml
from datetime import datetime, timedelta, timezone
import mysql.connector
from mysql.connector import Error
import uuid
import time
import yaml

upload = Blueprint('upload', __name__)
config = toml.load('conf.toml')

# Verbindungsdaten zur MySQL-Datenbank (Du kannst diese Informationen auch aus main.py importieren)
DB_HOST = config['mysql']['host']
DB_USER = config['mysql']['user']
DB_PASSWORD = config['mysql']['password']
DB_NAME =  config['mysql']['db']


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

connection = create_connection()
cursor = connection.cursor()
#überprüfe, od die tabelle uploads existiert, andernfalls erstelle sie (id, username, file_name, user_id, upload_date, upload_path)
try:
    cursor.execute("CREATE TABLE IF NOT EXISTS uploads (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), file_name VARCHAR(255), user_id INT, upload_date DATETIME, upload_path VARCHAR(255))")
    connection.commit()
except Error as e:
    print(f"Fehler bei der Verbindung zur MySQL-Datenbank: {e}")
@upload.route('/upload', methods=['GET', 'POST'])

def upload_file():
    if 'username' not in session:
        return redirect(url_for('login.login_user'))
    config = toml.load('conf.toml')
    language = config['server']['language']
    if language == 'de_DE':
        language_data = yaml.load(open('language/de_DE.yaml', 'r', encoding='utf-8'), Loader=yaml.SafeLoader)
    elif language == 'en_US':
        language_data = yaml.load(open('language/en_US.yaml', 'r', encoding='utf-8'), Loader=yaml.SafeLoader)
    elif language == 'es_ES':
        language_data = yaml.load(open('language/es_ES.yaml', 'r', encoding='utf-8'), Loader=yaml.SafeLoader)
    elif language == 'fr_FR':
        language_data = yaml.load(open('language/fr_FR.yaml', 'r', encoding='utf-8'), Loader=yaml.SafeLoader)
    elif language == 'it_IT':
        language_data = yaml.load(open('language/it_IT.yaml', 'r', encoding='utf-8'), Loader=yaml.SafeLoader)
    else:
        print('Language not found')
        exit()
    # Verbindungsdaten zur MySQL-Datenbank (Du kannst diese Informationen auch aus main.py importieren)
    DB_HOST = config['mysql']['host']
    DB_USER = config['mysql']['user']
    DB_PASSWORD = config['mysql']['password']
    DB_NAME =  config['mysql']['db']

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

    connection = create_connection()
    cursor = connection.cursor()

    username = session.get('username')

    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()

    session['rank'] = user[3]  # Annahme: Der Rang befindet sich in der vierten Spalte der Tabelle
    session['user_id'] = user[0]
    session['email'] = user[4]
    connection.close()

    if not config['upload']['enable_uploads']:
        return render_template('errors/error_message.html', error_message=language_data['upload_disabled_message'], error_type=language_data['upload_disabled_title'], return_url= '/dashboard')
    # überprüfe, ob der letzte upload vor 300 sekunden war
    if 'last_upload' in session:
        last_upload = session['last_upload']
        current_time = datetime.now(timezone.utc)
        print("last upload: ", last_upload)
        print(type(last_upload))
        print(type(current_time))
        time_difference = current_time - last_upload
        if time_difference.total_seconds() < int(config['upload']['upload_cooldown']):
            # Do something if the last upload was more than 300 seconds ago
            #setze wait auf keine nachkommerstelle
            connection = create_connection()
            cursor = connection.cursor()
            
            cursor.execute("SELECT * FROM uploads WHERE upload_date=%s", (last_upload.strftime("%Y-%m-%d %H:%M:%S"),))
            print("SELECT * FROM uploads WHERE upload_date=%s", (last_upload.strftime("%Y-%m-%d %H:%M:%S"),))
            print(last_upload)
            user = cursor.fetchone()
            test = user[5]
            wait = str(int(config['upload']['upload_cooldown']) - time_difference.total_seconds())
            wait = wait.split('.')[0]
            return render_template('/errors/wait.html', error_message=language_data['upload_wait_description'].format(wait=wait), error_message_line2=language_data['upload_wait_description2'], error_message_line3=language_data['upload_wait_description3'].format(test=test), error_type=language_data['upload_wait_title'].format(wait=wait), return_url=url_for('dashboard.show_dashboard'), error_message_line3_link='https://goldstudios.de/' + test)
    else:
        # Do something if there was no previous upload
        pass
    if request.method == 'POST':
        # Überprüfe, ob die POST-Anfrage eine Datei enthält
        if 'file' not in request.files:
            return render_template('upload.html', message='Keine Datei ausgewählt')

        file = request.files['file']

        # Überprüfe, ob eine Datei ausgewählt wurde
        if file.filename == '':
            return render_template('upload.html', message='Keine Datei ausgewählt')

        config = toml.load('conf.toml')

        rank_filesize_mapping = {
            'Starter': 'maxFileSize_starter',
            'Abonent': 'maxFileSize_aboment',
            'Supper-Abo': 'maxFileSize_supper-abo',
            'Supporter': 'maxFileSize_support',
            'Moderator': 'maxFileSize_moderator',
            'Developer': 'maxFileSize_developer',
            'Administrator': 'maxFileSize_admin'
        }

        # Überprüfe, ob der Rang in der Sitzung existiert
        user_rank = session.get('rank', 'default')

        # Verwende den Rang, um die entsprechende Dateigröße aus der Konfiguration zu erhalten
        max_file_size = int(config["upload"].get(rank_filesize_mapping.get(user_rank, 'maxFileSize_default')))
        
        # rechne von Bytes in MB um
        maxfilesize = max_file_size / 1024 / 1024

        if len(file.read()) > max_file_size:
            return render_template('errors/error.html', message='Datei zu groß. Maximal ' + str(maxfilesize) + ' MB erlaubt.')

        # Setze den Dateizeiger zurück, um die Datei später zu speichern
        file.seek(0)

        user_id = user[0]
        username = user[1]
        user_rang = user[3]
        date = datetime.now().strftime("%Y-%m-%d")
        random_id = str(uuid.uuid4())
        email = user[4]

        # Verzeichnispfad erstellen, wenn es nicht existiert
        upload_folder = config['upload']['upload_dir'].format(user_id=user_id, username=username, user_rang=user_rang, date=date, random_id=random_id, email=email)
        os.makedirs(upload_folder, exist_ok=True)

        # Dateipfad erstellen, um die Datei zu speichern
        file_path = os.path.join(upload_folder, file.filename)

        # Datei speichern
        file.save(file_path)

        rank = session.get('rank')
        # lade die letzte upload datum in die session
        if config['upload']['disable_upload_cooldown_for_admin'] and rank == 'Administrator':
            pass
        elif config['upload']['disable_upload_cooldown_for_developer'] and rank == 'Developer':
            pass
        elif config['upload']['disable_upload_cooldown_for_moderator'] and rank == 'Moderator':
            pass
        else:
            session['last_upload'] = datetime.now(timezone.utc)

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

        #speichere die datei in der Datenbank in der tabelle uploads
        # Verbindungsherstellung mit der Datenbank
        connection = create_connection()
        cursor = connection.cursor()

        # Speichere die Datei mit username, file_name, user id in der Datenbank in der Tabelle uploads
        upload_date = session.get('last_upload').strftime("%Y-%m-%d %H:%M:%S")
        user_name = session.get('username')
        file_name = file.filename
        upload_path = file_path

        cursor.execute("INSERT INTO uploads (username, file_name, user_id, upload_date, upload_path) VALUES (%s, %s, %s, %s, %s)", (user_name, file_name, user_id, upload_date, upload_path))
        connection.commit()
        print("upload_date: ",session['last_upload'])
        return redirect(url_for('upload.upload_file'))

    config = toml.load('conf.toml')

    rank_filesize_mapping = {
        'Starter': 'maxFileSize_starter',
        'Abonent': 'maxFileSize_aboment',
        'Supper-Abo': 'maxFileSize_supper-abo',
        'Supporter': 'maxFileSize_support',
        'Moderator': 'maxFileSize_moderator',
        'Developer': 'maxFileSize_developer',
        'Administrator': 'maxFileSize_admin'
    }

    # Überprüfe, ob der Rang in der Sitzung existiert
    user_rank = session.get('rank', 'default')

    # Verwende den Rang, um die entsprechende Dateigröße aus der Konfiguration zu erhalten
    max_file_size = int(config["upload"].get(rank_filesize_mapping.get(user_rank, 'maxFileSize_default')))
    
    # rechne von Bytes in MB oder GB um
    if max_file_size <= 1024:
        maxfilesize = max_file_size / 1024 / 1024
        maxfilesize_unit = 'MB'
    else:
        maxfilesize = max_file_size / 1024 / 1024 / 1024
        maxfilesize_unit = 'GB'
    return render_template('upload.html', max_file_size=maxfilesize, max_file_size_unit=maxfilesize_unit)
