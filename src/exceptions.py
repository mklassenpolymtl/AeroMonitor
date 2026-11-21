"""Exceptions personnalisées pour le projet INF1007."""


class AeroMonitorError(Exception):
    """Exception de base du projet AeroMonitor."""


class DonneeInvalideError(AeroMonitorError):
    """Levée quand une saisie de l'utilisateur est invalide"""