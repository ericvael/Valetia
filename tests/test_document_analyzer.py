"""
Test de la classe DocumentAnalyzer
"""
import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au chemin Python pour permettre les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from valetia.core.document_analyzer import DocumentAnalyzer

def create_test_document():
    """Crée un document de test."""
    test_dir = Path("data/raw/test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    test_file = test_dir / "test_document.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("""
        Ceci est un document de test pour Valetia.
        
        Dans ce document, nous allons tester l'analyse de texte juridique.
        
        Les parties concernées sont Jean Dupont et Marie Martin, associés de la SCI Horizon.
        
        La date du contrat est le 15 avril 2024.
        
        Le montant du loyer est de 1200 euros par mois.
        
        Le contrat prend fin le 31 décembre 2025.
        """)
    
    return test_file

def test_document_analyzer():
    """Teste les fonctionnalités de base de DocumentAnalyzer."""
    # Créer un document de test
    test_file = create_test_document()
    
    # Initialiser l'analyseur
    analyzer = DocumentAnalyzer()
    
    # Charger le document
    success = analyzer.load_document(test_file)
    print(f"Chargement du document: {'Succès' if success else 'Échec'}")
    
    if success:
        # Obtenir les informations sur le document
        doc_info = analyzer.get_document_info(index=0)
        print(f"\nInformations sur le document:")
        print(f"Nom: {doc_info['name']}")
        print(f"Extension: {doc_info['extension']}")
        print(f"Taille: {doc_info['size']} octets")
        
        # Analyser le document
        analysis = analyzer.analyze_document(0)
        print(f"\nAnalyse du document:")
        print(f"Nombre de mots: {analysis['word_count']}")
        print(f"Nombre de caractères: {analysis['character_count']}")
        
        print("\nEntités détectées:")
        for entity_type, entities in analysis['entities'].items():
            print(f"  {entity_type}: {', '.join(entities)}")
        
        print("\nMots-clés:")
        for keyword in analysis['keywords'][:5]:  # Afficher les 5 premiers mots-clés
            print(f"  {keyword['word']}: {keyword['count']} occurrences")
        
        print(f"\nRésumé:")
        print(f"  {analysis['summary']}")
    
    return success

if __name__ == "__main__":
    success = test_document_analyzer()
    sys.exit(0 if success else 1)
