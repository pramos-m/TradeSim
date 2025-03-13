import reflex as rx
from ..state.auth_state import AuthState
from ..utils.auth_middleware import require_auth
from ..components.layout import layout

@require_auth
def dashboard_page() -> rx.Component:
    """Dashboard protegido por autenticación con navbar y sidebar."""
    return layout(
        rx.center(
            rx.vstack(
                rx.heading(f"Bienvenido, {AuthState.username}!", size="9"),
                rx.text("Has iniciado sesión correctamente en TradeSim.", margin_y="4"),
                rx.flex(
                    rx.box(
                        rx.heading("Balance Actual", size="9"),
                        rx.heading("$10,000.00", size="9"),
                        rx.text("Balance inicial", color="gray.500"),
                        padding="4",
                        border="1px solid",
                        border_color="gray.200",
                        border_radius="md",
                    ),
                ),
                spacing="6",
                padding="8",
                border_radius="lg",
                box_shadow="xl",
                background="white",
                width="80%",
                max_width="800px",
            ),
            width="100%",
            padding_y="8",
        )
    )

# Add page with on_load event to verify the token is valid
dashboard = rx.page(
    route="/dashboard",
    title="TradeSim - Dashboard",
    on_load=AuthState.on_load
)(dashboard_page)