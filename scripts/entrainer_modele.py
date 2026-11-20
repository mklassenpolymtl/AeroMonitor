import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

from src.donnees import preparer_donnees, separer_variables
from src.modele import separer_entrainement_test, entrainer_modele, sauvegarder_modele, sauvegarder_metadata

fichier = "donnees/telemetrie_001.csv"

df = pd.read_csv(fichier)

df_clean = preparer_donnees(df)

X, y = separer_variables(df_clean)
# print(X.shape, y.shape) --> (10130, 7) (10130,)

X_train, X_test, y_train, y_test = separer_entrainement_test(X, y)
modele = entrainer_modele(X_train, y_train)

y_pred_baseline = X_test["vs_fpm"] # Prédit que la V/S restera identique pendant 10 secondes comme baseline

y_pred_ml = modele.predict(X_test) # On prédit les valeurs de l'ensemble de test

MAE = np.mean(np.abs(y_test - y_pred_baseline)) # On calcule l'erreur absolue moyenne entre les valeurs réelles et les prédictions

MAE_ml = np.mean(np.abs(y_test - y_pred_ml)) # On calcule l'erreur absolue moyenne entre les valeurs réelles et les prédictions du modèle

masque_descente = X_test["vs_fpm"] < -300

y_test_descente = y_test[masque_descente]
y_pred_descente = y_pred_ml[masque_descente]
MAE_descente = np.mean(np.abs(y_test_descente - y_pred_descente)) # On calcule l'erreur absolue moyenne entre les valeurs réelles et les prédictions du modèle pour les descentes

y_pred_baseline_descente = y_pred_baseline[masque_descente]
MAE_baseline_descente = np.mean(np.abs(y_test_descente - y_pred_baseline_descente)) # On calcule l'erreur absolue moyenne entre les valeurs réelles et les prédictions baseline pour les descentes

masque_palier = (X_test["vs_fpm"] >= -300) & (X_test["vs_fpm"] <= 300)

y_test_palier = y_test[masque_palier]
y_pred_palier = y_pred_ml[masque_palier]
MAE_palier = np.mean(np.abs(y_test_palier - y_pred_palier)) # On calcule l'erreur absolue moyenne entre les valeurs réelles et les prédictions du modèle pour les paliers

y_pred_baseline_palier = y_pred_baseline[masque_palier]
MAE_baseline_palier = np.mean(np.abs(y_test_palier - y_pred_baseline_palier)) # On calcule l'erreur absolue moyenne entre les valeurs réelles et les prédictions baseline pour les paliers

masque_montée = X_test["vs_fpm"] > 300

y_test_montée = y_test[masque_montée]
y_pred_montée = y_pred_ml[masque_montée]
MAE_montée = np.mean(np.abs(y_test_montée - y_pred_montée)) # On calcule l'erreur absolue moyenne entre les valeurs réelles et les prédictions du modèle pour les montées

y_pred_baseline_montée = y_pred_baseline[masque_montée]
MAE_baseline_montée = np.mean(np.abs(y_test_montée - y_pred_baseline_montée)) # On calcule l'erreur absolue moyenne entre les valeurs réelles et les prédictions baseline pour les montées

# Nombre de descentes : len(y_test_descente) = 536 
# Nombre de paliers : len(y_test_palier) = 1308
# Nombre de montées : len(y_test_montée) = 182


print(f"MAE baseline : {MAE:.2f} ft/min")
print(f"MAE ML : {MAE_ml:.2f} ft/min")
print(f"MAE ML descente : {MAE_descente:.2f} ft/min")
print(f"MAE baseline descente : {MAE_baseline_descente:.2f} ft/min")
print(f"MAE ML palier : {MAE_palier:.2f} ft/min")
print(f"MAE baseline palier : {MAE_baseline_palier:.2f} ft/min")
print(f"MAE ML montée : {MAE_montée:.2f} ft/min")
print(f"MAE baseline montée : {MAE_baseline_montée:.2f} ft/min")

erreurs = X_test.copy()
erreurs["vs_reelle"] = y_test
erreurs["vs_predite"] = y_pred_ml
erreurs["erreur_abs"] = np.abs(erreurs["vs_reelle"] - erreurs["vs_predite"])

erreurs = erreurs.sort_values(by="erreur_abs", ascending=False) # On trie les erreurs par ordre décroissant

evenement = erreurs.sort_index()

sauvegarder_modele(modele, "modeles/modele_vs.joblib") # On sauvegarde le modèle entraîné dans un fichier .joblib

modele_charge = joblib.load("modeles/modele_vs.joblib")
y_pred_charge = modele_charge.predict(X_test)
# print(np.allclose(y_pred_ml, y_pred_charge)) # True, ce qui signifie que les prédictions du modèle chargé sont identiques à celles du modèle original

metadata = { # On crée un dictionnaire contenant les métadonnées du modèle pour les sauvegarder dans un fichier JSON
    "cible" : "vs_future_10s",
    "features" : X.columns.tolist(), # On récupère la liste des colonnes de X pour les utiliser comme features
    "categories_gear" : ["DOWN", "TRANSIT", "UP"],
    "mae_ft_min" : float(MAE_ml), # numpy.float64 n'est pas JSON serializable, donc on le convertit en float
}

intervalles = {} # On crée un dictionnaire pour stocker les intervalles min et max de chaque feature dans l'ensemble d'entraînement

for feature in X_train.columns:
    if not feature.startswith("gear_"): # On ne calcule pas les intervalles pour les variables indicatrices (one-hot encoding) de la colonne gear
        intervalles[feature] = {
            "min": float(X_train[feature].min()),
            "max": float(X_train[feature].max())
        }

metadata["intervalles"] = intervalles

sauvegarder_metadata(metadata, "modeles/metadata.json")  # On sauvegarde les métadonnées dans un fichier JSON

print(len(metadata["intervalles"]))
print(metadata["features"])
