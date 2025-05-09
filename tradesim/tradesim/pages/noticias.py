# <<<--- CODI COMPLET FINAL PER A noticias.py --- >>>
import reflex as rx
# Assegura't que aquestes importacions siguin correctes per al teu projecte
from ..components.layout import layout
from ..state.news_state import NewsState, NewsArticle

# --- Definició de Colors ---
BLUE = "#5271FF"
BLUE_LIGHT = "#EEF1FF"
BLUE_DARK = "#3B55D9"
TEXT_DARK = "#202124"
TEXT_GRAY = "#5F6368"
LIGHT_GRAY_BORDER = "#E2E8F0"
WHITE = "#FFFFFF"
RECENT_CARD_BG = "#C2CDFF" # RGB(194, 205, 255) per a targetes de publicacions
PAGE_CONTAINER_BG = WHITE # Fons blanc per als contenidors principals

# --- Etiquetes ---
TAGS_LIST = ["#trade", "#down", "#trends", "#trends", "#news", "#trends", "#finance", "#crypto"]
TAGS_VAR = rx.Var.create(TAGS_LIST)

# --- Funció helper de validació d'URL (simple) ---
def is_valid_url(url: str) -> bool:
    # Comprova si és string i comença amb http:// o https://
    return isinstance(url, str) and url.startswith(("http://", "https://"))

# --- Components Reutilizables ---
def news_tag(tag: rx.Var[str]) -> rx.Component:
    """Componente para mostrar una etiqueta de categoría."""
    return rx.text(
        tag, bg=BLUE_LIGHT, color=BLUE_DARK, font_size="0.75em", font_weight="medium",
        padding_x="10px", padding_y="3px", border_radius="lg", # Arrodoniment tag
    )

# --- Componentes del Panel de Noticias (Pàgina Principal) ---
def featured_article(article: NewsArticle) -> rx.Component:
    """Componente para mostrar la noticia destacada (usa rx.link)."""
    return rx.link(
        rx.box(
            rx.vstack(
                rx.image(
                    src=rx.cond(article.image != "", article.image, "/api/placeholder/700/394"),
                    alt=article.title, width="100%", height="auto", aspect_ratio="16/9",
                    object_fit="cover", border_radius="2xl", margin_bottom="1.5rem",
                ),
                rx.heading(
                    article.title, size="7", color=TEXT_DARK, font_weight="bold",
                    line_height="1.3", margin_bottom="0.75rem", width="100%", text_align="left",
                ),
                rx.text(
                    article.summary, color=TEXT_GRAY, font_size="1em", line_height="1.6",
                    no_of_lines=3, margin_bottom="2rem", width="100%", text_align="left",
                ),
                rx.flex(
                    rx.button(
                        "Leer Mas", bg=BLUE, color=WHITE, border_radius="full",
                        padding_x="24px", padding_y="10px", size="2", font_weight="medium",
                        _hover={"bg": BLUE_DARK, "cursor": "pointer"},
                    ),
                    rx.spacer(),
                    rx.text(article.date, color=TEXT_GRAY, font_size="0.875em", align_self="center"),
                    width="100%", justify="between", align_items="center", margin_top="auto",
                ),
                align_items="flex-start", width="100%", height="100%", spacing="0",
            ),
            width="100%", padding="1.5rem", border_radius="2xl", overflow="hidden",
        ),
        href=article.url, is_external=True, _hover={"text_decoration": "none"}, width="100%", height="100%",
    )

def recent_post_item(article: NewsArticle) -> rx.Component:
    """Componente para mostrar un post reciente en la llista lateral (usa on_click + JS)."""
    # Funció helper per crear el script JS de forma segura
    def open_link_script(url: str) -> rx.event.EventSpec:
        if is_valid_url(url):
            safe_url = url.replace("'", "\\'") # Escapa cometes simples
            return rx.call_script(f"window.open('{safe_url}', '_blank')")
        else:
            print(f"URL invàlida per a script: {url}")
            return rx.console_log("URL invàlida, no s'obre.")

    return rx.box(
        rx.flex(
            rx.image(
                src=rx.cond(article.image != "", article.image, "/api/placeholder/80/80"),
                alt=article.title, width="80px", height="80px", object_fit="cover",
                border_radius="xl", flex_shrink=0,
            ),
            rx.vstack(
                rx.heading(
                    article.title, size="3", color=TEXT_DARK, font_weight="medium",
                    no_of_lines=2, line_height="1.4", margin_bottom="2px", text_align="left",
                ),
                rx.text(article.date, color=TEXT_GRAY, font_size="0.75em", text_align="left"),
                align_items="flex-start", justify_content="center", spacing="1",
                height="100%", margin_left="1rem", width="100%",
            ),
            spacing="3", align_items="center", width="100%",
        ),
        padding="0.75rem", margin_bottom="1rem", border_radius="xl", width="100%",
        _hover={
            "background_color": rx.color_mode_cond(light="#E0E7FF", dark="#3A3A3A"),
            "cursor": "pointer" # Cursor pointer explícit
        },
        # Utilitza on_click amb rx.call_script per forçar nova pestanya
        on_click=open_link_script(article.url),
    )

def recent_posts_section() -> rx.Component:
    """Sección de posts recientes (columna dreta)."""
    return rx.box(
        rx.vstack(
            rx.button(
                "Posts Recientes", size="3", color=WHITE, bg=BLUE, border_radius="full",
                padding_x="20px", padding_y="10px", font_weight="medium",
                align_self="flex-start", margin_bottom="1.5rem",
                _hover={"bg": BLUE_DARK, "cursor": "pointer"},
                on_click=lambda: NewsState.change_style("publicaciones"), # Canvia vista
            ),
            # Condició reforçada per evitar error 'map' durant la càrrega inicial
            rx.cond(
                NewsState.recent_news_list, # Comprova que la llista existeix
                rx.cond(
                    NewsState.recent_news_list.length() > 0, # Comprova que té elements
                    rx.vstack(
                        rx.foreach(
                            NewsState.recent_news_list[:3], # Itera només sobre els 3 primers
                            lambda article: recent_post_item(article)
                        ),
                        spacing="0", width="100%",
                    ),
                    # Cas: llista existeix però buida
                    rx.center(rx.text("No hay posts recientes.", color=TEXT_GRAY), padding_y="3rem", width="100%", min_height="200px")
                ),
                # Cas: llista no existeix (inicialment) o està carregant
                rx.center(
                    rx.cond(
                        NewsState.is_loading,
                        rx.vstack(rx.spinner(size="3", color=BLUE), rx.text("Cargando...", color=TEXT_GRAY, margin_top="0.5rem"), spacing="2"),
                        rx.text("No hay posts recientes.", color=TEXT_GRAY) # Fallback
                    ),
                    padding_y="3rem", width="100%", min_height="200px",
                ),
            ),
            spacing="0", align_items="stretch", width="100%",
        ),
        width="100%", height="100%", padding="1rem", border_radius="3xl",
        background=BLUE_LIGHT,
        box_shadow="0px 8px 16px -4px rgba(82, 113, 255, 0.15), 0px 4px 8px -4px rgba(82, 113, 255, 0.1)",
        overflow="hidden",
    )

def news_panel() -> rx.Component:
    """Panel de noticias completo (vista principal)."""
    return rx.box(
        rx.heading(
            "Panel de noticias", size="8", color=TEXT_DARK, margin_bottom="2rem",
            text_align=["center", "center", "left"],
        ),
        rx.grid(
            rx.box(
                rx.cond(
                    NewsState.featured_news,
                    featured_article(NewsState.featured_news),
                    rx.center(
                        rx.cond(
                            NewsState.is_loading,
                             rx.vstack(rx.spinner(size="3", color=BLUE), rx.text("Cargando...", color=TEXT_GRAY, margin_top="0.5rem"), spacing="2"),
                            rx.text("No hay artículo destacado.", color=TEXT_GRAY)
                        ),
                        min_height="400px", width="100%", border_radius="2xl", background="#f8f8f8",
                    )
                ),
                width="100%", grid_column=["span 12", "span 12", "span 8"],
                padding_bottom=["2rem", "2rem", "0"],
            ),
            rx.box(
                recent_posts_section(), width="100%", grid_column=["span 12", "span 12", "span 4"],
            ),
            columns="12", spacing="5", width="100%", align_items="stretch",
            # Ocupa amplada completa, marges controlats pel layout
        ),
        width="100%", padding="1.5rem", background=PAGE_CONTAINER_BG,
        border_radius="2xl", box_shadow="lg",
        # Marge exterior controlat pel padding del layout
    )

# --- Component per a la Pàgina de Publicacions Recents (Segona Vista) ---
def publication_card(article: NewsArticle, index: rx.Var[int]) -> rx.Component:
    """Targeta individual per a la vista de graella de publicacions."""
    tag_index = index % TAGS_VAR.length()

    # Helper per obtenir l'acció (obrir URL des de l'estat)
    def open_card_link():
         # Crida directament a l'event handler de l'estat
         return NewsState.open_url(article.url)

    return rx.box(
        rx.vstack(
            rx.image(
                src=rx.cond(article.image != "", article.image, f"/api/placeholder/400/225?text=Noticia+{index+1}"),
                alt=article.title, width="100%", height="auto", aspect_ratio="16/9",
                object_fit="cover", border_top_left_radius="3xl", border_top_right_radius="3xl",
            ),
            rx.vstack(
                news_tag(TAGS_VAR[tag_index]),
                rx.text(article.date, color=TEXT_GRAY, font_size="0.75em", margin_bottom="0.5rem"),
                rx.heading(
                    article.title, size="4", color=TEXT_DARK, font_weight="bold",
                    align="left", line_height="1.4", no_of_lines=3,
                    margin_bottom="1rem", flex_grow=1,
                ),
                 rx.link( # Link visual, però l'acció principal és a la targeta
                    "Read full post →", color=BLUE_DARK, font_size="0.875em",
                    font_weight="medium", _hover={"text_decoration": "underline"}, margin_top="auto",
                    href=article.url, # Afegir href per semàntica i accessibilitat
                    is_external=True, # Encara que el clic principal sigui a la targeta
                 ),
                align_items="flex-start", spacing="0", width="100%", padding="1.25rem",
                flex_grow=1, height="100%",
            ),
            align_items="stretch", spacing="0", width="100%", height="100%",
        ),
        width="100%", height="100%", background=RECENT_CARD_BG, # Fons #C2CDFF
        border=f"1px solid {LIGHT_GRAY_BORDER}", border_radius="3xl",
        overflow="hidden", box_shadow="md",
        transition="transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out",
        _hover={ "transform": "translateY(-5px)", "box_shadow": "xl", "cursor": "pointer" },
        # El clic a tota la targeta obre l'URL usant l'event handler de l'estat
        on_click=open_card_link,
    )

def publicaciones_recientes_style() -> rx.Component:
    """Contenido de noticias con el estilo de grid de tarjetas (Segona Vista)."""
    return rx.box(
        rx.vstack(
            rx.heading(
                "Publicaciones Recientes", size="8", color=TEXT_DARK, text_align="left", width="100%",
            ),
            rx.button(
                    "← Volver al Panel", on_click=lambda: NewsState.change_style("panel"),
                    variant="outline", color_scheme="gray", size="2", border_radius="full",
                    margin_bottom="2rem", margin_top="0.5rem", align_self="flex-start",
                    _hover={"background_color": LIGHT_GRAY_BORDER}
            ),
            align_items="flex-start", width="100%", margin_bottom="1.5rem", spacing="0",
        ),
        rx.grid(
            # Condició reforçada per evitar error 'map'
            rx.cond(
                NewsState.processed_news, # Comprova que existeix
                rx.cond(
                    NewsState.processed_news.length() > 0, # Comprova que té elements
                    rx.foreach(
                        NewsState.processed_news, # Itera sobre la llista segura
                        lambda article, i: publication_card(article, i)
                    ),
                    # Si existeix però està buida
                    rx.center(rx.text("No hay publicaciones.", color=TEXT_GRAY), min_height="300px", grid_column="span 1 / -1")
                ),
                 # Si processed_news és null/undefined inicialment o si està carregant
                rx.center(
                    rx.cond(
                        NewsState.is_loading,
                        rx.vstack(rx.spinner(size="3", color=BLUE), rx.text("Cargando...", color=TEXT_GRAY, margin_top="0.5rem"), spacing="2"),
                        rx.text("No hay publicaciones.", color=TEXT_GRAY) # Cas estrany
                    ),
                    min_height="300px", grid_column="span 1 / -1",
                )
            ),
            columns={"initial": "1", "sm": "2", "md": "3", "lg": "3"}, # 3 columnes en md/lg
            spacing="5", # Espai entre targetes
            width="100%",
            # Ocupa amplada completa (controlat pel layout)
        ),

        # Botó "Cargar más noticias"
        rx.cond(
            NewsState.can_load_more, # Mostra només si es pot carregar més
            rx.center( # Centra el botó
                rx.button(
                    rx.cond(NewsState.is_loading, "Cargando...", "Cargar más noticias"),
                    on_click=NewsState.load_more_news, # Crida a l'event handler
                    is_loading=NewsState.is_loading, # Mostra estat de càrrega
                    variant="soft", # Estil més suau
                    color_scheme="blue",
                    size="2",
                    border_radius="full", # Arrodonit
                    margin_top="2.5rem", # Espai sobre el botó
                    padding_x="6", # Padding del botó
                ),
                width="100%", # Ocupa amplada per centrar correctament
            ),
            rx.box() # No mostra res si no es pot carregar més
        ),

        # Estils generals del contenidor
        width="100%", padding="1.5rem", background=PAGE_CONTAINER_BG,
        border_radius="2xl", box_shadow="lg",
        # Marge exterior controlat pel padding del layout
    )

# --- Funció Principal de Contingut ---
def news_content() -> rx.Component:
    """Retorna el component adequat segons l'estat seleccionat."""
    return rx.cond(
            NewsState.selected_style == "publicaciones",
            publicaciones_recientes_style(),
            news_panel()
        )

# --- Definició de la Pàgina ---
def noticias_page() -> rx.Component:
    """Pàgina de notícies completa usant el layout."""
    # El layout s'encarrega de l'estructura (sidebar+navbar) i el padding exterior
    return layout(news_content())

# Registra la pàgina
noticias = rx.page(
    route="/noticias",
    title="TradeSim | Noticias Financieras",
    on_load=NewsState.get_news # Crida a get_news quan es carrega la pàgina
)(noticias_page)