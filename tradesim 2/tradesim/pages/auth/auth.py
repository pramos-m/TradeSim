import reflex as rx
from ..state import State

def require_auth(page):
    """Decorador para proteger rutas."""
    def wrapper():
        return rx.cond(
            State.is_authenticated,
            page(),
            rx.redirect("/login")
        )
    return wrapper
