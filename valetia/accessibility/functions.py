"""
Fonctions d'accessibilité pour ValetIA.

Ce module contient les fonctions et utilitaires pour améliorer
l'accessibilité de l'interface utilisateur, notamment:
- Support des lecteurs d'écran
- Modes de contraste et daltonien
- Navigation par clavier
"""

import streamlit as st
import html
import re
# Importer depuis le module parent
from valetia.logger.loguru_adapter import loguru_logger as logger
# Importer depuis config directement (pas via __init__)
from valetia.accessibility.config import get_accessibility_config, ContrastMode, ColorBlindMode

def inject_accessibility_css():
    """
    Injecte le CSS nécessaire pour les fonctionnalités d'accessibilité.
    """
    config = get_accessibility_config()
    theme = config.get_current_theme()
    text_sizes = config.get_text_sizes()
    
    # Construire le CSS pour le thème de couleurs
    color_css = f"""
    /* Thème de couleurs pour {config.contrast_mode}/{config.colorblind_mode} */
    :root {{
        --primary-color: {theme["primary"]};
        --secondary-color: {theme["secondary"]};
        --background-color: {theme["background"]};
        --text-color: {theme["text"]};
        --success-color: {theme["success"]};
        --warning-color: {theme["warning"]};
        --error-color: {theme["error"]};
        --info-color: {theme["info"]};
    }}
    
    .stButton>button {{
        background-color: var(--primary-color) !important;
        color: white !important;
    }}
    .stTextInput>div>div>input {{
        border: 2px solid var(--primary-color) !important;
    }}
    /* Ajouter plus de styles selon les besoins */
    """
    
    # Construire le CSS pour les tailles de texte
    text_css = f"""
    /* Tailles de texte pour {config.text_size} */
    h1, .stTitle {{
        font-size: {text_sizes["title"]} !important;
    }}
    h2, h3, .stHeader {{
        font-size: {text_sizes["header"]} !important;
    }}
    p, div, .stText {{
        font-size: {text_sizes["text"]} !important;
    }}
    .stSmall {{
        font-size: {text_sizes["small"]} !important;
    }}
    """
    
    # CSS pour le support des lecteurs d'écran
    screen_reader_css = ""
    if config.screen_reader_friendly:
        screen_reader_css = """
        /* Styles pour améliorer la compatibilité avec les lecteurs d'écran */
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border-width: 0;
        }
        
        a, button, [tabindex]:not([tabindex="-1"]) {
            transition: outline-offset 0.1s ease;
            outline: 2px solid transparent;
            outline-offset: 2px;
        }
        
        a:focus, button:focus, [tabindex]:not([tabindex="-1"]):focus {
            outline: 2px solid var(--primary-color);
            outline-offset: 2px;
        }
        """
    
    # Combiner tous les CSS
    combined_css = f"""
    {color_css}
    {text_css}
    {screen_reader_css}
    
    /* Styles généraux d'accessibilité */
    * {{
        line-height: 1.5;
        letter-spacing: 0.01em;
    }}
    """
    
    # Injecter le CSS dans Streamlit
    st.markdown(f"""
    <style>
    {combined_css}
    </style>
    """, unsafe_allow_html=True)
    
    logger.info(f"CSS d'accessibilité injecté: {config.contrast_mode}/{config.colorblind_mode}, {config.text_size}")

def create_accessible_label(label_text, for_id=None, hidden=False):
    """
    Crée une étiquette accessible pour les éléments de formulaire.
    
    Args:
        label_text (str): Texte de l'étiquette
        for_id (str, optional): ID de l'élément auquel l'étiquette est attachée
        hidden (bool, optional): Si True, l'étiquette est visible uniquement pour les lecteurs d'écran
    
    Returns:
        str: HTML pour l'étiquette accessible
    """
    label_text = html.escape(label_text)
    
    if hidden:
        return f'<label for="{for_id}" class="sr-only">{label_text}</label>'
    else:
        return f'<label for="{for_id}">{label_text}</label>'

def screen_reader_only(text):
    """
    Crée un texte uniquement visible par les lecteurs d'écran.
    
    Args:
        text (str): Texte à afficher pour les lecteurs d'écran
    
    Returns:
        str: HTML pour le texte accessible
    """
    return f'<span class="sr-only">{html.escape(text)}</span>'

def announce_to_screen_reader(text):
    """
    Annonce un message aux utilisateurs de lecteurs d'écran.
    
    Args:
        text (str): Texte à annoncer
    """
    # Utiliser un div avec l'attribut 'aria-live'
    st.markdown(f'<div aria-live="polite" class="sr-only">{html.escape(text)}</div>', unsafe_allow_html=True)

def create_skip_link():
    """
    Crée un lien 'Aller au contenu principal' pour les utilisateurs de clavier.
    """
    # Ce lien permet aux utilisateurs de sauter la navigation
    st.markdown("""
    <a href="#main-content" class="skip-link" style="position: absolute; left: -9999px; top: 1em; background: white; padding: 0.5em; z-index: 9999;">
        Aller au contenu principal
    </a>
    <div id="main-content" tabindex="-1"></div>
    """, unsafe_allow_html=True)

def add_keyboard_shortcuts_js():
    """
    Ajoute le JavaScript nécessaire pour les raccourcis clavier.
    """
    config = get_accessibility_config()
    
    if not config.keyboard_navigation:
        return
    
    # Convertir les raccourcis en format JavaScript
    shortcuts_js = {}
    for category, shortcuts in config.get_keyboard_shortcuts().items():
        for key, action in shortcuts.items():
            key_code = key.replace("Alt+", "alt+").replace("Maj+", "shift+").replace("Ctrl+", "ctrl+").replace("Échap", "escape").lower()
            shortcuts_js[key_code] = action
    
    # Créer le JavaScript pour les raccourcis
    js_code = f"""
    <script>
    // Raccourcis clavier pour ValetIA
    document.addEventListener('keydown', function(e) {{
        const shortcuts = {str(shortcuts_js).replace("'", '"')};
        
        // Construire la combinaison de touches
        let keyCombo = '';
        if (e.altKey) keyCombo += 'alt+';
        if (e.shiftKey) keyCombo += 'shift+';
        if (e.ctrlKey) keyCombo += 'ctrl+';
        keyCombo += e.key.toLowerCase();
        
        // Vérifier si un raccourci existe
        if (shortcuts[keyCombo]) {{
            console.log('Raccourci clavier: ' + keyCombo + ' -> ' + shortcuts[keyCombo]);
            
            // Empêcher le comportement par défaut pour éviter les conflits
            e.preventDefault();
            
            // Exécuter l'action correspondante
            // À implémenter: logique pour chaque action
            
            // Exemple: Alt+H pour aller à l'accueil
            if (keyCombo === 'alt+h') {{
                // Trouver le bouton/lien vers l'accueil et cliquer dessus
                document.querySelector('a[href="#/"]')?.click();
            }}
            
            // Annoncer l'action pour les lecteurs d'écran
            announceToScreenReader('Action: ' + shortcuts[keyCombo]);
        }}
    }});
    
    // Fonction pour annoncer aux lecteurs d'écran
    function announceToScreenReader(message) {{
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'assertive');
        announcement.classList.add('sr-only');
        announcement.textContent = message;
        document.body.appendChild(announcement);
        
        // Supprimer après l'annonce
        setTimeout(() => {{
            document.body.removeChild(announcement);
        }}, 1000);
    }}
    </script>
    """
    
    # Injecter le JavaScript dans Streamlit
    st.markdown(js_code, unsafe_allow_html=True)
    logger.info("JavaScript pour les raccourcis clavier injecté")

def setup_accessibility():
    """
    Configure toutes les fonctionnalités d'accessibilité.
    À appeler au début de l'application.
    """
    # Injecter le CSS
    inject_accessibility_css()
    
    # Ajouter le lien "Aller au contenu principal"
    create_skip_link()
    
    # Ajouter les raccourcis clavier
    add_keyboard_shortcuts_js()
    
    # Ajouter les thèmes avancés
    try:
        from valetia.accessibility.themes import apply_advanced_theme
        apply_advanced_theme()
    except ImportError:
        logger.warning("Module de thèmes avancés non disponible")
    
    logger.info("Configuration d'accessibilité appliquée")

def create_accessibility_settings():
    """
    Crée l'interface des paramètres d'accessibilité.
    À utiliser dans la barre latérale.
    """
    config = get_accessibility_config()
    
    st.sidebar.header("🔧 Accessibilité")
    
    # Mode de contraste
    contrast_mode = st.sidebar.selectbox(
        "Mode de contraste",
        [ContrastMode.NORMAL, ContrastMode.HIGH, ContrastMode.VERY_HIGH],
        format_func=lambda x: {
            ContrastMode.NORMAL: "Normal",
            ContrastMode.HIGH: "Contraste élevé",
            ContrastMode.VERY_HIGH: "Contraste très élevé"
        }.get(x, x),
        index=[ContrastMode.NORMAL, ContrastMode.HIGH, ContrastMode.VERY_HIGH].index(config.contrast_mode)
    )
    
    # Mode daltonien
    colorblind_mode = st.sidebar.selectbox(
        "Mode daltonien",
        [ColorBlindMode.NORMAL, ColorBlindMode.PROTANOPIA, ColorBlindMode.DEUTERANOPIA, 
         ColorBlindMode.TRITANOPIA, ColorBlindMode.ACHROMATOPSIA],
        format_func=lambda x: {
            ColorBlindMode.NORMAL: "Normal",
            ColorBlindMode.PROTANOPIA: "Protanopie (Rouge)",
            ColorBlindMode.DEUTERANOPIA: "Deutéranopie (Vert)",
            ColorBlindMode.TRITANOPIA: "Tritanopie (Bleu)",
            ColorBlindMode.ACHROMATOPSIA: "Achromatopsie (N&B)"
        }.get(x, x),
        index=[ColorBlindMode.NORMAL, ColorBlindMode.PROTANOPIA, ColorBlindMode.DEUTERANOPIA, 
              ColorBlindMode.TRITANOPIA, ColorBlindMode.ACHROMATOPSIA].index(config.colorblind_mode)
    )
    
    # Taille du texte
    text_size = st.sidebar.select_slider(
        "Taille du texte",
        options=["small", "medium", "large", "very_large"],
        value=config.text_size,
        format_func=lambda x: {
            "small": "Petite",
            "medium": "Moyenne",
            "large": "Grande",
            "very_large": "Très grande"
        }.get(x, x)
    )
    
    # Support des lecteurs d'écran
    screen_reader_friendly = st.sidebar.checkbox(
        "Mode lecteur d'écran",
        value=config.screen_reader_friendly,
        help="Optimise l'interface pour les utilisateurs de lecteurs d'écran"
    )
    
    # Navigation clavier
    keyboard_navigation = st.sidebar.checkbox(
        "Navigation clavier",
        value=config.keyboard_navigation,
        help="Active les raccourcis clavier pour naviguer dans l'application"
    )
    
    # Affichage des raccourcis
    if keyboard_navigation:
        with st.sidebar.expander("📋 Raccourcis clavier"):
            for category, shortcuts in config.get_keyboard_shortcuts().items():
                st.sidebar.subheader(category)
                for key, action in shortcuts.items():
                    st.sidebar.markdown(f"**{key}**: {action}")
    
    # Aide sur l'accessibilité
    with st.sidebar.expander("ℹ️ Aide sur l'accessibilité"):
        st.markdown("""
        ### Modes de contraste
        - **Normal** : Apparence standard de l'application
        - **Contraste élevé** : Améliore la lisibilité pour les personnes malvoyantes
        - **Contraste très élevé** : Contraste maximum pour les personnes ayant une vision très limitée
        
        ### Modes daltoniens
        - **Normal** : Couleurs standard
        - **Protanopie** : Adapté pour les personnes qui perçoivent mal le rouge
        - **Deutéranopie** : Adapté pour les personnes qui perçoivent mal le vert
        - **Tritanopie** : Adapté pour les personnes qui perçoivent mal le bleu
        - **Achromatopsie** : Pour les personnes ne percevant pas les couleurs (vision en noir et blanc)
        
        ### Taille du texte
        Ajustez la taille du texte selon vos besoins de lecture
        
        ### Mode lecteur d'écran
        Optimise l'interface pour les technologies d'assistance comme les lecteurs d'écran
        
        ### Navigation clavier
        Permet d'utiliser l'application uniquement au clavier avec des raccourcis
        """)
    
    # Sauvegarder les changements
    if (contrast_mode != config.contrast_mode or 
        colorblind_mode != config.colorblind_mode or 
        text_size != config.text_size or 
        screen_reader_friendly != config.screen_reader_friendly or 
        keyboard_navigation != config.keyboard_navigation):
        
        config.contrast_mode = contrast_mode
        config.colorblind_mode = colorblind_mode
        config.text_size = text_size
        config.screen_reader_friendly = screen_reader_friendly
        config.keyboard_navigation = keyboard_navigation
        
        config.save_preferences()
        
        # Forcer le rafraîchissement pour appliquer les changements
        st.experimental_rerun()
