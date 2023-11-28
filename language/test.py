import yaml

# Laden Sie die YAML-Datei
file_path = 'language/de_DE.yaml'
with open(file_path, 'r', encoding='utf-8') as file:
    language_data = yaml.load(file, Loader=yaml.SafeLoader)

# Beispielwerte für den Port und den Debug-Modus
port = 8080
debug = True

# Formatieren Sie die Startnachricht mit den Werten
start_message = language_data['main']['start_message'].format(port=port, debug=debug)

# Zeigen Sie die formatierte Nachricht an
print(start_message)
