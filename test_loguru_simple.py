# Importer le logger loguru configuré
from valetia.logger import loguru_logger

# Tester loguru
loguru_logger.debug("Ceci est un message de debug via loguru")
loguru_logger.info("Ceci est un message d'info via loguru")
loguru_logger.warning("Ceci est un avertissement via loguru")
loguru_logger.error("Ceci est une erreur via loguru")

# Tester avec des données structurées
loguru_logger.info(f"Utilisateur connecté: {{'user_id': 123, 'status': 'active'}}")
