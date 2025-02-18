# tradesim/__init__.py
import reflex as rx
from .database import init_db
from .components.layouts.auth_layout import auth_layout

# Initialize the database
init_db()

# Create the application
app = rx.App()

# Import the pages
from .pages.index import index
from .pages.dashboard import dashboard
from .pages.login import login_page

# Import the state after importing pages
from .state.auth_state import AuthState

# Add routes (landing page doesn't use auth_layout)
app.add_page(index, route="/")
# Wrap authenticated pages with auth_layout
app.add_page(lambda: auth_layout(dashboard()), route="/dashboard")
app.add_page(lambda: auth_layout(login_page()), route="/login")

# Set state
app.state = AuthState

__all__ = ["app"]