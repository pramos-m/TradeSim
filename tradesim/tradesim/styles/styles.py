# styles/styles.py
from enum import Enum

class Size(Enum):
    """Tamaños estándar para la aplicación."""
    SMALL = "4"
    DEFAULT = "6"
    MEDIUM = "8"
    LARGE = "12"
    EXTRA_LARGE = "16"

class Color(Enum):
    """Colores principales de la aplicación."""
    PRIMARY = "#3B82F6"
    SECONDARY = "#1F2937"
    ACCENT = "#F59E0B"
    BACKGROUND = "#FFFFFF"
    TEXT = "#111827"

# Estilos comunes
button_styles = {
    "border_radius": "full",
    "padding_x": Size.DEFAULT.value,
    "padding_y": Size.SMALL.value,
    "_hover": {"opacity": 0.9},
}

landing_styles = {
    "background_image": "url('/home.png')",
    "background_size": "cover",
    "background_position": "center",
    "min_height": "100vh",
}