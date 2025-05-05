# tradesim/database.py (CORREGIDO HISTORY_PERIOD)
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
import yfinance as yf
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
HISTORY_PERIOD = "5y" # <-- CORREGIDO a "5y"
DEFAULT_SECTOR_ID = 1

def populate_simulated_history(db: Session):
    logger.info(">>> Running populate_simulated_history...")
    from .models.stock import Stock; from .models.sector import Sector; from .models.stock_price_history import StockPriceHistory
    try:
        logger.info("Checking existing history count...")
        history_count = db.query(StockPriceHistory.id).limit(1).scalar()
        logger.info(f"History count: {history_count if history_count is not None else 'None (or 0)'}")
        if history_count is not None and history_count > 0:
            logger.info("Skipping population."); logger.info("<<< populate_simulated_history finished (skipped)."); return

        logger.info(f"Populating for {SYMBOLS_TO_POPULATE} (Period: {HISTORY_PERIOD})...")
        total_added_count = 0
        logger.info(f"Checking sector ID: {DEFAULT_SECTOR_ID}")
        default_sector = db.query(Sector).get(DEFAULT_SECTOR_ID)
        if not default_sector:
            logger.warning(f"Creating default sector 'Technology'..."); default_sector = Sector(id=DEFAULT_SECTOR_ID, sector_name="Technology"); db.add(default_sector); db.flush()

        for symbol in SYMBOLS_TO_POPULATE:
            logger.info(f"--- Processing: {symbol} ---")
            stock_obj = None
            try:
                logger.info(f"Fetching Ticker info..."); ticker = yf.Ticker(symbol); info = ticker.info; logger.info(f"Ticker info fetched.")
                stock_name = info.get("longName", info.get("shortName", f"{symbol} N/A"))
                current_price_val = info.get("currentPrice", info.get("regularMarketPrice", info.get("previousClose")))
                current_price = Decimal("0.00")
                if current_price_val is not None:
                    try: current_price = Decimal(str(current_price_val)).quantize(Decimal("0.01"))
                    except Exception: logger.error(f"Err converting price '{current_price_val}' for {symbol}.")
                stock_obj = db.query(Stock).filter(Stock.symbol == symbol).first()
                if not stock_obj:
                    stock_obj = Stock(symbol=symbol, name=stock_name, current_price=current_price, sector_id=DEFAULT_SECTOR_ID)
                    db.add(stock_obj); db.flush(); logger.info(f"Stock {symbol} CREATED (ID:{stock_obj.id}).")
                else: stock_obj.current_price = current_price; db.flush()
                logger.info(f"Fetching history (Period: {HISTORY_PERIOD})..."); hist = ticker.history(period=HISTORY_PERIOD); logger.info(f"Fetched {len(hist)} points.") # Ahora buscará 5y
                if hist.empty: logger.warning(f"No yfinance history for {symbol}. Skipping."); continue
                entries_to_add = [StockPriceHistory(stock_id=stock_obj.id, timestamp=pd.to_datetime(ts).to_pydatetime().replace(tzinfo=None), price=Decimal(str(row.get('Close'))).quantize(Decimal("0.01"))) for ts, row in hist.iterrows() if row.get('Close') is not None and stock_obj and stock_obj.id]
                if entries_to_add: db.add_all(entries_to_add); total_added_count += len(entries_to_add); logger.info(f"Added {len(entries_to_add)} history entries.")
            except Exception as ticker_err: logger.error(f"ERROR processing {symbol}: {ticker_err}", exc_info=True); continue
        if total_added_count > 0: logger.info(f"\nAttempting COMMIT ({total_added_count} entries)..."); db.commit(); logger.info("COMMIT successful!")
        else: logger.info("\nNo new history entries added.")
    except Exception as e: logger.error(f"DB ERROR POPULATION: {e}", exc_info=True); logger.warning("ROLLBACK..."); db.rollback()
    finally: logger.info("<<< populate_simulated_history finished.")

def init_db_tables():
    logger.info("--- init_db_tables called ---")
    try: from .models.user import User; from .models.stock import Stock; from .models.sector import Sector; from .models.transaction import Transaction; from .models.stock_price_history import StockPriceHistory;
    except ImportError as import_err: logger.error(f"ERROR importing models: {import_err}", exc_info=True); return
    try:
        logger.info("Creating tables if needed..."); Base.metadata.create_all(bind=engine); logger.info("Tables OK.")
        logger.info("Attempting population..."); db_session = SessionLocal()
        try: populate_simulated_history(db_session)
        except Exception as pop_err: logger.error(f"ERROR during population call: {pop_err}", exc_info=True)
        finally:
            if db_session and db_session.is_active: db_session.close()
        logger.info("Population attempt finished.")
    except Exception as e: logger.error(f"ERROR during DB init: {e}", exc_info=True)
    logger.info("--- init_db_tables finished ---")

def drop_all_tables(): logger.warning("!!! Dropping all tables !!!"); # ... (resto igual)