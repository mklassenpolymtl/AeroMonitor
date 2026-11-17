import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

fichier = "donnees/telemetrie_001.csv"

df = pd.read_csv(fichier)

df["vs_future_10s"] = df["vs_fpm"].shift(-10) # On récupère la vs à t + 10

df["delta_vs_3s"] = df["vs_fpm"] - df["vs_fpm"].shift(3) # On calcule la différence de vs entre t et t - 3 secondes

df_clean = df.dropna(subset=["vs_future_10s", "delta_vs_3s"]) # On supprime les lignes où vs_future_10s ou delta_vs_3s est NaN

features = [
    "ias_kts",
    "altitude_ft",
    "vs_fpm",
    "pitch",
    "throttle_1",
    "delta_vs_3s"
]

X = df_clean[features]
y = df_clean["vs_future_10s"]
print(X.shape, y.shape)

split_idx = int(0.8 * len(df_clean)) # On prend 80% des données pour l'entraînement et 20% pour le test

X_train = X.iloc[:split_idx - 10] # On prend 80% des données pour l'entraînement, en enlevant les 10 dernières lignes pour éviter d'avoir des valeurs NaN dans Y_train
y_train = y.iloc[:split_idx - 10] # Marge de 10 observations pour éviter une fuite temporelle

X_test = X.iloc[split_idx:]
y_test = y.iloc[split_idx:] # On prend les 20% restants pour l'ensemble de test

y_pred_baseline = X_test["vs_fpm"] # Prédit que la V/S restera identique pendant 10 secondes comme baseline

MAE = np.mean(np.abs(y_test - y_pred_baseline)) # On calcule l'erreur absolue moyenne entre les valeurs réelles et les prédictions

# MAE baseline : 191.16 ft/min

modele = RandomForestRegressor(
    n_estimators=100, 
    max_depth=12, 
    random_state=42, 
    n_jobs=-1
) # On crée un modèle de forêt aléatoire avec 100 arbres et une profondeur maximale de 12

modele.fit(X_train, y_train) # On entraîne le modèle sur l'ensemble d'entraînement
y_pred_ml = modele.predict(X_test) # On prédit les valeurs de l'ensemble de test
MAE_ml = np.mean(np.abs(y_test - y_pred_ml)) # On calcule l'erreur absolue moyenne entre les valeurs réelles et les prédictions du modèle
# MAE ML : 120.85 ft/min

masque_descente = X_test["vs_fpm"] < -300

y_test_descente = y_test[masque_descente]
y_pred_descente = y_pred_ml[masque_descente]
MAE_descente = np.mean(np.abs(y_test_descente - y_pred_descente)) # On calcule l'erreur absolue moyenne entre les valeurs réelles et les prédictions du modèle pour les descentes
# MAE_descente : 146.45 ft/min

y_pred_baseline_descente = y_pred_baseline[masque_descente]
MAE_baseline_descente = np.mean(np.abs(y_test_descente - y_pred_baseline_descente)) # On calcule l'erreur absolue moyenne entre les valeurs réelles et les prédictions baseline pour les descentes
# MAE_baseline_descente : 203.98 ft/min

masque_palier = (X_test["vs_fpm"] >= -300) & (X_test["vs_fpm"] <= 300)

y_test_palier = y_test[masque_palier]
y_pred_palier = y_pred_ml[masque_palier]
MAE_palier = np.mean(np.abs(y_test_palier - y_pred_palier)) # On calcule l'erreur absolue moyenne entre les valeurs réelles et les prédictions du modèle pour les paliers
# MAE palier : 57.66 ft/min

y_pred_baseline_palier = y_pred_baseline[masque_palier]
MAE_baseline_palier = np.mean(np.abs(y_test_palier - y_pred_baseline_palier)) # On calcule l'erreur absolue moyenne entre les valeurs réelles et les prédictions baseline pour les paliers
# MAE baseline palier : 81.26 ft/min

masque_montée = X_test["vs_fpm"] > 300

y_test_montée = y_test[masque_montée]
y_pred_montée = y_pred_ml[masque_montée]
MAE_montée = np.mean(np.abs(y_test_montée - y_pred_montée)) # On calcule l'erreur absolue moyenne entre les valeurs réelles et les prédictions du modèle pour les montées
# MAE_montée : 499.63 ft/min

y_pred_baseline_montée = y_pred_baseline[masque_montée]
MAE_baseline_montée = np.mean(np.abs(y_test_montée - y_pred_baseline_montée)) # On calcule l'erreur absolue moyenne entre les valeurs réelles et les prédictions baseline pour les montées
# MAE baseline montée: 943.29 ft/min

# Nombre de descentes : len(y_test_descente) = 536 
# Nombre de paliers : len(y_test_palier) = 1308
# Nombre de montées : len(y_test_montée) = 182