import reflex as rx
from ..state.auth_state import AuthState

def login_form() -> rx.Component:
    """Render login form."""
    return rx.vstack(
        rx.heading("Login", size="4"),
        rx.vstack(
            rx.input(
                placeholder="Username",
                value=AuthState.username,
                on_change=AuthState.set_username,
                margin_y="2",
            ),
            rx.input(
                placeholder="Password",
                type_="password",
                value=AuthState.password,
                on_change=AuthState.set_password,
                margin_y="2",
            ),
            rx.button(
                "Login",
                on_click=AuthState.login,
                color_scheme="blue",
                width="100%",
                margin_y="2",
            ),
            rx.cond(
                AuthState.error_message != "",
                rx.text(
                    AuthState.error_message,
                    color="red",
                ),
            ),
            spacing="4",
            padding="6",
            bg="white",
            border_radius="lg",
            box_shadow="lg",
            width="100%",
        ),
    )

