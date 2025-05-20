#!/bin/bash

# Script pour lancer l'application Valetia

# Définir le répertoire du projet
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$PROJECT_DIR"

# Définir les couleurs pour l'affichage
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Afficher un message de bienvenue
echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}Démarrage de Valetia - IA Juridique Locale${NC}"
echo -e "${BLUE}======================================${NC}"

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
  echo -e "${RED}Erreur: L'environnement virtuel 'venv' n'existe pas.${NC}"
  echo -e "${YELLOW}Exécutez d'abord: python -m venv venv${NC}"
  exit 1
fi

# Activer l'environnement virtuel
echo -e "${BLUE}Activation de l'environnement virtuel...${NC}"
source venv/bin/activate

# Vérifier si l'installation en mode développement a été effectuée
if ! pip show valetia &>/dev/null; then
  echo -e "${YELLOW}Le package valetia n'est pas installé. Installation en cours...${NC}"
  pip install -e .
fi

# Vérifier si streamlit est installé
python -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
  echo -e "${YELLOW}Streamlit n'est pas installé. Installation en cours...${NC}"
  pip install streamlit
fi

# Créer le répertoire de données si nécessaire
mkdir -p data/raw/test
mkdir -p data/temp

# Lancer l'application
echo -e "${GREEN}Lancement de l'application...${NC}"
echo -e "${YELLOW}L'interface sera accessible à l'adresse: http://localhost:8501${NC}"
python -m streamlit run valetia/ui/app.py
