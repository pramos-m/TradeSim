# tradesim/components/layout.py
import reflex as rx

def layout(content: rx.Component) -> rx.Component:
    """Application layout for authenticated pages."""
    return rx.box(
        content,
        width="100%",
        min_height="100vh",
        # Quitamos el background blanco o lo hacemos transparente
        color="#333333",
    )