import reflex as rx

# Create the application
app = rx.App()

# Import database and initialize tables
# Make sure this happens AFTER importing models
from .database import init_db_tables
init_db_tables()

# Import the pages
from .pages.index import index
from .pages.dashboard import dashboard
from .pages.login import login
from .pages.news import news  # Importar la nueva página de noticias

# Import the state
from .state.auth_state import AuthState

# Add routes
app.add_page(index)
app.add_page(dashboard)
app.add_page(login)
app.add_page(news)  # Agregar la ruta de noticias

# Set state
app.state = AuthState

__all__ = ["app"]