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
from .pages.profile import profile
from .pages.buscador import buscador
from .state.auth_state import AuthState

# Agregar rutas
app.add_page(index)
app.add_page(dashboard_page)
app.add_page(login)
app.add_page(clasificacion)
app.add_page(noticias)
app.add_page(profile)
app.add_page(buscador)

# Establecer estado
app.state = AuthState