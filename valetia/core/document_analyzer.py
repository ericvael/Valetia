"""
Module principal pour l'analyse de documents juridiques.
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from valetia.utils.logger import get_logger

logger = get_logger(__name__)

class DocumentAnalyzer:
    """
    Classe principale pour l'analyse de documents juridiques.
    Fournit des méthodes pour charger, analyser et extraire des informations
    à partir de différents types de documents.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialise l'analyseur de documents.
        
        Args:
            model_name: Nom du modèle à utiliser pour l'analyse (optionnel)
        """
        self.documents = []
        self.model_name = model_name
        logger.info(f"DocumentAnalyzer initialisé avec le modèle: {model_name}")
    
    def load_document(self, file_path: Union[str, Path]) -> bool:
        """
        Charge un document depuis un chemin de fichier.
        
        Args:
            file_path: Chemin vers le fichier à charger
            
        Returns:
            bool: True si le chargement a réussi, False sinon
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"Le fichier n'existe pas: {file_path}")
            return False
        
        try:
            # Déterminer le type de document en fonction de l'extension
            extension = file_path.suffix.lower()
            
            document_info = {
                "path": str(file_path),
                "name": file_path.name,
                "extension": extension,
                "size": file_path.stat().st_size,
                "content": None,
                "metadata": {}
            }
            
            # Charger le contenu en fonction du type de fichier
            if extension == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    document_info["content"] = f.read()
                logger.info(f"Document texte chargé: {file_path.name}")
            
            elif extension == ".pdf":
                try:
                    import pypdf2
                    reader = pypdf2.PdfReader(file_path)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    document_info["content"] = text
                    document_info["metadata"]["page_count"] = len(reader.pages)
                    logger.info(f"Document PDF chargé: {file_path.name} ({len(reader.pages)} pages)")
                except ImportError:
                    logger.error("Module pypdf2 non disponible pour charger le PDF")
                    return False
            
            elif extension in [".docx", ".doc"]:
                try:
                    import docx
                    doc = docx.Document(file_path)
                    text = "\n".join([para.text for para in doc.paragraphs])
                    document_info["content"] = text
                    logger.info(f"Document Word chargé: {file_path.name}")
                except ImportError:
                    logger.error("Module python-docx non disponible pour charger le document Word")
                    return False
            
            elif extension in [".xlsx", ".xls"]:
                try:
                    import pandas as pd
                    df = pd.read_excel(file_path)
                    document_info["content"] = df.to_string()
                    document_info["dataframe"] = df
                    logger.info(f"Document Excel chargé: {file_path.name}")
                except ImportError:
                    logger.error("Module pandas ou openpyxl non disponible pour charger le fichier Excel")
                    return False
            
            elif extension == ".eml":
                try:
                    import email
                    with open(file_path, "r", encoding="utf-8") as f:
                        msg = email.message_from_string(f.read())
                    
                    document_info["metadata"]["from"] = msg.get("From", "")
                    document_info["metadata"]["to"] = msg.get("To", "")
                    document_info["metadata"]["subject"] = msg.get("Subject", "")
                    document_info["metadata"]["date"] = msg.get("Date", "")
                    
                    if msg.is_multipart():
                        content = ""
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                content += part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    else:
                        content = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                    
                    document_info["content"] = content
                    logger.info(f"Email chargé: {file_path.name}")
                
                except Exception as e:
                    logger.error(f"Erreur lors du chargement de l'email: {e}")
                    return False
            
            else:
                logger.warning(f"Type de document non pris en charge: {extension}")
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    try:
                        document_info["content"] = f.read()
                        logger.info(f"Document chargé comme texte brut: {file_path.name}")
                    except Exception as e:
                        logger.error(f"Impossible de lire le fichier comme texte: {e}")
                        return False
            
            self.documents.append(document_info)
            return True
        
        except Exception as e:
            logger.error(f"Erreur lors du chargement du document: {e}")
            return False
    
    def load_directory(self, directory_path: Union[str, Path], extensions: Optional[List[str]] = None) -> Dict[str, int]:
        """
        Charge tous les documents d'un répertoire.
        
        Args:
            directory_path: Chemin vers le répertoire à charger
            extensions: Liste des extensions de fichiers à charger (optionnel)
            
        Returns:
            Dict[str, int]: Statistiques sur les fichiers chargés
        """
        directory_path = Path(directory_path)
        if not directory_path.exists() or not directory_path.is_dir():
            logger.error(f"Le répertoire n'existe pas: {directory_path}")
            return {"total": 0, "success": 0, "error": 0}
        
        stats = {"total": 0, "success": 0, "error": 0}
        
        for file_path in directory_path.glob("**/*"):
            if file_path.is_file():
                if extensions and file_path.suffix.lower() not in extensions:
                    continue
                
                stats["total"] += 1
                if self.load_document(file_path):
                    stats["success"] += 1
                else:
                    stats["error"] += 1
        
        logger.info(f"Chargement du répertoire terminé: {stats['success']}/{stats['total']} fichiers chargés")
        return stats
    
    def get_document_info(self, index: int = None, name: str = None) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations sur un document spécifique.
        
        Args:
            index: Indice du document dans la liste (optionnel)
            name: Nom du document à rechercher (optionnel)
            
        Returns:
            Optional[Dict[str, Any]]: Informations sur le document ou None si non trouvé
        """
        if index is not None and 0 <= index < len(self.documents):
            return self.documents[index]
        
        if name is not None:
            for doc in self.documents:
                if doc["name"] == name:
                    return doc
        
        return None
    
    def analyze_document(self, document_index: int) -> Dict[str, Any]:
        """
        Analyse un document et extrait des informations pertinentes.
        
        Args:
            document_index: Indice du document à analyser
            
        Returns:
            Dict[str, Any]: Résultats de l'analyse
        """
        if document_index < 0 or document_index >= len(self.documents):
            logger.error(f"Indice de document invalide: {document_index}")
            return {"error": "Document non trouvé"}
        
        document = self.documents[document_index]
        content = document["content"]
        
        if not content:
            logger.warning(f"Le document {document['name']} ne contient pas de texte à analyser")
            return {"error": "Document sans contenu"}
        
        result = {
            "document_name": document["name"],
            "word_count": len(content.split()),
            "character_count": len(content),
            "entities": [],
            "keywords": [],
            "summary": "",
        }
        
        # Analyse NLP basique
        try:
            import spacy
            try:
                nlp = spacy.load("fr_core_news_md")
            except:
                try:
                    nlp = spacy.load("fr_core_news_sm")
                except:
                    logger.error("Aucun modèle spaCy français n'est disponible")
                    return result
            
            # Limiter la taille du texte pour éviter les erreurs de mémoire
            max_chars = 100000  # 100K caractères max
            if len(content) > max_chars:
                logger.warning(f"Texte tronqué de {len(content)} à {max_chars} caractères")
                content = content[:max_chars]
            
            doc = nlp(content)
            
            # Extraire les entités nommées
            entities = {}
            for ent in doc.ents:
                if ent.label_ not in entities:
                    entities[ent.label_] = []
                if ent.text not in entities[ent.label_]:
                    entities[ent.label_].append(ent.text)
            
            result["entities"] = entities
            
            # Extraire les mots-clés (tokens importants sans les stopwords)
            keywords = []
            for token in doc:
                if not token.is_stop and not token.is_punct and token.is_alpha and len(token.text) > 3:
                    keywords.append(token.text)
            
            from collections import Counter
            keyword_counts = Counter(keywords)
            result["keywords"] = [{"word": word, "count": count} for word, count in keyword_counts.most_common(20)]
            
            # Créer un résumé basique (premières et dernières phrases)
            sentences = list(doc.sents)
            if len(sentences) > 6:
                summary = " ".join([sent.text for sent in list(sentences)[:3] + list(sentences)[-3:]])
            else:
                summary = " ".join([sent.text for sent in sentences])
            
            result["summary"] = summary
            
            logger.info(f"Analyse NLP terminée pour le document: {document['name']}")
        
        except ImportError:
            logger.error("Module spaCy non disponible pour l'analyse NLP")
        
        return result
