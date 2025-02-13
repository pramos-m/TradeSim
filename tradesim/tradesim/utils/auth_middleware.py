# utils/auth_middleware.py
import reflex as rx
from ..state.auth_state import AuthState
from functools import wraps

def require_auth(page_function):
    """Authentication middleware decorator."""
    @wraps(page_function)
    def wrapped_page():
        return rx.cond(
            AuthState.is_logged,
            page_function(),
            rx.vstack(
                rx.heading("Please log in to continue"),
                rx.button(
                    "Go to Login",
                    on_click=lambda: rx.redirect("/login"),
                    color_scheme="blue",
                ),
                spacing="4",
                py="8",
            ),
        )
    return wrapped_page