# tradesim/database.py (FINAL - Historial 5y, Logs Limpios)
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
logger = logging.getLogger(__name__)

# --- Database Configuration ---
DATABASE_URL_FALLBACK = "sqlite:///tradesim.db"
DATABASE_URL = os.getenv("DATABASE_URL", DATABASE_URL_FALLBACK)
logger.info(f"Using Database URL: {DATABASE_URL}")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try: yield db
    finally:
         if db and db.is_active: db.close()

# --- Data Population Logic ---
SYMBOLS_TO_POPULATE = ["AAPL", "GOOGL", "MSFT", "TSLA"]
HISTORY_PERIOD = "5y" # <-- CAMBIADO A 5 AÑOS
DEFAULT_SECTOR_ID = 1

def populate_simulated_history(db: Session):
    """Populates stock and price history using yfinance if the history table is empty."""
    logger.info(">>> Running populate_simulated_history...")
    from .models.stock import Stock
    from .models.sector import Sector
    from .models.stock_price_history import StockPriceHistory

    try:
        logger.info("Checking existing history count...")
        history_count = db.query(StockPriceHistory.id).limit(1).scalar()
        logger.info(f"History count: {history_count if history_count is not None else 'None (or 0)'}")

        if history_count is not None and history_count > 0: # Restaurada la comprobación
            logger.info("StockPriceHistory table already populated. Skipping population.")
            logger.info("<<< populate_simulated_history finished (skipped).")
            return

        logger.info(f"StockPriceHistory is empty. Attempting to populate for {SYMBOLS_TO_POPULATE} (Period: {HISTORY_PERIOD})...")
        total_added_count = 0

        # Asegurar sector
        logger.info(f"Checking for default sector ID: {DEFAULT_SECTOR_ID}")
        default_sector = db.query(Sector).get(DEFAULT_SECTOR_ID)
        if not default_sector:
            logger.warning(f"Default sector ID {DEFAULT_SECTOR_ID} not found. Creating 'Technology' sector.")
            try:
                default_sector = Sector(id=DEFAULT_SECTOR_ID, sector_name="Technology")
                db.add(default_sector); db.flush()
                logger.info(f"Default sector 'Technology' created.")
            except Exception as sector_err:
                logger.error(f"Failed to create default sector: {sector_err}", exc_info=True); db.rollback()
                logger.info("<<< populate_simulated_history finished (sector error)."); return
        # else: logger.info(f"Default sector '{default_sector.sector_name}' found.") # Log reducido

        # Procesar símbolos
        for symbol in SYMBOLS_TO_POPULATE:
            logger.info(f"--- Processing symbol: {symbol} ---")
            stock_obj = None
            try:
                logger.info(f"Fetching Ticker info for {symbol}..."); ticker = yf.Ticker(symbol); info = ticker.info; logger.info(f"Ticker info fetched.")
                stock_name = info.get("longName", info.get("shortName", f"{symbol} N/A"))
                current_price_val = info.get("currentPrice", info.get("regularMarketPrice", info.get("previousClose")))
                current_price = Decimal("0.00")
                if current_price_val is not None:
                    try: current_price = Decimal(str(current_price_val)).quantize(Decimal("0.01"))
                    except Exception: logger.error(f"Err converting price '{current_price_val}' for {symbol}.")

                logger.info(f"Querying/Creating stock entry for {symbol}..."); stock_obj = db.query(Stock).filter(Stock.symbol == symbol).first()
                if not stock_obj:
                    stock_obj = Stock(symbol=symbol, name=stock_name, current_price=current_price, sector_id=DEFAULT_SECTOR_ID)
                    db.add(stock_obj); db.flush()
                    logger.info(f"Stock {symbol} CREATED with ID {stock_obj.id}.")
                else:
                    stock_obj.current_price = current_price; db.flush()
                    # logger.info(f"Stock {symbol} FOUND with ID {stock_obj.id}, price updated.") # Log reducido

                logger.info(f"Fetching price history for {symbol} (Period: {HISTORY_PERIOD})..."); hist = ticker.history(period=HISTORY_PERIOD)
                if hist.empty: logger.warning(f"No yfinance history for {symbol}. Skipping."); continue
                logger.info(f"Fetched {len(hist)} historical data points for {symbol}.")

                entries_to_add = []
                for timestamp, row in hist.iterrows():
                    try:
                        ts = pd.to_datetime(timestamp).to_pydatetime().replace(tzinfo=None)
                        price_val = row.get('Close'); price = Decimal(str(price_val)).quantize(Decimal("0.01"))
                        if stock_obj and stock_obj.id and price_val is not None: entries_to_add.append(StockPriceHistory(stock_id=stock_obj.id, timestamp=ts, price=price))
                    except Exception: pass # Ignorar errores de fila

                if entries_to_add:
                    # logger.info(f"Adding {len(entries_to_add)} history entries for {symbol} to session..."); # Log reducido
                    db.add_all(entries_to_add); total_added_count += len(entries_to_add)

            except Exception as ticker_err: logger.error(f"--- ERROR processing symbol {symbol}: {ticker_err} ---", exc_info=True); continue

        # Commit final
        if total_added_count > 0:
            logger.info(f"\nAttempting to COMMIT {total_added_count} total entries..."); db.commit(); logger.info("COMMIT successful!")
        else: logger.info("\nNo new history entries added. No commit needed.")

    except Exception as e: logger.error(f"--- DB ERROR DURING POPULATION ---: {e}", exc_info=True); logger.warning("Attempting ROLLBACK..."); db.rollback(); logger.info("Rollback attempted.")
    finally: logger.info("<<< populate_simulated_history finished.")

# --- Table Initialization --- #
def init_db_tables():
    """Imports all models, creates tables, and populates history if needed."""
    logger.info("--- init_db_tables called ---")
    try:
        # logger.info("Importing models..."); # Log reducido
        from .models.user import User; from .models.stock import Stock; from .models.sector import Sector; from .models.transaction import Transaction; from .models.stock_price_history import StockPriceHistory;
        # logger.info("Models imported.") # Log reducido
    except ImportError as import_err: logger.error(f"ERROR importing models: {import_err}", exc_info=True); return

    try:
        logger.info("Creating database tables if they don't exist..."); Base.metadata.create_all(bind=engine); logger.info("Database tables check/creation finished.")
        logger.info("Attempting to populate history data via populate_simulated_history...") # Log mantenido
        db_session = SessionLocal()
        try: populate_simulated_history(db_session)
        except Exception as pop_err: logger.error(f"ERROR during history population call: {pop_err}", exc_info=True)
        finally:
            if db_session and db_session.is_active: db_session.close()
        logger.info("History population attempt finished.") # Log mantenido
    except Exception as e: logger.error(f"ERROR during DB initialization outer try block: {e}", exc_info=True)
    logger.info("--- init_db_tables finished ---")

# Opcional: Función para borrar tablas
def drop_all_tables(): # Sin cambios
    logger.warning("!!! Dropping all tables !!!"); # ... (resto igual)