# __init__.py
import reflex as rx
from .state.auth_state import AuthState

# Crear la aplicación
app = rx.App()

# Establecer el estado de la aplicación
app.state = AuthState  # Esta es la forma correcta de establecer el estado

# Importar las páginas después de crear la aplicación
from .pages.index import index
from .pages.dashboard import dashboard
from .pages.login import login_page

# Añadir las páginas
app.add_page(index, route="/")
app.add_page(dashboard, route="/dashboard")
app.add_page(login_page, route="/login")

__all__ = ["app"]