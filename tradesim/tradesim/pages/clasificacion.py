import reflex as rx
from ..components.layout import layout  # Asumo que tienes este componente
from ..state.ranking_state import RankingState
# from ..utils.auth_middleware import require_auth # No se usa directamente en esta página

# --- Definición de Estilos y Colores ---
PRIMARY_COLOR = "#5271FF" # Azul medio
SECONDARY_COLOR = "#3b5cf4" # Azul oscuro
ACCENT_COLOR_LIGHT = "#f0f4ff" # Azul muy claro
ACCENT_COLOR_HOVER = "#e0e7ff" # Azul claro para hover
TEXT_COLOR_PRIMARY = "#1A202C" # Para texto principal sobre fondos claros
TEXT_COLOR_SECONDARY = "#4A5568" # Para texto secundario sobre fondos claros
TEXT_COLOR_ON_DARK_BG = "white" # Para texto sobre fondos oscuros
POSITIVE_COLOR = "green.600"
NEGATIVE_COLOR = "red.600"
PAGE_BACKGROUND_COLOR = "gray.100"
CARD_BACKGROUND_COLOR = "white" # Para secciones principales y círculo de posición

FONT_FAMILY_SANS = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif"
CARD_BORDER_COLOR = "gray.200" # Borde para el círculo de posición si no es destacado

# --- Componente de Tarjeta de Usuario ---
def crear_tarjeta_usuario(usuario: dict, destacado: bool = False) -> rx.Component:
    is_roi_positive = usuario["is_roi_positive"]
    is_profit_positive = usuario["is_profit_positive"]
    roi_percentage = usuario["roi_percentage"]
    profit_loss = usuario["profit_loss"]

    return rx.box(
        rx.hstack(
            rx.center(
                rx.text(f"#{usuario['position']}", font_size=["xl", "2xl", "3xl"], font_weight="bold", color=PRIMARY_COLOR),
                min_width=["50px", "60px", "70px"], height=["50px", "60px", "70px"], padding="0",
                border_radius="full", background=CARD_BACKGROUND_COLOR,
                border=f"2px solid {PRIMARY_COLOR}", # Todos los círculos con borde azul primario
                box_shadow=rx.cond(destacado, "md", "sm"),
            ),
            rx.vstack(
                rx.text(usuario["username"], font_weight="bold", font_size=["lg", "xl", "xl"], color=TEXT_COLOR_PRIMARY, no_of_lines=1),
                align_items="flex-start", margin_left="15px",
            ),
            rx.spacer(),
            rx.vstack(
                rx.text("ROI", font_size=["xs", "sm"], color=TEXT_COLOR_SECONDARY),
                rx.text(
                    rx.cond(is_roi_positive, f"+{roi_percentage:.2f}%", f"{roi_percentage:.2f}%"),
                    color=rx.cond(is_roi_positive, POSITIVE_COLOR, NEGATIVE_COLOR),
                    font_weight="semibold", font_size=["md", "lg", "lg"],
                ),
                align_items="flex-end", spacing="0",
            ),
            rx.vstack(
                rx.text("Ganancia/Pérdida", font_size=["xs", "sm"], color=TEXT_COLOR_SECONDARY),
                rx.text(
                    rx.cond(is_profit_positive, f"+${profit_loss:,.2f}", f"${profit_loss:,.2f}"),
                    color=rx.cond(is_profit_positive, POSITIVE_COLOR, NEGATIVE_COLOR),
                    font_weight="semibold", font_size=["md", "lg", "lg"],
                ),
                align_items="flex-end", spacing="0", margin_left="15px",
            ),
            width="100%", padding_x=["15px", "20px"], padding_y=["10px", "15px"], align_items="center", spacing="4",
        ),
        width="100%", background=ACCENT_COLOR_LIGHT, border_radius="lg",
        box_shadow=rx.cond(destacado, "lg", "md"),
        border=f"1px solid {PRIMARY_COLOR}",
        _hover={
            "background": ACCENT_COLOR_HOVER, "transform": "translateY(-2px)",
            "box_shadow": rx.cond(destacado, "xl", "lg"),
        },
        transition="all 0.2s ease-out", cursor="pointer",
    )

# --- Página de Clasificación ---
def clasificacion_page() -> rx.Component:
    return layout(
        rx.box(
            rx.vstack(
                rx.heading("Clasificación de Inversores", as_="h1", size="8", margin_bottom="30px", color=TEXT_COLOR_PRIMARY, font_family=FONT_FAMILY_SANS, text_align="center"),
                rx.cond(
                    RankingState.ranking_loading,
                    rx.center(
                        rx.vstack(rx.spinner(color=PRIMARY_COLOR, size="3"), rx.text("Cargando clasificación...", margin_top="10px", color=TEXT_COLOR_SECONDARY), spacing="3"),
                        padding_y="50px",
                    ),
                    rx.cond(
                        RankingState.ranking_error_message != "",
                        rx.callout(RankingState.ranking_error_message, icon="triangle_alert", color_scheme="red", variant="outline", width="100%", margin_y="4"),
                        rx.box() # Placeholder if no error and not loading
                    )
                ),

                # Sección del TOP 3
                rx.box(
                    rx.vstack(
                        rx.heading("🏆 TOP 3 Inversores", as_="h2", size="6", font_weight="bold", color=TEXT_COLOR_PRIMARY, margin_bottom="20px"),
                        rx.vstack(
                            rx.foreach(RankingState.top_users[:3], lambda usuario: crear_tarjeta_usuario(usuario, destacado=True)),
                            spacing="4", width="100%",
                        ),
                        align_items="stretch", width="100%",
                    ),
                    background_color=CARD_BACKGROUND_COLOR, width="100%", padding=["25px", "30px", "35px"],
                    border_radius="xl", box_shadow="lg", margin_bottom="30px",
                ),

                # Sección de TOP 4 al 10
                rx.box(
                    rx.vstack(
                        rx.heading("Posiciones 4 a 10", as_="h2", size="6", font_weight="bold", color=TEXT_COLOR_PRIMARY, margin_bottom="20px"),
                        rx.hstack(
                            rx.text("Pos.", font_weight="bold", min_width=["50px", "60px", "70px"], text_align="center"),
                            rx.text("Usuario", font_weight="bold", flex="1", text_align="left"),
                            rx.text("ROI", font_weight="bold", width=["80px", "100px"], text_align="right"),
                            rx.text("Ganancias", font_weight="bold", width=["100px", "120px"], text_align="right"),
                            width="100%", padding_x="15px", padding_y="12px", color=TEXT_COLOR_ON_DARK_BG, background=SECONDARY_COLOR, border_top_radius="lg", # Cabecera más redondeada
                        ),
                        rx.vstack(
                            rx.foreach(RankingState.top_users[3:], crear_tarjeta_usuario),
                            spacing="4", width="100%", padding_top="4"
                        ),
                        align_items="stretch", width="100%",
                    ),
                    width="100%", background_color=CARD_BACKGROUND_COLOR, border_radius="xl", box_shadow="lg",
                    padding=["25px", "30px"], overflow="hidden", margin_bottom="30px",
                ),

                # Tu posición (si estás autenticado)
                rx.cond(
                    RankingState.is_authenticated & (RankingState.user_position != {}),
                    rx.box( # Contenedor de la sección "Tu Rendimiento Actual"
                        rx.vstack(
                            rx.heading(
                                "Tu Rendimiento Actual", as_="h2", size="6",
                                font_weight="bold", color=TEXT_COLOR_PRIMARY, margin_bottom="20px",
                            ),
                            # Tarjeta específica para "Tu Rendimiento Actual"
                            rx.box(
                                rx.hstack(
                                    rx.center(
                                        rx.text(
                                            "#13", # MODIFICADO: Posición fija
                                            font_size=["xl", "2xl", "3xl"], font_weight="bold", color=PRIMARY_COLOR,
                                        ),
                                        min_width=["50px", "60px", "70px"], height=["50px", "60px", "70px"], padding="0",
                                        border_radius="full", background=CARD_BACKGROUND_COLOR, # Fondo blanco para el círculo
                                        border=f"2px solid {PRIMARY_COLOR}",
                                        box_shadow="md",
                                    ),
                                    rx.vstack(
                                        rx.text(
                                            RankingState.username,
                                            font_weight="bold", font_size=["lg", "xl", "xl"], color=TEXT_COLOR_ON_DARK_BG, # MODIFICADO: Color de texto
                                            no_of_lines=1,
                                        ),
                                        align_items="flex-start", margin_left="15px",
                                    ),
                                    rx.spacer(),
                                    rx.vstack(
                                        rx.text("ROI", font_size=["xs", "sm"], color=TEXT_COLOR_ON_DARK_BG), # MODIFICADO: Color de texto
                                        rx.text(
                                            f"{RankingState.user_position.get('roi_percentage', 0):.2f}%",
                                            color=rx.cond(RankingState.user_position["is_roi_positive"], POSITIVE_COLOR, NEGATIVE_COLOR),
                                            font_weight="semibold", font_size=["md", "lg", "lg"],
                                        ),
                                        align_items="flex-end", spacing="0",
                                    ),
                                    rx.vstack(
                                        rx.text("Ganancia", font_size=["xs", "sm"], color=TEXT_COLOR_ON_DARK_BG), # MODIFICADO: Color de texto
                                        rx.text(
                                            f"${RankingState.user_position.get('profit_loss', 0):,.2f}",
                                            color=rx.cond(RankingState.user_position["is_profit_positive"], POSITIVE_COLOR, NEGATIVE_COLOR),
                                            font_weight="semibold", font_size=["md", "lg", "lg"],
                                        ),
                                        align_items="flex-end", spacing="0", margin_left="15px",
                                    ),
                                    width="100%", padding_x=["15px", "20px"], padding_y=["10px", "15px"], align_items="center", spacing="4",
                                ),
                                width="100%",
                                background=SECONDARY_COLOR, # MODIFICADO: Fondo azul oscuro
                                border_radius="lg",
                                box_shadow="xl",
                                border=f"2px solid {PRIMARY_COLOR}", # Borde azul primario (más claro que el fondo)
                                padding="15px",
                                _hover={
                                    "background": PRIMARY_COLOR, # MODIFICADO: Hover a azul primario (más claro)
                                    "transform": "translateY(-2px)",
                                    "box_shadow": "2xl",
                                },
                                transition="all 0.2s ease-out",
                            ),
                            align_items="stretch", width="100%",
                        ),
                        background_color=CARD_BACKGROUND_COLOR, # Fondo blanco para la sección exterior
                        width="100%", padding=["25px", "30px"], border_radius="xl",
                        box_shadow="lg", margin_bottom="50px",
                    ),
                    rx.box(), # Placeholder if not authenticated or no user position
                ),

                width="100%", max_width="1200px", align_items="center", margin_x="auto",
                spacing="8",
                padding_x=["15px", "20px", "30px"], padding_y="40px",
                font_family=FONT_FAMILY_SANS,
            ),
            background_color=PAGE_BACKGROUND_COLOR, min_height="100vh", width="100%",
            display="flex", flex_direction="column", align_items="center",
        )
    )

# Configuración de la página
clasificacion = rx.page(
    route="/clasificacion",
    title="TradeSim - Clasificación",
    on_load=[RankingState.load_ranking_data],
)(clasificacion_page)