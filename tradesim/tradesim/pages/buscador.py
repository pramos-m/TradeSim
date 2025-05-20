# tradesim/tradesim/pages/buscador.py
import reflex as rx
from ..components.layout import layout # Asegúrate que la ruta a tu layout es correcta
from ..state.search_state import SearchState # Asegúrate que la ruta a tu SearchState es correcta

def buscador_page_content() -> rx.Component:
    """Contenido de la página del buscador de acciones."""
    return rx.vstack(
        rx.heading(
            "Buscador de Acciones",
            size="7",
            margin_bottom="20px",
            margin_top="30px",
            align_self="flex-start",
            padding_x="30px"
        ),
        rx.vstack(
            rx.text("Encuentra Tu", size="8", text_align="center", width="100%"),
            rx.text(
                "Mejor Opción Aquí",
                size="8",
                font_weight="bold",
                color_scheme="blue",
                text_align="center",
                width="100%"
            ),
            align_items="center", width="100%", spacing="1", margin_top="20px", margin_bottom="15px",
        ),
        rx.text(
            "Explora una amplia gama de acciones globales. Encuentra datos en tiempo real y toma decisiones de inversión informadas.",
            size="4", color_scheme="gray", text_align="center", max_width="650px", 
            margin_x="auto", margin_bottom="25px", padding_x="15px"
        ),
        rx.box( 
            rx.hstack(
                rx.icon(tag="search", color_scheme="blue", size=24), 
                rx.divider(orientation="vertical", size="2", margin_x="10px"),
                rx.input(
                    placeholder="Buscar por símbolo o nombre de empresa...",
                    value=SearchState.search_query,
                    on_change=SearchState.set_search_query,
                    on_key_down=SearchState.handle_input_key_down,
                    flex_grow="1", variant="surface", size="3", 
                ),
                rx.button(
                    "Buscar", 
                    on_click=SearchState.search_stock, 
                    is_loading=SearchState.is_searching,
                    size="3", color_scheme="blue"
                ),
                spacing="3", align_items="center", width="100%",
            ),
            max_width="700px", width="90%", background_color="var(--gray-a2)", 
            border_radius="var(--radius-3)", box_shadow="var(--shadow-3)",
            padding="16px", margin_x="auto", margin_bottom="20px",
        ),

        # Mensaje de error de búsqueda
        rx.cond(
            SearchState.search_error != "", 
            rx.callout.root(
                rx.callout.icon(rx.icon(tag="alert_triangle")), 
                rx.callout.text(SearchState.search_error),
                color_scheme="red", variant="soft", margin_top="20px",
                max_width="700px", width="90%", margin_x="auto", 
            )
        ),

        # Resultados de la búsqueda
        rx.cond(
            SearchState.search_result.get("Symbol") & (SearchState.search_error == ""), 
            rx.box(
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            SearchState.search_result.get("PriceString", "N/A"), 
                            weight="bold", size="6", color_scheme="green"
                        ),
                        rx.text(SearchState.search_result.get("Name", "Nombre no disponible"), size="4", margin_top="4px", font_weight="medium"),
                        rx.text(f"Símbolo: {SearchState.search_result.get('Symbol', 'N/A')}", size="2", color_scheme="gray", margin_top="2px"),
                        rx.button(
                            "Ver Detalles", 
                            on_click=lambda: SearchState.go_to_stock_detail(SearchState.search_result.get("Symbol")),
                            color_scheme="blue", variant="solid", size="2", margin_top="16px",
                            is_disabled=(SearchState.search_result.get("Symbol", "N/A") == "N/A")
                        ),
                        align_items="start", spacing="2", flex_grow="1", 
                    ),
                    rx.vstack(
                        rx.image(
                            src=SearchState.search_result.get("Logo", "/default_logo.png"), 
                            alt=f"Logo de {SearchState.search_result.get('Name', 'empresa')}",
                            width="100px", height="auto", min_height="65px", 
                            object_fit="contain", border="1px solid var(--gray-a6)", 
                            border_radius="var(--radius-2)",
                        ),
                        align_items="center", spacing="3",
                    ),
                    spacing="6", align_items="center", width="100%",
                ),
                max_width="500px", width="90%", padding="24px", border_radius="var(--radius-4)",
                box_shadow="var(--shadow-4)", bg="var(--gray-a1)", 
                margin_top="20px", margin_x="auto", 
            )
        ),
        align_items="center", width="100%", min_height="calc(100vh - 160px)", 
        padding_x="15px", 
        padding_bottom="50px", spacing="5", 
    )

def buscador_page() -> rx.Component:
    """Página del buscador de acciones envuelta en el layout."""
    return layout(
        buscador_page_content()
    )

# --- ESTA LÍNEA ES CRUCIAL Y HA SIDO DESCOMENTADA ---
buscador = rx.page(
    route="/buscador", 
    title="TradeSim - Buscador"
)(buscador_page)
