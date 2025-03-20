import reflex as rx
from ..components.layouts.dashboard_layout import dashboard_layout
from ..state.news_state import NewsState

# Definición de colores
GOOGLE_BLUE = "#5271FF"
GOOGLE_BLUE_LIGHT = "#EEF1FF"
GOOGLE_BLUE_DARK = "#3B55D9"
TEXT_DARK = "#202124"
TEXT_GRAY = "#5F6368"

def featured_news_card(article) -> rx.Component:
    """Componente para mostrar la noticia destacada (más grande) con estilo Google."""
    if article is None:
        return rx.box()
    
    return rx.box(
        rx.flex(
            # Contenido de texto
            rx.vstack(
                rx.heading(
                    article.title, 
                    size="3", 
                    align="left", 
                    color=TEXT_DARK,
                    line_height="1.2",
                    font_weight="500"
                ),
                rx.hstack(
                    rx.text(article.publisher, color=GOOGLE_BLUE_DARK, font_size="sm", font_weight="500"),
                    rx.text("•", color=TEXT_GRAY, font_size="xs", margin_x="2"),
                    rx.text(article.date, color=TEXT_GRAY, font_size="xs", font_style="italic"),
                    width="100%",
                    align_items="center",
                    justify_content="flex_start",
                ),
                rx.text(
                    article.summary, 
                    color=TEXT_GRAY, 
                    font_size="md", 
                    align="left", 
                    margin_y="4",
                    line_height="1.5"
                ),
                rx.button(
                    "Leer noticia completa",
                    variant="solid",
                    size="2",
                    color="white",
                    background=GOOGLE_BLUE,
                    _hover={"background": GOOGLE_BLUE_DARK},
                    on_click=lambda url=article.url: NewsState.open_url(url),
                    width="full",
                ),
                align_items="flex_start",
                spacing="3",
                width="100%",
                height="100%",
            ),
            flex_direction="column",
            align_items="stretch",
            width="100%",
            spacing="4",
        ),
        width="100%",
        height="100%",
        padding="6",
        border_radius="xl",
        background="white",
        shadow="lg",
        _hover={"shadow": "xl", "transform": "translateY(-2px)"},
        transition="all 0.3s ease-in-out",
        border="1px solid",
        border_color="gray.100",
    )

def news_list_item(article) -> rx.Component:
    """Componente para mostrar un elemento de la lista de noticias con estilo Google."""
    return rx.box(
        rx.flex(
            # Contenido de texto
            rx.vstack(
                rx.heading(
                    article.title, 
                    size="4", 
                    align="left", 
                    no_of_lines=2, 
                    color=TEXT_DARK,
                    font_weight="500",
                    line_height="1.2"
                ),
                rx.hstack(
                    rx.text(article.publisher, color=GOOGLE_BLUE_DARK, font_size="xs", font_weight="500"),
                    rx.text("•", color=TEXT_GRAY, font_size="xs", margin_x="1"),
                    rx.text(article.date, color=TEXT_GRAY, font_size="xs", font_style="italic"),
                    width="100%",
                    align_items="center",
                    justify_content="flex_start",
                ),
                rx.text(
                    article.summary, 
                    color=TEXT_GRAY, 
                    font_size="sm", 
                    align="left", 
                    margin_y="2",
                    line_height="1.4",
                    # Usamos css para limitar líneas
                    css={"display": "-webkit-box", 
                         "WebkitLineClamp": "2", 
                         "WebkitBoxOrient": "vertical",
                         "overflow": "hidden"},
                ),
                rx.button(
                    "Leer más",
                    variant="outline",
                    size="1",
                    border_color=GOOGLE_BLUE,
                    color=GOOGLE_BLUE,
                    _hover={"background": GOOGLE_BLUE_LIGHT},
                    on_click=lambda url=article.url: NewsState.open_url(url),
                    width="full",
                ),
                align_items="flex_start",
                spacing="2",
                width="100%",
            ),
            flex_direction="column",
            width="100%",
            spacing="4",
        ),
        width="100%",
        padding="4",
        border_radius="lg",
        background="white",
        shadow="sm",
        _hover={
            "shadow": "md", 
            "transform": "translateY(-1px)",
            "border_left": f"4px solid {GOOGLE_BLUE}"
        },
        transition="all 0.2s ease-in-out",
        border="1px solid",
        border_color="gray.100",
        margin_bottom="3",
    )

def no_news_message() -> rx.Component:
    """Componente para mostrar cuando no hay noticias disponibles."""
    return rx.box(
        rx.vstack(
            rx.icon(tag="info", color=GOOGLE_BLUE, font_size="xl"),
            rx.heading("Sin resultados", size="4", color=GOOGLE_BLUE),
            rx.text("No hay noticias financieras disponibles en este momento. Intente más tarde.", 
                  color=TEXT_GRAY, text_align="center"),
            spacing="3",
            padding="6",
        ),
        width="100%",
        border_radius="lg",
        background=GOOGLE_BLUE_LIGHT,
        padding="4",
        shadow="sm",
    )

def news_content() -> rx.Component:
    """Contenido principal de la página de noticias con estilo Google."""
    return rx.vstack(
        # Botón oculto para cargar noticias automáticamente
        rx.button("Cargar noticias", on_click=NewsState.get_news, is_loading=NewsState.is_loading, display="none", id="load_news_button"),
        rx.script("document.getElementById('load_news_button').click();"),
        
        # Título de la página con estilo Google
        rx.flex(
            rx.heading(
                "Noticias Financieras", 
                size="2", 
                color=GOOGLE_BLUE,
                font_weight="normal"
            ),
            width="100%",
            border_bottom=f"2px solid {GOOGLE_BLUE}",
            padding_bottom="2",
            margin_bottom="6",
        ),
        
        # Contenido de noticias o indicadores de carga/no resultados
        rx.cond(
            NewsState.is_loading & ~NewsState.has_news,
            # Estado de carga
            rx.center(
                rx.vstack(
                    rx.spinner(size="3", color=GOOGLE_BLUE), 
                    rx.text("Cargando noticias financieras...", color=GOOGLE_BLUE, font_size="lg"),
                    spacing="4"
                ), 
                padding="10", 
                width="100%"
            ),
            # Contenido cuando finaliza la carga
            rx.cond(
                ~NewsState.has_news,
                # Cuando no hay noticias
                no_news_message(),
                # Cuando hay noticias
                rx.vstack(
                    rx.text(
                        NewsState.news_display_text, 
                        font_weight="normal",
                        color=TEXT_GRAY,
                        margin_bottom="4"
                    ),
                    
                    # Noticia destacada
                    featured_news_card(NewsState.featured_news),
                    
                    # Lista de noticias recientes
                    rx.cond(
                        NewsState.has_more_than_one_news,
                        rx.vstack(
                            rx.heading(
                                "Noticias recientes", 
                                size="3", 
                                margin_y="4",
                                color=GOOGLE_BLUE,
                                font_weight="normal"
                            ),
                            rx.foreach(
                                NewsState.recent_news_list,
                                news_list_item
                            ),
                            width="100%",
                            spacing="3",
                        ),
                        rx.box()  # No mostrar esta sección si no hay más que una noticia
                    ),
                    
                    # Mostrar todas las noticias adicionales
                    rx.vstack(
                        rx.heading(
                            "Más noticias", 
                            size="3", 
                            margin_y="4",
                            color=GOOGLE_BLUE,
                            font_weight="normal"
                        ),
                        rx.foreach(
                            NewsState.additional_news_list,
                            news_list_item
                        ),
                        width="100%",
                        spacing="3",
                        display=rx.cond(NewsState.has_more_than_five_news, "block", "none"),
                    ),
                    
                    # Botón para cargar más noticias estilo Google
                    rx.cond(
                        NewsState.can_load_more,
                        rx.center(
                            rx.button(
                                rx.cond(
                                    NewsState.is_loading,
                                    "Cargando...", 
                                    "Cargar más noticias"
                                ), 
                                on_click=NewsState.load_more_news,
                                is_loading=NewsState.is_loading,
                                background=GOOGLE_BLUE,
                                color="white",
                                _hover={"background": GOOGLE_BLUE_DARK},
                                size="2",
                                margin_top="8",
                                width=["100%", "auto", "auto"],
                                border_radius="full",
                                padding_x="6"
                            ),
                            width="100%",
                        ),
                        rx.box()
                    ),
                    
                    width="100%",
                    align_items="stretch",
                    spacing="4",
                ),
            ),
        ),
        width="100%",
        spacing="4",
        background="white",
        padding="4",
        border_radius="lg",
    )

def news_page() -> rx.Component:
    """Página de noticias utilizando el layout del dashboard."""
    return dashboard_layout(news_content())

news = rx.page(route="/news", title="TradeSim - Noticias Financieras")(news_page)