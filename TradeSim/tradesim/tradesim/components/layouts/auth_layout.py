# tradesim/components/layouts/auth_layout.py
import reflex as rx

def auth_layout(content: rx.Component) -> rx.Component:
    """Layout for authenticated pages."""
    return rx.box(
        content,
        width="100%",
        min_height="100vh",
        background="#ffffff",
        color="#333333",
    )