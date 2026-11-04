import requests
import time
import csv

url = "http://localhost:8086/api/v3/datarefs"

response = requests.get(url)
response.raise_for_status() #Cette méthode déclenche une exception HTTP si le serveur répond avec un code d'erreur, par exemple 404 Not Found
donnees = response.json()

"""
for key in donnees:
    print(key) #data uniquement

print(type(donnees["data"]))
print(len(donnees["data"]))
print(donnees["data"][0])

for dataref in donnees["data"]:
    if "airspeed" in dataref["name"]:
        print(dataref["name"]) #Trouver liste de datarefs reliés à la vitesse
"""

"""
ias_dataref = {}

for dataref in donnees["data"]:
    if dataref["name"] == "sim/cockpit2/gauges/indicators/airspeed_kts_pilot":
        ias_dataref = dataref

ias_id = ias_dataref["id"]
ias_url = f"http://localhost:8086/api/v3/datarefs/{ias_id}/value"

while True:
    response_ias = requests.get(ias_url)
    response_ias.raise_for_status()
    donnees_ias = response_ias.json()

    ias = donnees_ias['data']  # Récupère la valeur de l'IAS à partir de la réponse JSON
    print(f"IAS: {ias:.2f} kts")  # Affiche la valeur de l'IAS avec deux décimales

    time.sleep(1)  # Attendre 1 seconde avant la prochaine requête
"""

datarefs_voulues = {
    "ias": "sim/cockpit2/gauges/indicators/airspeed_kts_pilot",
    "vs": "sim/cockpit2/gauges/indicators/vvi_fpm_pilot",
    "altitude": "sim/cockpit2/gauges/indicators/altitude_ft_pilot"
}

datarefs_ids = {}

for variable, description in datarefs_voulues.items():
    for dataref in donnees["data"]:
        if dataref["name"] == description:
            datarefs_ids[variable] = dataref["id"]

def lire_dataref(dataref_id):
    url = f"http://localhost:8086/api/v3/datarefs/{dataref_id}/value"
    response = requests.get(url)
    response.raise_for_status()
    donnees = response.json() #dictionnaire avec clé 'data' associée à la valeur de la dataref
    return donnees['data']

with open("telemetrie.csv", "w", newline="", encoding = "utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["time_s","ias_kts", "vs_fpm", "altitude_ft"])  # Écrire l'en-tête du fichier CSV

    debut = time.monotonic()  # Enregistre le temps de début pour calculer la durée d'exécution

    while True:
        ias = lire_dataref(datarefs_ids["ias"])
        vs = lire_dataref(datarefs_ids["vs"])
        altitude = lire_dataref(datarefs_ids["altitude"])

        temps_ecoule = time.monotonic() - debut  # Calcule le temps écoulé depuis le début de l'exécution

        writer.writerow([temps_ecoule, ias, vs, altitude])  # Écrire les valeurs dans le fichier CSV

        f.flush()  # S'assure que les données sont écrites immédiatement dans le fichier

        time.sleep(1)  # Attendre 1 seconde avant la prochaine requête
