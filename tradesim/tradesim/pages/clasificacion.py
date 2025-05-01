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
        rx.vstack(
            # Título principal
            rx.heading(
                "Clasificación de Inversores",
                size="7",
                margin_y="50px",
                align_self="flex-start",
                margin_left="50px",
            ),
            
            # Mensaje de carga o error
            rx.cond(
                RankingState.ranking_loading,
                rx.center(
                    rx.spinner(color="#5271FF"),  # Cambiado de CircularProgress a rx.spinner
                    padding="10",
                ),
                rx.cond(
                    RankingState.ranking_error_message != "",
                    rx.box(
                        rx.text(
                            RankingState.ranking_error_message,
                            color="red.500",
                            font_size="lg",
                        ),
                        padding="5",
                        background="red.50",
                        border_radius="md",
                        width="90%",
                        margin_y="4",
                    ),
                    rx.box()  # Contenedor vacío si no hay error
                )
            ),
            
            # Sección del TOP 3
            rx.box(
                rx.vstack(
                    rx.heading(
                        "TOP 3",
                        size="5",
                        font_weight="bold",
                        margin_left="25px",
                        margin_top="20px",
                    ),
                    
                    # Contenedor para las tarjetas del TOP 3
                    rx.vstack(
                        rx.foreach(
                            RankingState.top_users[:3],
                            lambda usuario: crear_tarjeta_usuario(usuario, destacado=True)
                        ),
                        padding="4",
                        spacing="4",
                        width="100%",
                    ),
                    
                    align_items="flex-start",
                    width="100%",
                ),
                background_image="url('/top3bkg.png')",
                background_size="cover",
                background_position="center",
                width="90%",
                height="auto",
                min_height="550px",
                border_radius="md",
                box_shadow="md",
                padding="4",
                margin_top="20px",
            ),
            
            # Sección de TOP 4 al 10
            rx.box(
                rx.vstack(
                    rx.heading(
                        "TOP 4 a 10",
                        size="5",
                        font_weight="bold",
                        margin_left="25px",
                        margin_top="20px",
                    ),
                    
                    # Encabezados de columnas
                    rx.hstack(
                        rx.text("Posición", font_weight="bold", min_width="60px", text_align="center"),
                        rx.text("Usuario", font_weight="bold", flex="1"),
                        rx.text("ROI", font_weight="bold", width="100px", text_align="center"),
                        rx.text("Ganancias", font_weight="bold", width="100px", text_align="center"),
                        width="100%",
                        padding="4",
                        color="white",
                        background="#3b5cf4",  # Azul más oscuro para los encabezados
                        border_radius="md",
                    ),
                    
                    # Lista de usuarios del 4 al 10
                    rx.vstack(
                        rx.foreach(
                            RankingState.top_users[3:],
                            crear_tarjeta_usuario
                        ),
                        padding="4",
                        spacing="2",
                        width="100%",
                    ),
                    
                    # Tu posición (si estás autenticado)
                    rx.cond(
                        RankingState.is_authenticated & (RankingState.user_position != {}),
                        rx.vstack(
                            rx.divider(),
                            rx.heading(
                                "Tu Posición",
                                size="4",
                                margin_top="4",
                            ),
                            rx.box(
                                rx.hstack(
                                    rx.box(
                                        rx.text(
                                            f"#{RankingState.user_position.get('position', 'N/A')}",
                                            font_size="xl",
                                            font_weight="bold",
                                            color="white",
                                        ),
                                        padding="4",
                                        border_radius="full",
                                        background="#5271FF",
                                        min_width="60px",
                                        display="flex",
                                        align_items="center",
                                        justify_content="center",
                                    ),
                                    rx.box(
                                        rx.text(
                                            RankingState.user_position.get("username", ""),
                                            font_weight="bold",
                                            font_size="xl",
                                            color="white",
                                        ),
                                        flex="1",
                                        padding_x="4",
                                    ),
                                    rx.box(
                                        rx.text(
                                            f"{RankingState.user_position.get('roi_percentage', 0):.2f}%",
                                            color="white",
                                            font_weight="bold",
                                            font_size="xl",
                                        ),
                                        padding_x="4",
                                    ),
                                    rx.box(
                                        rx.text(
                                            f"${RankingState.user_position.get('profit_loss', 0):.2f}",
                                            color="white",
                                            font_weight="bold",
                                            font_size="xl",
                                        ),
                                        padding_x="4",
                                    ),
                                    width="100%",
                                    padding="3",
                                    align_items="center",
                                ),
                                width="100%",
                                background="#3b5cf4",  # Un azul más oscuro para tu posición
                                border_radius="md",
                                margin_y="4",
                                box_shadow="sm",
                            ),
                            width="100%",
                        ),
                        rx.box(),  # Empty box if not authenticated
                    ),
                    
                    align_items="flex-start",
                    width="100%",
                ),
                width="90%",
                background="white",
                border_radius="md",
                box_shadow="md",
                padding="4",
                margin_top="25px",
                margin_bottom="30px",
            ),
            
            width="100%",
            align_items="center",
            padding="20",
        )
    )

# Configuración de la página con carga de datos
clasificacion = rx.page(
    route="/clasificacion",
    title="TradeSim - Clasificación",
    on_load=RankingState.load_ranking_data
)(clasificacion_page)