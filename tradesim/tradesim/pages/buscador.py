import reflex as rx
from ..components.layout import layout
from ..state.search_state import SearchState  # Import the state

def buscador_page() -> rx.Component:
    """Placeholder page for Buscador."""
    return layout(
        rx.vstack(
            # Title
            rx.heading(
                "Buscador",
                size="7",
                margin_y="50",
                align_self="flex-start",
                margin_left="50px",
                margin_top="30px",
            ),
            # Centered Text
            rx.center(
                rx.vstack(
                    rx.text(
                        "Encuentra Tu",
                        size="8",
                        font_weight="normal",
                        margin_left="50px",
                        margin_top="20px",
                    ),
                    rx.text(
                        "Mejor Opción Aqui",
                        size="8",
                        font_weight="bold",
                        color="royalblue",
                        margin_left="50px",
                    ),
                    rx.box(
                        rx.text(
                            "En esta herramienta de búsqueda, puede explorar una amplia gama de acciones globales de varios mercados. Encuentre datos en tiempo real sobre las empresas y tome decisiones de inversión informadas con facilidad.",
                            font_size="5",
                            font_weight="normal",
                            color="gray",
                            line_height="1.5",
                            margin_top="10px",
                        ),
                        width="60%",
                        padding="20",
                        margin_top="30",
                        border_radius="md",
                        box_shadow="sm",
                        background="white",
                        margin_left="50px",
                    ),
                ),
                width="100%",
            ),
            # Search Bar
            rx.box(
                rx.hstack(
                    rx.icon(tag="search", color="royalblue", box_size="6"),
                    rx.input(
                        placeholder="Buscar acciones en el mercado",
                        value=SearchState.search_query,  # Bind to state
                        on_change=SearchState.set_search_query,  # Update state on input
                        width="100%",
                        padding="8",
                        border="none",
                        outline="none",
                        font_size="5",
                    ),
                    rx.button(
                        "Buscar",
                        color="white",
                        background="royalblue",
                        padding_x="15",
                        padding_y="8",
                        border_radius="md",
                        _hover={"background": "blue"},
                        on_click=SearchState.search_stock,  # Trigger search on click
                    ),
                    spacing="1",
                    align_items="center",
                    width="100%",
                    padding="10",
                    border="1px solid lightgray",
                    border_radius="md",
                    background="white",
                    margin_top="10px",
                ),
                width="80%",
                box_shadow="sm",
                margin_left="50px",
            ),
            # Search Results
            rx.box(
                rx.vstack(
                    rx.foreach(
                        SearchState.search_result.items(),  # Iterate over the dictionary
                        lambda item: rx.text(
                            f"{item[0]}: {item[1]}",  # Format each key-value pair
                            font_size="5",
                            color="royalblue",
                            font_weight="bold",
                        ),
                    )
                ),
                width="80%",
                margin_left="50px",
                padding="20",
                border_radius="md",
                box_shadow="sm",
                background="white",
                margin_top="20px",
            ),
        )
    )

buscador = rx.page(
    route="/buscador",
    title="TradeSim - Buscador"
)(buscador_page)