# pages/dashboard.py
import reflex as rx
from ..components.layout import layout
from ..state.auth_state import AuthState
from ..utils.auth_middleware import require_auth

@require_auth
def dashboard() -> rx.Component:
    """Página del dashboard protegida."""
    return layout(
        rx.vstack(
            rx.heading("Dashboard", size="2"),
            rx.text("Bienvenido al dashboard protegido"),
            rx.text(f"Usuario actual: {AuthState.username}"),
            rx.button(
                "Cerrar Sesión",
                on_click=AuthState.logout,
                bg="red.500",
                color="white"
            ),
            spacing="4",
            padding="4",
        )
    )