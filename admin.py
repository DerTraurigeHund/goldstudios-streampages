from flask import Blueprint, render_template, session, redirect, url_for, request, Flask
import mysql.connector
from mysql.connector import Error
from hashlib import sha256
import toml
import sys
import secrets

admin = Blueprint('admin', __name__)

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

@admin.route('/admin/edit_user')
def edit_user():
    # Überprüfe, ob der Benutzer eingeloggt und ein Administrator ist
    if 'username' in session and session['rank'] == 'Administrator':
        connection = create_connection()
        cursor = connection.cursor()

        # Lade alle Benutzer aus der Datenbank mit ID, Benutzername, Rang und E-Mail
        cursor.execute("SELECT id, username, rank, email FROM users")
        users = cursor.fetchall()

        connection.close()

        return render_template('admin/edit_user.html', users=users)
    else:
        # Falls nicht eingeloggt oder kein Administrator, zur Login-Seite weiterleiten
        return redirect(url_for('login.login_user'))

@admin.route('/admin/update_user/<int:user_id>', methods=['POST'])
def update_user(user_id):
    # Überprüfe, ob der Benutzer eingeloggt und ein Administrator ist
    if 'username' in session and session['rank'] == 'Administrator':
        connection = create_connection()
        cursor = connection.cursor()

        # Lese die aktualisierten Benutzerdaten aus dem Formular
        new_username = request.form['new_username']
        new_rank = request.form['new_rank']
        new_email = request.form['new_email']

        # Überprüfe, ob ein neuer Benutzername oder Rang eingegeben wurde und aktualisiere entsprechend
        if new_username:
            cursor.execute("UPDATE users SET username=%s WHERE id=%s", (new_username, user_id))
        elif new_rank:
            cursor.execute("UPDATE users SET rank=%s WHERE id=%s", (new_rank, user_id))
        elif new_email:
            cursor.execute("UPDATE users SET email=%s WHERE id=%s", (new_email, user_id))

        connection.commit()

        connection.close()

        return redirect(url_for('admin.edit_user'))
    else:
        # Falls nicht eingeloggt oder kein Administrator, zur Login-Seite weiterleiten
        return redirect(url_for('login.login_user'))
    
#user löschen
@admin.route('/admin/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'username' in session and session['rank'] == 'Administrator':
        connection = create_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))

        connection.commit()

        connection.close()

        return redirect(url_for('admin.edit_user'))
    else:
        return redirect(url_for('login.login_user'))

@admin.route('/admin/settings')
def settings():
    config = toml.load('conf.toml')
    port = config['server']['port']
    host = config['server']['host']
    log_file = config['server']['log_file']
    debug = config['server']['debug']
    mysql_host = config['mysql']['host']
    mysql_user = config['mysql']['user']
    mysql_password = config['mysql']['password']
    mysql_db = config['mysql']['db']
    enable_upload = config['upload']['enable_uploads']
    upload_folder = config['upload']['upload_dir']
    upload_cooldown = config['upload']['upload_cooldown']
    file_live_time = config['upload']['file_live_time']
    max_upload_size = config['upload']['maxFileSize']
    max_upload_size_default = config['upload']['maxFileSize_default']
    max_upload_size_starter = config['upload']['maxFileSize_starter']
    max_upload_size_abonent = config['upload']['maxFileSize_aboment']
    max_upload_size_supper_abo = config['upload']['maxFileSize_supper-abo']
    max_upload_size_support = config['upload']['maxFileSize_support']
    max_upload_size_moderator = config['upload']['maxFileSize_moderator']
    max_upload_size_developer = config['upload']['maxFileSize_developer']
    max_upload_size_admin = config['upload']['maxFileSize_admin']
    disable_upload_cooldown_for_moderator = config['upload']['disable_upload_cooldown_for_moderator']
    disable_upload_cooldown_for_developer = config['upload']['disable_upload_cooldown_for_developer']
    disable_upload_cooldown_for_admin = config['upload']['disable_upload_cooldown_for_admin']
    session_secret_key = config['session']['secret_key']
    gen_session_secret_key = secrets.token_hex(16)

    def setting_return():
        return render_template('admin/settings.html',port=port, host=host, log_file=log_file, debug=debug, mysql_host=mysql_host, mysql_user=mysql_user, mysql_password=mysql_password, mysql_db=mysql_db, language=config['server']['language'], enable_upload=enable_upload, upload_folder=upload_folder, upload_cooldown=upload_cooldown, file_live_time=file_live_time, max_upload_size=max_upload_size, max_file_size_default=max_upload_size_default, max_file_size_starter=max_upload_size_starter, max_file_size_abonent=max_upload_size_abonent, max_file_size_supper_abo=max_upload_size_supper_abo, max_file_size_support=max_upload_size_support, max_file_size_moderator=max_upload_size_moderator, max_file_size_developer=max_upload_size_developer, max_file_size_admin=max_upload_size_admin, disable_upload_cooldown_for_moderator=disable_upload_cooldown_for_moderator, disable_upload_cooldown_for_developer=disable_upload_cooldown_for_developer, disable_upload_cooldown_for_admin=disable_upload_cooldown_for_admin, session_secret_key=session_secret_key, gen_session_secret_key=gen_session_secret_key)

    if 'username' in session and session['rank'] == 'Administrator':
        if config['admin_settings']['enable_settings_site']:
            #wenn debug gesendet wird
            if 'debug' in request.args:
                debug = request.args.get('debug')
                config['server']['debug'] = str(debug).lower() == 'true'
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'language' in request.args:
                language = request.args.get('language')
                config['server']['language'] = language
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'port' in request.args:
                port = request.args.get('port')
                config['server']['port'] = int(port)
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'host' in request.args:
                host = request.args.get('host')
                config['server']['host'] = host
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'log_file' in request.args:
                log_file = request.args.get('log_file')
                config['server']['log_file'] = log_file
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'stop_webserver' in request.args:
                sys.exit(0)
            elif 'mysql_host' in request.args:
                mysql_host = request.args.get('mysql_host')
                config['mysql']['host'] = mysql_host
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'mysql_user' in request.args:
                mysql_user = request.args.get('mysql_user')
                config['mysql']['user'] = mysql_user
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'mysql_password' in request.args:
                mysql_password = request.args.get('mysql_password')
                config['mysql']['password'] = mysql_password
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'mysql_db' in request.args:
                mysql_db = request.args.get('mysql_db')
                config['mysql']['db'] = mysql_db
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'enable_upload' in request.args:
                enable_upload = request.args.get('enable_upload')
                config['upload']['enable_uploads'] = str(enable_upload).lower() == 'true'
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'upload_folder' in request.args:
                upload_folder = request.args.get('upload_folder')
                config['upload']['upload_dir'] = upload_folder
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'upload_cooldown' in request.args:
                upload_cooldown = request.args.get('upload_cooldown')
                config['upload']['upload_cooldown'] = int(upload_cooldown)
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'file_live_time' in request.args:
                file_live_time = request.args.get('file_live_time')
                config['upload']['file_live_time'] = int(file_live_time)
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'max_upload_size' in request.args:
                max_upload_size = request.args.get('max_upload_size')
                config['upload']['maxFileSize'] = int(max_upload_size)
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'max_file_size_default' in request.args:
                max_file_size_default = request.args.get('max_file_size_default')
                config['upload']['maxFileSize_default'] = int(max_file_size_default)
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'max_file_size_starter' in request.args:
                max_file_size_starter = request.args.get('max_file_size_starter')
                config['upload']['maxFileSize_starter'] = int(max_file_size_starter)
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'max_file_size_abonent' in request.args:
                max_file_size_abonent = request.args.get('max_file_size_abonent')
                config['upload']['maxFileSize_aboment'] = int(max_file_size_abonent)
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'max_file_size_supper_abo' in request.args:
                max_file_size_supper_abo = request.args.get('max_file_size_supper_abo')
                config['upload']['maxFileSize_supper-abo'] = int(max_file_size_supper_abo)
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'max_file_size_support' in request.args:
                max_file_size_support = request.args.get('max_file_size_support')
                config['upload']['maxFileSize_support'] = int(max_file_size_support)
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'max_file_size_moderator' in request.args:
                max_file_size_moderator = request.args.get('max_file_size_moderator')
                config['upload']['maxFileSize_moderator'] = int(max_file_size_moderator)
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'max_file_size_developer' in request.args:
                max_file_size_developer = request.args.get('max_file_size_developer')
                config['upload']['maxFileSize_developer'] = int(max_file_size_developer)
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'max_file_size_admin' in request.args:
                max_file_size_admin = request.args.get('max_file_size_admin')
                config['upload']['maxFileSize_admin'] = int(max_file_size_admin)
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'disable_upload_cooldown_for_moderator' in request.args:
                disable_upload_cooldown_for_moderator = request.args.get('disable_upload_cooldown_for_moderator')
                config['upload']['disable_upload_cooldown_for_moderator'] = str(disable_upload_cooldown_for_moderator).lower() == 'true'
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'disable_upload_cooldown_for_developer' in request.args:
                disable_upload_cooldown_for_developer = request.args.get('disable_upload_cooldown_for_developer')
                config['upload']['disable_upload_cooldown_for_developer'] = str(disable_upload_cooldown_for_developer).lower() == 'true'
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'disable_upload_cooldown_for_admin' in request.args:
                disable_upload_cooldown_for_admin = request.args.get('disable_upload_cooldown_for_admin')
                config['upload']['disable_upload_cooldown_for_admin'] = str(disable_upload_cooldown_for_admin).lower() == 'true'
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            elif 'session_secret_key' in request.args:
                session_secret_key = request.args.get('session_secret_key')
                config['session']['secret_key'] = session_secret_key
                with open('conf.toml', 'w') as f:
                    toml.dump(config, f)
                return setting_return()
            else:
                return setting_return()
        else:
            return render_template('errors/error_message.html', error_message="Die Einstellungen sind deaktiviert, du kannst diese in der Konfigurationsdatei aktivieren.", error_type="Die Seite ist Deaktiviert", error_message_line2="in conf.toml \"enable_settings_site = false\" zu \"enable_settings_site = true\"")
    else:
        return redirect(url_for('login.login_user'))