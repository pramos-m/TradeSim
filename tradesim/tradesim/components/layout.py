import reflex as rx
from ..state.auth_state import AuthState
from .navbarmain import navbar
from .sidebar import sidebar

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
                user_image_url=AuthState.profile_image_url, # <<< CANVIA AIXÒ! Posa AuthState.profile_image_url
                logo_url="/logonavbar.png",
            ),
            content,
            width="100%",
            min_height="100vh",
            background="gray.50",
        ),
        width="100%",
        min_height="100vh",
    )