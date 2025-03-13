import reflex as rx
from ..components.layout import layout

def clasificacion_page() -> rx.Component:
    """Placeholder page for Clasificacion."""
    return layout(
        rx.center(rx.text("Clasificacion Page"))
    )

clasificacion = rx.page(
    route="/clasificacion",
    title="TradeSim - Clasificacion"
)(clasificacion_page)