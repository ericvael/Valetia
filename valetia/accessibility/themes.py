"""
Thèmes et styles avancés pour l'accessibilité de ValetIA.

Ce module fournit des styles CSS avancés pour les différents modes de contraste
et de daltonisme, avec des optimisations spécifiques pour chaque combinaison.
"""

import streamlit as st
from valetia.logger.loguru_adapter import loguru_logger as logger
from .config import ContrastMode, ColorBlindMode, get_accessibility_config

# Palettes de couleurs optimisées pour chaque mode daltonien
COLOR_PALETTES = {
    # Mode normal
    ColorBlindMode.NORMAL.value: {
        "blue": "#0063B1",
        "red": "#D60036", 
        "green": "#008736",
        "orange": "#D97700",
        "purple": "#8031A7",
        "yellow": "#F2C811",
        "cyan": "#0099BB",
        "magenta": "#C42C85",
        "gray": "#505050"
    },
    
    # Protanopie (difficulté à percevoir le rouge)
    ColorBlindMode.PROTANOPIA.value: {
        "blue": "#0070C0",  # Bleu plus vif
        "red": "#E09200",   # Orange au lieu de rouge
        "green": "#00A9A9", # Cyan au lieu de vert
        "orange": "#FFB000", # Orange-jaune plus vif
        "purple": "#6B77FF", # Bleu-violet
        "yellow": "#F9F000", # Jaune vif
        "cyan": "#00BBD6",  # Cyan vif
        "magenta": "#AC8AFF", # Violet au lieu de magenta
        "gray": "#505050"
    },
    
    # Deutéranopie (difficulté à percevoir le vert)
    ColorBlindMode.DEUTERANOPIA.value: {
        "blue": "#005CE6",  # Bleu pur
        "red": "#D98600",   # Orange doré au lieu de rouge
        "green": "#00BDD6", # Bleu clair au lieu de vert
        "orange": "#E6AC00", # Jaune-orangé
        "purple": "#5561FF", # Bleu-violet
        "yellow": "#FFFB00", # Jaune vif
        "cyan": "#00C9FF",  # Bleu clair
        "magenta": "#9F7DFF", # Bleu-violet au lieu de magenta
        "gray": "#505050"
    },
    
    # Tritanopie (difficulté à percevoir le bleu)
    ColorBlindMode.TRITANOPIA.value: {
        "blue": "#E55763",  # Rouge-rose au lieu de bleu
        "red": "#FF0033",   # Rouge pur
        "green": "#D6C700", # Jaune-vert au lieu de vert
        "orange": "#FF7700", # Orange vif
        "purple": "#FF66A3", # Rose au lieu de violet
        "yellow": "#E6D100", # Jaune doré
        "cyan": "#FFB0C9",  # Rose pâle au lieu de cyan
        "magenta": "#FF4D94", # Rose au lieu de magenta
        "gray": "#505050"
    },
    
    # Achromatopsie (vision en noir et blanc)
    ColorBlindMode.ACHROMATOPSIA.value: {
        "blue": "#3F3F3F",   # Gris foncé
        "red": "#2A2A2A",    # Presque noir
        "green": "#5A5A5A",  # Gris moyen
        "orange": "#474747", # Gris
        "purple": "#383838", # Gris foncé
        "yellow": "#696969", # Gris clair
        "cyan": "#606060",   # Gris moyen
        "magenta": "#333333", # Gris très foncé
        "gray": "#505050"
    }
}

# Constantes pour les niveaux de contraste
CONTRAST_RATIOS = {
    ContrastMode.NORMAL.value: {
        "text_background": 4.5,  # Minimum recommandé par WCAG AA
        "large_text": 3,         # Minimum pour texte large (WCAG AA)
        "ui_elements": 3         # Éléments d'interface
    },
    ContrastMode.HIGH.value: {
        "text_background": 7,    # Recommandé par WCAG AAA
        "large_text": 4.5,       # WCAG AAA pour texte large
        "ui_elements": 4.5       # Éléments d'interface renforcés
    },
    ContrastMode.VERY_HIGH.value: {
        "text_background": 10,   # Très fort contraste
        "large_text": 7,         # Contraste maximal
        "ui_elements": 7         # Contraste maximal pour interfaces
    }
}

def apply_advanced_theme():
    """
    Applique des styles CSS avancés pour le mode d'accessibilité actuel.
    Cette fonction génère des CSS spécifiques pour chaque combinaison
    de mode de contraste et mode daltonien.
    """
    config = get_accessibility_config()
    palette = COLOR_PALETTES.get(config.colorblind_mode, COLOR_PALETTES[ColorBlindMode.NORMAL.value])
    
    # Ajuster les couleurs selon le niveau de contraste
    if config.contrast_mode == ContrastMode.HIGH.value:
        # Assombrir les couleurs pour augmenter le contraste
        for key in palette:
            if key != "gray":  # Ne pas modifier le gris
                # Assombrir les couleurs
                palette[key] = darken_color(palette[key], 15)
    elif config.contrast_mode == ContrastMode.VERY_HIGH.value:
        # Utiliser des couleurs primaires à fort contraste
        if config.colorblind_mode == ColorBlindMode.ACHROMATOPSIA.value:
            # Pour l'achromatopsie en contraste très élevé, utiliser noir et blanc
            palette = {
                "blue": "#000000",    # Noir
                "red": "#000000",     # Noir
                "green": "#000000",   # Noir
                "orange": "#000000",  # Noir
                "purple": "#000000",  # Noir
                "yellow": "#000000",  # Noir
                "cyan": "#000000",    # Noir
                "magenta": "#000000", # Noir
                "gray": "#000000"     # Noir
            }
        else:
            # Pour les autres modes, utiliser des couleurs primaires vives
            for key in palette:
                if key != "gray":  # Ne pas modifier le gris
                    # Assombrir davantage les couleurs
                    palette[key] = darken_color(palette[key], 30)
    
    # Générer le CSS avec la palette de couleurs optimisée
    css = f"""
    /* Thème d'accessibilité avancé pour {config.contrast_mode}/{config.colorblind_mode} */
    
    /* Couleurs de base */
    :root {{
        --a11y-primary: {palette["blue"]};
        --a11y-secondary: {palette["purple"]};
        --a11y-success: {palette["green"]};
        --a11y-warning: {palette["orange"]};
        --a11y-error: {palette["red"]};
        --a11y-info: {palette["cyan"]};
        --a11y-highlight: {palette["yellow"]};
    }}
    
    /* Améliorations de contraste pour le texte */
    p, li, div, span {{
        color: {"#000000" if config.contrast_mode != ContrastMode.NORMAL.value else "#262730"} !important;
    }}
    
    /* Améliorer la visibilité du focus */
    *:focus {{
        outline: 3px solid {palette["blue"]} !important;
        outline-offset: 2px !important;
    }}
    
    /* Boutons et éléments interactifs */
    .stButton>button {{
        background-color: var(--a11y-primary) !important;
        color: white !important;
        font-weight: {"bold" if config.contrast_mode != ContrastMode.NORMAL.value else "normal"} !important;
        border: {"2px solid #000000" if config.contrast_mode == ContrastMode.VERY_HIGH.value else "none"} !important;
    }}
    
    .stButton>button:hover {{
        background-color: {darken_color(palette["blue"], 10)} !important;
    }}
    
    /* Champs de formulaire */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stTextArea>div>div>textarea {{
        border: {"2px solid #000000" if config.contrast_mode != ContrastMode.NORMAL.value else "1px solid #ccc"} !important;
    }}
    
    /* Boîtes informatives */
    .stAlert {{
        border-width: {"2px" if config.contrast_mode != ContrastMode.NORMAL.value else "1px"} !important;
    }}
    
    /* Éléments dépliables */
    .streamlit-expanderHeader {{
        font-weight: {"bold" if config.contrast_mode != ContrastMode.NORMAL.value else "normal"} !important;
    }}
    
    /* Onglets */
    .stTabs [data-baseweb="tab-list"] {{
        gap: {"8px" if config.contrast_mode != ContrastMode.NORMAL.value else "1px"} !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {palette["blue"]} !important;
        color: white !important;
        font-weight: bold !important;
    }}
    
    /* Barres de progression et indicateurs */
    .stProgress>div>div>div {{
        background-color: var(--a11y-success) !important;
    }}
    
    /* Tableaux */
    .stTable th {{
        background-color: {palette["blue"]} !important;
        color: white !important;
        font-weight: bold !important;
    }}
    
    .stTable tr:nth-child(even) {{
        background-color: {"#f2f2f2" if config.contrast_mode == ContrastMode.NORMAL.value else "#e6e6e6"} !important;
    }}
    
    /* Widgets de sélection */
    .stSelectbox [data-baseweb="select"] {{
        border: {"2px solid #000000" if config.contrast_mode != ContrastMode.NORMAL.value else "1px solid #ccc"} !important;
    }}
    """
    
    # Injecter le CSS dans Streamlit
    st.markdown(f"""
    <style>
    {css}
    </style>
    """, unsafe_allow_html=True)
    
    logger.info(f"Thème d'accessibilité avancé appliqué: {config.contrast_mode}/{config.colorblind_mode}")

def darken_color(hex_color, percent):
    """
    Assombrit une couleur hexadécimale du pourcentage spécifié.
    
    Args:
        hex_color (str): Couleur au format hexadécimal (#RRGGBB)
        percent (int): Pourcentage d'assombrissement (0-100)
    
    Returns:
        str: Couleur assombrie au format hexadécimal
    """
    # Convertir la couleur hexadécimale en RGB
    h = hex_color.lstrip('#')
    r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    
    # Assombrir
    factor = 1 - percent/100
    r = max(0, int(r * factor))
    g = max(0, int(g * factor))
    b = max(0, int(b * factor))
    
    # Reconvertir en hexadécimal
    return f"#{r:02x}{g:02x}{b:02x}"
