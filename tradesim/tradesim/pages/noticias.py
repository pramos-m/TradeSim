import reflex as rx # Asegúrate de que rx esté importado
from ..components.layout import layout
from ..state.news_state import NewsState, NewsArticle
import random

# ... (definiciones de colores y TAGS_VAR) ...
BLUE = "#5271FF"
BLUE_LIGHT = "#EEF1FF"
BLUE_DARK = "#3B55D9"
TEXT_DARK = "#202124"
TEXT_GRAY = "#5F6368"
LIGHT_PURPLE = "#E9ECFF"

TAGS_LIST = ["trade", "down", "trends", "trends", "news", "trends"]
TAGS_VAR = rx.Var.create(TAGS_LIST)

# --- Componentes Reutilizables ---

def news_tag(tag: rx.Var[str]) -> rx.Component:
    """Componente para mostrar una etiqueta de categoría."""
    return rx.text(
        tag,
        background=BLUE_LIGHT,
        color=BLUE_DARK,
        font_size="sm",
        padding_x="3",
        padding_y="1",
        border_radius="full",
        margin="1",
    )

# --- ESTILO 1: PANEL DE NOTICIAS ---

def featured_article_card(article: NewsArticle) -> rx.Component:
    """Componente para mostrar la noticia destacada (estilo 1)."""
    return rx.box(
        rx.flex(
            rx.image(
                src=rx.cond(article.image != "", article.image, "/api/placeholder/640/360"),
                alt=article.title,
                width="100%",
                height="auto",
                aspect_ratio="16/9",
                object_fit="cover",
                border_radius="lg",
                margin_bottom="4",
            ),
            rx.box(
                rx.heading(
                    article.title,
                    size="6",
                    color=TEXT_DARK,
                    margin_bottom="2",
                    line_height="1.2",
                    font_weight="bold",
                    no_of_lines=2,
                ),
                rx.text(
                    article.summary,
                    color=TEXT_GRAY,
                    font_size="md",
                    line_height="1.5",
                    margin_bottom="4",
                    no_of_lines=3,
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
                    "Leer Más",
                    bg=BLUE,
                    color="white",
                    border_radius="full",
                    padding_x="5",
                    padding_y="2",
                    size="2",
                    _hover={"bg": BLUE_DARK},
                    on_click=lambda: NewsState.open_url(article.url),
                ),
                width="100%",
                justify="between",
                align_items="center",
                margin_top="auto",
            ),
            direction="column",
            height="100%",
            justify="between",
        ),
        width="100%",
        padding="4",
        border="1px solid #E2E8F0",
        border_radius="xl",
        box_shadow="md",
        bg="white",
        margin_bottom="6",
    )

def recent_post_card(article: NewsArticle) -> rx.Component:
    """Componente para mostrar una noticia reciente (sidebar estilo 1)."""
    return rx.link(
        rx.flex(
            rx.image(
                src=rx.cond(article.image != "", article.image, "/api/placeholder/100/100"),
                alt=article.title,
                width="80px",
                height="80px",
                object_fit="cover",
                border_radius="md",
                flex_shrink=0,
            ),
            rx.vstack(
                rx.heading(
                    article.title,
                    size="3",
                    color=TEXT_DARK,
                    align="left",
                    no_of_lines=2,
                    font_weight="medium",
                    line_height="1.3",
                ),
                rx.text(
                    article.date,
                    color=TEXT_GRAY,
                    font_size="xs",
                    font_style="italic",
                    align="left",
                ),
                align_items="flex-start",
                spacing="1",
                overflow="hidden",
                width="100%",
            ),
            spacing="3",
            align_items="center",
            width="100%",
        ),
        href=article.url,
        is_external=True,
        _hover={"text_decoration": "none"},
        display="block",
        margin_bottom="4",
    )

def panel_noticias_style() -> rx.Component:
    """Contenido de noticias con el estilo de la imagen 1."""
    return rx.box(
        rx.heading(
            "Panel de Noticias",
            size="8",
            color=TEXT_DARK,
            margin_bottom="8",
            text_align="center",
        ),
        rx.grid(
            rx.box(
                rx.cond(
                    NewsState.featured_news,
                    featured_article_card(NewsState.featured_news),
                    rx.cond(
                        NewsState.has_news,
                        rx.center(rx.text("No hay artículo destacado."), padding="10"),
                        rx.center(rx.spinner(size="3", color=BLUE), height="300px", padding="10")
                    )
                ),
                width="100%",
                grid_column=["span 2", "span 2", "span 3"],
            ),
            rx.box(
                rx.vstack(
                    rx.heading(
                        "Posts Recientes",
                        on_click=lambda: NewsState.change_style("publicaciones"),
                        variant=rx.cond(NewsState.selected_style == "publicaciones", "solid", "soft"),
                        color_scheme=rx.cond(NewsState.selected_style == "publicaciones", "blue", "gray"),
                        size="5",
                        color=TEXT_DARK, margin_bottom="4"
                    ),
                    rx.cond(
                        NewsState.recent_news_list.length() > 0,
                        rx.foreach(
                            NewsState.recent_news_list,
                            recent_post_card,
                        ),
                        rx.center(rx.text("No hay posts recientes."), padding="4"),
                    ),
                    spacing="0",
                    align_items="stretch",
                    width="100%",
                    padding="6",
                    border_radius="xl",
                    background=BLUE_LIGHT,
                    height="100%",
                ),
                width="100%",
                grid_column=["span 2", "span 2", "span 2"],
            ),
            columns={
                "initial": "repeat(2, 1fr)",
                "md": "repeat(2, 1fr)",
                "lg": "repeat(5, 1fr)"
            },
            gap="6",
            width="100%",
            max_width="1200px",
            margin_x="auto",
        ),
        width="100%",
        padding="6",
    )

# --- ESTILO 2: PUBLICACIONES RECIENTES ---

def publication_card(article: NewsArticle, tag: rx.Var[str]) -> rx.Component:
    """Componente para mostrar una publicación en formato tarjeta (estilo 2)."""
    return rx.box(
        rx.vstack(
            rx.box(
                rx.image(
                    src=rx.cond(article.image != "", article.image, "/api/placeholder/400/300"),
                    alt=article.title,
                    width="100%",
                    height="200px",
                    object_fit="cover",
                    border_top_left_radius="xl",
                    border_top_right_radius="xl",
                ),
                rx.box(
                    news_tag(tag),
                    position="absolute",
                    top="3",
                    left="3",
                ),
                position="relative",
                width="100%",
            ),
            rx.vstack(
                rx.text(
                    article.date,
                    color=TEXT_GRAY,
                    font_size="xs",
                    align="left",
                    width="100%",
                ),
                rx.heading(
                    article.title,
                    size="4",
                    color=TEXT_DARK,
                    align="left",
                    line_height="1.3",
                    margin_bottom="3",
                    no_of_lines=2,
                    font_weight="medium",
                ),
                rx.link(
                    "Leer post completo →",
                    href=article.url,
                    is_external=True,
                    color=BLUE_DARK,
                    font_size="sm",
                    font_weight="medium",
                    _hover={"text_decoration": "underline"},
                ),
                align_items="flex-start",
                spacing="2",
                width="100%",
                padding="4",
                flex_grow=1,
            ),
            align_items="stretch",
            spacing="0",
            width="100%",
            height="100%",
        ),
        width="100%",
        background="white",
        border="1px solid #E2E8F0",
        border_radius="xl",
        overflow="hidden",
        box_shadow="md",
        height="100%",
        display="flex",
        flex_direction="column",
    )

def publicaciones_recientes_style() -> rx.Component:
    """Contenido de noticias con el estilo de la imagen 2 (grid de tarjetas)."""
    return rx.box(
        rx.heading(
            "Publicaciones Recientes",
            size="8",
            color=TEXT_DARK,
            margin_bottom="8",
            text_align="center",
        ),
        rx.grid(
            rx.cond(
                NewsState.processed_news.length() > 0,
                rx.foreach(
                    NewsState.processed_news[:rx.cond(NewsState.processed_news.length() > 6, 6, NewsState.processed_news.length())],
                    lambda article, i: publication_card(article, TAGS_VAR[i % TAGS_VAR.length()]),
                ),
                rx.center(
                    rx.cond(
                        NewsState.is_loading,
                        rx.spinner(size="3", color=BLUE),
                        rx.text("No hay publicaciones recientes.")
                    ),
                    height="300px",
                    grid_column="span 3",
                )
            ),
            columns={
                "initial": "1",
                "md": "2",
                "lg": "3"
            },
            gap="5",
            width="100%",
            max_width="1200px",
            margin_x="auto",
        ),
        width="100%",
        padding="6",
    )

# --- ESTILO 3: NOTICIAS FINANCIERAS (Lista) ---

def simple_news_item(article: NewsArticle, with_border: bool = True) -> rx.Component:
    """Componente para mostrar una noticia simple en formato lista (estilo 3)."""
    return rx.vstack(
        rx.heading(
            article.title,
            size="4",
            color=TEXT_DARK,
            align="left",
            width="100%",
            font_weight="medium",
            line_height="1.3",
        ),
        rx.hstack(
            rx.text(article.publisher, color=BLUE_DARK, font_size="sm", font_weight="medium"),
            rx.text("•", color=TEXT_GRAY, font_size="sm", margin_x="2"),
            rx.text(article.date, color=TEXT_GRAY, font_size="sm", font_style="italic"),
            spacing="1",
            margin_y="1",
        ),
        rx.text(
            article.summary,
            color=TEXT_GRAY,
            font_size="sm",
            align="left",
            line_height="1.5",
            no_of_lines=2,
        ),
        rx.box(
            rx.button(
                "Leer más",
                variant="outline",
                size="1",
                color_scheme="blue",
                on_click=lambda: NewsState.open_url(article.url),
            ),
            margin_top="3",
        ),
        align_items="flex-start",
        width="100%",
        padding_y="5",
        border_bottom=rx.cond(
            with_border,
            "1px solid #E2E8F0",
            "none",
        ),
        spacing="1",
    )

def noticias_financieras_style() -> rx.Component:
    """Contenido de noticias con el estilo de la imagen 3 (lista)."""
    return rx.box(
        rx.heading(
            "Noticias Financieras",
            size="8",
            color=TEXT_DARK,
            margin_bottom="8",
            text_align="center",
        ),
        rx.vstack(
            rx.box(
                rx.heading("Destacado", size="5", color=TEXT_DARK, margin_bottom="3", border_bottom="1px solid #E2E8F0", padding_bottom="2"),
                rx.cond(
                    NewsState.featured_news,
                    simple_news_item(NewsState.featured_news, with_border=False),
                    rx.cond(
                        NewsState.has_news,
                        rx.center(rx.text("No hay noticia destacada."), padding="6"),
                        rx.center(rx.spinner(size="2", color=BLUE), padding="6")
                    )
                ),
                margin_bottom="8",
                padding="4",
                border="1px solid #E2E8F0",
                border_radius="lg",
                bg="white",
            ),
            rx.box(
                 rx.heading("Recientes", size="5", color=TEXT_DARK, margin_bottom="3", border_bottom="1px solid #E2E8F0", padding_bottom="2"),
                 rx.cond(
                    NewsState.processed_news.length() > 0,
                    rx.vstack(
                        rx.foreach(
                            NewsState.processed_news,
                            lambda article: simple_news_item(article),
                        ),
                        spacing="0",
                        align_items="stretch",
                        width="100%",
                    ),
                    rx.center(
                        rx.cond(
                            NewsState.is_loading,
                            rx.spinner(size="3", color=BLUE),
                            rx.text("No hay noticias recientes disponibles.")
                        ),
                        padding="10",
                    )
                ),
                width="100%",
            ),
            rx.cond(
                NewsState.can_load_more,
                rx.center(
                    rx.button(
                        rx.cond(NewsState.is_loading, "Cargando...", "Cargar más noticias"),
                        on_click=NewsState.load_more_news,
                        is_loading=NewsState.is_loading,
                        color_scheme="blue",
                        variant="soft",
                        size="2",
                        margin_top="6",
                    ),
                    width="100%",
                ),
                rx.box()
            ),
            align_items="stretch",
            spacing="6",
            width="100%",
            max_width="900px",
            margin_x="auto",
        ),
        width="100%",
        padding="6",
    )

# --- SELECTOR DE ESTILOS Y ESTRUCTURA PRINCIPAL ---

def select_style() -> rx.Component:
    """Selector de estilos para la página de noticias."""
    return rx.flex(
        rx.button(
            "Panel",
            on_click=lambda: NewsState.change_style("panel"),
            variant=rx.cond(NewsState.selected_style == "panel", "solid", "soft"),
            color_scheme=rx.cond(NewsState.selected_style == "panel", "blue", "gray"),
            size="2",
        ),
        rx.button(
            "Publicaciones",
            on_click=lambda: NewsState.change_style("publicaciones"),
            variant=rx.cond(NewsState.selected_style == "publicaciones", "solid", "soft"),
            color_scheme=rx.cond(NewsState.selected_style == "publicaciones", "blue", "gray"),
            size="2",
        ),
        rx.button(
            "Financieras",
            on_click=lambda: NewsState.change_style("financieras"),
            variant=rx.cond(NewsState.selected_style == "financieras", "solid", "soft"),
            color_scheme=rx.cond(NewsState.selected_style == "financieras", "blue", "gray"),
            size="2",
        ),
        justify="center",
        spacing="3",
        margin_bottom="8",
        wrap="wrap",
    )

def news_content() -> rx.Component:
    """Contenido principal de la página de noticias con selección de estilo."""
    return rx.vstack(
        select_style(),
        rx.box(
            rx.match(
                NewsState.selected_style,
                ("panel", panel_noticias_style()),
                ("publicaciones", publicaciones_recientes_style()),
                ("financieras", noticias_financieras_style()),
                panel_noticias_style(),
            ),
            width="100%",
        ),
        width="100%",
        align_items="stretch",
        min_height="70vh",
    )

def noticias_page() -> rx.Component:
    """Página de noticias completa usando el layout común."""
    # CORREGIDO: on_load se movió al decorador rx.page
    return layout(news_content())

# Define la página de Reflex
# CORREGIDO: Añadir on_load aquí
noticias = rx.page(
    route="/noticias",
    title="TradeSim - Noticias Financieras",
    on_load=NewsState.get_news
)(noticias_page)