"""
Gestionnaire de conversation hybride qui combine différents modèles
et intègre un apprentissage continu.
"""

import os
import random
import time
from pathlib import Path
import json
from typing import Dict, List, Optional, Any, Tuple

import numpy as np
from valetia.utils.logger import get_logger
from valetia.modules.api.claude_client import claude_client
from valetia.modules.learning.feedback import feedback_manager
from valetia.modules.chatbot.legal_prompts import (
    get_legal_prompt,
    LEGAL_PREFIXES,
    LEGAL_DISCLAIMERS
)

logger = get_logger(__name__)

class HybridConversationManager:
    """
    Gestionnaire de conversation hybride qui combine un modèle local
    et l'API Claude pour maximiser l'efficacité et l'apprentissage.
    """
    
    def __init__(self):
        """Initialise le gestionnaire de conversation hybride."""
        # Répertoire pour stocker les données d'apprentissage
        self.learning_dir = Path("data/learning")
        self.learning_dir.mkdir(parents=True, exist_ok=True)
        
        # Fichier pour les exemples d'apprentissage
        self.examples_file = self.learning_dir / "learned_examples.json"
        
        # Charger les exemples d'apprentissage existants
        self.learned_examples = self._load_learned_examples()
        
        # Seuil pour décider quand utiliser Claude
        self.claude_threshold = 0.7  # Probabilité au-dessus de laquelle on utilise Claude
        
        # Compteurs pour les stratégies
        self.local_responses = 0
        self.claude_responses = 0
        
        logger.info("Gestionnaire de conversation hybride initialisé")
        logger.info(f"Nombre d'exemples d'apprentissage chargés: {len(self.learned_examples)}")
    
    def get_response(self, 
                     user_input: str, 
                     conversation_id: str, 
                     context: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Génère une réponse en utilisant la stratégie la plus appropriée.
        
        Args:
            user_input: Texte envoyé par l'utilisateur
            conversation_id: Identifiant unique de la conversation
            context: Contexte optionnel (métadonnées sur le dossier)
            
        Returns:
            Réponse générée
        """
        # Vérifier si une réponse similaire existe déjà dans les exemples appris
        similar_example, similarity = self._find_similar_example(user_input)
        
        # Si un exemple similaire est trouvé avec une bonne confiance, l'utiliser
        if similar_example and similarity > 0.8:
            logger.info(f"Utilisation d'une réponse apprise (similarité: {similarity:.2f})")
            self.local_responses += 1
            return similar_example["response"]
        
        # Décider si on utilise Claude ou une réponse locale
        use_claude = self._should_use_claude(user_input, context, similarity)
        
        if use_claude:
            # Utiliser l'API Claude
            logger.info("Utilisation de l'API Claude pour la réponse")
            self.claude_responses += 1
            response = self._get_claude_response(user_input, context)
            
            # Apprendre de cette réponse pour les futures interactions
            self._learn_from_response(user_input, response)
        else:
            # Utiliser une approche locale
            logger.info("Utilisation d'une réponse locale")
            self.local_responses += 1
            
            if similar_example:
                # Utiliser l'exemple similaire mais l'adapter
                response = self._adapt_similar_response(similar_example["response"], user_input)
            else:
                # Générer une réponse basique
                response = self._generate_basic_response(user_input, context)
        
        # Enregistrer la conversation
        self._save_conversation(conversation_id, user_input, response, context)
        
        # Journaliser les statistiques d'utilisation
        total_responses = self.local_responses + self.claude_responses
        if total_responses % 10 == 0:
            logger.info(f"Statistiques - Local: {self.local_responses}, Claude: {self.claude_responses} "
                       f"(économie: {(self.local_responses / total_responses * 100):.1f}%)")
        
        return response
    
    def save_feedback(self, 
                     conversation_id: str, 
                     user_input: str, 
                     assistant_response: str,
                     is_helpful: bool, 
                     feedback_text: Optional[str] = None) -> bool:
        """
        Enregistre un feedback utilisateur et l'utilise pour l'apprentissage.
        
        Args:
            conversation_id: Identifiant de la conversation
            user_input: Question de l'utilisateur
            assistant_response: Réponse de l'assistant
            is_helpful: Si la réponse a été jugée utile
            feedback_text: Commentaire textuel optionnel
            
        Returns:
            bool: True si l'enregistrement a réussi, False sinon
        """
        # Enregistrer le feedback
        success = feedback_manager.save_feedback(
            conversation_id=conversation_id,
            user_input=user_input,
            assistant_response=assistant_response,
            is_helpful=is_helpful,
            feedback_text=feedback_text
        )
        
        # Si le feedback est positif, apprendre de cette interaction
        if success and is_helpful:
            self._learn_from_response(user_input, assistant_response, is_helpful=True)
        
        return success
    
    def _should_use_claude(self, 
                          user_input: str, 
                          context: Optional[List[Dict[str, str]]], 
                          similarity: float) -> bool:
        """
        Décide si Claude doit être utilisé pour cette requête.
        
        Args:
            user_input: La question de l'utilisateur
            context: Le contexte de la conversation
            similarity: Niveau de similarité avec les exemples connus
            
        Returns:
            bool: True si Claude doit être utilisé
        """
        # Si la question est très courte, éviter d'utiliser Claude
        if len(user_input.split()) < 5:
            return False
        
        # Si la question est très similaire à quelque chose de connu, éviter Claude
        if similarity > 0.7:
            return False
        
        # Si la question est complexe (longue ou contient des termes juridiques)
        is_complex = (
            len(user_input.split()) > 20 or
            any(term in user_input.lower() for term in [
                "article", "loi", "code", "juridique", "légal", "règlement",
                "jurisprudence", "tribunal", "cour", "contentieux", "judiciaire"
            ])
        )
        
        # Si du contexte est fourni, c'est probablement plus complexe
        has_context = context is not None and len(context) > 0
        
        # Décision basée sur complexité et contexte
        if is_complex or has_context:
            # Même pour les questions complexes, limiter l'utilisation de Claude
            # pour économiser les appels API
            random_factor = random.random()
            return random_factor > 0.3  # 70% de chance d'utiliser Claude
        
        # Pour les questions normales, utiliser Claude avec parcimonie
        random_factor = random.random()
        return random_factor > 0.7  # 30% de chance d'utiliser Claude
    
    def _get_claude_response(self, 
                            user_input: str, 
                            context: Optional[List[Dict[str, str]]]) -> str:
        """
        Obtient une réponse de l'API Claude.
        
        Args:
            user_input: Question de l'utilisateur
            context: Contexte optionnel
            
        Returns:
            La réponse générée
        """
        # Préparer le prompt avec le contexte si disponible
        if context:
            context_str = "Contexte: "
            for ctx in context:
                for key, value in ctx.items():
                    context_str += f"{key}: {value}. "
            enhanced_input = f"{context_str}\n\nQuestion: {user_input}"
        else:
            enhanced_input = user_input
        
        # Obtenir une réponse de Claude
        system_prompt = """
        Tu es Valetia, un assistant juridique français intelligent spécialisé dans la copropriété,
        les prud'hommes et les successions. Tes réponses sont précises, basées sur le droit français
        et européen, mais vulgarisées pour être comprises par tous. Tu cites les références légales
        pertinentes et proposes des pistes d'action concrètes. Tu indiques toujours tes limites et
        rappelles que tes conseils ne remplacent pas ceux d'un professionnel du droit.
        """
        
        result = claude_client.get_response(
            prompt=enhanced_input,
            system_prompt=system_prompt,
            max_tokens=800,
            temperature=0.7
        )
        
        # Extraire la réponse du résultat
        if "content" in result and isinstance(result["content"], list):
            response_parts = []
            for content_item in result["content"]:
                if content_item.get("type") == "text":
                    response_parts.append(content_item.get("text", ""))
            return " ".join(response_parts)
        
        # Fallback si la structure est différente
        if isinstance(result, dict) and "error" in result:
            return f"Désolé, je n'ai pas pu traiter votre demande. {result['error'].get('message', 'Une erreur est survenue.')}"
        
        # Autre fallback
        return "Je n'ai pas pu générer une réponse à votre question juridique. Pourriez-vous reformuler votre demande?"
    
    def _generate_basic_response(self, 
                                user_input: str, 
                                context: Optional[List[Dict[str, str]]]) -> str:
        """
        Génère une réponse basique en local.
        
        Args:
            user_input: Question de l'utilisateur
            context: Contexte optionnel
            
        Returns:
            La réponse générée
        """
        # Détecter le domaine juridique concerné
        domain = "général"
        
        if any(keyword in user_input.lower() for keyword in ["copropriété", "syndic", "assemblée générale", "ag", "lot", "immeuble"]):
            domain = "copropriété"
            response = self._get_coproprietee_response(user_input)
        elif any(keyword in user_input.lower() for keyword in ["travail", "licenciement", "contrat", "employeur", "salarié", "prud'homme"]):
            domain = "prud'hommes"
            response = self._get_prudhommes_response(user_input)
        elif any(keyword in user_input.lower() for keyword in ["héritage", "succession", "testament", "héritier", "notaire"]):
            domain = "succession"
            response = self._get_succession_response(user_input)
        else:
            # Réponse générique
            response = "Pour répondre précisément à votre question juridique, j'aurais besoin de plus d'informations. "
            response += "Pourriez-vous préciser si votre question concerne la copropriété, le droit du travail (prud'hommes) "
            response += "ou les successions? Cela me permettra de vous fournir une réponse plus adaptée."
        
        # Ajouter un disclaimer juridique
        response += f"\n\n{random.choice(LEGAL_DISCLAIMERS)}"
        
        return response
    
    def _get_coproprietee_response(self, user_input: str) -> str:
        """Génère une réponse pour les questions de copropriété."""
        responses = [
            "En matière de copropriété, la loi du 10 juillet 1965 et son décret d'application du 17 mars 1967 constituent le cadre légal principal. ",
            "Les problématiques de copropriété relèvent principalement de la loi du 10 juillet 1965, qui définit les droits et obligations des copropriétaires. ",
            "Dans une copropriété, les décisions importantes sont prises en assemblée générale, selon des règles de majorité différentes en fonction de la nature des décisions. "
        ]
        
        if "assemblée" in user_input.lower() or "ag" in user_input.lower():
            responses.append("Les assemblées générales de copropriété doivent être convoquées au moins 21 jours à l'avance, par lettre recommandée avec accusé de réception. L'ordre du jour doit être précis et complet.")
        
        if "travaux" in user_input.lower():
            responses.append("Les travaux en copropriété sont soumis à des règles de majorité différentes selon leur nature : majorité simple (article 24), majorité absolue (article 25) ou double majorité (article 26).")
        
        if "charges" in user_input.lower():
            responses.append("Les charges de copropriété sont réparties selon les tantièmes définis dans le règlement de copropriété, avec une distinction entre charges générales et charges spéciales.")
        
        # Sélectionner aléatoirement 2 réponses et les combiner
        selected_responses = random.sample(responses, min(2, len(responses)))
        response = " ".join(selected_responses)
        
        return response
    
    def _get_prudhommes_response(self, user_input: str) -> str:
        """Génère une réponse pour les questions de prud'hommes."""
        responses = [
            "En droit du travail français, le Conseil de Prud'hommes est compétent pour trancher les litiges individuels entre employeurs et salariés. ",
            "La procédure prud'homale commence généralement par une phase de conciliation obligatoire, suivie si nécessaire d'une phase de jugement. ",
            "Le Code du travail protège les salariés contre les licenciements abusifs et définit les indemnités auxquelles ils peuvent prétendre. "
        ]
        
        if "licenciement" in user_input.lower():
            responses.append("En cas de licenciement sans cause réelle et sérieuse, les indemnités sont encadrées par le barème Macron (articles L.1235-3 et suivants du Code du travail), dont l'application a été confirmée par la Cour de cassation.")
        
        if "démission" in user_input.lower():
            responses.append("La démission doit être claire et non équivoque. Le salarié démissionnaire n'a pas droit aux allocations chômage, sauf dans certains cas de démission légitime.")
        
        if "contrat" in user_input.lower():
            responses.append("Le contrat de travail peut être à durée indéterminée (CDI) ou à durée déterminée (CDD). Le CDD ne peut être utilisé que dans des cas précis et sa requalification en CDI est possible en cas d'irrégularité.")
        
        # Sélectionner aléatoirement 2 réponses et les combiner
        selected_responses = random.sample(responses, min(2, len(responses)))
        response = " ".join(selected_responses)
        
        return response
    
    def _get_succession_response(self, user_input: str) -> str:
        """Génère une réponse pour les questions de succession."""
        responses = [
            "En matière de succession, le Code civil français organise la dévolution des biens selon un ordre précis, en l'absence de testament. ",
            "La réserve héréditaire protège une partie du patrimoine qui revient obligatoirement aux héritiers réservataires (enfants et, à défaut, conjoint). ",
            "L'acceptation d'une succession peut se faire purement et simplement, à concurrence de l'actif net, ou être refusée. "
        ]
        
        if "testament" in user_input.lower():
            responses.append("Le testament permet d'organiser sa succession, mais il doit respecter la réserve héréditaire. Il peut être olographe (écrit à la main), authentique (devant notaire) ou mystique (remis cacheté au notaire).")
        
        if "héritier" in user_input.lower() or "hériter" in user_input.lower():
            responses.append("Les héritiers sont déterminés selon quatre ordres : les descendants, les parents et collatéraux privilégiés, les ascendants ordinaires, et les collatéraux ordinaires, avec des règles de priorité entre ces ordres.")
        
        if "fiscalité" in user_input.lower() or "impôt" in user_input.lower() or "droit" in user_input.lower():
            responses.append("Les droits de succession sont calculés après application d'abattements qui varient selon le lien de parenté. Entre parent et enfant, l'abattement est de 100 000 euros par enfant, renouvelable tous les 15 ans.")
        
        # Sélectionner aléatoirement 2 réponses et les combiner
        selected_responses = random.sample(responses, min(2, len(responses)))
        response = " ".join(selected_responses)
        
        return response
    
    def _find_similar_example(self, user_input: str) -> Tuple[Optional[Dict[str, str]], float]:
        """
        Cherche un exemple similaire dans les exemples appris.
        
        Args:
            user_input: Question de l'utilisateur
            
        Returns:
            Tuple (exemple similaire ou None, score de similarité)
        """
        if not self.learned_examples:
            return None, 0.0
        
        # Simplifier pour trouver des correspondances
        input_words = set(user_input.lower().split())
        
        best_example = None
        best_similarity = 0.0
        
        for example in self.learned_examples:
            example_words = set(example["question"].lower().split())
            
            # Calculer la similarité de Jaccard
            if not input_words or not example_words:
                similarity = 0.0
            else:
                intersection = len(input_words.intersection(example_words))
                union = len(input_words.union(example_words))
                similarity = intersection / union
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_example = example
        
        return best_example, best_similarity
    
    def _adapt_similar_response(self, base_response: str, user_input: str) -> str:
        """
        Adapte une réponse similaire à la question actuelle.
        
        Args:
            base_response: Réponse de base à adapter
            user_input: Question de l'utilisateur
            
        Returns:
            La réponse adaptée
        """
        # Pour l'instant, une adaptation simple
        if random.random() < 0.3:
            prefix = random.choice([
                "D'après mon analyse, ",
                "Selon le droit français, ",
                "En réponse à votre question, ",
                "Pour éclairer votre interrogation, "
            ])
            return prefix + base_response
        
        return base_response
    
    def _learn_from_response(self, 
                            user_input: str, 
                            response: str, 
                            is_helpful: bool = False) -> None:
        """
        Apprend d'une réponse pour améliorer les futures interactions.
        
        Args:
            user_input: Question de l'utilisateur
            response: Réponse générée
            is_helpful: Si la réponse a été jugée utile par l'utilisateur
        """
        # Ne pas apprendre les réponses trop courtes ou génériques
        if len(response.split()) < 10:
            return
        
        # Vérifier si une question similaire existe déjà
        similar_example, similarity = self._find_similar_example(user_input)
        
        # Si très similaire, mettre à jour plutôt qu'ajouter
        if similar_example and similarity > 0.9:
            # Si feedback positif, remplacer; sinon, conserver l'existant
            if is_helpful:
                similar_example["response"] = response
                similar_example["positive_feedback"] = similar_example.get("positive_feedback", 0) + 1
                logger.info(f"Exemple d'apprentissage mis à jour: {user_input[:30]}...")
            else:
                similar_example["seen_count"] = similar_example.get("seen_count", 0) + 1
        else:
            # Ajouter un nouvel exemple
            new_example = {
                "question": user_input,
                "response": response,
                "timestamp": time.time(),
                "seen_count": 1,
                "positive_feedback": 1 if is_helpful else 0
            }
            self.learned_examples.append(new_example)
            logger.info(f"Nouvel exemple d'apprentissage ajouté: {user_input[:30]}...")
        
        # Sauvegarder périodiquement
        if random.random() < 0.2:  # 20% de chance de sauvegarder à chaque apprentissage
            self._save_learned_examples()
    
    def _load_learned_examples(self) -> List[Dict[str, Any]]:
        """
        Charge les exemples d'apprentissage depuis le fichier.
        
        Returns:
            Liste des exemples d'apprentissage
        """
        if not self.examples_file.exists():
            return []
        
        try:
            with open(self.examples_file, "r", encoding="utf-8") as f:
                examples = json.load(f)
            
            logger.info(f"Chargé {len(examples)} exemples d'apprentissage")
            return examples
        except Exception as e:
            logger.error(f"Erreur lors du chargement des exemples d'apprentissage: {e}")
            return []
    
    def _save_learned_examples(self) -> None:
        """Sauvegarde les exemples d'apprentissage dans le fichier."""
        try:
            # Limiter le nombre d'exemples pour éviter une croissance excessive
            if len(self.learned_examples) > 1000:
                # Garder les exemples les plus utiles (avec feedback positif) et les plus récents
                sorted_examples = sorted(
                    self.learned_examples,
                    key=lambda x: (x.get("positive_feedback", 0), x.get("timestamp", 0)),
                    reverse=True
                )
                self.learned_examples = sorted_examples[:1000]
            
            with open(self.examples_file, "w", encoding="utf-8") as f:
                json.dump(self.learned_examples, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Sauvegardé {len(self.learned_examples)} exemples d'apprentissage")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des exemples d'apprentissage: {e}")
    
    def _save_conversation(self, 
                          conversation_id: str, 
                          user_input: str, 
                          assistant_response: str,
                          context: Optional[List[Dict[str, str]]] = None) -> None:
        """
        Enregistre une conversation.
        
        Args:
            conversation_id: ID de la conversation
            user_input: Question de l'utilisateur
            assistant_response: Réponse générée
            context: Contexte optionnel
        """
        # Créer un fichier de conversation simple
        conversation_dir = Path(f"data/conversations/{conversation_id}")
        conversation_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = int(time.time())
        exchange_file = conversation_dir / f"exchange_{timestamp}.json"
        
        exchange_data = {
            "timestamp": timestamp,
            "user_input": user_input,
            "assistant_response": assistant_response,
            "context": context
        }
        
        try:
            with open(exchange_file, "w", encoding="utf-8") as f:
                json.dump(exchange_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Conversation {conversation_id} mise à jour")
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de la conversation: {e}")


# Singleton pour l'utilisation dans l'application
conversation_manager = HybridConversationManager()
