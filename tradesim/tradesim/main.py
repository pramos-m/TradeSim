import reflex as rx
from tradesim.pages.index import index
from tradesim.pages.dashboard import dashboard
from tradesim.database import Base, engine
from tradesim.state import State

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear la aplicación
app = rx.App(
    state=State,
    style={"font_family": "Inter, sans-serif"}
)

# Definir las rutas
app.add_page(index, route="/")
app.add_page(dashboard, route="/dashboard")