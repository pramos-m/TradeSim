# import reflex as rx  # Asegúrate de que rx esté importado
# from ..components.layout import layout
# from ..state.news_state import NewsState, NewsArticle
# import random

# # ... (definiciones de colores y TAGS_VAR) ...
# BLUE = "#5271FF"
# BLUE_LIGHT = "#EEF1FF"
# BLUE_DARK = "#3B55D9"
# TEXT_DARK = "#202124"
# TEXT_GRAY = "#5F6368"
# LIGHT_PURPLE = "#E9ECFF"

# TAGS_LIST = ["trade", "down", "trends", "trends", "news", "trends"]
# TAGS_VAR = rx.Var.create(TAGS_LIST)

# # --- Componentes Reutilizables ---

# def news_tag(tag: rx.Var[str]) -> rx.Component:
#     """Componente para mostrar una etiqueta de categoría."""
#     return rx.text(
#         tag,
#         background=BLUE_LIGHT,
#         color=BLUE_DARK,
#         font_size="sm",
#         padding_x="3",
#         padding_y="1",
#         border_radius="full",
#         margin="1",
#     )

# # --- ESTILO 1: PANEL DE NOTICIAS ---

# def featured_article_card(article: NewsArticle) -> rx.Component:
#     """Componente para mostrar la noticia destacada (estilo 1)."""
#     return rx.box(
#         rx.flex(
#             rx.image(
#                 src=rx.cond(article.image != "", article.image, "/api/placeholder/640/360"),
#                 alt=article.title,
#                 width="100%",
#                 height="auto",
#                 aspect_ratio="16/9",
#                 object_fit="cover",
#                 # border_radius="3xl",  # Muy redondeado
#                 border_radius="full",
#                 margin_bottom="4",
#             ),
#             rx.box(
#                 rx.heading(
#                     article.title,
#                     size="6",
#                     color=TEXT_DARK,
#                     margin_bottom="2",
#                     line_height="1.2",
#                     font_weight="bold",
#                     no_of_lines=2,
#                 ),
#                 rx.text(
#                     article.summary,
#                     color=TEXT_GRAY,
#                     font_size="md",
#                     line_height="1.5",
#                     margin_bottom="4",
#                     no_of_lines=3,
#                 ),
#                 width="100%",
#             ),
#             rx.flex(
#                 rx.button(  # Primero "Leer Más"
#                     "Leer Más",
#                     bg=BLUE,
#                     color="white",
#                     border_radius="full",  # Botón completamente redondeado
#                     padding_x="5",
#                     padding_y="2",
#                     size="2",
#                     _hover={"bg": BLUE_DARK},
#                     on_click=lambda: NewsState.open_url(article.url),
#                 ),
#                 rx.spacer(),
#                 rx.text(  # Después la fecha
#                     article.date,
#                     color=TEXT_GRAY,
#                     font_size="sm",
#                     font_style="italic",
#                 ),
#                 width="100%",
#                 justify="between",
#                 align_items="center",
#                 margin_top="auto",
#             ),
#             direction="column",
#             height="100%",
#             justify="between",
#         ),
#         width="100%",
#         padding="4",
#         border="1px solid #E2E8F0",
#         border_radius="xl",
#         box_shadow="md",
#         bg="white",
#         margin_bottom="6",
#     )

# def recent_post_card(article: NewsArticle) -> rx.Component:
#     """Componente para mostrar una noticia reciente (sidebar estilo 1)."""
#     return rx.link(
#         rx.flex(
#             rx.image(
#                 src=rx.cond(article.image != "", article.image, "/api/placeholder/100/100"),
#                 alt=article.title,
#                 width="80px",
#                 height="80px",
#                 object_fit="cover",
#                 border_radius="lg",  # Aumentado el redondeo
#                 flex_shrink=0,
#             ),
#             rx.vstack(
#                 rx.heading(
#                     article.title,
#                     size="3",
#                     color=TEXT_DARK,
#                     align="left",
#                     no_of_lines=2,
#                     font_weight="medium",
#                     line_height="1.3",
#                 ),
#                 rx.text(
#                     article.date,
#                     color=TEXT_GRAY,
#                     font_size="xs",
#                     font_style="italic",
#                     align="left",
#                 ),
#                 align_items="flex-start",
#                 spacing="1",
#                 overflow="hidden",
#                 width="100%",
#             ),
#             spacing="3",
#             align_items="center",
#             width="100%",
#         ),
#         href=article.url,
#         is_external=True,
#         _hover={"text_decoration": "none"},
#         display="block",
#         margin_bottom="4",
#     )

# def panel_noticias_style() -> rx.Component:
#     """Contenido de noticias con el estilo de la imagen de referencia."""
#     return rx.box(
#         rx.heading(
#             "Panel de Noticias",
#             size="8",
#             color=TEXT_DARK,
#             margin_bottom="8",
#             text_align="center",
#         ),
#         rx.grid(
#             # Columna izquierda: Artículo destacado (imagen grande)
#             rx.box(
#                 rx.cond(
#                     NewsState.featured_news,
#                     rx.vstack(
#                         rx.image(
#                             src=rx.cond(NewsState.featured_news.image != "", NewsState.featured_news.image, "/api/placeholder/640/360"),
#                             alt=NewsState.featured_news.title,
#                             width="100%",
#                             height="auto",
#                             aspect_ratio="16/9",
#                             object_fit="cover",
#                             margin_bottom="4",
#                             border_radius="3xl",
#                         ),
#                         rx.heading(
#                             NewsState.featured_news.title,
#                             size="6",
#                             color=TEXT_DARK,
#                             margin_bottom="2",
#                             line_height="1.2",
#                             font_weight="bold",
#                             no_of_lines=2,
#                         ),
#                         rx.text(
#                             NewsState.featured_news.summary,
#                             color=TEXT_GRAY,
#                             font_size="md",
#                             line_height="1.5",
#                             margin_bottom="4",
#                             no_of_lines=3,
#                         ),
#                         rx.flex(
#                             rx.button(  # Primero "Leer Más"
#                                 "Leer Más",
#                                 bg=BLUE,
#                                 color="white",
#                                 border_radius="full",  # Botón completamente redondeado
#                                 padding_x="5",
#                                 padding_y="2",
#                                 size="2",
#                                 _hover={"bg": BLUE_DARK},
#                                 on_click=lambda: NewsState.open_url(NewsState.featured_news.url),
#                             ),
#                             rx.spacer(),
#                             rx.text(  # Después la fecha
#                                 NewsState.featured_news.date,
#                                 color=TEXT_GRAY,
#                                 font_size="sm",
#                                 font_style="italic",
#                             ),
#                             width="100%",
#                             justify="between",
#                             align_items="center",
#                             margin_top="auto",
#                         ),
#                         width="100%",
#                         height="100%",
#                         align_items="flex-start",
#                         border="1px solid #E2E8F0",
#                         box_shadow="md",
#                         bg="white",
#                         padding="4",
#                         border_radius="3xl",  # Aumentado el redondeo

#                     ),
#                     rx.center(
#                         rx.cond(
#                             NewsState.is_loading,
#                             rx.spinner(size="3", color=BLUE),
#                             rx.text("No hay artículo destacado.")
#                         ),
#                         height="100%",
#                         border="1px dashed #E2E8F0",
#                         border_radius="xl",
#                     )
#                 ),
#                 width="100%",
#                 grid_column=["span 12", "span 12", "span 8"],
#             ),
#             # Columna derecha: Posts recientes
#             rx.box(
#                 rx.vstack(
#                     rx.button(  # Convertido a botón más grande y redondeado
#                         "Posts Recientes",
#                         size="4",  # Cambiado de "5" a "4" para evitar el error
#                         color="white",
#                         bg=BLUE,
#                         border_radius="full",
#                         padding_x="6",
#                         padding_y="3",
#                         margin_bottom="4",
#                         _hover={"bg": BLUE_DARK},
#                         font_weight="medium",
#                     ),
#                     rx.cond(
#                         NewsState.recent_news_list.length() > 0,
#                         rx.vstack(
#                             rx.foreach(
#                                 NewsState.recent_news_list,
#                                 lambda article, i: rx.hstack(
#                                     rx.image(
#                                         src=rx.cond(article.image != "", article.image, f"/api/placeholder/100/100"),
#                                         alt=article.title,
#                                         width="80px",
#                                         height="80px",
#                                         object_fit="cover",
#                                         border_radius="lg",  # Aumentado el redondeo
#                                     ),
#                                     rx.vstack(
#                                         rx.heading(
#                                             article.title,
#                                             size="3",
#                                             color=TEXT_DARK,
#                                             no_of_lines=2,
#                                             font_weight="medium",
#                                         ),
#                                         rx.text(
#                                             article.date,
#                                             color=TEXT_GRAY,
#                                             font_size="xs",
#                                             font_style="italic",
#                                         ),
#                                         align_items="flex-start",
#                                         spacing="1",
#                                         width="100%",
#                                     ),
#                                     spacing="3",
#                                     align_items="center",
#                                     width="100%",
#                                     margin_bottom="4",
#                                     padding="2",
#                                     border_radius="md",
#                                     _hover={"bg": LIGHT_PURPLE, "cursor": "pointer"},
#                                     on_click=lambda: NewsState.open_url(article.url),
#                                 ),
#                             ),
#                             spacing="2",
#                             width="100%",
#                         ),
#                         rx.center(
#                             rx.text("No hay posts recientes."),
#                             padding="4",
#                         ),
#                     ),
#                     spacing="2",
#                     align_items="stretch",
#                     width="100%",
#                     padding="6",
#                     border_radius="2xl",  # Mayor redondeo para la caja de Posts Recientes
#                     background=BLUE_LIGHT,
#                     height="100%",
#                 ),
#                 width="100%",
#                 grid_column=["span 12", "span 12", "span 4"],
#             ),
#             columns={
#                 "initial": "repeat(12, 1fr)",
#                 "md": "repeat(12, 1fr)",
#                 "lg": "repeat(12, 1fr)",
#             },
#             template_rows={
#                 "initial": "auto auto", 
#                 "md": "auto auto", 
#                 "lg": "auto",
#             },
#             gap="6",
#             width="100%",
#             max_width="1200px",
#             margin_x="auto",
#         ),
#         width="100%",
#         padding="6",
#     )

# # --- ESTILO 2: PUBLICACIONES RECIENTES ---

# def publication_card(article: NewsArticle, tag: rx.Var[str]) -> rx.Component:
#     """Componente para mostrar una publicación en formato tarjeta (estilo 2)."""
#     return rx.box(
#         rx.vstack(
#             rx.box(
#                 rx.image(
#                     src=rx.cond(article.image != "", article.image, "/api/placeholder/400/300"),
#                     alt=article.title,
#                     width="100%",
#                     height="200px",
#                     object_fit="cover",
#                     border_top_left_radius="xl",
#                     border_top_right_radius="xl",
#                 ),
#                 rx.box(
#                     news_tag(tag),
#                     position="absolute",
#                     top="3",
#                     left="3",
#                 ),
#                 position="relative",
#                 width="100%",
#             ),
#             rx.vstack(
#                 rx.hstack(  # Cambiado a hstack para colocar elementos en línea
#                     rx.link(  # Primero "Leer post completo"
#                         "Leer post completo →",
#                         href=article.url,
#                         is_external=True,
#                         color=BLUE_DARK,
#                         font_size="sm",
#                         font_weight="medium",
#                         _hover={"text_decoration": "underline"},
#                     ),
#                     rx.spacer(),
#                     rx.text(  # Después la fecha
#                         article.date,
#                         color=TEXT_GRAY,
#                         font_size="xs",
#                     ),
#                     width="100%",
#                 ),
#                 rx.heading(
#                     article.title,
#                     size="4",
#                     color=TEXT_DARK,
#                     align="left",
#                     line_height="1.3",
#                     margin_bottom="3",
#                     no_of_lines=2,
#                     font_weight="medium",
#                 ),
#                 align_items="flex-start",
#                 spacing="2",
#                 width="100%",
#                 padding="4",
#                 flex_grow=1,
#             ),
#             align_items="stretch",
#             spacing="0",
#             width="100%",
#             height="100%",
#         ),
#         width="100%",
#         background="white",
#         border="1px solid #E2E8F0",
#         border_radius="xl",
#         overflow="hidden",
#         box_shadow="md",
#         height="100%",
#         display="flex",
#         flex_direction="column",
#     )

# def publicaciones_recientes_style() -> rx.Component:
#     """Contenido de noticias con el estilo de grid de tarjetas."""
#     return rx.box(
#         rx.heading(
#             "Publicaciones Recientes",
#             size="8",
#             color=TEXT_DARK,
#             margin_bottom="8",
#             text_align="center",
#         ),
#         rx.grid(
#             rx.cond(
#                 NewsState.processed_news.length() > 0,
#                 rx.foreach(
#                     NewsState.processed_news[:rx.cond(NewsState.processed_news.length() > 6, 6, NewsState.processed_news.length())],
#                     lambda article, i: rx.box(
#                         rx.vstack(
#                             rx.box(
#                                 rx.image(
#                                     src=rx.cond(article.image != "", article.image, f"/api/placeholder/400/250"),
#                                     alt=article.title,
#                                     width="100%",
#                                     height="200px",
#                                     object_fit="cover",
#                                     border_top_left_radius="xl",
#                                     border_top_right_radius="xl",
#                                 ),
#                                 rx.box(
#                                     news_tag(TAGS_VAR[i % TAGS_VAR.length()]),
#                                     position="absolute",
#                                     top="3",
#                                     left="3",
#                                 ),
#                                 position="relative",
#                                 width="100%",
#                             ),
#                             rx.vstack(
#                                 rx.hstack(  # Cambiado a hstack para colocar elementos en línea
#                                     rx.link(  # Primero "Leer post completo"
#                                         "Leer post completo →",
#                                         href=article.url,
#                                         is_external=True,
#                                         color=BLUE_DARK,
#                                         font_size="sm",
#                                         font_weight="medium",
#                                         _hover={"text_decoration": "underline"},
#                                         border_radius="full",  # Añadido border-radius
#                                     ),
#                                     rx.spacer(),
#                                     rx.text(  # Después la fecha
#                                         article.date,
#                                         color=TEXT_GRAY,
#                                         font_size="xs",
#                                     ),
#                                     width="100%",
#                                 ),
#                                 rx.heading(
#                                     article.title,
#                                     size="4",
#                                     color=TEXT_DARK,
#                                     align="left",
#                                     line_height="1.3",
#                                     margin_bottom="3",
#                                     no_of_lines=2,
#                                 ),
#                                 align_items="flex-start",
#                                 spacing="2",
#                                 width="100%",
#                                 padding="4",
#                                 flex_grow=1,
#                             ),
#                             align_items="stretch",
#                             spacing="0",
#                             width="100%",
#                             height="100%",
#                         ),
#                         width="100%",
#                         background="white",
#                         border="1px solid #E2E8F0",
#                         border_radius="xl",
#                         overflow="hidden",
#                         box_shadow="md",
#                         height="100%",
#                     ),
#                 ),
#                 rx.center(
#                     rx.cond(
#                         NewsState.is_loading,
#                         rx.spinner(size="3", color=BLUE),
#                         rx.text("No hay publicaciones recientes.")
#                     ),
#                     height="300px",
#                     grid_column="span 3",
#                 )
#             ),
#             columns={
#                 "initial": "1",
#                 "sm": "2",
#                 "md": "2",
#                 "lg": "3",
#             },
#             gap="5",
#             width="100%",
#             max_width="1200px",
#             margin_x="auto",
#         ),
#         width="100%",
#         padding="6",
#     )

# # --- ESTILO 3: NOTICIAS FINANCIERAS (Lista) ---

# def simple_news_item(article: NewsArticle, with_border: bool = True) -> rx.Component:
#     """Componente para mostrar una noticia simple en formato lista (estilo 3)."""
#     return rx.vstack(
#         rx.heading(
#             article.title,
#             size="4",
#             color=TEXT_DARK,
#             align="left",
#             width="100%",
#             font_weight="medium",
#             line_height="1.3",
#         ),
#         rx.hstack(
#             rx.text(article.publisher, color=BLUE_DARK, font_size="sm", font_weight="medium"),
#             rx.text("•", color=TEXT_GRAY, font_size="sm", margin_x="2"),
#             rx.text(article.date, color=TEXT_GRAY, font_size="sm", font_style="italic"),
#             spacing="1",
#             margin_y="1",
#         ),
#         rx.text(
#             article.summary,
#             color=TEXT_GRAY,
#             font_size="sm",
#             align="left",
#             line_height="1.5",
#             no_of_lines=2,
#         ),
#         rx.hstack(  # Cambiado a hstack para colocar elementos en línea
#             rx.button(  # Primero "Leer más"
#                 "Leer más",
#                 variant="outline",
#                 size="1",
#                 color_scheme="blue",
#                 on_click=lambda: NewsState.open_url(article.url),
#                 border_radius="full",  # Botón completamente redondeado
#             ),
#             rx.spacer(),
#             # Si quisieras mostrar otra información a la derecha, podrías añadirla aquí
#             width="100%",
#             margin_top="3",
#         ),
#         align_items="flex-start",
#         width="100%",
#         padding_y="5",
#         border_bottom=rx.cond(
#             with_border,
#             "1px solid #E2E8F0",
#             "none",
#         ),
#         spacing="1",
#     )

# def noticias_financieras_style() -> rx.Component:
#     """Contenido de noticias con el estilo de lista (estilo 3)."""
#     return rx.box(
#         rx.heading(
#             "Noticias Financieras",
#             size="8",
#             color=TEXT_DARK,
#             margin_bottom="8",
#             text_align="center",
#         ),
#         rx.vstack(
#             # Sección de noticia destacada
#             rx.box(
#                 rx.heading("Destacado", size="5", color=TEXT_DARK, margin_bottom="3", border_bottom="1px solid #E2E8F0", padding_bottom="2"),
#                 rx.cond(
#                     NewsState.featured_news,
#                     simple_news_item(NewsState.featured_news, with_border=False),
#                     rx.cond(
#                         NewsState.has_news,
#                         rx.center(rx.text("No hay noticia destacada."), padding="6"),
#                         rx.center(rx.spinner(size="2", color=BLUE), padding="6")
#                     )
#                 ),
#                 margin_bottom="8",
#                 padding="4",
#                 border="1px solid #E2E8F0",
#                 border_radius="lg",
#                 bg="white",
#             ),

#             # Sección de noticias recientes (lista principal)
#             rx.box(
#                  rx.heading("Recientes", size="5", color=TEXT_DARK, margin_bottom="3", border_bottom="1px solid #E2E8F0", padding_bottom="2"),
#                  rx.cond(
#                     NewsState.processed_news.length() > 0,
#                     rx.vstack(
#                         rx.foreach(
#                             NewsState.processed_news,
#                             lambda article: simple_news_item(article),
#                         ),
#                         spacing="0",
#                         align_items="stretch",
#                         width="100%",
#                     ),
#                     rx.center(
#                         rx.cond(
#                             NewsState.is_loading,
#                             rx.spinner(size="3", color=BLUE),
#                             rx.text("No hay noticias recientes disponibles.")
#                         ),
#                         padding="10",
#                     )
#                 ),
#                 width="100%",
#             ),

#             # Botón "Cargar más noticias"
#             rx.cond(
#                 NewsState.can_load_more,
#                 rx.center(
#                     rx.button(
#                         rx.cond(NewsState.is_loading, "Cargando...", "Cargar más noticias"),
#                         on_click=NewsState.load_more_news,
#                         is_loading=NewsState.is_loading,
#                         color_scheme="blue",
#                         variant="soft",
#                         size="2",
#                         margin_top="6",
#                         border_radius="full",  # Botón completamente redondeado
#                     ),
#                     width="100%",
#                 ),
#                 rx.box()
#             ),
#             align_items="stretch",
#             spacing="6",
#             width="100%",
#             max_width="900px",
#             margin_x="auto",
#         ),
#         width="100%",
#         padding="6",
#     )

# # --- SELECTOR DE ESTILOS Y ESTRUCTURA PRINCIPAL ---

# def select_style() -> rx.Component:
#     """Selector de estilos para la página de noticias."""
#     return rx.flex(
#         rx.button(
#             "Panel",
#             on_click=lambda: NewsState.change_style("panel"),
#             variant=rx.cond(NewsState.selected_style == "panel", "solid", "soft"),
#             color_scheme=rx.cond(NewsState.selected_style == "panel", "blue", "gray"),
#             size="2",
#             border_radius="full",  # Botones redondeados
#         ),
#         rx.button(
#             "Publicaciones",
#             on_click=lambda: NewsState.change_style("publicaciones"),
#             variant=rx.cond(NewsState.selected_style == "publicaciones", "solid", "soft"),
#             color_scheme=rx.cond(NewsState.selected_style == "publicaciones", "blue", "gray"),
#             size="2",
#             border_radius="full",  # Botones redondeados
#         ),
#         rx.button(
#             "Financieras",
#             on_click=lambda: NewsState.change_style("financieras"),
#             variant=rx.cond(NewsState.selected_style == "financieras", "solid", "soft"),
#             color_scheme=rx.cond(NewsState.selected_style == "financieras", "blue", "gray"),
#             size="2",
#             border_radius="full",  # Botones redondeados
#         ),
#         justify="center",
#         spacing="3",
#         margin_bottom="8",
#         wrap="wrap",
#     )

# def news_content() -> rx.Component:
#     """Contenido principal de la página de noticias con selección de estilo."""
#     return rx.vstack(
#         select_style(),
#         rx.box(
#             rx.match(
#                 NewsState.selected_style,
#                 ("panel", panel_noticias_style()),
#                 ("publicaciones", publicaciones_recientes_style()),
#                 ("financieras", noticias_financieras_style()),
#                 panel_noticias_style(),
#             ),
#             width="100%",
#         ),
#         width="100%",
#         align_items="stretch",
#         min_height="70vh",
#     )

# def noticias_page() -> rx.Component:
#     """Página de noticias completa usando el layout común."""
#     return layout(news_content())

# # Define la página de Reflex
# noticias = rx.page(
#     route="/noticias",
#     title="TradeSim - Noticias Financieras",
#     on_load=NewsState.get_news
# )(noticias_page)

import reflex as rx
from ..components.layout import layout
from ..state.news_state import NewsState, NewsArticle
import random

# --- Definición de colores ---
BLUE = "#5271FF"
BLUE_LIGHT = "#EEF1FF"
BLUE_DARK = "#3B55D9"
TEXT_DARK = "#202124"
TEXT_GRAY = "#5F6368"
LIGHT_PURPLE = "#E9ECFF"

# Definir las etiquetas
TAGS_LIST = ["trade", "news", "trends", "markets", "finance", "crypto"]
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

# --- Componentes del Panel de Noticias ---

def featured_article(article: NewsArticle) -> rx.Component:
    """Componente para mostrar la noticia destacada."""
    return rx.box(
        rx.vstack(
            rx.image(
                src=rx.cond(article.image != "", article.image, "/api/placeholder/640/360"),
                alt=article.title,
                width="90%",
                height="auto",
                object_fit="cover",
                margin_bottom="4",
            ),
            rx.heading(
                article.title,
                size="6",
                color=TEXT_DARK,
                width="90%",
                margin_bottom="2",
                line_height="1.2",
                font_weight="bold",
            ),
            rx.text(
                article.summary,
                color=TEXT_GRAY,
                font_size="md",
                width="90%",
                line_height="1.5",
                margin_bottom="4",
            ),
            rx.flex(
                rx.button(
                    "Leer Mas",
                    bg=BLUE,
                    color="white",
                    border_radius="full",
                    padding_x="5",
                    padding_y="2",
                    size="2",
                    _hover={"bg": BLUE_DARK},
                    on_click=lambda: NewsState.open_url(article.url),
                ),
                rx.spacer(),
                rx.text(
                    article.date,
                    color=TEXT_GRAY,
                    font_size="sm",
                    font_style="italic",
                ),
                width="100%",
                justify="between",
                align_items="center",
                margin_top="auto",
            ),
            align_items="flex-start",
            width="90%",
            height="90%",
        ),
        width="90%",
    )

def recent_post_item(article: NewsArticle) -> rx.Component:
    """Componente para mostrar un post reciente."""
    return rx.flex(
        rx.image(
            src=rx.cond(article.image != "", article.image, "/api/placeholder/80/80"),
            alt=article.title,
            width="100",
            height="100px",
            object_fit="cover",
            border_radius="lg",
        ),
        rx.vstack(
            rx.heading(
                article.title,
                size="3",
                color=TEXT_DARK,
                no_of_lines=2,
                font_weight="medium",
            ),
            rx.text(
                article.date,
                color=TEXT_GRAY,
                font_size="xs",
                font_style="italic",
            ),
            align_items="flex-start",
            spacing="1",
            width="95%",
        ),
        spacing="3",
        align_items="center",
        width="95%",
        margin_bottom="4",
        padding="2",
        border_radius="2xl",
        _hover={"bg": LIGHT_PURPLE, "cursor": "pointer"},
        on_click=lambda: NewsState.open_url(article.url),
    )

def recent_posts_section() -> rx.Component:
    """Sección de posts recientes."""
    return rx.vstack(
        rx.button(
            "Posts Recientes",
            size="3",
            color="white",
            bg=BLUE,
            border_radius="full",
            margin_bottom="4",
            _hover={"bg": BLUE_DARK},
            font_weight="medium",
            on_click=lambda: NewsState.change_style("publicaciones"),
        ),
        rx.cond(
            NewsState.recent_news_list.length() > 0,
            rx.vstack(
                rx.foreach(
                    NewsState.recent_news_list[:3],  # Limitamos a 3 posts recientes
                    lambda article: recent_post_item(article),
                ),
                spacing="2",
                width="100%",
            ),
            rx.center(
                rx.cond(
                    NewsState.is_loading,
                    rx.spinner(size="3", color=BLUE),
                    rx.text("No hay posts recientes.")
                ),
                padding="6",
            ),
        ),
        spacing="2",
        align_items="stretch",
        width="100%",
        padding="6",
        border_radius="2xl",
        background=BLUE_LIGHT,
        height="100%",
    )

def news_panel() -> rx.Component:
    """Panel de noticias completo."""
    return rx.box(
        rx.heading(
            "Panel de noticias",
            size="8",
            color=TEXT_DARK,
            margin_bottom="8",
        ),
        rx.grid(
            # Columna izquierda: Artículo destacado
            rx.box(
                rx.cond(
                    NewsState.featured_news,
                    featured_article(NewsState.featured_news),
                    rx.center(
                        rx.cond(
                            NewsState.is_loading,
                            rx.spinner(size="3", color=BLUE),
                            rx.text("No hay artículo destacado.")
                        ),
                        height="100%",
                    )
                ),
                width="100%",
                grid_column=["span 12", "span 12", "span 8"],
            ),
            # Columna derecha: Posts recientes
            rx.box(
                recent_posts_section(),
                width="100%",
                grid_column=["span 12", "span 12", "span 4"],
            ),
            columns={
                "initial": "repeat(12, 1fr)",
                "md": "repeat(12, 1fr)",
                "lg": "repeat(12, 1fr)",
            },
            template_rows={
                "initial": "auto auto", 
                "md": "auto auto", 
                "lg": "auto",
            },
            gap="6",
            width="100%",
            max_width="1200px",
            margin_x="auto",
        ),
        width="100%",
        padding="6",
    )

def publicaciones_recientes_style() -> rx.Component:
    """Contenido de noticias con el estilo de grid de tarjetas."""
    return rx.box(
        rx.flex(
            rx.button(
                "Volver al Panel de Noticias",
                on_click=lambda: NewsState.change_style("panel"),
                variant="soft",
                color_scheme="blue",
                size="2",
                border_radius="full",
                margin_bottom="4",
            ),
            # Cambiado de "flex-start" a "start" para corregir el error
            justify="start",
            width="100%",
            max_width="1200px",
            margin_x="auto",
        ),
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
                    lambda article, i: rx.box(
                        rx.vstack(
                            rx.box(
                                rx.image(
                                    src=rx.cond(article.image != "", article.image, f"/api/placeholder/400/250"),
                                    alt=article.title,
                                    width="100%",
                                    height="200px",
                                    object_fit="cover",
                                    border_top_left_radius="xl",
                                    border_top_right_radius="xl",
                                ),
                                rx.box(
                                    news_tag(TAGS_VAR[i % TAGS_VAR.length()]),
                                    position="absolute",
                                    top="3",
                                    left="3",
                                ),
                                position="relative",
                                width="100%",
                            ),
                            rx.vstack(
                                rx.hstack(
                                    rx.link(
                                        "Leer post completo →",
                                        href=article.url,
                                        is_external=True,
                                        color=BLUE_DARK,
                                        font_size="sm",
                                        font_weight="medium",
                                        _hover={"text_decoration": "underline"},
                                        border_radius="full",
                                    ),
                                    rx.spacer(),
                                    rx.text(
                                        article.date,
                                        color=TEXT_GRAY,
                                        font_size="xs",
                                    ),
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
                    ),
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
                "sm": "2",
                "md": "2",
                "lg": "3",
            },
            gap="5",
            width="100%",
            max_width="1200px",
            margin_x="auto",
        ),
        width="100%",
        padding="6",
    )

def news_content() -> rx.Component:
    """Función que devuelve el contenido según el estilo seleccionado."""
    return rx.vstack(
        # Contenido condicionado al estilo seleccionado
        rx.cond(
            NewsState.selected_style == "publicaciones",
            publicaciones_recientes_style(),  # Si el estilo es "publicaciones", muestra este componente
            news_panel()  # Default: panel de noticias
        ),
        width="100%",
        spacing="4",
    )

def noticias_page() -> rx.Component:
    """Página de noticias usando el layout común."""
    return layout(news_content())

# Define la página de Reflex
noticias = rx.page(
    route="/noticias",
    title="TradeSim - Noticias Financieras",
    on_load=NewsState.get_news  # Importante: carga los datos de la API cuando la página se carga
)(noticias_page)