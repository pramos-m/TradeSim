# import reflex as rx
# from functools import wraps
# from typing import Callable
# from ..state.auth_state import AuthState

# def require_auth(page_function: Callable) -> Callable:
#     """Decorator to protect routes that require authentication."""
#     @wraps(page_function)
#     def wrapped_page(*args, **kwargs):
#         return rx.cond(
#             AuthState.is_authenticated,
#             page_function(*args, **kwargs),
#             rx.center(
#                 rx.vstack(
#                     rx.text("No has iniciado sesión. Redirigiendo al login...", color="red.500"),
#                     rx.script("setTimeout(() => window.location.href = '/login', 1500);"),
#                 ),
#                 height="100vh",
#             )
#         )
#     return wrapped_page

# def public_only(page_function: Callable) -> Callable:
#     """Middleware for public pages that don't need auth checks."""
#     # Simply return the page without any auth checking
#     return page_function

# from functools import wraps
# from typing import Callable
# import reflex as rx
# from ..state.auth_state import AuthState

# def require_auth(page_function: Callable) -> Callable:
#     """Decorator to protect routes that require authentication."""
#     @wraps(page_function)
#     def wrapped_page(*args, **kwargs):
#         component = page_function(*args, **kwargs)
        
#         # Create a wrapped page that checks authentication on load
#         def auth_wrapper() -> rx.Component:
#             return rx.cond(
#                 AuthState.is_authenticated,
#                 component,
#                 rx.fragment()  # Mostrar nada si no está autenticado, dejar que on_load haga la redirección
#             )
            
#         # Return the wrapped component
#         return auth_wrapper()
    
#     return wrapped_page

# def public_only(page_function: Callable) -> Callable:
#     """Middleware for public pages that don't need auth checks."""
#     # Simply return the page without any auth checking
#     return page_function


from functools import wraps
from typing import Callable
import reflex as rx
from ..state.auth_state import AuthState

def require_auth(page_function: Callable) -> Callable:
    """Decorator to protect routes that require authentication."""
    @wraps(page_function)
    def wrapped_page(*args, **kwargs):
        # Simplemente devolver el componente, la verificación de autenticación
        # se realizará en el evento on_load de AuthState
        return page_function(*args, **kwargs)
    
    return wrapped_page

def public_only(page_function: Callable) -> Callable:
    """Middleware for public pages that don't need auth checks."""
    # Simply return the page without any auth checking
    return page_function