# tradesim/tradesim/pages/index.py
import reflex as rx
from ..components.layouts.landing_layout import landing_layout
from ..components.buttons import navbar_button, comenzar_button
from ..state.auth_state import AuthState

LOGO_IMAGE = "./logo.svg"

def index_content() -> rx.Component:
    """Landing page content."""
    return rx.box(
        rx.box(
            rx.image(src="/logo.svg", height="200px"),
            position="absolute",
            top="0",
            left="20px",
        ),
        rx.box(
            rx.link(
                navbar_button(),
                href="/login",
            ),
            position="absolute",
            top="60px",
            right="70px",
            z_index="2",
        ),
        rx.vstack(
             rx.box(
                rx.vstack(
                    rx.box(
                        rx.heading(
                            "Bienvenido",
                            font_family="mono",
                            font_size="150px",
                            white_space="nowrap",
                            color="black",
                            letter_spacing="tight",
                            font_weight="bold",
                        ),
                        bg="white",
                        padding="40",
                        margin="0",
                        border_top_left_radius="20px",
                        border_top_right_radius="20px",
                        border_bottom_left_radius="0px",
                        border_bottom_right_radius="-20px",
                        box_shadow="sm",
                        width="750px",
                        height="175px",
                        text_align="center",
                        justify_content="center",
                        display="flex",
                        align_items="center",
                    ),
                    rx.box(
                        rx.heading(
                            "a TradeSim!!!",
                            font_family="mono",
                            font_size="150px",
                            white_space="nowrap",
                            color="black",
                            letter_spacing="tight",
                            font_weight="bold",
                        ),
                        bg="white",
                        padding="40",
                        margin="0",
                        border_top_left_radius="0px",
                        border_top_right_radius="20px",
                        border_bottom_left_radius="20px",
                        border_bottom_right_radius="20px",
                        box_shadow="sm",
                        width="925px",
                        height="175px",
                        text_align="center",
                        justify_content="center",
                        display="flex",
                        align_items="center",
                    ),
                    spacing="0",
                ),
            ),
            rx.link(
                comenzar_button(),
                href="/login",
            ),
            spacing="8",
            align_items="flex-start",
            padding_top="16",
            padding_x="6",
            position="absolute",
            top="25%",
            left="10%",
        ),
        width="100%",
        height="100vh",
        position="relative",
    )

index = rx.page(
    route="/",
    title="TradeSim - Inicio"
)(index_content)



# import reflex as rx
# from ..components.layouts.landing_layout import landing_layout
# from ..components.buttons import navbar_button, comenzar_button
# from ..state.auth_state import AuthState

# LOGO_IMAGE = "./logo.svg"

# def index_content() -> rx.Component:
#     """Landing page content."""
#     return rx.box(
#         rx.box(
#             rx.image(src="/logo.svg", height="200px"),
#             position="absolute",
#             top="0",
#             left="20px",
#         ),
#         rx.box(
#             rx.link(
#                 navbar_button(),
#                 href="/login",
#             ),
#             position="absolute",
#             top="60px",
#             right="70px",
#             z_index="2",
#         ),
#         rx.vstack(
#              rx.box(
#                 rx.vstack(
#                     rx.box(
#                         rx.heading(
#                             "Bienvenido",
#                             font_family="mono",
#                             font_size="150px",
#                             white_space="nowrap",
#                             color="black",
#                             letter_spacing="tight",
#                             font_weight="bold",
#                         ),
#                         bg="white",
#                         padding="40",
#                         margin="0",
#                         border_top_left_radius="20px",
#                         border_top_right_radius="20px",
#                         border_bottom_left_radius="0px",
#                         border_bottom_right_radius="-20px",
#                         box_shadow="sm",
#                         width="750px",
#                         height="175px",
#                         text_align="center",
#                         justify_content="center",
#                         display="flex",
#                         align_items="center",
#                     ),
#                     rx.box(
#                         rx.heading(
#                             "a TradeSim!!!",
#                             font_family="mono",
#                             font_size="150px",
#                             white_space="nowrap",
#                             color="black",
#                             letter_spacing="tight",
#                             font_weight="bold",
#                         ),
#                         bg="white",
#                         padding="40",
#                         margin="0",
#                         border_top_left_radius="0px",
#                         border_top_right_radius="20px",
#                         border_bottom_left_radius="20px",
#                         border_bottom_right_radius="20px",
#                         box_shadow="sm",
#                         width="925px",
#                         height="175px",
#                         text_align="center",
#                         justify_content="center",
#                         display="flex",
#                         align_items="center",
#                     ),
#                     spacing="0",
#                 ),
#             ),
#             rx.link(
#                 comenzar_button(),
#                 href="/login",
#             ),
#             spacing="8",
#             align_items="flex-start",
#             padding_top="16",
#             padding_x="6",
#             position="absolute",
#             top="25%",
#             left="10%",
#         ),
#         width="100%",
#         height="100vh",
#         position="relative",
#     )

# def index() -> rx.Component:
#     """Landing page with layout."""
#     return landing_layout(index_content())

# # Configure the page
# index = rx.page(
#     route="/",
#     title="TradeSim - Inicio",
# )(index)

