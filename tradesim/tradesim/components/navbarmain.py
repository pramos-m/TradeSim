# navbarmain.py (VERSIÓ FINAL - Amb Link a Perfil)
import reflex as rx
from ..state.auth_state import AuthState # Necessari per DEFAULT_AVATAR i fallback

# Defineix aquestes constants amb els teus valors reals
NAVBAR_HEIGHT = "60px"
DEFAULT_AVATAR = "/default_avatar.png"

def navbar(user_name: str, user_image_url: str, logo_url: str) -> rx.Component:
    """
    Navbar original amb imatge d'estat, link a perfil i fallback corregit.
    """
    return rx.box( # Box exterior per posicionament
        rx.hstack(
            # <<< Secció de perfil clicable >>>
            rx.link(
                rx.hstack(
                    # Avatar corregit (només 1, amb src i fallback)
                    rx.avatar(
                        src=user_image_url,
                        fallback=rx.cond(user_name != "", user_name[:1].upper(), "?"),
                        size="4" # Mida Radix
                    ),
                    rx.text(user_name, font_size="1.5em", font_weight="bold"),
                    spacing="2",
                    align="center",
                    _hover={"opacity": 0.8}, # Efecte visual
                    transition="all 0.2s ease-in-out", # Efecte visual
                ),
                href="/profile", # Enllaç
                _hover={"text_decoration": "none"}, # Treu subratllat
            ),
            rx.spacer(),
            # Logo
            rx.box(
                rx.image(src=logo_url, width="120px"),
                padding="0.5em",
                border_radius="md",
            ),
            width="100%",
            padding="1em", # Padding original
            align="center",
        ),
         # Estils del box exterior (per fixar la navbar)
        height=NAVBAR_HEIGHT,
        width="100%",
        bg="white",
        border_bottom="1px solid #ddd",
        position="fixed",
        top="0",
        left="0",
        z_index="1000",
    )