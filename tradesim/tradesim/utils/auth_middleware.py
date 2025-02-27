import reflex as rx
from functools import wraps
from typing import Callable
from ..state.auth_state import AuthState

def require_auth(page_function: Callable) -> Callable:
    """Decorator to protect routes that require authentication."""
    @wraps(page_function)
    def wrapped_page(*args, **kwargs):
        # Use rx.cond instead of direct if/else
        return rx.cond(
            AuthState.is_authenticated,
            page_function(*args, **kwargs),
            rx.center(
                rx.vstack(
                    rx.text("No has iniciado sesión. Redirigiendo al login...", color="red.500"),
                    rx.script("setTimeout(() => window.location.href = '/login', 1500);"),
                ),
                height="100vh",
            )
        )
    return wrapped_page

def public_only(page_function: Callable) -> Callable:
    """Middleware for public pages that don't need auth checks."""
    # Simply return the page without any auth checking
    return page_function