# auth_middleware.py
import reflex as rx
from functools import wraps
from typing import Callable
from ..state.auth_state import AuthState

def require_auth(page_function: Callable) -> Callable:
    """Middleware to require authentication for protected pages."""
    @wraps(page_function)
    def wrapped_page(*args, **kwargs):
        return rx.cond(
            AuthState.is_authenticated,
            page_function(*args, **kwargs),
            rx.vstack(
                rx.script("window.location.href = '/login'"),
                rx.text("Redirecting to login..."),
            )
        )
    return wrapped_page

def public_only(page_function: Callable) -> Callable:
    """Middleware to restrict access to public-only pages when authenticated."""
    @wraps(page_function)
    def wrapped_page(*args, **kwargs):
        return rx.cond(
            AuthState.is_authenticated,
            rx.vstack(
                rx.script("window.location.href = '/dashboard'"),
                rx.text("Redirecting to dashboard..."),
            ),
            page_function(*args, **kwargs)
        )
    return wrapped_page
