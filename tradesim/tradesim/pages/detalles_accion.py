import reflex as rx
from ..components.layout import layout
from ..state.news_state import NewsState
from ..pages.noticias import featured_article

# Página de detalles de acción

def detalles_accion_page() -> rx.Component:
    return layout(
        rx.hstack(
            # Primera mitad: Información de la acción
            rx.box(
                rx.vstack(
                    rx.heading("Información de la Acción", size="5", margin_bottom="4"),
                    rx.text("Nombre: Tesla Inc.", font_size="lg"),
                    rx.text("Símbolo: TSLA", font_size="lg"),
                    rx.text("Precio actual: $720.00", font_size="lg"),
                    rx.text("Sector: Tecnología", font_size="lg"),
                    rx.text("Variación diaria: +2.5%", font_size="lg"),
                    rx.text("Volumen: 10,000,000", font_size="lg"),
                    # Gráfico (placeholder)
                    rx.box(
                        rx.text("[Gráfico de la acción]", font_size="lg", font_weight="bold"),
                        height="300px",
                        width="100%",
                        background="#f0f4ff",
                        border_radius="md",
                        box_shadow="sm",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        margin_bottom="4",
                    ),
                    # Botones debajo del gráfico
                    rx.hstack(
                        rx.button("Comprar", color="white", background="#5271FF"),
                        rx.button("Vender", color="white", background="#FF5271"),
                        spacing="4",
                        margin_bottom="4",
                    ),
                    width="100%",
                    spacing="3",
                    background="#fff",
                    border_radius="md",
                    box_shadow="md",
                    padding="6",
                ),
                width="50%",
                padding="6",
            ),
            # Segunda mitad: Noticia principal desde la API
            rx.box(
                rx.vstack(
                    rx.box(
                        rx.cond(
                            NewsState.featured_news,
                            featured_article(NewsState.featured_news),
                            rx.center(
                                rx.cond(
                                    NewsState.is_loading,
                                    rx.text("Cargando noticia...", font_size="md"),
                                    rx.text("No hay noticia disponible.", font_size="md")
                                ),
                                min_height="200px"
                            )
                        ),
                        background="#f9fafb",
                        border_radius="md",
                        box_shadow="xs",
                        padding="3",
                        margin_top="2",
                        width="100%",
                    ),
                    # Botón de noticia debajo del contenedor de noticia
                    rx.button(
                        "Vita nuestro panel de noticias!",
                        on_click=rx.redirect("/noticias"),
                        color="white",
                        background="#3b5cf4",
                        width="100%",
                        margin_top="2",
                    ),
                ),
                width="50%",
                padding="6",
            ),
            width="100%",
            spacing="0",
        )
    )

# Registrar la página

detalles_accion = rx.page(
    route="/detalles_accion",
    title="TradeSim - Detalles de Acción",
    on_load=NewsState.get_news
)(detalles_accion_page)
