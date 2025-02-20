# tradesim/components/buttons.py
import reflex as rx
from ..state.auth_state import AuthState

def navbar_button() -> rx.Component:
    """Botón de iniciar sesión con flecha."""
    return rx.button(
        rx.hstack(
            "Iniciar Sesion",
            rx.icon("arrow-right", size=16),
        ),
        on_click=lambda: AuthState.set_active_tab("login"),
        bg="white",
        color="black",
        border_radius="full",
        px="6",
        py="2",
        font_weight="normal",
        font_size="sm",
        _hover={"bg": "gray.100"},
        border="1px solid #E2E8F0",
    )

def comenzar_button() -> rx.Component:
    """Botón de comenzar con flecha."""
    return rx.button(
        rx.hstack(
            "Comenzar",
            rx.box(
                rx.icon("arrow-right", size=18),
                bg="white",
                color="black",
                padding="2",
                border_radius="full",
                ml="2",
            ),
        ),
        on_click=lambda: AuthState.set_active_tab("register"),
        bg="black",
        color="white",
        border_radius="full",
        px="8",
        py="4",
        font_weight="medium",
        _hover={"bg": "gray.800"},
    )