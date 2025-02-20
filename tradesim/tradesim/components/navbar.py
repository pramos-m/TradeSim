import reflex as rx
from ..styles.colors import colors

def navbar() -> rx.Component:
    """Barra de navegación."""
    return rx.hstack(
        rx.heading("TradeSim", size="2"),
        rx.spacer(),
        rx.hstack(
            rx.link("Home", href="/", padding="2"),
            rx.link("Dashboard", href="/dashboard", padding="2"),
        ),
        width="100%",
        padding="4",
        background=colors["primary"],
        color="white", 
    )