# tradesim/pages/noticias.py
import reflex as rx
from ..components.layout import layout
# Importar AuthState y NewsArticle (definido ahora en auth_state.py)
from ..state.auth_state import AuthState, NewsArticle
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- Constantes de Estilo ---
BLUE="#5271FF"; BLUE_LIGHT="#EEF1FF"; BLUE_DARK="#3B55D9"; TEXT_DARK="#202124"
TEXT_GRAY="#5F6368"; LIGHT_GRAY_BORDER="#E2E8F0"; WHITE="#FFFFFF"
RECENT_CARD_BG="#C2CDFF"; PAGE_CONTAINER_BG=WHITE

# --- Etiquetes ---
TAGS_LIST = ["#trade", "#down", "#trends", "#trends", "#news", "#trends", "#finance", "#crypto"]
TAGS_VAR = rx.Var.create(TAGS_LIST)

# --- Components Reutilizables ---
def news_tag(tag: rx.Var[str]) -> rx.Component:
    return rx.text(tag, bg=BLUE_LIGHT, color=BLUE_DARK, font_size="0.75em", font_weight="medium", px="10px", py="3px", border_radius="lg")

# --- Componentes Panel Principal ---
def featured_article(article: NewsArticle) -> rx.Component:
    # Usa AuthState para datos y handlers si fuera necesario, aquí usa rx.link directo
    return rx.link(rx.box(rx.vstack(rx.image(src=rx.cond(article.image != "", article.image, "/api/placeholder/700/394"), alt=article.title, width="100%", aspect_ratio="16/9", object_fit="cover", border_radius="2xl", mb="1.5rem"), rx.heading(article.title, size="7", color=TEXT_DARK, weight="bold", line_height="1.3", mb="0.75rem", w="100%", text_align="left"), rx.text(article.summary, color=TEXT_GRAY, font_size="1em", line_height="1.6", no_of_lines=3, mb="2rem", w="100%", text_align="left"), rx.flex(rx.button("Leer Mas", bg=BLUE, color=WHITE, border_radius="full", px="24px", py="10px", size="2", weight="medium", _hover={"bg": BLUE_DARK}, as_child=True), rx.spacer(), rx.text(article.date, color=TEXT_GRAY, font_size="0.875em", align_self="center"), width="100%", justify="between", align_items="center", mt="auto"), align_items="flex-start", w="100%", h="100%", spacing="0"), w="100%", p="1.5rem", border_radius="2xl", overflow="hidden"),
                  href=article.url, is_external=True, _hover={"text_decoration": "none"}, w="100%", h="100%")

def recent_post_item(article: NewsArticle) -> rx.Component:
    # Usa handler de AuthState para abrir link con script
    return rx.box(rx.flex(rx.image(src=rx.cond(article.image != "", article.image, "/api/placeholder/80/80"), alt=article.title, width="80px", height="80px", object_fit="cover", border_radius="xl", flex_shrink=0), rx.vstack(rx.heading(article.title, size="3", color=TEXT_DARK, weight="medium", no_of_lines=2, line_height="1.4", mb="2px", text_align="left"), rx.text(article.date, color=TEXT_GRAY, font_size="0.75em", text_align="left"), align_items="flex-start", justify_content="center", spacing="1", h="100%", ml="1rem", w="100%"), spacing="3", align_items="center", w="100%"), p="0.75rem", mb="1rem", border_radius="xl", w="100%", _hover={"bg": rx.color_mode_cond(light="#E0E7FF", dark="#3A3A3A"), "cursor": "pointer"},
                  on_click=lambda: AuthState.open_url_script(article.url)) # Llama al handler correcto

def recent_posts_section() -> rx.Component:
    # Usa AuthState
    return rx.box(rx.vstack(rx.button("Posts Recientes", size="3", color=WHITE, bg=BLUE, border_radius="full", px="20px", py="10px", weight="medium", align_self="flex-start", mb="1.5rem", _hover={"bg": BLUE_DARK, "cursor": "pointer"}, on_click=AuthState.change_style("publicaciones")), # Llama a handler de AuthState
                           rx.cond(AuthState.processed_news, rx.cond(AuthState.processed_news.length() > 0, rx.vstack(rx.foreach(AuthState.recent_news_list, recent_post_item), spacing="0", w="100%"), rx.center(rx.text("No hay posts recientes.", color=TEXT_GRAY), py="3rem", w="100%", min_h="200px")), rx.center(rx.cond(AuthState.is_loading_news, rx.vstack(rx.spinner(size="3", color=BLUE), rx.text("Cargando...", color=TEXT_GRAY, mt="0.5rem"), spacing="2"), rx.text("No hay posts recientes.", color=TEXT_GRAY)), py="3rem", w="100%", min_h="200px")), spacing="0", align_items="stretch", w="100%"), w="100%", h="100%", p="1rem", border_radius="3xl", background=BLUE_LIGHT, box_shadow="0px 8px 16px -4px rgba(82, 113, 255, 0.15), 0px 4px 8px -4px rgba(82, 113, 255, 0.1)", overflow="hidden")

def news_panel() -> rx.Component:
    # Usa AuthState
    return rx.box(rx.heading("Panel de noticias", size="8", color=TEXT_DARK, mb="2rem", text_align=["center", "center", "left"]), rx.grid(rx.box(rx.cond(AuthState.featured_news, featured_article(AuthState.featured_news), rx.center(rx.cond(AuthState.is_loading_news, rx.vstack(rx.spinner(size="3", color=BLUE), rx.text("Cargando...", color=TEXT_GRAY, mt="0.5rem"), spacing="2"), rx.text("No hay art\u00EDculo destacado.", color=TEXT_GRAY)), min_h="400px", w="100%", border_radius="2xl", bg="#f8f8f8")), w="100%", grid_column=["span 12", "span 12", "span 8"], pb=["2rem", "2rem", "0"]), rx.box(recent_posts_section(), w="100%", grid_column=["span 12", "span 12", "span 4"]), columns="12", spacing="5", w="100%", align_items="stretch"), w="100%", p="1.5rem", bg=PAGE_CONTAINER_BG, border_radius="2xl", box_shadow="lg")

# --- Componentes Vista Publicaciones ---
def publication_card(article: NewsArticle, index: rx.Var[int]) -> rx.Component:
    tag_index = index % TAGS_VAR.length()
    # Usa AuthState para el click
    return rx.box(rx.vstack(rx.image(src=rx.cond(article.image != "", article.image, f"/api/placeholder/400/225?text=Noticia+{index+1}"), alt=article.title, width="100%", aspect_ratio="16/9", object_fit="cover", border_top_left_radius="3xl", border_top_right_radius="3xl"), rx.vstack(news_tag(TAGS_VAR[tag_index]), rx.text(article.date, color=TEXT_GRAY, font_size="0.75em", mb="0.5rem"), rx.heading(article.title, size="4", color=TEXT_DARK, weight="bold", align="left", line_height="1.4", no_of_lines=3, mb="1rem", flex_grow=1), rx.link("Read full post \u2192", color=BLUE_DARK, font_size="0.875em", weight="medium", _hover={"text_decoration": "underline"}, mt="auto", href=article.url, is_external=True), align_items="flex-start", spacing="0", width="100%", padding="1.25rem", flex_grow=1, height="100%"), align_items="stretch", spacing="0", width="100%", height="100%"), width="100%", height="100%", background=RECENT_CARD_BG, border=f"1px solid {LIGHT_GRAY_BORDER}", border_radius="3xl", overflow="hidden", box_shadow="md", transition="transform 0.2s, box-shadow 0.2s", _hover={"transform": "translateY(-5px)", "box_shadow": "xl", "cursor": "pointer"},
                  # Llamar al handler open_url_script de AuthState
                  on_click=lambda: AuthState.open_url_script(article.url))

def publicaciones_recientes_style() -> rx.Component:
    # Usa AuthState
    return rx.box(
        rx.vstack(rx.heading("Publicaciones Recientes", size="8", color=TEXT_DARK, text_align="left", width="100%"), rx.button("\u2190 Volver al Panel", on_click=AuthState.change_style("panel"), variant="outline", color_scheme="gray", size="2", border_radius="full", mb="2rem", mt="0.5rem", align_self="flex-start", _hover={"background_color": LIGHT_GRAY_BORDER}), align_items="flex-start", width="100%", mb="1.5rem", spacing="0"),
        rx.grid(rx.cond(AuthState.processed_news, rx.cond(AuthState.processed_news.length() > 0, rx.foreach(AuthState.processed_news, lambda article, i: publication_card(article, i)), rx.center(rx.text("No hay publicaciones.", color=TEXT_GRAY), min_h="300px", grid_column="span 1 / -1")), rx.center(rx.cond(AuthState.is_loading_news, rx.vstack(rx.spinner(size="3", color=BLUE), rx.text("Cargando...", color=TEXT_GRAY, mt="0.5rem"), spacing="2"), rx.text("No hay publicaciones.", color=TEXT_GRAY)), min_h="300px", grid_column="span 1 / -1")), columns={"initial": "1", "sm": "2", "md": "3", "lg": "3"}, spacing="5", width="100%"),
        rx.cond(AuthState.can_load_more, rx.center(rx.button(rx.cond(AuthState.is_loading_news, "Cargando...", "Cargar más noticias"),
                                                        # CORRECCIÓN: Usar referencia directa al método de AuthState
                                                        on_click=AuthState.load_more_news,
                                                        is_loading=AuthState.is_loading_news, variant="soft", color_scheme="blue", size="2", border_radius="full", mt="2.5rem", px="6"), width="100%"), rx.box()),
        width="100%", padding="1.5rem", background=PAGE_CONTAINER_BG, border_radius="2xl", box_shadow="lg")

# --- Funció Principal i Definició de Pàgina ---
def news_content() -> rx.Component:
    # Usa AuthState
    return rx.cond(AuthState.selected_style == "publicaciones", publicaciones_recientes_style(), news_panel())
def noticias_page() -> rx.Component: return layout(news_content())
noticias = rx.page(route="/noticias", title="TradeSim | Noticias",
                   # Usar AuthState para cargar noticias en on_load
                   on_load=AuthState.get_news)(noticias_page)