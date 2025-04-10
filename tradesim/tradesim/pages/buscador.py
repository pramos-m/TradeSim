import reflex as rx
from ..components.layout import layout

def buscador_page() -> rx.Component:
    """Placeholder page for Buscador."""
    return layout(
        rx.vstack(
            # Title
            rx.heading(
                "Buscador",
                size="7",  # Adjust the font size of the title
                margin_y="50",  # Add vertical margin to move the title down
                align_self="flex-start",  # Align the title to the far left
                margin_left="50px",  # Add left margin to move the title slightly right
                margin_top="30px",  # Add top margin to move the title down
            ),
            # Centered Text
            rx.center(
                rx.vstack(
                    # First Line: "Encuentra Tu"
                    rx.text(
                        "Encuentra Tu",
                        size="8",  # Adjust the font size of the title
                        font_weight="normal",  # Normal weight for this line
                        margin_left="50px",  # Add left margin to move the title slightly right
                        margin_top="20px",  # Add top margin to move the title down
                    ),
                    # Second Line: "Mejor Opción Aqui"
                    rx.text(
                        "Mejor Opción Aqui",
                        size="8",  # Adjust the font size of the title
                        font_weight="bold",  # Bold for emphasis
                        color="royalblue",  # Blue color for "Mejor Opción"
                        margin_left="50px",  # Add left margin to move the title slightly right
                    ),
                    
                    rx.box(
                        rx.text(
                            "En esta herramienta de búsqueda, puede explorar una amplia gama de acciones globales de varios mercados. Encuentre datos en tiempo real sobre las empresas y tome decisiones de inversión informadas con facilidad.",
                            font_size="5",  # Smaller font size for the definition
                            font_weight="normal",  # Normal weight for the text
                            color="gray",  # Gray color for the text
                            line_height="1.5",  # Adjust line height for better readability
                            margin_top="10px",  # Add top margin to move the title down
                        ),
                        width="60%",  # Adjust the width of the box
                        padding="20",  # Add padding inside the box
                        margin_top="30",  # Add top margin to separate it from the centered text
                        border_radius="md",  # Optional: Add border radius to the box
                        box_shadow="sm",  # Optional: Add a subtle shadow to the box
                        background="white",  # Background color of the box
                        margin_left="50px",  # Add left margin to move the title slightly right
                    ),
                ),
                width="100%",  # Ensure the content spans the full width
            ),
            # Search Bar
            rx.box(
                rx.hstack(
                    # Search Icon
                    rx.icon(tag="search", color="royalblue", box_size="6"),  # Add the 'tag' argument
                    # Input Field
                    rx.input(
                        placeholder="Buscar acciones en el mercado",
                        width="100%",  # Make the input field take up the remaining space
                        padding="8",  # Reduce padding inside the input field
                        border="none",  # Remove the border
                        outline="none",  # Remove the outline
                        font_size="5",  # Adjust the font size
                    ),
                    # Search Button
                    rx.button(
                        "Buscar",
                        color="white",  # Text color
                        background="royalblue",  # Background color
                        padding_x="15",  # Reduce horizontal padding
                        padding_y="8",  # Reduce vertical padding
                        border_radius="md",  # Add border radius
                        _hover={"background": "blue"},  # Change background color on hover
                    ),
                    spacing="1",  # Reduce spacing between the icon, input field, and button
                    align_items="center",  # Align items vertically
                    width="100%",  # Make the search bar take up the full width
                    padding="10",  # Add padding inside the search bar
                    border="1px solid lightgray",  # Add a border around the search bar
                    border_radius="md",  # Add border radius to the search bar
                    background="white",  # Background color of the search bar
                    margin_top="10px",  # Add top margin to move the title down
                ),
                width="80%",  # Adjust the width of the entire search bar container
                box_shadow="sm",  # Optional: Add a subtle shadow to the search bar
                margin_left="50px",  # Add left margin to move the title slightly right
            ),
        )
    )

buscador = rx.page(
    route="/buscador",
    title="TradeSim - Buscador"
)(buscador_page)