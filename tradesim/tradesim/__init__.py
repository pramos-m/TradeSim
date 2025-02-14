# __init__.py
import reflex as rx
from .database import init_db

# Initialize the database
init_db()

# Create the application
app = rx.App()

# Import the pages
from .pages.index import index
from .pages.dashboard import dashboard
from .pages.login import login_page

# Import the state after importing pages to avoid circular imports
from .state.auth_state import AuthState

# Add routes
app.add_page(index, route="/")
app.add_page(dashboard, route="/dashboard")
app.add_page(login_page, route="/login")

# Set state
app.state = AuthState

__all__ = ["app"]