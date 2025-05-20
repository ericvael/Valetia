"""
Module pour la gestion des feedbacks utilisateur.
Permet d'enregistrer et d'analyser les feedbacks pour améliorer les réponses.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

from valetia.utils.logger import get_logger

logger = get_logger(__name__)

class FeedbackManager:
    """Gère les feedbacks des utilisateurs sur les réponses du chatbot."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialise le gestionnaire de feedback.
        
        Args:
            storage_path: Chemin vers le répertoire de stockage des feedbacks
        """
        if storage_path is None:
            storage_path = "data/feedbacks"
        
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"FeedbackManager initialisé avec stockage dans {self.storage_path}")
    
    def save_feedback(self, 
                     conversation_id: str, 
                     user_input: str, 
                     assistant_response: str,
                     is_helpful: bool, 
                     feedback_text: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Enregistre un feedback utilisateur.
        
        Args:
            conversation_id: Identifiant de la conversation
            user_input: Question de l'utilisateur
            assistant_response: Réponse de l'assistant
            is_helpful: Si la réponse a été jugée utile
            feedback_text: Commentaire textuel optionnel
            metadata: Métadonnées supplémentaires
            
        Returns:
            bool: True si l'enregistrement a réussi, False sinon
        """
        try:
            # Créer un identifiant unique pour ce feedback
            timestamp = int(time.time())
            feedback_id = f"{conversation_id}_{timestamp}"
            
            # Préparer les données à enregistrer
            feedback_data = {
                "feedback_id": feedback_id,
                "conversation_id": conversation_id,
                "timestamp": timestamp,
                "user_input": user_input,
                "assistant_response": assistant_response,
                "is_helpful": is_helpful,
                "feedback_text": feedback_text
            }
            
            # Ajouter les métadonnées si présentes
            if metadata:
                feedback_data["metadata"] = metadata
            
            # Enregistrer dans un fichier JSON
            feedback_file = self.storage_path / f"{feedback_id}.json"
            with open(feedback_file, "w", encoding="utf-8") as f:
                json.dump(feedback_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Feedback enregistré avec succès: {feedback_id}")
            return True
        
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du feedback: {e}")
            return False
    
    def get_feedbacks(self, 
                     conversation_id: Optional[str] = None, 
                     limit: int = 100) -> List[Dict[str, Any]]:
        """
        Récupère les feedbacks enregistrés.
        
        Args:
            conversation_id: Filtrer par ID de conversation (optionnel)
            limit: Nombre maximum de feedbacks à récupérer
            
        Returns:
            Liste des feedbacks
        """
        try:
            feedbacks = []
            
            # Récupérer tous les fichiers JSON dans le répertoire
            json_files = list(self.storage_path.glob("*.json"))
            
            # Filtrer par conversation_id si spécifié
            for file_path in json_files[:limit]:
                with open(file_path, "r", encoding="utf-8") as f:
                    feedback_data = json.load(f)
                    
                    # Filtrer par conversation_id si spécifié
                    if conversation_id is None or feedback_data.get("conversation_id") == conversation_id:
                        feedbacks.append(feedback_data)
            
            # Trier par timestamp (du plus récent au plus ancien)
            feedbacks.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
            
            return feedbacks[:limit]
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des feedbacks: {e}")
            return []
    
    def get_stats(self, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calcule des statistiques sur les feedbacks.
        
        Args:
            conversation_id: Filtrer par ID de conversation (optionnel)
            
        Returns:
            Statistiques (taux de satisfaction, nombre de feedbacks, etc.)
        """
        feedbacks = self.get_feedbacks(conversation_id=conversation_id, limit=1000)
        
        if not feedbacks:
            return {
                "total_count": 0,
                "helpful_count": 0,
                "unhelpful_count": 0,
                "satisfaction_rate": 0
            }
        
        total_count = len(feedbacks)
        helpful_count = sum(1 for f in feedbacks if f.get("is_helpful", False))
        unhelpful_count = total_count - helpful_count
        
        satisfaction_rate = (helpful_count / total_count) * 100 if total_count > 0 else 0
        
        return {
            "total_count": total_count,
            "helpful_count": helpful_count,
            "unhelpful_count": unhelpful_count,
            "satisfaction_rate": satisfaction_rate
        }

# Instance unique pour l'utilisation dans l'application
feedback_manager = FeedbackManager()
