import reflex as rx
from ..components.layout import layout
from ..state.search_state import SearchState

def buscador_page() -> rx.Component:
    return layout(
        rx.vstack(
            rx.heading(
                "Buscador",
                size="7",
                margin_y="50",
                align_self="flex-start",
                margin_left="50px",
                margin_top="30px",
            ),
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
            rx.box(
                rx.hstack(
                    rx.icon(tag="search", color="royalblue", box_size="6"),
                    rx.input(
                        placeholder="Buscar acciones en el mercado",
                        value=SearchState.search_query,
                        on_change=SearchState.set_search_query,
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
                        on_click=SearchState.search_stock,
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
            # Results Box
            rx.box(
                rx.vstack(
                    # Show logo if present
                    rx.cond(
                        SearchState.search_result["Logo"],
                        rx.image(
                            src=SearchState.search_result["Logo"],
                            width="80px",
                            height="80px",
                            margin_bottom="10px",
                        ),
                    ),
                    # Show details except Logo
                    rx.foreach(
                        SearchState.search_result,
                        lambda item: rx.cond(
                            item[0] != "Logo",
                            rx.text(
                                f"{item[0]}: {item[1]}",
                                font_size="4",
                                color="black",
                                font_weight="bold",
                                margin_bottom="2px",
                            ),
                        ),
                    ),
                ),
                width="20%",
                margin_left="50px",
                padding="16px",
                border_radius="md",
                box_shadow="sm",
                background="white",
                margin_top="20px",
                border="4px solid black",
            ),
        )
    )

buscador = rx.page(
    route="/buscador",
    title="TradeSim - Buscador"
)(buscador_page)