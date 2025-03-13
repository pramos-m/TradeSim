import reflex as rx
from ..components.layout import layout

def noticias_page() -> rx.Component:
    """Placeholder page for Noticias."""
    return layout(
        rx.center(rx.text("Noticias Page"))
    )

noticias = rx.page(
    route="/noticias",
    title="TradeSim - Noticias"
)(noticias_page)