"""Module d'accessibilité pour Valetia."""
from .config import get_accessibility_config, set_accessibility_config, AccessibilityConfig, ContrastMode, ColorBlindMode, FontSize, TextToSpeech, KeyboardNavigation, ScreenReaderSupport, MotionReduction
from .functions import setup_accessibility, apply_accessibility_settings
from .components import create_accessibility_settings

__all__ = [
    "get_accessibility_config",
    "set_accessibility_config",
    "AccessibilityConfig",
    "ContrastMode",
    "ColorBlindMode",
    "FontSize",
    "TextToSpeech",
    "KeyboardNavigation",
    "ScreenReaderSupport",
    "MotionReduction",
    "setup_accessibility",
    "apply_accessibility_settings",
    "create_accessibility_settings"
]
