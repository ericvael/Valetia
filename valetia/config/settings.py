"""
Configuration principale de Valetia.
"""
import os
from pathlib import Path

# Chemins principaux
ROOT_DIR = Path(__file__).parent.parent.parent.absolute()
DATA_DIR = os.path.join(ROOT_DIR, "data")
MODELS_DIR = os.path.join(ROOT_DIR, "models")
LOGS_DIR = os.path.join(ROOT_DIR, "logs")

# Configuration des logs
LOG_LEVEL = "INFO"
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"

# Configuration des modèles
DEFAULT_MODEL = "mistral-7b-instruct-v0.2.Q4_K_M"
MODEL_MAX_TOKENS = 4096
MODEL_TEMPERATURE = 0.1

# Configuration API
API_TIMEOUT = 30
API_RATE_LIMIT = 5  # requêtes par minute

# Configuration base de données vectorielle
VECTOR_DB_PATH = os.path.join(DATA_DIR, "embeddings")
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
