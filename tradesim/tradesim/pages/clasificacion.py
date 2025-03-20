import reflex as rx
from ..components.layout import layout

def clasificacion_page() -> rx.Component:
    """Placeholder page for Clasificacion."""
    return layout(
        rx.vstack(
            # Title
            rx.heading(
                "Clasificacion",
                size="7",  # Adjust the font size of the title
                margin_y="50",  # Add vertical margin to move the title down
                align_self="flex-start",  # Align the title to the far left
                margin_left="30",  # Add left margin to move the title slightly right
                margin_top="50",  # Add top margin to move the title down
            ),
            # First Box (Top 3)
            rx.box(
                rx.text("TOP 3", font_size="5", font_weight="bold", margin="1"),  # Title inside the first box
                background_image="url('/top3bkg.png')",  # Path to the background picture
                background_size="cover",  # Cover the entire box
                background_position="center",  # Center the background image
                width="90%",  # Make the box skinnier by reducing the width
                height="400px",  # Adjust the height of the first box
                margin_y="20",  # Add vertical margin to move the box down
                padding="10",  # Add padding inside the box
                border_radius="md",  # Optional: Add border radius to the box
                box_shadow="md",  # Optional: Add box shadow
            ),
            # Second Box (Top 4 to 10)
            rx.box(
                rx.text("TOP 4 TO 10", font_size="3", font_weight="bold", margin="1"),  # Title inside the second box
                width="90%",  # Make the box skinnier by reducing the width
                height="500px",  # Adjust the height of the second box
                margin_y="20",  # Add vertical margin to move the box down
                padding="10",  # Add padding inside the box
                border_radius="md",  # Optional: Add border radius to the box
                box_shadow="md",  # Optional: Add box shadow
                background="#5271ff",  # Background color of the second box
            ),
            width="100%",  # Ensure the content spans the full width
            align_items="center",  # Center-align the content horizontally
            padding="20",  # Add padding around the content
        )
    )

clasificacion = rx.page(
    route="/clasificacion",
    title="TradeSim - Clasificacion"
)(clasificacion_page)