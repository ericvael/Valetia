"""
Module de conversation intelligente pour Valetia.
Utilise transformers pour la compréhension et génération de texte.
"""

import os
import random
from pathlib import Path
import time
from typing import Dict, List, Optional, Tuple, Union

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, AutoModelForSeq2SeqLM
import chromadb
from chromadb.config import Settings

from valetia.utils.logger import get_logger
from valetia.modules.learning.feedback import feedback_manager
from valetia.modules.chatbot.legal_prompts import (
    get_legal_prompt,
    get_vulgarization_prompt,
    LEGAL_PREFIXES,
    LEGAL_DISCLAIMERS,
    COMMON_LEGAL_REFERENCES
)

logger = get_logger(__name__)

class ConversationManager:
    """Gère les conversations avec l'utilisateur."""
    
    def __init__(self, model_name: str = "facebook/blenderbot-400M-distill"):
        """
        Initialise le gestionnaire de conversation.
        
        Args:
            model_name: Nom du modèle à charger. Par défaut "facebook/blenderbot-400M-distill".
                        Pour un modèle plus léger, utiliser "distilgpt2".
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initialisation du ConversationManager avec le modèle {model_name} sur {self.device}")
        
        # Chargement du modèle et du tokenizer
        try:
            # Différentes approches selon le modèle utilisé
            if "blenderbot" in model_name:
                # BlenderBot est un modèle seq2seq
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
                self.model.to(self.device)
                logger.info(f"Modèle {model_name} (seq2seq) chargé avec succès")
                self.model_type = "seq2seq"
            else:
                # GPT-2 est un modèle causal LM
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForCausalLM.from_pretrained(model_name)
                self.model.to(self.device)
                logger.info(f"Modèle {model_name} (causal LM) chargé avec succès")
                self.model_type = "causal_lm"
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle {model_name}: {e}")
            # Fallback sur un modèle plus léger en cas d'erreur
            self.model_name = "distilgpt2"
            self.tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
            self.model = AutoModelForCausalLM.from_pretrained("distilgpt2")
            self.model.to(self.device)
            self.model_type = "causal_lm"
            logger.info("Fallback sur le modèle distilgpt2")
        
        # Initialisation de la base de données vectorielle pour stocker l'historique
        self.db_path = Path("data/conversations")
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        self.db = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(allow_reset=True)
        )
        
        # Création de la collection pour stocker les conversations
        try:
            self.collection = self.db.get_or_create_collection(name="conversations")
            logger.info("Collection ChromaDB 'conversations' initialisée")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de ChromaDB: {e}")
    
    def get_response(self, 
                     user_input: str, 
                     conversation_id: str, 
                     context: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Génère une réponse à partir de l'entrée utilisateur.
        
        Args:
            user_input: Texte envoyé par l'utilisateur
            conversation_id: Identifiant unique de la conversation
            context: Contexte optionnel (métadonnées sur le dossier)
            
        Returns:
            Réponse générée
        """
        # Récupérer l'historique de la conversation
        history = self._get_conversation_history(conversation_id)
        
        # Ajout du contexte à la question si fourni
        if context:
            context_str = "Contexte: "
            for ctx in context:
                for key, value in ctx.items():
                    context_str += f"{key}: {value}. "
            enhanced_input = f"{context_str}\n\nQuestion: {user_input}"
        else:
            enhanced_input = user_input
        
        # Appliquer le template juridique à la question
        legal_input = get_legal_prompt(enhanced_input)
        
        # Génération de la réponse selon le type de modèle
        try:
            if self.model_type == "seq2seq":
                # Pour les modèles de type seq2seq (comme BlenderBot)
                inputs = self.tokenizer([legal_input], return_tensors="pt").to(self.device)
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=150,
                    num_return_sequences=1,
                    temperature=0.7,
                    top_k=50,
                    top_p=0.95,
                    do_sample=True
                )
                
                response = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            else:
                # Pour les modèles de type causal LM (comme GPT-2)
                
                # Construction du prompt avec l'historique
                prompt = self._build_prompt(legal_input, history)
                
                inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=150,
                    num_return_sequences=1,
                    temperature=0.7,
                    top_k=50,
                    top_p=0.95,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                
                full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Extraire seulement la réponse sans répéter le prompt
                response = full_response[len(prompt):].strip()
            
            # Fallback si la réponse est vide
            if not response:
                response = "Je ne suis pas sûr de comprendre votre question juridique. Pourriez-vous la reformuler ou préciser le domaine du droit concerné (copropriété, prud'hommes, succession)?"
                
            # Post-traitement de la réponse pour la rendre plus juridique en français
            response = self._enhance_legal_response(response, user_input)
                
        except Exception as e:
            logger.error(f"Erreur lors de la génération de la réponse: {e}")
            response = "Désolé, j'ai rencontré un problème technique lors de l'analyse de votre question juridique. Veuillez réessayer en reformulant."
        
        # Enregistrer l'échange dans l'historique
        self._save_conversation(conversation_id, user_input, response, context)
        
        return response
    
    def _enhance_legal_response(self, response: str, question: str) -> str:
        """
        Améliore la réponse pour la rendre plus juridique et française.
        
        Args:
            response: La réponse brute du modèle
            question: La question originale
            
        Returns:
            La réponse améliorée
        """
        # Détecter le domaine juridique concerné
        domain = "général"
        if any(keyword in question.lower() for keyword in ["copropriété", "syndic", "assemblee generale", "ag", "lot", "immeuble"]):
            domain = "copropriété"
        elif any(keyword in question.lower() for keyword in ["travail", "licenciement", "contrat", "employeur", "salarié", "prud'homme"]):
            domain = "prud'hommes"
        elif any(keyword in question.lower() for keyword in ["héritage", "succession", "testament", "héritier", "notaire"]):
            domain = "succession"
        
        # Ajouter un préfixe juridique s'il n'y en a pas déjà
        if not any(prefix in response[:30] for prefix in LEGAL_PREFIXES):
            response = random.choice(LEGAL_PREFIXES) + response
        
        # Ajouter une référence juridique si pertinent
        if domain in COMMON_LEGAL_REFERENCES and random.random() < 0.7:  # 70% de chance
            reference = random.choice(COMMON_LEGAL_REFERENCES[domain])
            if "selon" not in response.lower()[:50] and "d'après" not in response.lower()[:50]:
                response += f"\n\nSelon {reference}, cette position est bien établie."
        
        # Ajouter un disclaimer juridique si non présent
        if not any(disclaimer in response.lower() for disclaimer in [d.lower() for d in LEGAL_DISCLAIMERS]):
            response += f"\n\n{random.choice(LEGAL_DISCLAIMERS)}"
        
        return response
    
    def save_feedback(self, 
                     conversation_id: str, 
                     user_input: str, 
                     assistant_response: str,
                     is_helpful: bool, 
                     feedback_text: Optional[str] = None) -> bool:
        """
        Enregistre un feedback utilisateur.
        
        Args:
            conversation_id: Identifiant de la conversation
            user_input: Question de l'utilisateur
            assistant_response: Réponse de l'assistant
            is_helpful: Si la réponse a été jugée utile
            feedback_text: Commentaire textuel optionnel
            
        Returns:
            bool: True si l'enregistrement a réussi, False sinon
        """
        return feedback_manager.save_feedback(
            conversation_id=conversation_id,
            user_input=user_input,
            assistant_response=assistant_response,
            is_helpful=is_helpful,
            feedback_text=feedback_text
        )
    
    def _build_prompt(self, user_input: str, history: List[Dict[str, str]]) -> str:
        """Construit le prompt avec l'historique de la conversation."""
        prompt = ""
        
        # Inclure l'historique récent dans le prompt (limité aux 5 derniers échanges)
        for exchange in history[-5:]:
            prompt += f"Utilisateur: {exchange['user']}\nAssistant: {exchange['assistant']}\n"
        
        # Ajouter la question actuelle
        prompt += f"Utilisateur: {user_input}\nAssistant:"
        
        return prompt
    
    def _get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """Récupère l'historique de la conversation depuis ChromaDB."""
        try:
            results = self.collection.get(
                where={"conversation_id": conversation_id},
                limit=10  # Limiter aux 10 derniers échanges
            )
            
            if not results or not results['metadatas']:
                return []
            
            # Trier par timestamp
            exchanges = [(metadata, metadata.get('timestamp', 0)) 
                        for metadata in results['metadatas']]
            exchanges.sort(key=lambda x: x[1])
            
            history = []
            for exchange, _ in exchanges:
                if 'user_input' in exchange and 'assistant_response' in exchange:
                    history.append({
                        'user': exchange['user_input'],
                        'assistant': exchange['assistant_response']
                    })
            
            return history
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'historique: {e}")
            return []
    
    def _save_conversation(self, 
                          conversation_id: str, 
                          user_input: str, 
                          assistant_response: str,
                          context: Optional[List[Dict[str, str]]] = None) -> None:
        """Enregistre l'échange dans ChromaDB."""
        try:
            timestamp = int(time.time())
            exchange_id = f"{conversation_id}_{timestamp}"
            
            metadata = {
                "conversation_id": conversation_id,
                "user_input": user_input,
                "assistant_response": assistant_response,
                "timestamp": timestamp
            }
            
            # Ajouter le contexte aux métadonnées s'il est fourni
            if context:
                for i, ctx in enumerate(context):
                    for key, value in ctx.items():
                        metadata[f"context_{i}_{key}"] = str(value)
            
            # Créer un embeddings (simplifiée pour l'instant)
            # TODO: Utiliser un modèle d'embeddings plus sophistiqué
            combined_text = f"{user_input} {assistant_response}"
            
            self.collection.add(
                ids=[exchange_id],
                documents=[combined_text],
                metadatas=[metadata]
            )
            
            logger.info(f"Conversation {conversation_id} mise à jour")
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de la conversation: {e}")


# Exemple d'utilisation:
if __name__ == "__main__":
    # Test simple
    conversation_manager = ConversationManager()
    response = conversation_manager.get_response(
        "Quelle est la procédure à suivre pour contester une décision d'assemblée générale de copropriété?",
        "test_conversation_123"
    )
    print(f"Réponse: {response}")
