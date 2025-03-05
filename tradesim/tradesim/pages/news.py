import reflex as rx
from ..components.layouts.dashboard_layout import dashboard_layout
from ..state.news_state import NewsState
from ..utils.auth_middleware import require_auth

def news_card(article: dict) -> rx.Component:
    """Componente para mostrar una noticia individual."""
    # En lugar de usar el enlace dinámicamente dentro del componente,
    # vamos a usar rx.cond para crear diferentes botones según el caso
    
    return rx.box(
        rx.hstack(
            # Parte izquierda: Miniatura o icono
            rx.box(
                rx.cond(
                    article["thumbnail_url"] != None,
                    rx.image(
                        src=article["thumbnail_url"],
                        width="100px",
                        height="75px",
                        border_radius="md",
                        object_fit="cover",
                    ),
                    rx.icon(
                        tag="newspaper",
                        font_size="2em",
                        color="gray.500",
                        box_size="75px",
                    ),
                ),
                min_width="100px",
            ),
            
            # Parte derecha: Contenido de la noticia
            rx.vstack(
                rx.heading(
                    article["title"],
                    size="4",
                    align="left",
                ),
                rx.text(
                    article["publisher"],
                    color="gray.600",
                    font_size="sm",
                    align="left",
                ),
                rx.text(
                    article["formatted_date"],
                    color="gray.500",
                    font_size="xs",
                    font_style="italic",
                    align="left",
                ),
                rx.text(
                    article["summary_display"],
                    color="gray.700",
                    font_size="sm",
                    align="left",
                ),
                # En lugar de un enlace con href dinámico, usamos un botón que abre una nueva ventana
                rx.button(
                    "Leer más",
                    variant="outline",
                    size="1",
                    color_scheme="blue",
                    on_click=rx.client_side("window.open('" + str(article["link"]) + "', '_blank')"),
                ),
                align_items="flex_start",
                spacing="1",
                width="100%",
            ),
            spacing="4",
            align_items="flex_start",
            width="100%",
        ),
        padding="4",
        border_radius="md",
        border="1px solid",
        border_color="gray.200",
        margin_bottom="4",
        width="100%",
        background="white",
        _hover={"shadow": "md"},
        transition="all 0.2s",
    )

# El resto del archivo permanece igual

def news_content() -> rx.Component:
    """Contenido principal de la página de noticias."""
    return rx.vstack(
        # Auto-cargar noticias al inicio
        rx.button(
            "Cargar noticias",
            on_click=NewsState.get_news,
            is_loading=NewsState.is_loading,
            display="none",
            id="load_news_button",
        ),
        rx.script("document.getElementById('load_news_button').click();"),
        
        # Título de la página
        rx.heading("Noticias Financieras", size="2", margin_bottom="6"),
        
        # Selector de empresas y buscador
        rx.hstack(
            rx.select(
                NewsState.default_tickers,
                default_value=NewsState.selected_ticker,
                on_change=NewsState.set_ticker,
                placeholder="Selecciona una empresa",
                width=["100%", "70%", "60%", "50%"],
            ),
            rx.hstack(
                rx.input(
                    placeholder="Buscar por símbolo",
                    value=NewsState.custom_ticker,
                    on_change=NewsState.set_custom_ticker,
                ),
                rx.button(
                    "Buscar",
                    on_click=NewsState.search_custom_ticker,
                    color_scheme="blue",
                ),
                spacing="2",
                width=["100%", "30%", "40%", "50%"],
            ),
            width="100%",
            spacing="4",
            margin_bottom="6",
            flex_direction=["column", "column", "row", "row"],
        ),
        
        # Contenido principal - Cargando, sin resultados o listado de noticias
        rx.cond(
            NewsState.is_loading,
            # Caso 1: Mostrando indicador de carga
            rx.center(
                rx.spinner(),
                rx.text("Cargando noticias..."),
                padding="10",
            ),
            # Caso 2: Verificar si hay noticias o no
            rx.cond(
                ~NewsState.has_news,
                # Sin noticias - Mostrar mensaje informativo
                rx.box(
                    rx.vstack(
                        rx.icon(
                            tag="info", 
                            color="blue.400", 
                            font_size="xl"
                        ),
                        rx.heading(
                            "Sin resultados", 
                            size="4", 
                            color="blue.600"
                        ),
                        rx.text(
                            f"No hay noticias disponibles para {NewsState.selected_ticker}. Prueba con otro símbolo.",
                            color="blue.600"
                        ),
                        spacing="2",
                        padding="4",
                    ),
                    width="100%",
                    border="1px solid",
                    border_color="blue.100",
                    border_radius="md",
                    background="blue.50",
                    padding="2",
                ),
                # Con noticias - Mostrar listado
                rx.vstack(
                    # Texto informativo
                    rx.text(
                        NewsState.news_display_text,
                        font_weight="bold",
                    ),
                    
                    # Listado de noticias
                    rx.vstack(
                        rx.box(
                            rx.foreach(
                                NewsState.displayed_news,
                                lambda article: news_card(article),
                            ),
                        ),
                        width="100%",
                        spacing="4",
                    ),
                    
                    # Botón para ver más/menos
                    rx.cond(
                        NewsState.has_more_than_five_news,
                        rx.cond(
                            ~NewsState.show_all_news,
                            rx.button(
                                "Ver todas las noticias",
                                on_click=NewsState.toggle_show_all,
                                color_scheme="blue",
                                variant="outline",
                                size="2",
                            ),
                            rx.button(
                                "Ver menos noticias",
                                on_click=NewsState.toggle_show_all,
                                color_scheme="blue",
                                variant="outline",
                                size="2",
                            ),
                        ),
                        rx.box(),
                    ),
                    width="100%",
                    align_items="center",
                ),
            ),
        ),
        width="100%",
        spacing="4",
    )

@require_auth
def news_page() -> rx.Component:
    """Página de noticias utilizando el layout del dashboard."""
    return dashboard_layout(news_content())

# Configurar la página
news = rx.page(
    route="/news",
    title="TradeSim - Noticias Financieras",
)(news_page)