"""
Script de test pour les fonctionnalités d'accessibilité.
"""

import streamlit as st
from valetia.accessibility import (
    get_accessibility_config,
    setup_accessibility,
    ContrastMode,
    ColorBlindMode
)

def main():
    st.set_page_config(
        page_title="Test d'Accessibilité - Valetia",
        page_icon="🔍",
        layout="wide",
    )
    
    # Configuration de l'accessibilité
    setup_accessibility()
    
    st.title("🔍 Test des Fonctionnalités d'Accessibilité")
    
    # Obtenir la configuration actuelle
    config = get_accessibility_config()
    
    # Afficher les paramètres actuels
    st.header("Paramètres d'accessibilité actuels")
    st.write(f"**Mode de contraste:** {config.contrast_mode}")
    st.write(f"**Mode daltonien:** {config.colorblind_mode}")
    st.write(f"**Taille du texte:** {config.text_size}")
    st.write(f"**Mode lecteur d'écran:** {'Activé' if config.screen_reader_friendly else 'Désactivé'}")
    st.write(f"**Navigation clavier:** {'Activée' if config.keyboard_navigation else 'Désactivée'}")
    
    # Test du contraste et des couleurs
    st.header("Test de contraste et couleurs")
    
    col1, col2, col3, col4 = st.columns(4)
    
    theme = config.get_current_theme()
    
    with col1:
        st.markdown(f"""
        <div style="background-color: {theme['primary']}; color: white; padding: 10px; text-align: center;">
            Couleur primaire
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background-color: {theme['secondary']}; color: white; padding: 10px; text-align: center;">
            Couleur secondaire
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background-color: {theme['success']}; color: white; padding: 10px; text-align: center;">
            Succès
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background-color: {theme['error']}; color: white; padding: 10px; text-align: center;">
            Erreur
        </div>
        """, unsafe_allow_html=True)
    
    # Test des tailles de texte
    st.header("Test des tailles de texte")
    
    text_sizes = config.get_text_sizes()
    
    st.markdown(f"""
    <h1 style="font-size: {text_sizes['title']}">Titre (H1)</h1>
    <h2 style="font-size: {text_sizes['header']}">Sous-titre (H2)</h2>
    <p style="font-size: {text_sizes['text']}">Texte normal - Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
    <p style="font-size: {text_sizes['small']}">Petit texte - Lorem ipsum dolor sit amet.</p>
    """, unsafe_allow_html=True)
    
    # Test des éléments d'interface
    st.header("Test des éléments d'interface")
    
    st.subheader("Boutons")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("Bouton principal", type="primary")
    with col2:
        st.button("Bouton secondaire")
    with col3:
        st.button("Bouton d'action", type="secondary")
    
    st.subheader("Champs de saisie")
    name = st.text_input("Votre nom")
    age = st.number_input("Votre âge", min_value=0, max_value=120, value=30)
    
    st.subheader("Sélecteurs")
    option = st.selectbox("Choisissez une option", ["Option 1", "Option 2", "Option 3"])
    
    # Test de l'accessibilité pour lecteurs d'écran
    st.header("Test pour lecteurs d'écran")
    
    st.markdown("""
    <div aria-label="Exemple de contenu accessible">
        <h3>Contenu accessible</h3>
        <p>Ce paragraphe est accessible aux lecteurs d'écran avec des attributs ARIA appropriés.</p>
        <button aria-label="Exemple de bouton accessible" tabindex="0">Bouton accessible</button>
    </div>
    """, unsafe_allow_html=True)
    
    # Instructions pour les raccourcis clavier
    st.header("Test des raccourcis clavier")
    
    if config.keyboard_navigation:
        st.markdown("""
        ### Raccourcis à tester:
        
        - `Alt+H` : Simuler un retour à l'accueil
        - `Alt+1` : Simuler l'accès au module Analyse de Document
        - `Alt+C` : Simuler le changement de mode de contraste
        
        *Note: Ces raccourcis sont simulés pour ce test et peuvent ne pas fonctionner complètement.*
        """)
    else:
        st.warning("La navigation clavier est désactivée. Activez-la dans les paramètres d'accessibilité pour tester les raccourcis.")

if __name__ == "__main__":
    main()
