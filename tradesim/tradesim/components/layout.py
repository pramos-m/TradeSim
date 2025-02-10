import reflex as rx
from ..components.navbar import navbar
from ..styles.colors import colors

def layout(content: rx.Component) -> rx.Component:
    """Layout principal de la aplicación."""
    return rx.vstack(
        navbar(),
        rx.box(
            content,
            padding="4",
            width="100%",
            max_width="1200px",
            margin="0 auto",
        ),
        min_height="100vh",
        background=colors["background"],
        color=colors["text"],
        spacing="4",
    )