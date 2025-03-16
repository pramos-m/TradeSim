import reflex as rx
from ..components.layout import layout

def clasificacion_page() -> rx.Component:
    """Placeholder page for Clasificacion."""
    return layout(
        rx.vstack(
            rx.heading(
                "Clasificacion",
                size="5",  # Adjust the font size of the title
                margin_y="5",  # Adjust the vertical margin around the title
                align_self="flex-start",  # Align the title to the far left
                margin_left="10",  # Adjust the left margin to move the title right
                margin_top="10",  # Adjust the top margin to move the title down
                margin_bottom="5",  # Adjust the bottom margin to move the title up
            ),
            rx.box(
                rx.text("TOP 3", font_size="3", font_weight="bold", margin="1"),  # Title inside the first box
                # Placeholder for the background picture
                margin_top="20",  # Adjust the top margin to move the box down
                background_image="url('/top3bkg.png')",  # Path to the background picture
                background_size="cover",  # Cover the entire box
                background_position="center",  # Center the background image
                width="100%",  # Adjust the width of the first box
                height="300px",  # Adjust the height of the first box
                margin_y="1",  # Vertical margin
                padding="1",  # Padding inside the box
                border_radius="md",  # Optional: Add border radius to the box
                box_shadow="md",  # Optional: Add box shadow
            ),
            rx.box(
                rx.text("TOP 4 TO 10", font_size="2", font_weight="bold", margin="1"),  # Title inside the second box
                width="100%",  # Adjust the width of the second box
                height="400px",  # Adjust the height of the second box
                margin_y="1",  # Vertical margin
                padding="1",  # Padding inside the box
                border_radius="md",  # Optional: Add border radius to the box
                box_shadow="md",  # Optional: Add box shadow
                background="white",  # Background color of the second box
            ),
            width="100%",  # Ensure the content spans the full width
            align_items="center",  # Center-align the content horizontally
            padding="2",  # Add padding around the content
        )
    )

clasificacion = rx.page(
    route="/clasificacion",
    title="TradeSim - Clasificacion"
)(clasificacion_page)