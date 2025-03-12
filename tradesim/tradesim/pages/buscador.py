import reflex as rx
from ..state.auth_state import AuthState
from ..components.navbarmain import navbar
from ..components.sidebar import sidebar

def buscador_page() -> rx.Component:
    """Placeholder page for Buscador."""
    return rx.hstack(
        sidebar(),
        rx.vstack(
            navbar(
                user_name=AuthState.username,  # Pass the username from AuthState
                user_image_url="/elonmusk.png",  # Path to the user's profile picture
                logo_url="/logonavbar.png",  # Path to the logo
            ),
            rx.center(rx.text("Buscador Page")),
            width="100%",
            min_height="100vh",
            background="gray.50",
        ),
        width="100%",
        min_height="100vh",
    )

buscador = rx.page(
    route="/buscador",
    title="TradeSim - Buscador"
)(buscador_page)