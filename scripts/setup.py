#!/usr/bin/env python3
"""
Script d'installation et de configuration de Valetia.
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.absolute()

def print_status(message, status="INFO"):
    """Affiche un message avec un statut coloré."""
    colors = {
        "INFO": "\033[94m",  # Bleu
        "SUCCESS": "\033[92m",  # Vert
        "WARNING": "\033[93m",  # Jaune
        "ERROR": "\033[91m",  # Rouge
        "RESET": "\033[0m"  # Reset
    }
    print(f"{colors[status]}[{status}]{colors['RESET']} {message}")

def get_python_info():
    """Récupère les informations sur la version de Python."""
    python_version = sys.version_info
    print_status(f"Version de Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
    print_status(f"Implémentation: {platform.python_implementation()}")
    print_status(f"Architecture système: {platform.machine()}")
    return python_version

def check_dependencies():
    """Vérifie si les dépendances système sont installées."""
    print_status("Vérification des dépendances système...")
    
    # Vérification de Python
    python_version = get_python_info()
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print_status("Erreur: Python 3.8+ est requis.", "ERROR")
        sys.exit(1)
    
    # Vérification de Git
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        print_status("Git est installé.", "SUCCESS")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_status("Avertissement: Git n'est pas installé ou n'est pas dans le PATH.", "WARNING")
    
    # Vérification de pip
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True, text=True)
        print_status(f"pip est installé: {result.stdout.strip()}", "SUCCESS")
    except subprocess.CalledProcessError:
        print_status("Erreur: pip n'est pas installé correctement.", "ERROR")
        sys.exit(1)
    
    print_status("Vérification des dépendances terminée.", "SUCCESS")
    return python_version

def create_directories():
    """Crée les répertoires nécessaires s'ils n'existent pas."""
    print_status("Création des répertoires...")
    
    dirs = [
        os.path.join(ROOT_DIR, "data/raw"),
        os.path.join(ROOT_DIR, "data/processed"),
        os.path.join(ROOT_DIR, "data/embeddings"),
        os.path.join(ROOT_DIR, "models"),
        os.path.join(ROOT_DIR, "logs"),
    ]
    
    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print_status(f"Répertoire créé: {directory}", "SUCCESS")
        else:
            print_status(f"Répertoire existe déjà: {directory}", "INFO")
    
    print_status("Structure de répertoires créée.", "SUCCESS")

def generate_requirements(python_version):
    """Génère le fichier requirements.txt adapté à la version de Python."""
    print_status("Génération du fichier requirements.txt adapté...")
    
    # Base requirements
    requirements = [
        "# Frameworks et base",
        "fastapi",
        "uvicorn",
        "pydantic",
        "",
        "# Traitement de données",
        "pandas",
        "numpy",
        "",
        "# Traitement du langage naturel",
        "spacy",
        "nltk",
        "",
        "# Gestion des fichiers",
        "python-multipart",
        "pypdf2",
        "python-docx",
        "openpyxl",
        "",
        "# Interface utilisateur",
        "streamlit",
        "",
        "# Base de données vectorielle",
        "chromadb",
        "",
        "# Logging et monitoring",
        "loguru",
        "",
        "# Tests",
        "pytest",
        "pytest-cov",
        "",
        "# Outils de développement",
        "black",
        "isort",
        "flake8",
    ]
    
    # Add PyTorch with appropriate version for the system
    requirements.append("")
    requirements.append("# IA et optimisation")
    
    if python_version.minor >= 10:
        # Pour Python 3.10+
        requirements.append("torch")  # Latest compatible version
        requirements.append("transformers")
        requirements.append("onnx")
        requirements.append("onnxruntime")
    else:
        # Pour Python 3.8 et 3.9
        requirements.append("torch<=2.0.1")  # Version compatible avec Python 3.8-3.9
        requirements.append("transformers<=4.30.0")
        requirements.append("onnx<=1.14.0")
        requirements.append("onnxruntime<=1.15.1")
    
    # Écriture du fichier
    with open(os.path.join(ROOT_DIR, "requirements.txt"), "w") as f:
        f.write("\n".join(requirements))
    
    print_status("Fichier requirements.txt généré.", "SUCCESS")

def install_python_dependencies():
    """Installe les dépendances Python."""
    print_status("Installation des dépendances Python...")
    
    requirements_file = os.path.join(ROOT_DIR, "requirements.txt")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", requirements_file],
            check=True
        )
        print_status("Dépendances Python installées avec succès.", "SUCCESS")
    except subprocess.CalledProcessError:
        print_status("Erreur lors de l'installation des dépendances Python.", "ERROR")
        print_status("Essai d'installation par groupes...", "INFO")
        
        # Essai d'installation par groupes
        with open(requirements_file, "r") as f:
            lines = f.readlines()
        
        current_group = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                if current_group:
                    try:
                        subprocess.run(
                            [sys.executable, "-m", "pip", "install"] + current_group,
                            check=True
                        )
                        print_status(f"Groupe installé: {', '.join(current_group)}", "SUCCESS")
                    except subprocess.CalledProcessError:
                        print_status(f"Échec d'installation du groupe: {', '.join(current_group)}", "ERROR")
                    current_group = []
            else:
                current_group.append(line)
        
        if current_group:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install"] + current_group,
                    check=True
                )
                print_status(f"Groupe installé: {', '.join(current_group)}", "SUCCESS")
            except subprocess.CalledProcessError:
                print_status(f"Échec d'installation du groupe: {', '.join(current_group)}", "ERROR")

def setup_spacy():
    """Télécharge les modèles spaCy nécessaires."""
    print_status("Configuration de spaCy...")
    
    try:
        # Vérifier si spaCy est installé
        subprocess.run(
            [sys.executable, "-c", "import spacy"],
            check=True, stderr=subprocess.DEVNULL
        )
        
        # Télécharger le modèle français
        try:
            subprocess.run(
                [sys.executable, "-m", "spacy", "download", "fr_core_news_md"],
                check=True
            )
            print_status("Modèle spaCy fr_core_news_md installé avec succès.", "SUCCESS")
        except subprocess.CalledProcessError:
            print_status("Tentative d'installation d'un modèle plus petit...", "WARNING")
            try:
                subprocess.run(
                    [sys.executable, "-m", "spacy", "download", "fr_core_news_sm"],
                    check=True
                )
                print_status("Modèle spaCy fr_core_news_sm installé avec succès.", "SUCCESS")
            except subprocess.CalledProcessError:
                print_status("Erreur lors de l'installation des modèles spaCy.", "ERROR")
    except subprocess.CalledProcessError:
        print_status("spaCy n'est pas installé correctement.", "ERROR")

def create_config_files():
    """Crée les fichiers de configuration de base."""
    print_status("Création des fichiers de configuration...")
    
    # Fichier __init__.py principal
    init_file = os.path.join(ROOT_DIR, "valetia", "__init__.py")
    with open(init_file, "w") as f:
        f.write('"""Valetia - IA Juridique Locale"""\n\n__version__ = "0.1.0"\n')
    print_status(f"Fichier créé: {init_file}", "SUCCESS")
    
    # Autres fichiers __init__.py
    for dir_path in [
        "valetia/core",
        "valetia/modules",
        "valetia/modules/commun",
        "valetia/modules/copropriete",
        "valetia/modules/prudhommes",
        "valetia/ui",
        "valetia/utils",
        "valetia/config",
        "valetia/tests"
    ]:
        init_file = os.path.join(ROOT_DIR, dir_path, "__init__.py")
        os.makedirs(os.path.dirname(init_file), exist_ok=True)
        with open(init_file, "w") as f:
            f.write(f'"""Module {dir_path.replace("/", ".")}"""\n')
        print_status(f"Fichier créé: {init_file}", "SUCCESS")
    
    # Fichier de configuration principal
    config_file = os.path.join(ROOT_DIR, "valetia", "config", "settings.py")
    with open(config_file, "w") as f:
        f.write('''"""
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
''')
    print_status(f"Fichier créé: {config_file}", "SUCCESS")
    
    # Fichier logger
    logger_file = os.path.join(ROOT_DIR, "valetia", "utils", "logger.py")
    with open(logger_file, "w") as f:
        f.write('''"""
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
''')
    print_status(f"Fichier créé: {logger_file}", "SUCCESS")
    
    print_status("Fichiers de configuration créés.", "SUCCESS")

def main():
    """Fonction principale d'installation."""
    print_status("=== Installation de Valetia ===", "INFO")
    
    python_version = check_dependencies()
    create_directories()
    generate_requirements(python_version)
    install_python_dependencies()
    setup_spacy()
    create_config_files()
    
    print_status("\n=== Installation terminée avec succès! ===", "SUCCESS")
    print_status("Vous pouvez maintenant utiliser Valetia.", "INFO")
    print_status("Pour commencer, activez l'environnement virtuel:", "INFO")
    print_status("    source venv/bin/activate", "INFO")
    print_status("Puis importez le module valetia dans vos scripts:", "INFO")
    print_status("    import valetia", "INFO")
    print_status("\nBon développement!", "SUCCESS")

if __name__ == "__main__":
    main()
