"""Initialize the tradesim application."""
import reflex as rx
from .state import State

# Create the app instance
app = rx.App(state=State)

# Import pages after app creation to avoid circular imports
from .pages.index import index
from .pages.dashboard import dashboard

# Add pages to the app
app.add_page(index, route="/")
app.add_page(dashboard, route="/dashboard")

# Export the app variable
__all__ = ["app"]