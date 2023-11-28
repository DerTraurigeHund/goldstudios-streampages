from flask import Flask, render_template, redirect, url_for, send_from_directory, session
import toml
from login import login
from register import register
from dashboard import dashboard
from logout import logout
from admin import admin
from upload import upload
import yaml
import colorama
import os
import signal
import time
import mysql.connector
from mysql.connector import Error
import json

app = Flask(__name__)

#lade die Konfigurationsdatei
config = toml.load('conf.toml')

#lade die Konfigurationsdaten
port = config['server']['port']
host = config['server']['host']
debug = config['server']['debug']
secret_key = config['session']['secret_key']
language = config['server']['language']

# Setze den geheimen Schlüssel für die Flask-Session
app.config['SECRET_KEY'] = secret_key

# ordnere Route für die Startseite
@app.route('/')
def index():
    return render_template('index.html')

app.register_blueprint(login)
app.register_blueprint(register)
app.register_blueprint(dashboard)
app.register_blueprint(logout)
app.register_blueprint(admin)
app.register_blueprint(upload)

# Route für Fehlerseite
@app.route('/error')
def error():
    #lade die Konfigurationsdaten
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

    print(language)

    error_404_title = language_data['error_404_title']
    error_404_description = language_data['error_404_description']
    return render_template('/errors/error.html' , error_404_title=error_404_title, error_404_description=error_404_description)

# Fange alle anderen Anfragen ab und leite sie zur Fehlerseite weiter
@app.route('/<path:path>')
def catch_all(path):
    return redirect(url_for('error'))

# ordnere Route für die CSS-Dateien
@app.route('/style/<path:filename>')
def serve_style(filename):
    return send_from_directory('styles', filename)

# ordnere Route für die JavaScript-Dateien
@app.route('/scripts/<path:filename>')
def serve_scripts(filename):
    return send_from_directory('scripts', filename)

# ordnere Route für die Bilder und Filme/Videos
@app.route('/media/<path:filename>')
def serve_media(filename):
    return send_from_directory('media', filename)

# ordnere Route für die uploaded-Dateien
@app.route('/uploads/<path:filename>')
def serve_uploaded(filename):
    return send_from_directory('uploads', filename)

# restarte Flask
@app.route('/restart')
def restart():
    
    #überprüfe ob user Admin ist
    if 'username' in session and session['rank'] == 'Administrator':
        if debug == False:
            #führe restart.py aus und schliese den aktuellen code
            os.system('python restart.py')
            os.kill(os.getpid(), 9)
        else:
            error_404_title = 'Restart faild'
            error_404_description = 'Restarting is only possible if debug mode is deactivated'
            return render_template('errors/error_message.html', error_type=error_404_title, error_message=error_404_description, return_url=url_for('admin.settings'))
    else:
        return redirect(url_for('login.login_user'))

if __name__ == '__main__':
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

    print(language)

    message = language_data['start_message'].format(port=port, debug=debug)
    print(colorama.Fore.GREEN + message + colorama.Style.RESET_ALL) #beste nachrich von ChatGBT
    # printe die prozess id und spiechere sie in id.json
    print(colorama.Fore.BLUE + 'Process ID: ' + str(os.getpid()) + colorama.Style.RESET_ALL)
    with open('id.json', 'w') as f:
        json.dump({'process_id': os.getpid()}, f)
    app.run(host, port, debug)