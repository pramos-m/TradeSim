import reflex as rx
from ..components.layout import layout
from ..state.ranking_state import RankingState
from ..utils.auth_middleware import require_auth

def crear_tarjeta_usuario(usuario: dict, destacado: bool = False) -> rx.Component:
    """Crear una tarjeta para un usuario en la clasificación."""
    # Usar los booleanos pre-calculados del estado
    is_roi_positive = usuario["is_roi_positive"]
    is_profit_positive = usuario["is_profit_positive"]

    # Acceder directamente a los valores numéricos para formateo
    roi_percentage = usuario["roi_percentage"]
    profit_loss = usuario["profit_loss"]

    return rx.box(
        rx.hstack(
            # Indicador de posición
            rx.box(
                rx.text(
                    f"#{usuario['position']}",
                    font_size=["lg", "xl", "2xl"],
                    font_weight="bold",
                    color="#5271FF",
                ),
                padding="4",
                border_radius="full",
                background="white",
                box_shadow="sm",
                min_width="60px",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            
            # Nombre de usuario
            rx.box(
                rx.text(
                    usuario["username"],
                    font_weight="bold",
                    font_size=["md", "lg", "xl"],
                    color="black",
                ),
                flex="1",
                padding_x="4",
            ),
            
            # ROI
            rx.box(
                rx.text(
                    rx.cond(
                        is_roi_positive,
                        f"+{roi_percentage:.2f}%",
                        f"{roi_percentage:.2f}%"
                    ),
                    color="black",
                    font_weight="bold",
                    font_size=["md", "lg", "xl"],
                ),
                padding_x="4",
            ),
            
            # Ganancias/Pérdidas
            rx.box(
                rx.text(
                    rx.cond(
                        is_profit_positive,
                        f"+${profit_loss:.2f}",
                        f"${profit_loss:.2f}"
                    ),
                    color="black",
                    font_weight="bold",
                    font_size=["md", "lg", "xl"],
                ),
                padding_x="4",
            ),
            
            width="100%",
            padding="3",
            align_items="center",
        ),
        width="100%",
        # Usar el booleano 'destacado' directamente en rx.cond
        background=rx.cond(destacado, "#f0f4ff", "white"),
        border_radius="md",
        margin_y="2",
        box_shadow="sm",
        # Usar el booleano 'destacado' directamente en rx.cond para _hover
        _hover={
            "background": rx.cond(destacado, "#e6ebff", "#f0f4ff")
        },
        transition="all 0.2s",
        cursor="pointer",
    )

def clasificacion_page() -> rx.Component:
    """Página de clasificación con ranking de usuarios."""
    return layout(
        rx.center(rx.text("Clasificacion Page"))
    )

clasificacion = rx.page(
    route="/clasificacion",
    title="TradeSim - Clasificación",
    on_load=RankingState.load_ranking_data
)(clasificacion_page)