import reflex as rx
from ..state.auth_state import AuthState
from ..utils.auth_middleware import require_auth

@require_auth
def dashboard() -> rx.Component:
    """Dashboard protegido."""
    return rx.vstack(
        rx.heading(f"Bienvenido {AuthState.username}!"),
        rx.button(
            "Cerrar Sesión",
            on_click=AuthState.logout,
            color_scheme="red",
        ),
        padding="4",
        spacing="4",
    )
