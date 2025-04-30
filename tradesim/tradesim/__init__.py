# tradesim/__init__.py
import reflex as rx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# logger.info("--- tradesim/__init__.py TOP LEVEL ---") # Log reducido

# --- Importar e inicializar DB ---
try:
    from .database import init_db_tables
    # logger.info("Imported init_db_tables successfully.") # Log reducido
    # logger.info(">>> tradesim/__init__.py: Calling init_db_tables()...") # Log reducido
    init_db_tables() # Llamada
    # logger.info("<<< tradesim/__init__.py: init_db_tables() finished.") # Log reducido
except Exception as e:
    logger.error(f"FATAL ERROR during init_db_tables call in __init__.py: {e}", exc_info=True)
# -----------------------------------------

# logger.info("Continuing with App creation...") # Log reducido
app = rx.App( ) # Crear app
# logger.info("rx.App instance created.") # Log reducido

# Importar páginas y estado
# logger.info("Importing pages and state...") # Log reducido
from .pages.index import index
from .pages.dashboard_page import dashboard_page
from .pages.login import login
from .pages.clasificacion import clasificacion
from .pages.noticias import noticias
from .pages.profile import profile
from .pages.buscador import buscador
from .state.auth_state import AuthState
# logger.info("Pages and state imported.") # Log reducido

# Agregar rutas
# logger.info("Adding pages to app...") # Log reducido
app.add_page(index)
app.add_page(dashboard_page)
app.add_page(login)
app.add_page(clasificacion)
app.add_page(noticias)
app.add_page(profile)
app.add_page(buscador)
# logger.info("Pages added.") # Log reducido

# Establecer estado
# logger.info("Setting app state...") # Log reducido
app.state = AuthState
# logger.info("App state set.") # Log reducido
# logger.info("--- tradesim/__init__.py END OF FILE ---") # Log reducido