import pandas as pd

def preparer_donnees(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prépare les données pour l'entraînement du modèle de prédiction de la vitesse verticale future.

    Args:
        df (pd.DataFrame): Le DataFrame contenant les données de télémétrie.

    Returns:
        pd.DataFrame: Le DataFrame préparé avec les colonnes nécessaires pour l'entraînement.
    """
    df = df.copy()  # Crée une copie du DataFrame pour éviter de modifier l'original
    df["vs_future_10s"] = df["vs_fpm"].shift(-10)  # On récupère la vs à t + 10
    df["delta_vs_3s"] = df["vs_fpm"] - df["vs_fpm"].shift(3)  # On calcule la différence de vs entre t et t - 3 secondes
    df["delta_pitch_3s"] = df["pitch"] - df["pitch"].shift(3)  # On calcule la différence de pitch entre t et t - 3 secondes
    df = pd.get_dummies(df, columns=["gear"], dtype=int) # On transforme la colonne gear en variables indicatrices (one-hot encoding) pour les valeurs "DOWN", "TRANSIT" et "UP"

    colonnes_gear = ["gear_DOWN", "gear_TRANSIT", "gear_UP"]

    for colonne in colonnes_gear:
        if colonne not in df.columns:
            df[colonne] = 0 # On ajoute une colonne de 0 si la valeur n'est pas présente dans le DataFrame

    # On supprime les lignes où vs_future_10s ou delta_vs_3s ou delta_pitch_3s est NaN
    df_clean = df.dropna(subset=["vs_future_10s", "delta_vs_3s", "delta_pitch_3s"]) 

    return df_clean

def separer_variables(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Sépare les variables explicatives (features) de la variable cible (target).

    Args:
        df (pd.DataFrame): Le DataFrame contenant les données préparées.

    Returns:
        tuple[pd.DataFrame, pd.Series]: Un tuple contenant le DataFrame des features et la Series de la target.
    """
    features = [
        "ias_kts",
        "altitude_ft",
        "vs_fpm",
        "pitch",
        "throttle_1",
        "delta_vs_3s",
        "delta_pitch_3s",
        "gear_DOWN",
        "gear_TRANSIT",
        "gear_UP"
    ]

    X = df[features]
    y = df["vs_future_10s"]

    return X, y