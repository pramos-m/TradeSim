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
    return rx.vstack(
        # Place the fixed navbar outside the hstack
        navbar(
            user_name=AuthState.username,
            user_image_url=AuthState.profile_image_url,
            logo_url="/logonavbar.PNG", # Keep the updated path
        ),
        rx.hstack(
            sidebar(),
            rx.vstack(
                # Remove the navbar from here
                # navbar(
                #     user_name=AuthState.username,
                #     user_image_url=AuthState.profile_image_url,
                #     # logo_url="/assets/logonavbar.PNG",
                #     logo_url="/logonavbar.PNG",
                # ),
                content,
                width="100%",
                min_height="100vh",
                background="gray.50",
                margin_left="90px",
                # Adjust padding-top to only account for the content below the navbar
                # The main vstack containing the hstack will handle the navbar offset
                padding_top="0px", # Remove padding_top from here
                
                # Removed horizontal padding and centering as requested
                # padding_x="1rem", # Add horizontal padding
                # max_width="1000px", # Set max width, adjust as needed
                # margin_x="auto", # Center the content horizontally
            ),
            width="100%",
            min_height="100vh",
        ),
        width="100%",
        min_height="100vh",
        # Add padding-top to the root vstack to push content below the fixed navbar
        # Adjust this value based on the actual height of your navbar
        padding_top="70px", # This will offset the content below the fixed navbar
    )