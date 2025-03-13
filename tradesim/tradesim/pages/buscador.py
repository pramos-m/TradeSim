import reflex as rx
from ..components.layout import layout

def buscador_page() -> rx.Component:
    """Placeholder page for Buscador."""
    return layout(
        rx.center(rx.text("Buscador Page"))
    )

buscador = rx.page(
    route="/buscador",
    title="TradeSim - Buscador"
)(buscador_page)