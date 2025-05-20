# import reflex as rx
# from ..state.auth_state import AuthState
# from .navbarmain import navbar
# from .sidebar import sidebar

# def layout(content: rx.Component) -> rx.Component:
#     """
#     Application layout for authenticated pages with navbar and sidebar.

#     Args:
#         content (rx.Component): The main content of the page.

#     Returns:
#         rx.Component: The layout component.
#     """
#     return rx.hstack(
#         sidebar(),
#         rx.vstack(
#             navbar(
#                 user_name=AuthState.username,  # Pass the username from AuthState
#                 user_image_url="/elonmusk.png",  # Path to the user's profile picture
#                 logo_url="/logonavbar.png",  # Path to the logo
#             ),
#             content,
#             width="100%",
#             min_height="100vh",
#             background="gray.50",
#         ),
#         width="100%",
#         min_height="100vh",
#     )

import reflex as rx
from ..state.auth_state import AuthState
from .navbarmain import navbar # Asumo que 'navbarmain' es el archivo donde está tu función navbar
from .sidebar import sidebar

# Podrías definir tu DEFAULT_AVATAR aquí o importarlo si lo necesitas como fallback explícito
# DEFAULT_AVATAR = "/default_avatar.png" # O el que uses en tu AuthState

def layout(content: rx.Component) -> rx.Component:
    """
    Application layout for authenticated pages with navbar and sidebar.

    Args:
        content (rx.Component): The main content of the page.

    Returns:
        rx.Component: The layout component.
    """
    return rx.hstack(
        sidebar(),
        rx.vstack(
            navbar(
                user_name=AuthState.username,
                user_image_url=AuthState.profile_image_url,
                logo_url="/assets/logonavbar.PNG",  # Updated path to use /assets/ prefix
            ),
            content,
            width="100%",
            min_height="100vh",
            background="gray.50", # Considera usar rx.color_mode_cond para temas claro/oscuro si es relevante
        ),
        width="100%",
        min_height="100vh",
    )