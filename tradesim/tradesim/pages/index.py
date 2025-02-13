import reflex as rx
from ..components.layout import layout
from ..state.base_state import State

def index() -> rx.Component:
    """Página principal."""
    return layout(
        rx.vstack(
            rx.heading("TradeSim", size="4"),
            rx.text("Tu plataforma de simulación de trading"),
            rx.cond(
                State.is_logged,
                rx.text(f"Bienvenido, {State.username}!"),
                rx.link(
                    "Iniciar Sesión",
                    href="/login",
                    color="blue.500",
                ),
            ),
            rx.box(
                rx.hstack(
                    rx.button(
                        "-",
                        on_click=State.decrement,
                        size="2",
                        background="red.500",
                        color="white"
                    ),
                    rx.heading(State.count, size="3"),
                    rx.button(
                        "+",
                        on_click=State.increment,
                        size="2",
                        background="green.500",
                        color="white"
                    ),
                    spacing="4"
                ),
                padding="4",
                border_radius="md",
                background="gray.100",
                box_shadow="md",
            ),
            spacing="6",
            align="center",
            padding="6"
        )
    )
