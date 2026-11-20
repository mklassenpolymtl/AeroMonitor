import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import json

def separer_entrainement_test(
    X: pd.DataFrame,
    y: pd.Series
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Sépare les données en ensembles d'entraînement et de test.

    Args:
        X (pd.DataFrame): Les variables explicatives.
        y (pd.Series): La variable cible.

    Returns:
        tuple: Contient les ensembles d'entraînement et de test pour X et y.
    """
    split_idx = int(0.8 * len(X))  # On prend 80% des données pour l'entraînement et 20% pour le test

    X_train = X.iloc[:split_idx - 10]  # On exclut 10 observations avant le test pour éviter que les cibles d'entraînement utilisent des V/S du test.
    y_train = y.iloc[:split_idx - 10]

    X_test = X.iloc[split_idx:]
    y_test = y.iloc[split_idx:]  # On prend les 20% restants pour l'ensemble de test

    return X_train, X_test, y_train, y_test

def entrainer_modele(
    X_train: pd.DataFrame,
    y_train: pd.Series
) -> RandomForestRegressor:
    """
    Entraîne un modèle de forêt aléatoire sur les données d'entraînement.

    Args:
        X_train (pd.DataFrame): Les variables explicatives pour l'entraînement.
        y_train (pd.Series): La variable cible pour l'entraînement.

    Returns:
        RandomForestRegressor: Le modèle entraîné.
    """
    modele = RandomForestRegressor(
        n_estimators=100,
        max_depth=12,
        random_state=42,
        n_jobs=-1
    )  # On crée un modèle de forêt aléatoire avec 100 arbres et une profondeur maximale de 12

    modele.fit(X_train, y_train)  # On entraîne le modèle sur l'ensemble d'entraînement

    return modele

def sauvegarder_modele(
    modele: RandomForestRegressor,
    chemin: str
) -> None:
    """
    Sauvegarde le modèle entraîné dans un fichier.

    Args:
        modele (RandomForestRegressor): Le modèle entraîné.
        chemin (str): Le chemin du fichier où sauvegarder le modèle.
    """
    joblib.dump(modele, chemin)  # On sauvegarde le modèle dans un fichier

def sauvegarder_metadata(metadata: dict, chemin: str) -> None:
    """
    Sauvegarde les métadonnées dans un fichier JSON.

    Args:
        metadata (dict): Les métadonnées à sauvegarder.
        chemin (str): Le chemin du fichier où sauvegarder les métadonnées.
    """
    with open(chemin, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)  # On sauvegarde les métadonnées dans un fichier JSON