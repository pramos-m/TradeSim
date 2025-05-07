import reflex as rx
from ..components.layout import layout
from ..state.search_state import SearchState

def buscador_page() -> rx.Component:
    return layout(
        rx.vstack(
            rx.heading(
                "Buscador",
                size="6",
                margin_y="50",
                align_self="flex-start",
                margin_left="30px",
                margin_top="20px",
            ),
            # Centered intro texts
            rx.box(
                rx.vstack(
                    rx.text(
                        "Encuentra Tu",
                        size="8",
                        font_weight="normal",
                        text_align="center",
                        width="100%",
                        margin_top="20px",
                    ),
                    rx.text(
                        "Mejor Opción Aqui",
                        size="8",
                        font_weight="bold",
                        color="royalblue",
                        text_align="center",
                        width="100%",
                        margin_top="0px",
                    ),
                    align_items="center",
                    width="100%",
                ),
                width="100%",
                display="flex",
                justify_content="center",
            ),
            rx.box(
                rx.text(
                    "En esta herramienta de búsqueda, puede explorar una amplia gama de acciones globales de varios mercados. Encuentre datos en tiempo real sobre las empresas y tome decisiones de inversión informadas con facilidad.",
                    font_size="10",
                    font_weight="normal",
                    color="gray",
                    line_height="1.5",
                    text_align="center",
                    width="650px",
                    margin_top="10px",
                    align_self="center",
                ),
                width="100%",
                display="flex",
                justify_content="center",
            ),
            rx.box(
                rx.hstack(
                    rx.icon(tag="search", color="royalblue", box_size="6"),
                    rx.box(width="1px", height="28px", background="#e0e0e0", margin_x="10px"),  # vertical divider
                    rx.input(
                        placeholder="buscar acciones en el mercado",
                        value=SearchState.search_query,
                        on_change=SearchState.set_search_query,
                        width="100%",
                        padding="0 8px",
                        border="none",
                        outline="none",
                        font_size="6",
                        background="transparent",
                    ),
                    rx.button(
                        "Buscar",
                        color="white",
                        background="royalblue",
                        padding_x="24px",
                        padding_y="10px",
                        border_radius="md",
                        _hover={"background": "blue"},
                        on_click=SearchState.search_stock,
                    ),
                    spacing="0",
                    align_items="center",
                    width="100%",
                ),
                width="700px",
                background="#fdf9f6",
                border_radius="12px",
                box_shadow="0 6px 24px 0 #ececec",
                padding="8px",
                margin_top="20px",
                align_self="center",
            ),
            # Results Box: only show if a search has been made
            rx.cond(
                SearchState.search_result.contains("Name"),
                rx.box(
                    rx.hstack(
                        # Left: Price, Name, Buy button
                        rx.vstack(
                            rx.text(
                                f"{SearchState.search_result['Current Price']} €",
                                font_size="25px",
                                font_weight="bold",
                                color="black",
                            ),
                            rx.text(
                                f"{SearchState.search_result['Name']}",
                                font_size="12px",
                                color="black",
                                margin_top="0px",
                            ),
                            rx.button(
                                "Buy",
                                color="white",
                                background="royalblue",
                                border_radius="md",
                                width="80px",
                                margin_top="18px",
                                cursor="pointer",
                            ),
                            align_items="flex-start",
                            spacing="0",
                            flex="1",
                        ),
                        # Right: Logo and Ver Detalles button
                        rx.vstack(
                            rx.cond(
                                SearchState.search_result["Logo"],
                                rx.image(
                                    src=SearchState.search_result["Logo"],
                                    width="100px",
                                    height="65px",
                                ),
                            ),
                            rx.button(
                                "Ver Detalles",
                                color="black",
                                background="none",
                                border="none",
                                border_radius="md",
                                width="auto",
                                white_space="nowrap",
                                text_decoration="underline",
                                font_weight="normal",
                                cursor="pointer",
                                _hover={"text_decoration": "underline", "color": "royalblue"},
                            ),
                            align_items="flex-start",
                            spacing="2",
                            flex="1",
                        ),
                        spacing="6",
                        align_items="flex-start",
                        justify_content="space-between",
                        width="100%",
                    ),
                    width="300px",
                    min_width="260px",
                    padding="20px",
                    border_radius="16px",
                    box_shadow="sm",
                    background="#dbeafe",
                    margin_top="20px",
                    border="none",
                    align_self="center",
                ),
            ),
            align_items="center",
            width="100%",
        )
    )

buscador = rx.page(
    route="/buscador",
    title="TradeSim - Buscador"
)(buscador_page)