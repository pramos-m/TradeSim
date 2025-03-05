import reflex as rx
from ...state.auth_state import AuthState
from ...utils.auth_middleware import require_auth

def dashboard_layout(content: rx.Component) -> rx.Component:
    """
    Layout común para las páginas del dashboard.
    
    Args:
        content: El contenido específico de la página que se renderizará dentro del layout.
        
    Returns:
        El componente con el layout completo que incluye el contenido proporcionado.
    """
    return rx.vstack(
        # Barra de navegación superior
        rx.box(
            rx.hstack(
                rx.image(src="/logo.svg", height="50px"),
                rx.spacer(),
                rx.text(f"Usuario: {AuthState.username}", margin_right="4"),
                rx.button(
                    "Cerrar Sesión",
                    on_click=AuthState.logout,
                    color_scheme="red",
                    # No especificamos size, usará el predeterminado
                ),
                width="100%",
                padding="4",
                border_bottom="1px solid",
                border_color="gray.200",
            ),
        ),
        # Contenedor para el contenido específico de cada página
        rx.center(
            rx.box(
                # Aquí insertamos el contenido específico de la página
                content,
                padding="8",
                border_radius="lg",
                box_shadow="xl",
                background="white",
                width="90%",
                max_width="1000px",
            ),
            width="100%",
            padding_y="8",
        ),
        width="100%",
        min_height="100vh",
        background="gray.50",
    )