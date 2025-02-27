# tradesim/tradesim/pages/dashboard.py
import reflex as rx
from ..state.auth_state import AuthState
from ..utils.auth_middleware import require_auth

@require_auth
def dashboard_page() -> rx.Component:
    """Dashboard simple protegido por autenticación."""
    return rx.vstack(
        rx.box(
            rx.hstack(
                rx.image(src="/logo.svg", height="50px"),
                rx.spacer(),
                rx.text(f"Usuario: {AuthState.username}", margin_right="4"),
                rx.button(
                    "Cerrar Sesión",
                    on_click=AuthState.logout,
                    color_scheme="red",
                ),
                width="100%",
                padding="4",
                border_bottom="1px solid",
                border_color="gray.200",
            ),
        ),
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
        ),
        width="100%",
        min_height="100vh",
        background="gray.50",
    )

# Add page with on_load event to verify the token is valid
dashboard = rx.page(
    route="/dashboard",
    title="TradeSim - Dashboard",
    on_load=AuthState.on_load
)(dashboard_page)





# import reflex as rx
# from ..state.auth_state import AuthState
# from ..utils.auth_middleware import require_auth

# @require_auth
# def dashboard_page() -> rx.Component:
#     """Dashboard simple protegido por autenticación."""
#     return rx.vstack(
#         rx.box(
#             rx.hstack(
#                 rx.image(src="/logo.svg", height="50px"),
#                 rx.spacer(),
#                 rx.text(f"Usuario: {AuthState.username}", margin_right="4"),
#                 rx.button(
#                     "Cerrar Sesión",
#                     on_click=AuthState.logout,
#                     color_scheme="red",
#                 ),
#                 width="100%",
#                 padding="4",
#                 border_bottom="1px solid",
#                 border_color="gray.200",
#             ),
#         ),
#         rx.center(
#             rx.vstack(
#                 rx.heading(f"Bienvenido, {AuthState.username}!", size="9"),
#                 rx.text("Has iniciado sesión correctamente en TradeSim.", margin_y="4"),
#                 rx.flex(
#                     rx.box(
#                         rx.heading("Balance Actual", size="9"),
#                         rx.heading("$10,000.00", size="9"),
#                         rx.text("Balance inicial", color="gray.500"),
#                         padding="4",
#                         border="1px solid",
#                         border_color="gray.200",
#                         border_radius="md",
#                     ),
#                 ),
#                 spacing="6",
#                 padding="8",
#                 border_radius="lg",
#                 box_shadow="xl",
#                 background="white",
#                 width="80%",
#                 max_width="800px",
#             ),
#             width="100%",
#             padding_y="8",
#         ),
#         width="100%",
#         min_height="100vh",
#         background="gray.50",
#     )

# # Add page with on_load event to verify the token is valid
# dashboard = rx.page(
#     route="/dashboard",
#     title="TradeSim - Dashboard",
#     on_load=AuthState.on_load
# )(dashboard_page)