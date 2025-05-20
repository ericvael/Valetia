"""
Interface utilisateur principale de Valetia basée sur Streamlit.
"""
import os
import sys
import tempfile
from pathlib import Path
import traceback
import uuid

import streamlit as st
from valetia.core.document_analyzer import DocumentAnalyzer
from valetia.utils.logger import get_logger

# Commenter temporairement pour éviter les problèmes d'importation circulaire
# from valetia.accessibility import setup_accessibility, create_accessibility_settings
# Importer le module de gestion des dépendances
from valetia.deps import setup_periodic_check

logger = get_logger(__name__)

def show_chatbot():
    """Affiche l'interface du chatbot."""
    st.header("Assistant IA")
    
    # Initialiser l'historique des messages s'il n'existe pas
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Initialiser l'ID de conversation s'il n'existe pas
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
    
    # Initialiser le dictionnaire des feedbacks s'il n'existe pas
    if "feedbacks" not in st.session_state:
        st.session_state.feedbacks = {}
    
    # Vérifier si un document a été analysé et utilisé comme contexte
    document_context = None
    if "current_document" in st.session_state:
        doc_info = st.session_state.current_document
        st.info(f"📄 Contexte actuel: Document '{doc_info['name']}'")
        
        # Créer un contexte pour l'IA
        document_context = [{
            "document_name": doc_info["name"],
            "document_type": doc_info["type"],
            "document_summary": doc_info.get("summary", "")
        }]
        
        # Option pour effacer le contexte
        if st.button("❌ Effacer le contexte du document"):
            del st.session_state.current_document
            st.rerun()
    
    # Afficher les messages précédents
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Afficher les boutons de feedback pour les réponses de l'assistant
            if message["role"] == "assistant":
                # Vérifier si un feedback a déjà été donné pour ce message
                message_id = f"message_{i}"
                feedback_given = message_id in st.session_state.feedbacks
                
                if not feedback_given:
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("👍 Utile", key=f"useful_{i}"):
                            # Enregistrer le feedback positif
                            from valetia.modules.chatbot.hybrid_manager import conversation_manager
                            
                            # Récupérer la question et la réponse
                            question = st.session_state.messages[i-1]["content"] if i > 0 else ""
                            answer = message["content"]
                            
                            # Enregistrer le feedback
                            success = conversation_manager.save_feedback(
                                conversation_id=st.session_state.conversation_id,
                                user_input=question,
                                assistant_response=answer,
                                is_helpful=True
                            )
                            
                            if success:
                                st.success("Merci pour votre feedback positif!")
                                st.session_state.feedbacks[message_id] = True
                            else:
                                st.error("Erreur lors de l'enregistrement du feedback.")
                    
                    with col2:
                        if st.button("👎 Pas utile", key=f"not_useful_{i}"):
                            # Enregistrer le feedback négatif
                            from valetia.modules.chatbot.hybrid_manager import conversation_manager
                            
                            # Récupérer la question et la réponse
                            question = st.session_state.messages[i-1]["content"] if i > 0 else ""
                            answer = message["content"]
                            
                            # Enregistrer le feedback
                            success = conversation_manager.save_feedback(
                                conversation_id=st.session_state.conversation_id,
                                user_input=question,
                                assistant_response=answer,
                                is_helpful=False
                            )
                            
                            if success:
                                st.info("Merci pour votre feedback. Nous nous améliorerons.")
                                st.session_state.feedbacks[message_id] = False
                            else:
                                st.error("Erreur lors de l'enregistrement du feedback.")
                else:
                    # Afficher un message indiquant que le feedback a été donné
                    if st.session_state.feedbacks[message_id]:
                        st.success("✓ Vous avez trouvé cette réponse utile")
                    else:
                        st.info("✗ Vous avez trouvé cette réponse peu utile")
    
    # Zone d'entrée avec texte et option vocale
    col1, col2 = st.columns([5, 1])
    
    with col1:
        # Zone de saisie pour la question écrite
        prompt = st.chat_input("Comment puis-je vous aider sur cette question juridique?")
    
    with col2:
        # Bouton pour le futur input vocal (fonctionnalité à venir)
        voice_button = st.button("🎤", help="Commande vocale (à venir)")
        if voice_button:
            st.info("La commande vocale sera disponible dans une prochaine version")
    
    # Traitement de l'entrée textuelle
    if prompt:
        # Ajouter la question à l'historique
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Afficher la question
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Afficher la réponse de l'assistant
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                # Import ici pour éviter les problèmes de chargement circulaire
                from valetia.modules.chatbot.hybrid_manager import conversation_manager
                
                # Obtenir la réponse avec le contexte du document s'il existe
                with st.spinner("Réflexion en cours..."):
                    response = conversation_manager.get_response(
                        prompt, 
                        st.session_state.conversation_id,
                        context=document_context
                    )
                
                # Afficher la réponse
                message_placeholder.markdown(response)
                
                # Ajouter la réponse à l'historique
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"Une erreur s'est produite: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
                
    # Zone pour les outils et les préférences
    with st.sidebar:
        st.subheader("⚙️ Outils et préférences")
        
        # Sélection des domaines juridiques d'intérêt
        st.write("Domaines juridiques d'intérêt:")
        copropriete = st.checkbox("✓ Copropriété", value=True)
        prudhommes = st.checkbox("✓ Prud'hommes", value=True)
        succession = st.checkbox("✓ Succession", value=True)
        
        st.divider()
        
        # Option pour effacer l'historique
        if st.button("🗑️ Effacer l'historique"):
            st.session_state.messages = []
            st.session_state.feedbacks = {}
            st.rerun()
        
        # Option pour démarrer une nouvelle conversation
        if st.button("🔄 Nouvelle conversation"):
            st.session_state.messages = []
            st.session_state.feedbacks = {}
            st.session_state.conversation_id = str(uuid.uuid4())
            if "current_document" in st.session_state:
                del st.session_state.current_document
            st.rerun()
            
        # Afficher l'ID de conversation pour le débogage
        st.caption(f"ID de conversation: {st.session_state.conversation_id}")
        
        # Information sur la préparation à la reconnaissance vocale
        st.divider()
        st.markdown("##### 🎤 Commande vocale")
        st.caption("La commande vocale sera disponible dans une prochaine version. Elle vous permettra d'interagir avec Valetia simplement en parlant.")
        
        # Section sur l'apprentissage
        st.divider()
        st.markdown("##### 🧠 Apprentissage")
        st.caption("Valetia apprend de vos interactions pour s'améliorer. Vos feedbacks aident à construire une meilleure expérience.")
        st.caption("Votre feedback est utilisé pour améliorer les réponses futures sur des questions similaires.")

def main():
    """Application Streamlit principale pour Valetia."""
    st.set_page_config(
        page_title="Valetia - IA Juridique Locale",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Commenter temporairement pour éviter les erreurs
    # Configurer l'accessibilité
    # setup_accessibility()
    
    # Initialiser la vérification périodique des dépendances
    setup_periodic_check()
    
    # Titre et introduction
    st.title("⚖️ Valetia - IA Juridique Locale")
    st.markdown(
        """
        Bienvenue dans Valetia, votre assistant d'IA juridique local pour l'analyse de documents
        et la préparation de dossiers juridiques.
        """
    )
    
    # Barre latérale avec sélection de module
    st.sidebar.title("Navigation")
    module = st.sidebar.selectbox(
        "Sélectionnez un module:",
        ["Accueil", "Analyse de Document", "Assistant IA", "Copropriété", "Prud'hommes", "Succession"]
    )
    
    # Commenter temporairement pour éviter les erreurs
    # Ajouter les paramètres d'accessibilité dans la barre latérale
    # create_accessibility_settings()
    
    # Affichage du module sélectionné
    if module == "Accueil":
        show_home()
    elif module == "Analyse de Document":
        show_document_analysis()
    elif module == "Assistant IA":
        show_chatbot()
    elif module == "Copropriété":
        show_copropriete()
    elif module == "Prud'hommes":
        show_prudhommes()
    elif module == "Succession":
        show_succession()

def show_home():
    """Affiche la page d'accueil."""
    st.header("Bienvenue dans Valetia")
    
    st.markdown(
        """
        ### Fonctionnalités disponibles:
        
        - **Analyse de Document**: Chargez et analysez tout type de document (PDF, Word, texte, etc.)
        - **Module Copropriété**: Analysez les documents de copropriété pour détecter les irrégularités
        - **Module Prud'hommes**: Analysez les documents liés à un litige prud'hommal
        - **Module Succession**: Gérez les documents d'une succession conflictuelle
        
        ### Commencer:
        
        Utilisez la barre latérale pour naviguer entre les différents modules.
        """
    )
    
    st.info("Valetia est en cours de développement. De nouvelles fonctionnalités seront ajoutées régulièrement.")

def safe_save_uploaded_file(uploaded_file):
    """
    Sauvegarde de manière sécurisée un fichier téléchargé.
    
    Args:
        uploaded_file: Le fichier téléchargé via Streamlit
        
    Returns:
        Path: Le chemin vers le fichier sauvegardé
    """
    try:
        # Créer un fichier temporaire avec l'extension correcte
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            # Écrire le contenu du fichier téléchargé dans le fichier temporaire
            tmp_file.write(uploaded_file.getbuffer())
            return Path(tmp_file.name)
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du fichier: {e}")
        st.error(f"Erreur lors de la sauvegarde du fichier: {e}")
        return None

def show_document_analysis():
    """Affiche le module d'analyse de document."""
    st.header("Analyse de Document")
    
    # Zone de téléchargement de fichier
    st.subheader("Étape 1: Choisissez un document")
    uploaded_file = st.file_uploader(
        "Formats supportés: TXT, PDF, DOCX, DOC, XLS, XLSX, EML", 
        type=["txt", "pdf", "docx", "doc", "xlsx", "xls", "eml"]
    )
    
    if uploaded_file:
        # Afficher les informations sur le fichier
        st.success(f"✅ Document sélectionné: **{uploaded_file.name}**")
        
        file_info_col1, file_info_col2 = st.columns(2)
        with file_info_col1:
            st.write(f"**Type:** {uploaded_file.type}")
        with file_info_col2:
            st.write(f"**Taille:** {uploaded_file.size / 1024:.1f} KB")
        
        # Étape 2: Analyse du document
        st.subheader("Étape 2: Analyser le document")
        
        analyze_button = st.button("📊 Lancer l'analyse", type="primary")
        
        if analyze_button:
            # Afficher un spinner pendant l'analyse
            with st.spinner("⏳ Analyse en cours..."):
                try:
                    # Sauvegarder le fichier temporairement
                    temp_file_path = safe_save_uploaded_file(uploaded_file)
                    
                    if temp_file_path:
                        # Créer l'analyseur et charger le document
                        analyzer = DocumentAnalyzer()
                        success = analyzer.load_document(temp_file_path)
                        
                        if success:
                            # Analyser le document
                            analysis = analyzer.analyze_document(0)
                            
                            # Afficher les résultats dans des sections pliables
                            st.subheader("📝 Résultats de l'analyse")
                            
                            metrics_col1, metrics_col2 = st.columns(2)
                            with metrics_col1:
                                st.metric("Nombre de mots", analysis.get("word_count", 0))
                            with metrics_col2:
                                st.metric("Nombre de caractères", analysis.get("character_count", 0))
                            
                            # Résumé
                            with st.expander("📋 Résumé du document", expanded=True):
                                summary = analysis.get("summary", "")
                                if summary:
                                    st.write(summary)
                                else:
                                    st.info("Aucun résumé généré pour ce document.")
                            
                            # Entités détectées
                            with st.expander("🔍 Entités détectées", expanded=True):
                                entities = analysis.get("entities", {})
                                if entities:
                                    for entity_type, entity_list in entities.items():
                                        if entity_list:
                                            st.write(f"**{entity_type}:** {', '.join(entity_list)}")
                                else:
                                    st.info("Aucune entité détectée dans ce document.")
                            
                            # Mots-clés
                            with st.expander("🔑 Mots-clés", expanded=True):
                                keywords = analysis.get("keywords", [])
                                if keywords:
                                    for keyword in keywords[:10]:  # Afficher les 10 premiers
                                        word = keyword.get("word", "")
                                        count = keyword.get("count", 0)
                                        if word and count:
                                            st.write(f"- **{word}:** {count} occurrences")
                                else:
                                    st.info("Aucun mot-clé significatif trouvé.")
                            
                            # Téléchargement des résultats
                            with st.expander("📥 Exporter les résultats"):
                                st.write("Fonctionnalité en développement.")
                                
                            # Option pour interroger l'assistant sur ce document
                            with st.expander("💬 Poser des questions sur ce document", expanded=True):
                                st.write("Vous pouvez poser des questions sur ce document à l'Assistant IA.")
                                if st.button("Aller à l'Assistant IA avec ce document comme contexte"):
                                    # Sauvegarder les informations du document dans la session
                                    st.session_state.current_document = {
                                        "name": uploaded_file.name,
                                        "type": uploaded_file.type,
                                        "summary": analysis.get("summary", ""),
                                        "entities": analysis.get("entities", {}),
                                        "keywords": analysis.get("keywords", [])
                                    }
                                    # Rediriger vers l'assistant
                                    st.session_state.redirect_to_assistant = True
                        else:
                            st.error(f"❌ Impossible d'analyser le fichier {uploaded_file.name}.")
                            st.info("Essayez avec un autre format de fichier ou vérifiez que le fichier n'est pas corrompu.")
                        
                        # Nettoyage du fichier temporaire
                        try:
                            os.unlink(temp_file_path)
                        except:
                            pass
                    
                except Exception as e:
                    st.error(f"❌ Une erreur s'est produite lors de l'analyse: {str(e)}")
                    st.code(traceback.format_exc())
    else:
        st.info("👆 Veuillez télécharger un document pour commencer l'analyse.")
        
        # Exemples de documents
        with st.expander("📚 Vous n'avez pas de document à analyser?"):
            st.write("Vous pouvez essayer avec un exemple de texte:")
            
            example_text = """
            CONTRAT DE BAIL ENTRE LES SOUSSIGNÉS
            
            Monsieur Jean Dupont, né le 15 janvier 1970 à Paris, demeurant au 12 rue des Fleurs, 75001 Paris,
            ci-après dénommé "LE BAILLEUR",
            
            ET
            
            Madame Marie Martin, née le 25 juin 1985 à Lyon, demeurant actuellement au 8 avenue des Arbres, 75002 Paris,
            ci-après dénommée "LA LOCATAIRE",
            
            IL A ÉTÉ CONVENU CE QUI SUIT :
            
            Article 1 : Le bailleur loue à la locataire un appartement de 65m² situé au 9 rue du Commerce, 75015 Paris.
            
            Article 2 : Le loyer mensuel est fixé à 1200 euros, charges comprises.
            
            Article 3 : Le bail est conclu pour une durée de 3 ans à compter du 1er septembre 2023.
            """
            
            if st.button("Utiliser cet exemple de texte"):
                # Créer un fichier temporaire avec le texte d'exemple
                temp_dir = Path("data/temp")
                temp_dir.mkdir(parents=True, exist_ok=True)
                
                example_file = temp_dir / "exemple_contrat.txt"
                with open(example_file, "w", encoding="utf-8") as f:
                    f.write(example_text)
                
                st.success(f"Exemple créé: {example_file}")
                st.info("Retournez à la section 'Analyse de Document' et téléchargez ce fichier.")

    # Vérifier s'il faut rediriger vers l'assistant
    if st.session_state.get("redirect_to_assistant", False):
        st.session_state.redirect_to_assistant = False
        st.rerun()

def show_copropriete():
    """Affiche le module de copropriété."""
    st.header("Module Copropriété")
    
    tab1, tab2, tab3 = st.tabs(["📋 Informations", "📄 Documents", "🔍 Analyse"])
    
    with tab1:
        # Informations sur la copropriété
        st.subheader("Informations sur la copropriété")
        
        col1, col2 = st.columns(2)
        with col1:
            nom_copro = st.text_input("Nom de la copropriété")
            adresse = st.text_input("Adresse")
            syndic = st.text_input("Nom du syndic")
        
        with col2:
            nb_lots = st.number_input("Nombre de lots", min_value=1, value=10)
            date_ag = st.date_input("Date de la dernière AG")
            president_cs = st.text_input("Président du conseil syndical")
        
        if st.button("💾 Enregistrer les informations"):
            if nom_copro and adresse:
                st.success(f"✅ Informations enregistrées pour la copropriété: {nom_copro}")
            else:
                st.error("❌ Veuillez remplir au moins le nom et l'adresse de la copropriété.")
    
    with tab2:
        # Documents de la copropriété
        st.subheader("Documents de la copropriété")
        
        document_types = [
            "Procès-verbal d'AG",
            "Règlement de copropriété",
            "État descriptif de division",
            "Contrat de syndic",
            "Appels de fonds",
            "Comptes annuels",
            "Relevés bancaires",
            "Courriers et notifications",
            "Autre"
        ]
        
        doc_type = st.selectbox("Type de document", document_types)
        doc_date = st.date_input("Date du document")
        doc_file = st.file_uploader("Télécharger le document", type=["pdf", "docx", "txt"])
        
        if st.button("📤 Ajouter le document"):
            if doc_file:
                st.success(f"✅ Document ajouté: {doc_type} du {doc_date}")
            else:
                st.error("❌ Veuillez sélectionner un fichier à télécharger.")
        
        st.divider()
        
        st.subheader("Documents enregistrés")
        st.info("Aucun document enregistré pour le moment.")
    
    with tab3:
        # Analyse de la copropriété
        st.subheader("Analyse de la copropriété")
        
        st.info("🚧 Cette fonctionnalité est en cours de développement.")
        
        st.write("""
        ### Fonctionnalités à venir:
        
        - Détection des irrégularités dans les PV d'AG
        - Analyse des décisions non conformes à la loi
        - Vérification des majorités requises
        - Analyse des comptes et détection d'anomalies
        - Suivi des délais légaux (convocations, notifications)
        - Préparation de dossier pour administrateur judiciaire
        """)
        
        if st.button("🔍 Détecter les irrégularités"):
            st.warning("🚧 Fonctionnalité en cours de développement.")

def show_prudhommes():
    """Affiche le module prud'hommes."""
    st.header("Module Prud'hommes")
    
    tab1, tab2, tab3 = st.tabs(["📋 Informations", "📄 Documents", "⏱️ Analyse horaire"])
    
    with tab1:
        # Informations sur le dossier prud'hommes
        st.subheader("Informations sur le dossier prud'hommes")
        
        col1, col2 = st.columns(2)
        with col1:
            employeur = st.text_input("Nom de l'employeur")
            poste = st.text_input("Poste occupé")
            date_debut = st.date_input("Date de début du contrat")
        
        with col2:
            convention = st.text_input("Convention collective applicable")
            type_contrat = st.selectbox("Type de contrat", ["CDI", "CDD", "Intérim", "Autre"])
            date_fin = st.date_input("Date de fin du contrat/licenciement")
        
        st.text_area("Motif du litige", height=100)
        
        if st.button("💾 Enregistrer les informations"):
            if employeur and poste:
                st.success(f"✅ Informations enregistrées pour le dossier prud'hommes contre: {employeur}")
            else:
                st.error("❌ Veuillez remplir au moins le nom de l'employeur et le poste occupé.")
    
    with tab2:
        # Documents du dossier prud'hommes
        st.subheader("Documents du dossier prud'hommes")
        
        document_types = [
            "Contrat de travail",
            "Avenants au contrat",
            "Fiches de paie",
            "Plannings",
            "Emails professionnels",
            "Lettres/courriers",
            "Attestations",
            "Certificats médicaux",
            "Autre"
        ]
        
        doc_type = st.selectbox("Type de document", document_types, key="prudhommes_doc_type")
        doc_date = st.date_input("Date du document", key="prudhommes_doc_date")
        doc_file = st.file_uploader("Télécharger le document", type=["pdf", "docx", "txt"], key="prudhommes_doc_file")
        
        if st.button("📤 Ajouter le document", key="prudhommes_add_doc"):
            if doc_file:
                st.success(f"✅ Document ajouté: {doc_type} du {doc_date}")
            else:
                st.error("❌ Veuillez sélectionner un fichier à télécharger.")
        
        st.divider()
        
        st.subheader("Documents enregistrés")
        st.info("Aucun document enregistré pour le moment.")
    
    with tab3:
        # Analyse des horaires de travail
        st.subheader("Analyse des horaires de travail")
        
        st.info("🚧 Cette fonctionnalité est en cours de développement.")
        
        st.write("""
        ### Fonctionnalités à venir:
        
        - Analyse des plannings et extraction des horaires travaillés
        - Calcul des heures supplémentaires
        - Détection du non-respect des temps de repos
        - Calcul des indemnités dues
        - Cartographie des déplacements professionnels
        - Analyse du respect des adaptations liées au handicap
        """)
        
        if st.button("⏱️ Analyser les horaires"):
            st.warning("🚧 Fonctionnalité en cours de développement.")

def show_succession():
    """Affiche le module succession."""
    st.header("Module Succession")
    
    st.info("🚧 Cette fonctionnalité est en cours de développement.")
    
    st.write("""
    ### Fonctionnalités à venir:
    
    - Organisation des documents de succession
    - Analyse des actes notariés
    - Suivi des échéances et délais
    - Validation des calculs et répartitions
    - Détection d'irrégularités dans les procédures
    """)
    
    if st.button("📨 M'informer quand cette fonctionnalité sera disponible"):
        st.success("✅ Nous vous informerons dès que cette fonctionnalité sera disponible.")

if __name__ == "__main__":
    main()
