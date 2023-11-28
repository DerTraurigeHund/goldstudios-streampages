import time
import os
import json
import signal

def kill_process(pid):
    try:
        # Das SIGTERM-Signal senden, um den Prozess zu beenden
        os.kill(pid, signal.SIGTERM)
        print(f"Prozess mit der PID {pid} wurde beendet.")
    except ProcessLookupError:
        print(f"Prozess mit der PID {pid} nicht gefunden.")
    except PermissionError:
        print(f"Keine Berechtigung, um den Prozess mit der PID {pid} zu beenden.")

# beende den prozess mit der prozess id die in id.json steht
with open('id.json', 'r') as file:
    process_id = json.load(file)['process_id']

kill_process(process_id)

print("Webserver wird in 5 Sekunden neugestartet")
time.sleep(5)
print("Webserver wird neugestartet")
os.system('python main.py')
exit()