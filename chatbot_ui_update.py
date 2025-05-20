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
                            from valetia.modules.chatbot.conversation import ConversationManager
                            
                            # Récupérer la question et la réponse
                            question = st.session_state.messages[i-1]["content"] if i > 0 else ""
                            answer = message["content"]
                            
                            # Initialiser le gestionnaire de conversation
                            conversation_manager = ConversationManager()
                            
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
                            from valetia.modules.chatbot.conversation import ConversationManager
                            
                            # Récupérer la question et la réponse
                            question = st.session_state.messages[i-1]["content"] if i > 0 else ""
                            answer = message["content"]
                            
                            # Initialiser le gestionnaire de conversation
                            conversation_manager = ConversationManager()
                            
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
    
    # Zone de saisie pour la question
    if prompt := st.chat_input("Comment puis-je vous aider?"):
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
                from valetia.modules.chatbot.conversation import ConversationManager
                
                # Initialiser le gestionnaire de conversation
                conversation_manager = ConversationManager()
                
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
