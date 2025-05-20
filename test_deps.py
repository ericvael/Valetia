"""
Script de test pour la gestion des dépendances.
"""

from valetia.deps import scan_dependencies, get_dependency_report
from valetia.deps import configure_alerts, check_and_alert, get_alerts_summary

print("=== TEST DE LA GESTION DES DÉPENDANCES ===\n")

# Tester la configuration des alertes
print("Configuration des alertes...")
config = configure_alerts(
    enabled=True,
    check_interval=24,
    notify_updates=True,
    notify_vulnerabilities=True
)
print(f"Configuration: {config}\n")

# Scanner les dépendances
print("Analyse des dépendances...")
result = scan_dependencies()
print(f"Résultat: {len(result['updates_available'])} mises à jour, {len(result['vulnerabilities'])} vulnérabilités\n")

# Afficher le rapport
print("=== RAPPORT DE DÉPENDANCES ===")
report = get_dependency_report()
print(report)
print()

# Tester les alertes
print("Vérification des alertes...")
alerts_sent = check_and_alert()
print(f"Alertes envoyées: {alerts_sent}\n")

# Afficher le résumé des alertes
print("=== RÉSUMÉ DES ALERTES ===")
summary = get_alerts_summary()
print(summary)
