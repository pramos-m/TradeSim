import reflex as rx
from ..components.layouts.landing_layout import landing_layout
from ..components.buttons import navbar_button, comenzar_button

def index_content() -> rx.Component:
    """Landing page content."""
    return rx.box(
        # Navbar
        rx.hstack(
            rx.image(src="/logo.png", height="24px", width="auto"),
            rx.spacer(),
            rx.link(
                navbar_button(),
                href="/login",
            ),
            width="100%",
            padding="6",
            z_index="2",
        ),
        # Hero section
        rx.vstack(
            rx.box(
                rx.heading(
                    "Bienvenido\na TradeSim!!!",
                    font_family="mono",
                    size="7",
                    white_space="pre-line",
                    color="black",
                    letter_spacing="tight",
                ),
                bg="white",
                padding="6",
                border_radius="lg",
                box_shadow="sm",
            ),
            rx.link(
                comenzar_button(),
                href="/login",
            ),
            spacing="8",
            align_items="flex-start",
            padding_top="16",
            padding_x="6",
            position="absolute",
            top="25%",
            left="10%",
        ),
        width="100%",
        height="100vh",
        position="relative",
    )

def index() -> rx.Component:
    """Landing page with layout."""
    return landing_layout(index_content())

# Configure the page
index = rx.page(
    route="/",
    title="TradeSim - Inicio",
)(index)