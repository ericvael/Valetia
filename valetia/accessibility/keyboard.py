"""
Gestionnaire avancé de raccourcis clavier pour ValetIA.

Ce module fournit des fonctionnalités avancées pour la navigation
au clavier, avec prise en charge de commandes complexes et contextuelle.
"""

import streamlit as st
import json
from valetia.logger.loguru_adapter import loguru_logger as logger
from .config import get_accessibility_config

# Définition des actions pour les raccourcis clavier
KEYBOARD_ACTIONS = {
    # Navigation générale
    "go_home": {
        "description": "Naviguer vers l'accueil",
        "js_code": """
            // Simuler un clic sur le sélecteur de module pour Accueil
            document.querySelector('div[data-baseweb="select"] select option[value="Accueil"]').selected = true;
            document.querySelector('div[data-baseweb="select"] select').dispatchEvent(new Event('change', {'bubbles': true}));
        """
    },
    "go_document_analysis": {
        "description": "Naviguer vers l'analyse de document",
        "js_code": """
            // Simuler un clic sur le sélecteur de module pour Analyse de Document
            document.querySelector('div[data-baseweb="select"] select option[value="Analyse de Document"]').selected = true;
            document.querySelector('div[data-baseweb="select"] select').dispatchEvent(new Event('change', {'bubbles': true}));
        """
    },
    "go_copropriete": {
        "description": "Naviguer vers le module Copropriété",
        "js_code": """
            // Simuler un clic sur le sélecteur de module pour Copropriété
            document.querySelector('div[data-baseweb="select"] select option[value="Copropriété"]').selected = true;
            document.querySelector('div[data-baseweb="select"] select').dispatchEvent(new Event('change', {'bubbles': true}));
        """
    },
    "go_prudhommes": {
        "description": "Naviguer vers le module Prud'hommes",
        "js_code": """
            // Simuler un clic sur le sélecteur de module pour Prud'hommes
            document.querySelector('div[data-baseweb="select"] select option[value="Prud'hommes"]').selected = true;
            document.querySelector('div[data-baseweb="select"] select').dispatchEvent(new Event('change', {'bubbles': true}));
        """
    },
    "go_succession": {
        "description": "Naviguer vers le module Succession",
        "js_code": """
            // Simuler un clic sur le sélecteur de module pour Succession
            document.querySelector('div[data-baseweb="select"] select option[value="Succession"]').selected = true;
            document.querySelector('div[data-baseweb="select"] select').dispatchEvent(new Event('change', {'bubbles': true}));
        """
    },
    
    # Actions d'accessibilité
    "toggle_accessibility_panel": {
        "description": "Ouvrir/fermer les paramètres d'accessibilité",
        "js_code": """
            // Trouver et cliquer sur l'en-tête des paramètres d'accessibilité
            const headers = Array.from(document.querySelectorAll('h3'));
            const accessibilityHeader = headers.find(h => h.textContent.includes('Accessibilité'));
            if (accessibilityHeader) {
                accessibilityHeader.click();
            }
        """
    },
    "increase_contrast": {
        "description": "Augmenter le contraste",
        "js_code": """
            // Logique pour augmenter le contraste
            const selectElements = Array.from(document.querySelectorAll('div[data-baseweb="select"] select'));
            const contrastSelect = selectElements.find(select => 
                Array.from(select.options).some(option => option.text.includes('Contraste'))
            );
            
            if (contrastSelect) {
                const currentIndex = contrastSelect.selectedIndex;
                if (currentIndex < contrastSelect.options.length - 1) {
                    contrastSelect.selectedIndex = currentIndex + 1;
                    contrastSelect.dispatchEvent(new Event('change', {'bubbles': true}));
                }
            }
        """
    },
    "decrease_contrast": {
        "description": "Diminuer le contraste",
        "js_code": """
            // Logique pour diminuer le contraste
            const selectElements = Array.from(document.querySelectorAll('div[data-baseweb="select"] select'));
            const contrastSelect = selectElements.find(select => 
                Array.from(select.options).some(option => option.text.includes('Contraste'))
            );
            
            if (contrastSelect) {
                const currentIndex = contrastSelect.selectedIndex;
                if (currentIndex > 0) {
                    contrastSelect.selectedIndex = currentIndex - 1;
                    contrastSelect.dispatchEvent(new Event('change', {'bubbles': true}));
                }
            }
        """
    },
    "increase_text_size": {
        "description": "Augmenter la taille du texte",
        "js_code": """
            // Logique pour augmenter la taille du texte
            const sliders = Array.from(document.querySelectorAll('input[type="range"]'));
            const textSizeSlider = sliders.find(slider => 
                slider.parentElement.textContent.includes('Taille du texte')
            );
            
            if (textSizeSlider) {
                const max = parseInt(textSizeSlider.max);
                const step = parseInt(textSizeSlider.step) || 1;
                const newValue = Math.min(max, parseInt(textSizeSlider.value) + step);
                textSizeSlider.value = newValue;
                textSizeSlider.dispatchEvent(new Event('change', {'bubbles': true}));
            }
        """
    },
    "decrease_text_size": {
        "description": "Diminuer la taille du texte",
        "js_code": """
            // Logique pour diminuer la taille du texte
            const sliders = Array.from(document.querySelectorAll('input[type="range"]'));
            const textSizeSlider = sliders.find(slider => 
                slider.parentElement.textContent.includes('Taille du texte')
            );
            
            if (textSizeSlider) {
                const min = parseInt(textSizeSlider.min);
                const step = parseInt(textSizeSlider.step) || 1;
                const newValue = Math.max(min, parseInt(textSizeSlider.value) - step);
                textSizeSlider.value = newValue;
                textSizeSlider.dispatchEvent(new Event('change', {'bubbles': true}));
            }
        """
    },
    "toggle_screen_reader_mode": {
        "description": "Activer/désactiver le mode lecteur d'écran",
        "js_code": """
            // Logique pour basculer le mode lecteur d'écran
            const checkboxes = Array.from(document.querySelectorAll('input[type="checkbox"]'));
            const screenReaderCheckbox = checkboxes.find(checkbox => 
                checkbox.parentElement.textContent.includes('Mode lecteur d\'écran')
            );
            
            if (screenReaderCheckbox) {
                screenReaderCheckbox.checked = !screenReaderCheckbox.checked;
                screenReaderCheckbox.dispatchEvent(new Event('change', {'bubbles': true}));
            }
        """
    },
    
    # Actions spécifiques par module
    "upload_document": {
        "description": "Télécharger un document",
        "js_code": """
            // Simuler un clic sur le bouton de téléchargement
            document.querySelector('button.uploadButton').click();
        """
    },
    "analyze_document": {
        "description": "Lancer l'analyse du document",
        "js_code": """
            // Rechercher le bouton d'analyse
            const buttons = Array.from(document.querySelectorAll('button'));
            const analyzeButton = buttons.find(button => 
                button.textContent.includes('Lancer l\'analyse') || 
                button.textContent.includes('📊')
            );
            
            if (analyzeButton) {
                analyzeButton.click();
            }
        """
    },
    "export_results": {
        "description": "Exporter les résultats",
        "js_code": """
            // Rechercher le bouton d'exportation
            const expanderHeaders = Array.from(document.querySelectorAll('.streamlit-expanderHeader'));
            const exportHeader = expanderHeaders.find(header => 
                header.textContent.includes('Exporter les résultats') || 
                header.textContent.includes('📥')
            );
            
            if (exportHeader) {
                exportHeader.click();
            }
        """
    }
}

def generate_keyboard_shortcuts_js():
    """
    Génère le code JavaScript pour gérer les raccourcis clavier avancés.
    
    Returns:
        str: Code JavaScript pour les raccourcis clavier
    """
    config = get_accessibility_config()
    
    if not config.keyboard_navigation:
        return ""
    
    # Mapper les raccourcis clavier avec les actions
    shortcuts_map = {}
    for category, shortcuts in config.get_keyboard_shortcuts().items():
        for key, action_desc in shortcuts.items():
            # Rechercher l'action correspondante dans KEYBOARD_ACTIONS
            action_key = None
            for possible_action, details in KEYBOARD_ACTIONS.items():
                if details["description"].lower() == action_desc.lower():
                    action_key = possible_action
                    break
            
            # Si aucune action trouvée, utiliser une action par défaut
            if action_key is None:
                # Créer une action générique qui affiche un message
                action_key = f"custom_{key.lower().replace('+', '_')}"
                KEYBOARD_ACTIONS[action_key] = {
                    "description": action_desc,
                    "js_code": f"""
                        console.log("Action: {action_desc}");
                        // Annoncer l'action aux lecteurs d'écran
                        announceToScreenReader("Action: {action_desc}");
                    """
                }
            
            # Convertir la clé en format JavaScript
            key_code = key.replace("Alt+", "alt+").replace("Maj+", "shift+").replace("Ctrl+", "ctrl+").replace("Échap", "escape").lower()
            shortcuts_map[key_code] = action_key
    
    # Créer le JavaScript avec les actions détaillées
    js_code = f"""
    <script>
    // Configuration des raccourcis clavier pour ValetIA
    const keyboardActions = {json.dumps(KEYBOARD_ACTIONS)};
    const keyboardShortcuts = {json.dumps(shortcuts_map)};
    
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
    
    // Gestionnaire d'événements pour les raccourcis clavier
    document.addEventListener('keydown', function(e) {{
        // Construire la combinaison de touches
        let keyCombo = '';
        if (e.altKey) keyCombo += 'alt+';
        if (e.shiftKey) keyCombo += 'shift+';
        if (e.ctrlKey) keyCombo += 'ctrl+';
        keyCombo += e.key.toLowerCase();
        
        // Vérifier si un raccourci existe
        if (keyboardShortcuts[keyCombo]) {{
            const actionKey = keyboardShortcuts[keyCombo];
            
            // Empêcher le comportement par défaut pour éviter les conflits
            e.preventDefault();
            
            console.log('Raccourci clavier: ' + keyCombo + ' -> ' + actionKey);
            
            // Exécuter l'action correspondante si elle existe
            if (keyboardActions[actionKey]) {{
                try {{
                    // Exécuter le code JavaScript de l'action
                    eval(keyboardActions[actionKey].js_code);
                    
                    // Annoncer l'action pour les lecteurs d'écran
                    announceToScreenReader('Action: ' + keyboardActions[actionKey].description);
                }} catch (error) {{
                    console.error('Erreur lors de l\\'exécution de l\\'action: ' + error);
                }}
            }}
        }}
    }});
    
    // Ajouter des attributs ARIA pour améliorer l'accessibilité
    document.addEventListener('DOMContentLoaded', function() {{
        // Ajouter des informations sur les raccourcis clavier aux éléments
        const shortcutDocs = {{}};
        
        // Extraire les descriptions de raccourcis par fonctionnalité
        for (const [combo, actionKey] of Object.entries(keyboardShortcuts)) {{
            const actionDesc = keyboardActions[actionKey]?.description || actionKey;
            shortcutDocs[actionDesc] = (shortcutDocs[actionDesc] || []).concat(combo);
        }}
        
        // Parcourir les éléments de l'interface pour ajouter les informations de raccourcis
        setTimeout(() => {{
            // Ajouter des conseils pour les boutons
            document.querySelectorAll('button').forEach(button => {{
                const buttonText = button.textContent.trim().toLowerCase();
                
                // Trouver le raccourci correspondant au texte du bouton
                for (const [desc, combos] of Object.entries(shortcutDocs)) {{
                    if (desc.toLowerCase().includes(buttonText) || buttonText.includes(desc.toLowerCase())) {{
                        // Ajouter l'attribut aria-keyshortcuts
                        button.setAttribute('aria-keyshortcuts', combos.join(' '));
                        
                        // Ajouter un tooltip
                        const title = button.getAttribute('title') || '';
                        button.setAttribute('title', `${{title}} Raccourci: ${{combos.join(', ')}}`);
                    }}
                }}
            }});
        }}, 1000);
    }});
    </script>
    """
    
    return js_code

def inject_keyboard_navigation():
    """
    Injecte le JavaScript pour la navigation avancée au clavier.
    """
    js_code = generate_keyboard_shortcuts_js()
    if js_code:
        st.markdown(js_code, unsafe_allow_html=True)
        logger.info("JavaScript pour la navigation avancée au clavier injecté")
