import requests
import time
import csv
from pathlib import Path

url = "http://localhost:8086/api/v3/datarefs"

session = requests.Session() # Délai de requete réduit de 2s à 0,02s en utilisant une session persistante pour les requêtes HTTP

response = session.get(url)
response.raise_for_status() #Cette méthode déclenche une exception HTTP si le serveur répond avec un code d'erreur, par exemple 404 Not Found
donnees = response.json()

datarefs_voulues = {
    "ias": "sim/cockpit2/gauges/indicators/airspeed_kts_pilot",
    "altitude": "sim/cockpit2/gauges/indicators/altitude_ft_pilot",
    "radio_alt": "sim/cockpit2/gauges/indicators/radio_altimeter_height_ft_pilot",
    "vs": "sim/cockpit2/gauges/indicators/vvi_fpm_pilot",
    "pitch": "sim/flightmodel/position/theta",
    "bank": "sim/flightmodel/position/phi",
    "rudder": "sim/flightmodel2/wing/rudder1_deg",
    "throttle": "sim/cockpit2/engine/actuators/throttle_ratio",
    "flaps": "sim/cockpit2/controls/flap_system_deploy_ratio",
    "speedbrake": "sim/cockpit2/controls/speedbrake_ratio",
    "gear": "sim/flightmodel2/gear/deploy_ratio"
}

datarefs_ids = {}

for variable, description in datarefs_voulues.items():
    for dataref in donnees["data"]:
        if dataref["name"] == description:
            datarefs_ids[variable] = dataref["id"]

def lire_dataref(dataref_id):
    url = f"http://localhost:8086/api/v3/datarefs/{dataref_id}/value"
    response = session.get(url)
    response.raise_for_status()
    donnees = response.json() #dictionnaire avec clé 'data' associée à la valeur de la dataref
    return donnees['data']

def etat_train(gear):
    if gear[0] == 1.0 and gear[1] == 1.0 and gear[2] == 1.0:
        return "DOWN"
    elif gear[0] == 0.0 and gear[1] == 0.0 and gear[2] == 0.0:
        return "UP"
    else:
        return "TRANSIT"

numero = 1
nom_fichier = f"telemetrie_{numero:03d}.csv" # Exemple de nom de fichier : telemetrie_001.csv

while Path(nom_fichier).exists(): # Vérifie si le fichier existe déjà et incrémente le numéro jusqu'à trouver un nom de fichier unique
    numero += 1
    nom_fichier = f"telemetrie_{numero:03d}.csv"

with open(nom_fichier, "w", newline="", encoding = "utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["time_s","ias_kts", "altitude_ft", "radio_alt_ft", "vs_fpm", "pitch", "bank", "rudder", "throttle_1", "throttle_2", "flaps", "speedbrake", "gear"])  # Écrire l'en-tête du fichier CSV

    debut = time.monotonic()  # Enregistre le temps de début pour calculer la durée d'exécution

    while True:
        debut_iteration = time.monotonic()  # Enregistre le temps de début de l'itération pour calculer le temps écoulé

        ias = lire_dataref(datarefs_ids["ias"])
        vs = lire_dataref(datarefs_ids["vs"])
        altitude = lire_dataref(datarefs_ids["altitude"])
        radio_alt = lire_dataref(datarefs_ids["radio_alt"])
        pitch = lire_dataref(datarefs_ids["pitch"])
        bank = lire_dataref(datarefs_ids["bank"])
        flaps = lire_dataref(datarefs_ids["flaps"])
        throttle = lire_dataref(datarefs_ids["throttle"])
        throttle_1 = throttle[0]
        throttle_2 = throttle[1]
        speedbrake = lire_dataref(datarefs_ids["speedbrake"])
        gear = etat_train(lire_dataref(datarefs_ids["gear"]))
        rudder = lire_dataref(datarefs_ids["rudder"])[10]

        temps_ecoule = time.monotonic() - debut  # Calcule le temps écoulé depuis le début de l'exécution

        writer.writerow([temps_ecoule, ias, altitude, radio_alt, vs, pitch, bank, rudder, throttle_1, throttle_2, flaps, speedbrake, gear])  # Écrire les valeurs dans le fichier CSV

        f.flush()  # S'assure que les données sont écrites immédiatement dans le fichier

        time.sleep(max(0, 1 - (time.monotonic() - debut_iteration))) # Ajuste le temps de sommeil pour maintenir un intervalle d'une seconde
