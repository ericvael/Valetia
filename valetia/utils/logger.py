"""
Module de journalisation pour Valetia.
Configuration centralisée des logs.
"""
import os
import sys
from pathlib import Path

try:
    from loguru import logger
    
    # Import de la configuration
    try:
        from valetia.config.settings import LOGS_DIR, LOG_LEVEL, LOG_FORMAT
    except ImportError:
        # Fallback pour les tests ou l'utilisation standalone
        LOGS_DIR = os.path.join(Path(__file__).parent.parent.parent, "logs")
        LOG_LEVEL = "INFO"
        LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    
    # Créer le répertoire de logs s'il n'existe pas
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Configuration de base du logger
    logger.remove()  # Supprimer la configuration par défaut
    
    # Format console
    logger.add(
        sys.stderr,
        format=LOG_FORMAT,
        level=LOG_LEVEL,
        colorize=True,
    )
    
    # Format fichier
    logger.add(
        os.path.join(LOGS_DIR, "valetia_{time:YYYY-MM-DD}.log"),
        format=LOG_FORMAT,
        level=LOG_LEVEL,
        rotation="00:00",  # Nouveau fichier chaque jour
        retention="30 days",  # Garde les logs pendant 30 jours
        compression="zip",  # Compresse les anciens logs
    )
    
    def get_logger(name):
        """
        Retourne un logger configuré pour le module spécifié.
        
        Args:
            name (str): Nom du module (généralement __name__)
            
        Returns:
            object: Instance du logger configurée
        """
        return logger.bind(module=name)

except ImportError:
    # Fallback si loguru n'est pas installé
    import logging
    
    def get_logger(name):
        """Fallback logger utilisant le module logging standard."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        return logging.getLogger(name)
