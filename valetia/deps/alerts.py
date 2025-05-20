"""
Module d'alertes pour les mises à jour de sécurité.
Permet de configurer et d'envoyer des alertes lorsque des mises à jour
de sécurité sont disponibles pour les dépendances.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import time

# Importer le logger
from valetia.logger import loguru_logger as logger

# Importer le module de vérification des dépendances
from .checker import scan_dependencies, get_dependency_report, DEPS_DIR

# Fichier de configuration des alertes
ALERTS_CONFIG_FILE = DEPS_DIR / "alerts_config.json"
ALERTS_LOG_FILE = DEPS_DIR / "alerts_log.json"

def init_alerts_config():
    """
    Initialise la configuration des alertes avec des valeurs par défaut.
    """
    if not ALERTS_CONFIG_FILE.exists():
        config = {
            "enabled": True,
            "check_interval_hours": 24,
            "last_check": None,
            "notify_on_updates": False,
            "notify_on_vulnerabilities": True,
            "min_severity": "medium",
            "notification_methods": ["log"]
        }
        
        with open(ALERTS_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Configuration des alertes initialisée avec les valeurs par défaut")
    
    return load_alerts_config()

def load_alerts_config():
    """
    Charge la configuration des alertes depuis le fichier.
    
    Returns:
        dict: Configuration des alertes
    """
    if not ALERTS_CONFIG_FILE.exists():
        return init_alerts_config()
    
    with open(ALERTS_CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    return config

def save_alerts_config(config):
    """
    Sauvegarde la configuration des alertes.
    
    Args:
        config (dict): Configuration à sauvegarder
    """
    with open(ALERTS_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"Configuration des alertes mise à jour")

def log_alert(alert_type, details):
    """
    Enregistre une alerte dans le fichier de log.
    
    Args:
        alert_type (str): Type d'alerte (update, vulnerability)
        details (dict): Détails de l'alerte
    """
    # Charger les alertes existantes
    alerts = []
    if ALERTS_LOG_FILE.exists():
        with open(ALERTS_LOG_FILE, 'r') as f:
            alerts = json.load(f)
    
    # Ajouter la nouvelle alerte
    alert = {
        "timestamp": datetime.now().isoformat(),
        "type": alert_type,
        "details": details
    }
    
    alerts.append(alert)
    
    # Sauvegarder les alertes
    with open(ALERTS_LOG_FILE, 'w') as f:
        json.dump(alerts, f, indent=2)
    
    logger.info(f"Alerte enregistrée: {alert_type}")

def check_and_alert():
    """
    Vérifie les dépendances et envoie des alertes si nécessaire.
    
    Returns:
        bool: True si des alertes ont été envoyées, False sinon
    """
    config = load_alerts_config()
    
    # Si les alertes sont désactivées, ne rien faire
    if not config.get("enabled", True):
        logger.info("Les alertes de dépendances sont désactivées")
        return False
    
    # Vérifier si c'est le moment de faire une vérification
    last_check = config.get("last_check")
    interval_hours = config.get("check_interval_hours", 24)
    
    if last_check:
        last_check_time = datetime.fromisoformat(last_check)
        now = datetime.now()
        elapsed_hours = (now - last_check_time).total_seconds() / 3600
        
        if elapsed_hours < interval_hours:
            logger.info(f"Vérification des dépendances ignorée (dernière: il y a {elapsed_hours:.1f}h, intervalle: {interval_hours}h)")
            return False
    
    # Effectuer l'analyse des dépendances
    logger.info("Démarrage de la vérification périodique des dépendances")
    result = scan_dependencies()
    
    # Mettre à jour la date de dernière vérification
    config["last_check"] = datetime.now().isoformat()
    save_alerts_config(config)
    
    # Vérifier s'il faut envoyer des alertes
    alerts_sent = False
    
    # Alertes pour les mises à jour
    if config.get("notify_on_updates", False) and result["updates_available"]:
        logger.warning(f"ALERTE: {len(result['updates_available'])} mises à jour disponibles")
        log_alert("updates", result["updates_available"])
        alerts_sent = True
    
    # Alertes pour les vulnérabilités
    if config.get("notify_on_vulnerabilities", True) and result["vulnerabilities"]:
        logger.warning(f"ALERTE: {len(result['vulnerabilities'])} vulnérabilités détectées")
        log_alert("vulnerabilities", result["vulnerabilities"])
        alerts_sent = True
    
    if alerts_sent:
        logger.info("Des alertes ont été envoyées")
    else:
        logger.info("Aucune alerte n'a été envoyée")
    
    return alerts_sent

def configure_alerts(enabled=None, check_interval=None, notify_updates=None, 
                    notify_vulnerabilities=None, min_severity=None):
    """
    Configure les paramètres des alertes.
    
    Args:
        enabled (bool, optional): Activer/désactiver les alertes
        check_interval (int, optional): Intervalle de vérification en heures
        notify_updates (bool, optional): Notifier pour les mises à jour
        notify_vulnerabilities (bool, optional): Notifier pour les vulnérabilités
        min_severity (str, optional): Sévérité minimale pour les alertes
    """
    config = load_alerts_config()
    
    if enabled is not None:
        config["enabled"] = bool(enabled)
    
    if check_interval is not None:
        config["check_interval_hours"] = int(check_interval)
    
    if notify_updates is not None:
        config["notify_on_updates"] = bool(notify_updates)
    
    if notify_vulnerabilities is not None:
        config["notify_on_vulnerabilities"] = bool(notify_vulnerabilities)
    
    if min_severity is not None:
        config["min_severity"] = str(min_severity)
    
    save_alerts_config(config)
    logger.info("Configuration des alertes mise à jour")
    
    return config

def get_alerts_summary():
    """
    Retourne un résumé des alertes récentes.
    
    Returns:
        str: Résumé des alertes
    """
    if not ALERTS_LOG_FILE.exists():
        return "Aucune alerte enregistrée."
    
    with open(ALERTS_LOG_FILE, 'r') as f:
        alerts = json.load(f)
    
    if not alerts:
        return "Aucune alerte enregistrée."
    
    # Trier les alertes par date (les plus récentes d'abord)
    alerts.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Générer le résumé
    summary = ["=== RÉSUMÉ DES ALERTES ==="]
    
    # Limiter aux 10 alertes les plus récentes
    for alert in alerts[:10]:
        timestamp = datetime.fromisoformat(alert["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        alert_type = "Mises à jour" if alert["type"] == "updates" else "Vulnérabilités"
        count = len(alert["details"])
        
        summary.append(f"{timestamp} - {alert_type}: {count}")
    
    if len(alerts) > 10:
        summary.append(f"... et {len(alerts) - 10} alertes plus anciennes")
    
    return "\n".join(summary)

def setup_periodic_check():
    """
    Configure une vérification périodique des dépendances.
    Cette fonction est destinée à être appelée au démarrage de l'application.
    """
    config = load_alerts_config()
    
    # Si les alertes sont désactivées, ne rien faire
    if not config.get("enabled", True):
        logger.info("Les alertes de dépendances sont désactivées")
        return
    
    # Effectuer une vérification immédiate si nécessaire
    if not config.get("last_check"):
        logger.info("Première vérification des dépendances")
        check_and_alert()
    
    logger.info("Vérification périodique des dépendances configurée")

# Initialiser les alertes au chargement du module
if __name__ != "__main__":
    try:
        init_alerts_config()
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des alertes: {str(e)}")
