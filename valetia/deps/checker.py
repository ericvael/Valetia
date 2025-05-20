"""
Module de vérification des dépendances.
Permet de surveiller les versions des packages installés et d'alerter
sur les mises à jour de sécurité.
"""

import pkg_resources
import requests
import json
import os
from datetime import datetime
import subprocess
from pathlib import Path
import sys

# Importer le logger
from valetia.logger import loguru_logger as logger

# Chemin pour stocker les informations sur les dépendances
DEPS_DIR = Path("data/deps")
DEPS_DIR.mkdir(parents=True, exist_ok=True)
DEPS_FILE = DEPS_DIR / "dependencies.json"
SAFETY_DB_FILE = DEPS_DIR / "safety_db.json"

def get_installed_packages():
    """
    Récupère la liste des packages installés avec leur version.
    
    Returns:
        dict: Dictionnaire {nom_package: version}
    """
    packages = {}
    for package in pkg_resources.working_set:
        packages[package.key] = package.version
    
    logger.info(f"Récupération de {len(packages)} packages installés")
    return packages

def save_dependencies_info(packages):
    """
    Sauvegarde les informations sur les dépendances dans un fichier JSON.
    
    Args:
        packages (dict): Dictionnaire {nom_package: version}
    """
    data = {
        "timestamp": datetime.now().isoformat(),
        "packages": packages
    }
    
    with open(DEPS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Informations sur les dépendances sauvegardées dans {DEPS_FILE}")

def check_for_updates():
    """
    Vérifie les mises à jour disponibles pour les packages installés.
    
    Returns:
        list: Liste des packages avec des mises à jour disponibles
    """
    if not DEPS_FILE.exists():
        logger.warning("Fichier de dépendances non trouvé. Exécutez d'abord scan_dependencies().")
        return []
    
    with open(DEPS_FILE, 'r') as f:
        data = json.load(f)
    
    packages = data["packages"]
    updates = []
    
    for package_name, current_version in packages.items():
        try:
            # Utiliser pip pour vérifier la dernière version
            result = subprocess.run(
                [sys.executable, "-m", "pip", "index", "versions", package_name],
                capture_output=True,
                text=True
            )
            
            output = result.stdout
            if "Available versions:" in output:
                available_versions = output.split("Available versions:")[1].strip().split("\n")[0]
                latest_version = available_versions.split(",")[0].strip()
                
                if latest_version != current_version:
                    updates.append({
                        "name": package_name,
                        "current_version": current_version,
                        "latest_version": latest_version
                    })
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la mise à jour pour {package_name}: {str(e)}")
    
    logger.info(f"Vérification terminée: {len(updates)} mises à jour disponibles")
    return updates

def check_security_vulnerabilities():
    """
    Vérifie les vulnérabilités de sécurité connues pour les packages installés.
    
    Returns:
        list: Liste des packages avec des vulnérabilités
    """
    if not DEPS_FILE.exists():
        logger.warning("Fichier de dépendances non trouvé. Exécutez d'abord scan_dependencies().")
        return []
    
    try:
        # Utiliser safety pour vérifier les vulnérabilités
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "safety"],
            capture_output=True,
            text=True
        )
        
        result = subprocess.run(
            ["safety", "check", "--json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Erreur lors de la vérification des vulnérabilités: {result.stderr}")
            return []
        
        vulnerabilities = json.loads(result.stdout)
        
        # Sauvegarder les résultats
        with open(SAFETY_DB_FILE, 'w') as f:
            json.dump(vulnerabilities, f, indent=2)
        
        logger.info(f"Vérification de sécurité terminée: {len(vulnerabilities)} vulnérabilités trouvées")
        return vulnerabilities
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des vulnérabilités: {str(e)}")
        return []

def scan_dependencies():
    """
    Analyse complète des dépendances: 
    - Liste les packages installés
    - Sauvegarde les informations
    - Vérifie les mises à jour disponibles
    - Vérifie les vulnérabilités de sécurité
    
    Returns:
        dict: Résultats de l'analyse
    """
    logger.info("Démarrage de l'analyse des dépendances")
    
    packages = get_installed_packages()
    save_dependencies_info(packages)
    
    updates = check_for_updates()
    vulnerabilities = check_security_vulnerabilities()
    
    result = {
        "timestamp": datetime.now().isoformat(),
        "total_packages": len(packages),
        "updates_available": updates,
        "vulnerabilities": vulnerabilities
    }
    
    # Journaliser les résultats
    logger.info(f"Analyse des dépendances terminée: {len(packages)} packages, {len(updates)} mises à jour, {len(vulnerabilities)} vulnérabilités")
    
    # Alerter si des vulnérabilités sont trouvées
    if vulnerabilities:
        logger.warning(f"ALERTE: {len(vulnerabilities)} vulnérabilités de sécurité trouvées!")
        for vuln in vulnerabilities:
            logger.warning(f"Vulnérabilité dans {vuln['package_name']}: {vuln['vulnerability_id']}")
    
    return result

def get_dependency_report():
    """
    Génère un rapport sur l'état des dépendances.
    
    Returns:
        str: Rapport formaté
    """
    if not DEPS_FILE.exists():
        return "Aucune information sur les dépendances disponible. Exécutez d'abord scan_dependencies()."
    
    with open(DEPS_FILE, 'r') as f:
        data = json.load(f)
    
    packages = data["packages"]
    timestamp = data["timestamp"]
    
    updates = check_for_updates()
    
    # Lecture des vulnérabilités si disponibles
    vulnerabilities = []
    if SAFETY_DB_FILE.exists():
        with open(SAFETY_DB_FILE, 'r') as f:
            vulnerabilities = json.load(f)
    
    # Générer le rapport
    report = [
        "=== RAPPORT SUR LES DÉPENDANCES ===",
        f"Date de l'analyse: {timestamp}",
        f"Nombre total de packages: {len(packages)}",
        "",
        "--- MISES À JOUR DISPONIBLES ---",
    ]
    
    if updates:
        for update in updates:
            report.append(f"{update['name']}: {update['current_version']} -> {update['latest_version']}")
    else:
        report.append("Aucune mise à jour disponible.")
    
    report.append("")
    report.append("--- VULNÉRABILITÉS DE SÉCURITÉ ---")
    
    if vulnerabilities:
        for vuln in vulnerabilities:
            report.append(f"{vuln['package_name']} ({vuln['installed_version']}): {vuln['vulnerability_id']}")
            report.append(f"  Description: {vuln['description']}")
            report.append("")
    else:
        report.append("Aucune vulnérabilité détectée.")
    
    return "\n".join(report)

if __name__ == "__main__":
    # Exécuter l'analyse si le script est lancé directement
    scan_dependencies()
    print(get_dependency_report())
