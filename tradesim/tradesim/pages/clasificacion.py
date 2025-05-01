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
                margin_left="50px",  # Add left margin to move the title slightly right
                margin_top="30px",  # Add top margin to move the title down
            ),
            # First Box (Top 3)
            rx.box(
                rx.text(
                    "TOP 3",
                    size="6",  # Adjust the font size to make it bigger
                    font_weight="bold",  # Make the text bold
                    margin_top="20px",  # Move the text down
                    margin_left="25px",  # Move the text to the right
                ),
                background_image="url('/top3bkg.png')",  # Path to the background picture
                background_size="cover",  # Cover the entire box
                background_position="center",  # Center the background image
                width="90%",  # Make the box skinnier by reducing the width
                height="550px",  # Adjust the height of the first box
                margin_y="20",  # Add vertical margin to move the box down
                padding="10",  # Add padding inside the box
                border_radius="md",  # Optional: Add border radius to the box
                box_shadow="md",  # Optional: Add box shadow
                margin_top="20px",  # Add top margin to move the box down
            ),
            # Second Box (Top 4 to 10)
            rx.box(
                rx.text(
                    "TOP 4 TO 10",  
                    size="5",  # Adjust the font size to make it bigger
                    font_weight="bold",  # Make the text bold
                    margin_top="20px",  # Move the text down
                    margin_left="25px",  # Move the text to the right
                ),
                width="90%",  # Make the box skinnier by reducing the width
                height="500px",  # Adjust the height of the second box
                margin_y="20",  # Add vertical margin to move the box down
                padding="10",  # Add padding inside the box
                border_radius="md",  # Optional: Add border radius to the box
                box_shadow="md",  # Optional: Add box shadow
                background="lightgray",  # Background color of the second box
                margin_top="25px",  # Add top margin to move the box down
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