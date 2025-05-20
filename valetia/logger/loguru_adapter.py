"""
Configuration de loguru pour le projet ValetIA.
"""

import sys
from pathlib import Path
from loguru import logger
import os

# Obtenir le niveau de log depuis les variables d'environnement ou utiliser INFO par défaut
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

# Définir le chemin du fichier de log
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
LOG_FILE = os.path.join(log_dir, f"valetia-loguru.log")

# Configurer loguru
def setup_loguru():
    # Supprimer les handlers par défaut
    logger.remove()
    
    # Ajouter un handler pour la console avec formatage coloré
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=LOG_LEVEL
    )
    
    # Ajouter un handler pour le fichier avec rotation
    logger.add(
        LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=LOG_LEVEL,
        rotation="1 day",
        retention="14 days",
        compression="zip"
    )
    
    return logger

# Initialiser et exposer le logger
loguru_logger = setup_loguru()
