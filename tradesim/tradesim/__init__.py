# tradesim/__init__.py
import reflex as rx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Importar e inicializar DB ---
try:
    from .database import init_db_tables
    init_db_tables() # Llamada directa
except Exception as e:
    logger.error(f"FATAL ERROR during init_db_tables call in __init__.py: {e}", exc_info=True)
# -----------------------------------------

app = rx.App() # Crear app

# Importar páginas y estado
from .pages.index import index
from .pages.dashboard_page import dashboard_page
from .pages.login import login
from .pages.clasificacion import clasificacion
from .pages.noticias import noticias
from .pages.profile import profile_page # Importa la función de página
from .pages.buscador import buscador
from .state.auth_state import AuthState
from .pages.detalles_accion import detalles_accion_page # Importa la función de página
from .pages.aprender import aprender

# Agregar rutas
app.add_page(index)
app.add_page(dashboard_page)
app.add_page(login)
app.add_page(clasificacion)
app.add_page(noticias)
app.add_page(profile_page, route="/profile") # Asegúrate que la ruta es correcta
app.add_page(buscador)
app.add_page(detalles_accion_page, route="/detalles_accion/[symbol]") # Ruta con parámetro
app.add_page(aprender)

# Establecer estado
app.state = AuthState

__all__ = ["app"]