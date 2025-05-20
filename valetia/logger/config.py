import logging
import os
import sys
from datetime import datetime
import structlog
from pythonjsonlogger import jsonlogger

# Création du répertoire de logs s'il n'existe pas
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Configuration des niveaux de logs
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.path.join(log_dir, f"valetia-{datetime.now().strftime('%Y-%m-%d')}.log")

# Configuration du format JSON pour les logs
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['level'] = record.levelname
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['module'] = record.module
        log_record['function'] = record.funcName

# Configuration du handler pour les fichiers
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(module)s %(function)s %(message)s'))

# Configuration du handler pour la console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))

# Configuration de structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.render_to_log_kwargs,
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Fonction pour obtenir un logger configuré
def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return structlog.wrap_logger(logger)
