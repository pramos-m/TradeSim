import reflex as rx
from ..components.layout import layout
from ..components.login_form import login_form
from ..components.register_form import register_form
from ..state.auth_state import AuthState

def login_page() -> rx.Component:
    """Render login page."""
    return layout(
        rx.center(
            rx.cond(
                AuthState.is_logged,
                rx.vstack(
                    rx.heading(f"Welcome, {AuthState.username}!", size="4"),
                    rx.button(
                        "Logout",
                        on_click=AuthState.logout,
                        color_scheme="red",
                        size="3",
                    ),
                ),
                rx.tabs(
                    items=[
                        ("Login", login_form()),
                        ("Register", register_form()),
                    ],
                    align="center",
                    variant="enclosed",
                ),
            ),
            width="100%",
            max_width="400px",
            padding_y="8",
        )
    )