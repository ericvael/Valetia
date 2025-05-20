"""
Configuration pour les fonctionnalités d'accessibilité.
"""
from enum import Enum
from typing import Dict, Optional, Any

from pydantic import BaseModel

# Définition des modes d'accessibilité
class ContrastMode(str, Enum):
    NORMAL = "normal"
    HIGH = "high"
    VERY_HIGH = "very_high"

class ColorBlindMode(str, Enum):
    NONE = "none"
    PROTANOPIA = "protanopia"  # Déficience rouge-vert (type 1)
    DEUTERANOPIA = "deuteranopia"  # Déficience rouge-vert (type 2)
    TRITANOPIA = "tritanopia"  # Déficience bleu-jaune
    ACHROMATOPSIA = "achromatopsia"  # Vision monochrome

class FontSize(str, Enum):
    NORMAL = "normal"
    LARGE = "large"
    VERY_LARGE = "very_large"

class TextToSpeech(str, Enum):
    OFF = "off"
    ON = "on"

class KeyboardNavigation(str, Enum):
    OFF = "off"
    ON = "on"

class ScreenReaderSupport(str, Enum):
    OFF = "off"
    ON = "on"

class MotionReduction(str, Enum):
    OFF = "off"
    ON = "on"

class AccessibilityConfig(BaseModel):
    """Configuration pour l'accessibilité de l'interface."""
    contrast_mode: ContrastMode = ContrastMode.NORMAL
    color_blind_mode: ColorBlindMode = ColorBlindMode.NONE
    font_size: FontSize = FontSize.NORMAL
    text_to_speech: TextToSpeech = TextToSpeech.OFF
    keyboard_navigation: KeyboardNavigation = KeyboardNavigation.OFF
    screen_reader_support: ScreenReaderSupport = ScreenReaderSupport.OFF
    motion_reduction: MotionReduction = MotionReduction.OFF
    custom_styles: Optional[Dict[str, Any]] = None

# Singleton pour la configuration d'accessibilité
_accessibility_config = AccessibilityConfig()

def get_accessibility_config() -> AccessibilityConfig:
    """
    Récupère la configuration d'accessibilité actuelle.
    
    Returns:
        AccessibilityConfig: La configuration d'accessibilité
    """
    return _accessibility_config

def set_accessibility_config(config: AccessibilityConfig) -> None:
    """
    Met à jour la configuration d'accessibilité.
    
    Args:
        config: La nouvelle configuration
    """
    global _accessibility_config
    _accessibility_config = config
