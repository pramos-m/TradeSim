import reflex as rx # Asegúrate de que rx esté importado
from ..components.layout import layout
from ..state.news_state import NewsState
import random

# Definición de colores
BLUE = "#5271FF"
BLUE_LIGHT = "#EEF1FF"
BLUE_DARK = "#3B55D9"
TEXT_DARK = "#202124"
TEXT_GRAY = "#5F6368"
LIGHT_PURPLE = "#E9ECFF"  # Color para el fondo de las tarjetas

# Define TAGS como una constante y luego crea una Var a partir de ella
TAGS_LIST = ["trade", "down", "trends", "trends", "news", "trends"]
TAGS_VAR = rx.Var.create(TAGS_LIST)

def news_tag(tag: str) -> rx.Component:
    """Componente para mostrar una etiqueta de categoría."""
    return rx.text(
        tag,
        background=BLUE_LIGHT,
        color=BLUE_DARK,
        font_size="sm",
        padding_x="3",
        padding_y="1",
        border_radius="full",
    )

# =========== ESTILO 1: PANEL DE NOTICIAS ===========

def featured_article_card(article) -> rx.Component:
    """Componente para mostrar la noticia destacada (estilo imagen 1)."""
    if article is None:
        return rx.box() # Devuelve un componente vacío si no hay artículo
    
    return rx.box(
        rx.flex(
            # ... (contenido de featured_article_card sin cambios) ...
            rx.image(
                src=rx.cond(article.image != "", article.image, "/api/placeholder/640/360"),
                alt=article.title,
                width="100%",
                height="auto",
                object_fit="cover",
                border_radius="lg",
            ),
            rx.box(
                rx.heading(
                    article.title,
                    size="3",
                    color=TEXT_DARK,
                    margin_top="4",
                    margin_bottom="2",
                    line_height="1.2",
                    font_weight="bold",
                ),
                rx.text(
                    article.summary,
                    color=TEXT_GRAY,
                    font_size="md",
                    line_height="1.5",
                    margin_bottom="3",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    css={"display": "-webkit-box", "WebkitLineClamp": "3", "WebkitBoxOrient": "vertical"},
                ),
                width="100%",
            ),
            rx.flex(
                rx.text(
                    article.date,
                    color=TEXT_GRAY,
                    font_size="sm",
                    font_style="italic",
                ),
                rx.spacer(),
                rx.button(
                    "Leer Mas",
                    bg=BLUE,
                    color="white",
                    border_radius="full",
                    padding_x="6",
                    padding_y="2",
                    _hover={"bg": BLUE_DARK},
                    on_click=lambda url=article.url: NewsState.open_url(url),
                ),
                width="100%",
                justify="between",
                align_items="center",
                margin_top="auto",
            ),
            direction="column",
            height="100%",
        ),
        width="100%",
        padding="0",
        margin_bottom="6",
    )

def recent_post_card(article) -> rx.Component:
    """Componente para mostrar una noticia reciente (estilo imagen 1 sidebar)."""
    if article is None:
        return rx.box() # Devuelve un componente vacío si no hay artículo
    
    return rx.flex(
        # ... (contenido de recent_post_card sin cambios) ...
        rx.image(
            src=rx.cond(article.image != "", article.image, "/api/placeholder/100/100"),
            alt=article.title,
            width="80px",
            height="80px",
            object_fit="cover",
            border_radius="md",
        ),
        rx.vstack(
            rx.heading(
                article.title,
                size="5",
                color=TEXT_DARK,
                align="left",
                no_of_lines=2,
                font_weight="medium",
            ),
            rx.text(
                article.date,
                color=TEXT_GRAY,
                font_size="sm",
                font_style="italic",
                align="left",
            ),
            align_items="flex-start",
            spacing="1",
            overflow="hidden",
        ),
        spacing="4",
        align_items="start",
        width="100%",
        margin_bottom="4",
    )

def panel_noticias_style() -> rx.Component:
    """Contenido de noticias con el estilo de la imagen 1."""
    return rx.box(
        # ... (contenido de panel_noticias_style sin cambios) ...
        rx.heading(
            "Panel de noticias",
            size="1",
            color=TEXT_DARK,
            margin_bottom="6",
        ),
        rx.grid(
            rx.box(
                rx.cond(
                    NewsState.has_news,
                    featured_article_card(NewsState.featured_news),
                    rx.center(
                        rx.spinner(size="3", color=BLUE),
                        padding="10",
                    ),
                ),
                width="100%",
            ),
            rx.box(
                rx.vstack(
                    rx.box(
                        rx.center(
                            rx.button(
                                "Posts Recientes",
                                bg=BLUE,
                                color="white",
                                border_radius="full",
                                padding_x="6",
                                padding_y="2",
                                size="2",
                                width="auto",
                            ),
                            width="100%",
                            margin_bottom="4",
                        ),
                        rx.vstack(
                            rx.cond(
                                NewsState.has_more_than_one_news,
                                rx.foreach(
                                    NewsState.recent_news_list[:3],
                                    recent_post_card,
                                ),
                                rx.center(
                                    rx.text("No hay posts recientes"),
                                    padding="4",
                                ),
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        padding="6",
                        border_radius="xl",
                        background=BLUE_LIGHT,
                        width="100%",
                    ),
                    align_items="stretch",
                    width="100%",
                ),
                width="100%",
            ),
            template_columns=["1fr", "1fr", "3fr 2fr"],
            gap="6",
            width="100%",
            margin_bottom="12",
        ),
        width="100%",
        padding="6",
    )


# =========== ESTILO 2: PUBLICACIONES RECIENTES ===========

def publication_card(article, tag: rx.Var[str]) -> rx.Component: # Acepta tag como Var
    """Componente para mostrar una publicación en formato tarjeta (estilo imagen 2)."""
    if article is None:
        return rx.box() # Devuelve un componente vacío si no hay artículo
    
    return rx.box(
        rx.vstack(
            # Imagen con tag superpuesto
            rx.box(
                rx.image(
                    src=rx.cond(article.image != "", article.image, "/api/placeholder/400/300"),
                    alt=article.title,
                    width="100%",
                    height="auto",
                    border_radius="lg 0 0 0",
                    object_fit="cover",
                ),
                rx.box(
                    news_tag(tag), # Usa la Var tag directamente
                    position="absolute",
                    top="4",
                    left="4",
                ),
                position="relative",
                width="100%",
            ),
            # ... (resto del contenido de publication_card sin cambios) ...
            rx.text(
                article.date,
                color=TEXT_GRAY,
                font_size="sm",
                font_style="normal",
                align="left",
                width="100%",
                margin_top="3",
            ),
            rx.heading(
                article.title,
                size="5",
                color=TEXT_DARK,
                align="left",
                line_height="1.2",
                margin_bottom="3",
                no_of_lines=2,
            ),
            rx.link(
                "Read full post →",
                color=TEXT_GRAY,
                font_size="sm",
                font_weight="medium",
                href=article.url,
                is_external=True,
            ),
            align_items="flex-start",
            spacing="1",
            width="100%",
            padding="4",
            height="100%",
        ),
        width="100%",
        background=LIGHT_PURPLE,
        border_radius="xl",
        overflow="hidden",
        height="100%",
    )

def publicaciones_recientes_style() -> rx.Component:
    """Contenido de noticias con el estilo de la imagen 2 (grid de tarjetas)."""
    # TAGS_LIST y TAGS_VAR están definidos globalmente ahora
    
    return rx.box(
        # Título principal
        rx.heading(
            "Publicaciones Recientes",
            size="1",
            color=TEXT_DARK,
            margin_bottom="6",
        ),
        
        # Grid de tarjetas
        rx.grid(
            rx.cond(
                NewsState.has_news,
                rx.foreach(
                    rx.cond(
                        NewsState.has_more_than_five_news,
                        NewsState.processed_news[:6],
                        NewsState.processed_news,
                    ),
                    # CORREGIDO: Usar TAGS_VAR para indexar
                    # Asumiendo que el operador % funciona con rx.Var[int]
                    lambda article, i: publication_card(article, TAGS_VAR[i % len(TAGS_LIST)]),
                ),
                rx.center(
                    rx.spinner(size="3", color=BLUE),
                    padding="10",
                ),
            ),
            template_columns=["1fr", "1fr 1fr", "1fr 1fr 1fr"],
            gap="4",
            width="100%",
        ),
        
        width="100%",
        padding="6",
    )

# =========== ESTILO 3: NOTICIAS FINANCIERAS ===========

def simple_news_item(article, with_border: bool = True) -> rx.Component:
    """Componente para mostrar una noticia simple (estilo imagen 3)."""
    if article is None:
        return rx.box() # Devuelve un componente vacío si no hay artículo
    
    return rx.vstack(
        # ... (contenido de simple_news_item sin cambios) ...
        rx.heading(
            article.title,
            size="5",
            color=TEXT_DARK,
            align="left",
            width="100%",
        ),
        rx.hstack(
            rx.text(
                article.publisher, 
                color=BLUE_DARK, 
                font_size="sm", 
                font_weight="medium"
            ),
            rx.text(
                "•", 
                color=TEXT_GRAY, 
                font_size="sm", 
                margin_x="2"
            ),
            rx.text(
                article.date, 
                color=TEXT_GRAY, 
                font_size="sm", 
                font_style="italic"
            ),
            spacing="1",
            margin_top="1",
            margin_bottom="2",
        ),
        rx.text(
            article.summary,
            color=TEXT_GRAY,
            font_size="sm",
            align="left",
            line_height="1.5",
        ),
        rx.box(
            rx.button(
                "Leer más",
                variant="outline",
                size="1",
                color=BLUE,
                border_color=BLUE,
                _hover={"bg": BLUE_LIGHT},
                on_click=lambda url=article.url: NewsState.open_url(url),
            ),
            margin_top="2",
            margin_bottom="2",
        ),
        align_items="flex-start",
        width="100%",
        padding_y="4",
        border_bottom=rx.cond(
            with_border,
            "1px solid #E2E8F0",
            "none",
        ),
    )

def noticias_financieras_style() -> rx.Component:
    """Contenido de noticias con el estilo de la imagen 3 (lista sencilla)."""
    return rx.box(
        # ... (contenido de noticias_financieras_style sin cambios) ...
        rx.heading(
            "Noticias Financieras",
            size="2",
            color=BLUE,
            margin_bottom="2",
            border_bottom=f"1px solid {BLUE}",
            padding_bottom="2",
        ),
        rx.text(
            rx.cond(
                NewsState.has_news,
                NewsState.news_display_text,
                "Cargando noticias..."
            ),
            color=TEXT_GRAY,
            margin_bottom="4",
        ),
        rx.box(
            rx.heading(
                "Noticia Destacada",
                size="4",
                color=TEXT_DARK,
                margin_bottom="2",
            ),
            rx.cond(
                NewsState.has_news,
                rx.box(
                    simple_news_item(NewsState.featured_news, with_border=False),
                    border="1px solid #E2E8F0",
                    border_radius="md",
                    padding="4",
                    margin_bottom="6",
                ),
                rx.center(
                    rx.spinner(size="2", color=BLUE),
                    padding="6",
                ),
            ),
            margin_bottom="6",
        ),
        rx.box(
            rx.heading(
                "Noticias Recientes",
                size="4",
                color=TEXT_DARK,
                margin_bottom="4",
            ),
            rx.cond(
                NewsState.has_more_than_one_news,
                rx.vstack(
                    rx.foreach(
                        NewsState.recent_news_list,
                        lambda article: simple_news_item(article),
                    ),
                    spacing="0",
                    align_items="stretch",
                    width="100%",
                ),
                rx.center(
                    rx.text("No hay noticias recientes disponibles"),
                    padding="6",
                ),
            ),
            margin_bottom="6",
        ),
        rx.cond(
            NewsState.can_load_more,
            rx.box(
                rx.heading(
                    "Más noticias financieras",
                    size="4",
                    color=TEXT_DARK,
                    margin_bottom="4",
                ),
                rx.center(
                    rx.button(
                        rx.cond(
                            NewsState.is_loading,
                            "Cargando...",
                            "Cargar más noticias"
                        ),
                        on_click=NewsState.load_more_news,
                        is_loading=NewsState.is_loading,
                        color="white",
                        bg=BLUE,
                        _hover={"bg": BLUE_DARK},
                        margin_top="4",
                    ),
                    width="100%",
                ),
                margin_top="6",
            ),
            rx.box(),
        ),
        width="100%",
        padding="6",
    )


# =========== SELECTOR DE ESTILOS Y ESTRUCTURA PRINCIPAL ===========

def select_style() -> rx.Component:
    """Selector de estilos para la página de noticias."""
    return rx.flex(
        # ... (contenido de select_style sin cambios) ...
        rx.button(
            "Estilo Panel",
            on_click=NewsState.change_style("panel"),
            variant=rx.cond(NewsState.selected_style == "panel", "solid", "outline"),
            color=rx.cond(NewsState.selected_style == "panel", "white", BLUE),
            bg=rx.cond(NewsState.selected_style == "panel", BLUE, "white"),
            margin_right="2",
        ),
        rx.button(
            "Estilo Publicaciones",
            on_click=NewsState.change_style("publicaciones"),
            variant=rx.cond(NewsState.selected_style == "publicaciones", "solid", "outline"),
            color=rx.cond(NewsState.selected_style == "publicaciones", "white", BLUE),
            bg=rx.cond(NewsState.selected_style == "publicaciones", BLUE, "white"),
            margin_right="2",
        ),
        rx.button(
            "Estilo Noticias Financieras",
            on_click=NewsState.change_style("financieras"),
            variant=rx.cond(NewsState.selected_style == "financieras", "solid", "outline"),
            color=rx.cond(NewsState.selected_style == "financieras", "white", BLUE),
            bg=rx.cond(NewsState.selected_style == "financieras", BLUE, "white"),
        ),
        justify="center",
        margin_bottom="6",
    )

def news_content() -> rx.Component:
    """Contenido principal de la página de noticias con selección de estilo."""
    return rx.vstack(
        # ... (contenido de news_content sin cambios) ...
        rx.button("Cargar noticias", on_click=NewsState.get_news, is_loading=NewsState.is_loading, display="none", id="load_news_button"),
        rx.script("document.getElementById('load_news_button').click();"),
        select_style(),
        rx.cond(
            NewsState.selected_style == "panel",
            panel_noticias_style(),
            rx.cond(
                NewsState.selected_style == "publicaciones",
                publicaciones_recientes_style(),
                noticias_financieras_style(),
            ),
        ),
        width="100%",
        align_items="stretch",
        background="white",
        border_radius="lg",
    )

def noticias_page() -> rx.Component:
    """Página de noticias utilizando el layout común."""
    return layout(news_content())

# Define the page using the common layout structure
noticias = rx.page(route="/noticias", title="TradeSim - Noticias Financieras")(noticias_page)
