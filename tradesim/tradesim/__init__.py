import reflex as rx

# Crear la aplicación
app = rx.App()

# Importar la base de datos y inicializar las tablas
# Asegúrate de que esto se realice DESPUÉS de importar los modelos
from .database import init_db_tables
init_db_tables()

# Importar las páginas
from .pages.index import index
# from .pages.dashboard import dashboard # Remove old import
from .pages.dashboard_page import dashboard_page
from .pages.login import login
from .pages.clasificacion import clasificacion
from .pages.noticias import noticias
from .pages.profile import profile
from .pages.buscador import buscador  # Eliminamos la referencia a `stock`

# Importar el estado
from .state.auth_state import AuthState

# Agregar las rutas
app.add_page(index)
# app.add_page(dashboard) # Remove old page route
app.add_page(dashboard_page) # Keep the new page, it's already routed to /dashboard
app.add_page(login)
app.add_page(clasificacion)
app.add_page(noticias)
app.add_page(profile)
app.add_page(buscador)

# Establecer el estado
app.state = AuthState

__all__ = ["app"]