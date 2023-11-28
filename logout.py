from flask import Blueprint, redirect, url_for, session

logout = Blueprint('logout', __name__)

@logout.route('/logout')
def logout_user():
    # Überprüfe, ob der Benutzer angemeldet ist
    if 'username' in session:
        # Lösche den Benutzernamen aus der Sitzung
        session.pop('username', None)
        session.pop('rank', None)
        session.pop('user_id', None)
    # Leite den Benutzer zur Login-Seite weiter, unabhängig davon, ob er angemeldet war oder nicht
    return redirect(url_for('login.login_user'))
