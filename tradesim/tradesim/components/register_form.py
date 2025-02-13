import reflex as rx
from ..state.auth_state import AuthState

def register_form() -> rx.Component:
    """Formulario de registro."""
    return rx.vstack(
        rx.heading("Registro", size="4"),
        rx.input(
            placeholder="Usuario",
            on_change=AuthState.set_username,
            margin_y="2",
        ),
        rx.input(
            placeholder="Email",
            type_="email",
            on_change=AuthState.set_email,
            margin_y="2",
        ),
        rx.input(
            placeholder="Contraseña",
            type_="password",
            on_change=AuthState.set_password,
            margin_y="2",
        ),
        rx.button(
            "Registrarse",
            on_click=AuthState.register,
            bg="green.500",
            color="white",
            margin_y="2",
        ),
        rx.text(
            AuthState.error_message,
            color="red.500",
            condition=AuthState.error_message != "",
        ),
        padding="6",
        bg="white",
        border_radius="lg",
        box_shadow="lg",
        width="100%",
        max_width="400px",
    )
