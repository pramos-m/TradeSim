# tradesim/components/layout.py (CORREGIDO FINALÍSIMO - user_image_url añadido)
import reflex as rx
from ..state.auth_state import AuthState
# Asegúrate que el nombre del archivo navbar sea correcto (navbarmain o navbar)
from .navbarmain import navbar # O from .navbar import navbar si se llama así
from .sidebar import sidebar

def layout(content: rx.Component) -> rx.Component:
    """
    Application layout for authenticated pages with navbar and sidebar.
    """
    return rx.hstack(
        sidebar(),
        rx.vstack(
            navbar( # Llamada a navbar
                user_name=AuthState.username,
                # *** CORRECCIÓN AQUÍ: Añadir/Descomentar user_image_url ***
                user_image_url="/elonmusk.png", # Placeholder - Asegúrate que esta imagen exista en /assets o cambia la ruta
                logo_url="/logonavbar.png",
            ),
            content, # El contenido específico de la página
            width="100%",
            height="100vh",
            background="rgb(248, 249, 250)",
            padding_left="260px", # Espacio para sidebar
            padding_right="20px",
            padding_top="20px",
            padding_bottom="20px",
            overflow="auto",
            align_items="stretch"
        ),
        width="100%",
        min_height="100vh",
        align_items="stretch",
        spacing="0",
        # No lleva on_mount aquí
    )