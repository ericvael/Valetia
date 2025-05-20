"""
Test simple pour vérifier que les imports fonctionnent correctement.
"""
import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au chemin Python pour permettre les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_basic_imports():
    """Teste que les imports de base fonctionnent."""
    try:
        import valetia
        print(f"Valetia version: {valetia.__version__}")
        
        from valetia.config import settings
        print(f"Root directory: {settings.ROOT_DIR}")
        
        from valetia.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Logger fonctionne correctement!")
        
        print("Tous les imports de base fonctionnent correctement!")
        return True
    except Exception as e:
        print(f"Erreur lors de l'import: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_imports()
    sys.exit(0 if success else 1)
