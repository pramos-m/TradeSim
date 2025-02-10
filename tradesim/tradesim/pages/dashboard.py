import reflex as rx
from ..components.layout import layout

def dashboard() -> rx.Component:
    """Página del dashboard."""
    return layout(
        rx.vstack(
            rx.heading("Dashboard", size="2"),
            rx.text("Aquí irá tu dashboard de trading"),
            spacing="4",
            padding="4",
        )
    )