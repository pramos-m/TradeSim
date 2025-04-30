# tradesim/database.py (VERSIÓN FINAL Y COMPLETA)
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
import yfinance as yf
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) # Usar el logger estándar de Python

# --- Database Configuration ---
DATABASE_URL_FALLBACK = "sqlite:///tradesim.db"
DATABASE_URL = os.getenv("DATABASE_URL", DATABASE_URL_FALLBACK)
logger.info(f"Using Database URL: {DATABASE_URL}") # Log para saber qué BBDD se usa
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False) # echo=False para producción
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for FastAPI/Reflex routes to get a DB session."""
    db = SessionLocal()
    try: yield db
    finally:
         if db and db.is_active: db.close()

# --- Data Population Logic ---
SYMBOLS_TO_POPULATE = ["AAPL", "GOOGL", "MSFT", "TSLA"] # Acciones a poblar
HISTORY_PERIOD = "1y" # Periodo de historial a obtener de yfinance
DEFAULT_SECTOR_ID = 1 # ID del sector por defecto (ej. Tecnología)

def populate_simulated_history(db: Session):
    """Populates stock and price history using yfinance if the history table is empty."""
    logger.info(">>> Running populate_simulated_history...")
    # Importar modelos aquí para evitar problemas de importación circular
    from .models.stock import Stock
    from .models.sector import Sector
    from .models.stock_price_history import StockPriceHistory

    try:
        # Comprobar si la tabla de HISTORIAL tiene ya algún dato
        logger.info("Checking existing history count...")
        # Contar solo un ID es más rápido que contar todas las filas
        history_count = db.query(StockPriceHistory.id).limit(1).scalar()
        logger.info(f"History count: {history_count if history_count is not None else 'None (or 0)'}")

        # Si ya hay historial, no hacer nada
        if history_count is not None and history_count > 0:
            logger.info("StockPriceHistory table already populated. Skipping yfinance population.")
            logger.info("<<< populate_simulated_history finished (skipped).")
            return

        # Si la tabla de historial está vacía, proceder a poblar
        logger.info(f"StockPriceHistory is empty. Attempting to populate for {SYMBOLS_TO_POPULATE}...")
        total_added_count = 0

        # 1. Asegurar que existe el Sector por defecto
        logger.info(f"Checking for default sector ID: {DEFAULT_SECTOR_ID}")
        default_sector = db.query(Sector).get(DEFAULT_SECTOR_ID)
        if not default_sector:
            logger.warning(f"Default sector ID {DEFAULT_SECTOR_ID} not found. Creating 'Technology' sector.")
            try:
                default_sector = Sector(id=DEFAULT_SECTOR_ID, sector_name="Technology")
                db.add(default_sector)
                db.flush() # Aplicar para obtener el ID si fuera necesario y asegurar que existe
                logger.info(f"Default sector 'Technology' (ID: {DEFAULT_SECTOR_ID}) added and flushed.")
            except Exception as sector_err:
                logger.error(f"Failed to create default sector: {sector_err}", exc_info=True)
                db.rollback() # Revertir cambios si falla la creación del sector
                logger.info("<<< populate_simulated_history finished (sector error).")
                return # No podemos continuar sin un sector válido
        else:
            logger.info(f"Default sector '{default_sector.sector_name}' found.")

        # 2. Iterar sobre los símbolos a poblar
        for symbol in SYMBOLS_TO_POPULATE:
            logger.info(f"--- Processing symbol: {symbol} ---")
            stock_obj = None # Reiniciar para cada símbolo
            try:
                # 2a. Obtener información actual de yfinance
                logger.info(f"Fetching Ticker info for {symbol}..."); ticker = yf.Ticker(symbol); info = ticker.info; logger.info(f"Ticker info fetched for {symbol}.")
                stock_name = info.get("longName", info.get("shortName", f"{symbol} Name N/A"))
                # Intentar obtener precio actual de varios campos comunes
                current_price_val = info.get("currentPrice", info.get("regularMarketPrice", info.get("previousClose")))
                current_price = Decimal("0.00") # Default
                if current_price_val is not None:
                    try: current_price = Decimal(str(current_price_val)).quantize(Decimal("0.01"))
                    except Exception: logger.error(f"Error converting price '{current_price_val}' for {symbol}. Setting 0.0")
                logger.info(f"Data for {symbol}: Name='{stock_name}', Current Price={current_price}")

                # 2b. Buscar o crear la entrada en la tabla 'stocks'
                logger.info(f"Querying existing stock for {symbol}..."); stock_obj = db.query(Stock).filter(Stock.symbol == symbol).first()
                if not stock_obj:
                    logger.info(f"Stock {symbol} not found, CREATING...")
                    stock_obj = Stock(symbol=symbol, name=stock_name, current_price=current_price, sector_id=DEFAULT_SECTOR_ID)
                    db.add(stock_obj)
                    db.flush() # Necesario para obtener stock_obj.id antes de añadir historial
                    logger.info(f"Stock {symbol} CREATED with ID {stock_obj.id}.")
                else:
                    # Si ya existe, actualizar su precio actual
                    logger.info(f"Stock {symbol} FOUND with ID {stock_obj.id}. Updating price.")
                    stock_obj.current_price = current_price
                    db.flush() # Aplicar el cambio de precio

                # 2c. Obtener historial de precios de yfinance
                logger.info(f"Fetching price history for {symbol} (Period: {HISTORY_PERIOD})..."); hist = ticker.history(period=HISTORY_PERIOD)
                if hist.empty:
                    logger.warning(f"No yfinance history found for {symbol} (Period: {HISTORY_PERIOD}). Skipping history population for this stock."); continue

                logger.info(f"Fetched {len(hist)} historical data points for {symbol}.")

                # 2d. Preparar las entradas para 'stock_price_history'
                entries_to_add = []
                for timestamp, row in hist.iterrows():
                    try:
                        # Convertir timestamp a datetime Python naive
                        ts = pd.to_datetime(timestamp).to_pydatetime().replace(tzinfo=None)
                        # Obtener precio de cierre y convertir a Decimal
                        price_val = row.get('Close')
                        if price_val is None: continue # Saltar si no hay precio de cierre
                        price = Decimal(str(price_val)).quantize(Decimal("0.01"))

                        # Asegurar que tenemos un stock_id válido
                        if stock_obj and stock_obj.id:
                             entries_to_add.append(StockPriceHistory(stock_id=stock_obj.id, timestamp=ts, price=price))
                        else:
                            logger.error(f"Cannot create history entry for {symbol} at {ts}, stock_obj or ID is invalid!")
                            continue # Saltar esta entrada

                    except Exception as row_err:
                        logger.error(f"Error processing row for {symbol} at {timestamp}: {row_err}", exc_info=True)
                        continue # Saltar fila con error

                # 2e. Añadir las entradas preparadas a la sesión de SQLAlchemy
                if entries_to_add:
                    logger.info(f"Adding {len(entries_to_add)} history entries for {symbol} to session...");
                    db.add_all(entries_to_add) # add_all es generalmente bueno para añadir objetos nuevos a la sesión
                    total_added_count += len(entries_to_add)
                    logger.info(f"Entries for {symbol} added to session.")
                # else: logger.info(f"No valid history entries generated for {symbol}.") # Log reducido

            except Exception as ticker_err:
                 # Capturar errores específicos del procesamiento de un símbolo (ej. error de yfinance)
                 logger.error(f"--- ERROR processing symbol {symbol}: {ticker_err} ---", exc_info=True)
                 continue # Continuar con el siguiente símbolo

        # 3. Hacer commit de TODOS los cambios al final si se añadió algo
        if total_added_count > 0:
            logger.info(f"\nAttempting to COMMIT {total_added_count} total entries to database...")
            db.commit()
            logger.info("COMMIT successful!")
        else:
            logger.info("\nNo new history entries were added to the session. No commit needed.")

    except Exception as e:
        # Capturar cualquier otro error durante la población
        logger.error(f"--- DATABASE ERROR DURING POPULATION ---: {e}", exc_info=True)
        logger.warning("Attempting to ROLLBACK changes...")
        db.rollback() # Intentar revertir si hubo un error general
        logger.info("Rollback attempted.")
    finally:
        logger.info("<<< populate_simulated_history finished.")
        # La sesión db_session se cierra en init_db_tables

# --- Table Initialization --- #
def init_db_tables():
    """Imports all models, creates tables, and populates history if needed."""
    logger.info("--- init_db_tables called ---") # <--- NIVEL INFO
    try:
        logger.info("Importing models..."); from .models.user import User; from .models.stock import Stock; from .models.sector import Sector; from .models.transaction import Transaction; from .models.stock_price_history import StockPriceHistory; logger.info("Models imported.")
    except ImportError as import_err: logger.error(f"ERROR importing models: {import_err}", exc_info=True); return

    try:
        logger.info("Creating database tables if they don't exist..."); Base.metadata.create_all(bind=engine); logger.info("Database tables check/creation finished.")

        logger.info("Attempting to populate history data via populate_simulated_history...")
        db_session = SessionLocal()
        try:
            populate_simulated_history(db_session) # Llamar a la función de población completa
        except Exception as pop_err: logger.error(f"ERROR during history population call: {pop_err}", exc_info=True)
        finally:
            if db_session and db_session.is_active: db_session.close(); # logger.info("Population DB session closed.")
            # else: logger.warning("Population DB session was not active or already closed.")
        logger.info("History population attempt finished.")
    except Exception as e: logger.error(f"ERROR during DB initialization outer try block: {e}", exc_info=True)
    logger.info("--- init_db_tables finished ---")

# Opcional: Función para borrar tablas
def drop_all_tables():
    logger.warning("!!! Dropping all tables !!!")
    try: from .models.user import User; from .models.stock import Stock; from .models.sector import Sector; from .models.transaction import Transaction; from .models.stock_price_history import StockPriceHistory; Base.metadata.drop_all(bind=engine); logger.info("All tables dropped successfully.")
    except Exception as e: logger.error(f"Error dropping tables: {e}")