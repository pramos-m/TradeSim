# buttons.py
import reflex as rx
from ..state.auth_state import AuthState

def navbar_button() -> rx.Component:
    """Botón de iniciar sesión con flecha."""
    return rx.button(
        rx.hstack(
            "Iniciar Sesión",
            rx.icon("arrow-right", size=32),
            spacing="4",
            align_items="center",
        ),
        on_click=lambda: AuthState.set_active_tab("login"),
        bg="white",
        color="black",
        border_radius="9999px",
        width="200px",    # Ancho específico
        height="70px",    # Altura específica
        font_weight="medium",
        font_size="21px",  # Aumentado de 2xl a 3xl
        _hover={"bg": "gray.100"},
        border="1px solid #E2E8F0",
        box_shadow="2px -2px 4px rgba(0, 0, 0, 0.1)",
        display="flex",
        justify_content="center",
        align_items="center",
    )

def comenzar_button() -> rx.Component:
    """Botón de comenzar con flecha."""
    return rx.button(
        rx.hstack(
            rx.box(
                rx.text(
                    "  Comenzar",
                    font_size="27px",
                    font_weight="medium",
                ),
                width="150px",  # Ancho fijo para la sección de texto
                display="flex",
                justify_content="flex-start",
                # pl="30px",
            ),
            rx.center(
                rx.icon("arrow-right", size=50, color="black"),
                bg="white",
                border_radius="9999px",
                w="50px",
                h="50px",
                flex="none",
            ),
            spacing="0",
            align_items="center",
            width="100%",
            justify_content="space-between",
            px="10px",
        ),
        on_click=lambda: AuthState.set_active_tab("register"),
        bg="black",
        color="white",
        border_radius="9999px",
        width="250px",    # Ancho específico
        height="75px",    # Altura específica
        p="0",
        font_weight="medium",
        _hover={"bg": "gray.800"},
        box_shadow="md",
        overflow="hidden",
    )