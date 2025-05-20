from valetia.logger import get_logger

# Créer un logger pour ce module
logger = get_logger(__name__)

# Tester différents niveaux de logs
logger.debug("Ceci est un message de débogage")
logger.info("Ceci est un message d'information")
logger.warning("Ceci est un avertissement")
logger.error("Ceci est une erreur")
logger.critical("Ceci est une erreur critique")

# Tester avec des données structurées
logger.info("Action utilisateur", action="login", user_id=123, status="success")
