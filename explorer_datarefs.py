import requests
import time

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
