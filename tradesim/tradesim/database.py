# # tradesim/database.py (CORREGIDO HISTORY_PERIOD)
# from sqlmodel import SQLModel, create_engine, Session
# from sqlalchemy.orm import sessionmaker
# import os
# import yfinance as yf
# from datetime import datetime, timedelta
# from decimal import Decimal
# import pandas as pd
# import logging
# from .models.base import BaseModel  # Import BaseModel instead of Base
# from .models.portfolio_item import PortfolioItemDB
# from .models.user import User
# from .models.stock import Stock
# from .models.sector import Sector
# from .models.transaction import StockTransaction
# from .models.stock_price_history import StockPriceHistory

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# DATABASE_URL_FALLBACK = "sqlite:///tradesim.db"
# DATABASE_URL = os.getenv("DATABASE_URL", DATABASE_URL_FALLBACK)
# logger.info(f"Using Database URL: {DATABASE_URL}")
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         if db and db.is_active:
#             db.close()

# # --- Data Population Logic ---
# SYMBOLS_TO_POPULATE = ["AAPL", "GOOG", "MSFT", "TSLA"]
# HISTORY_PERIOD = "max" # <-- CORREGIDO (antes era "MAX" implícito o "1y", ahora "5y")
# DEFAULT_SECTOR_ID = 1

# def populate_simulated_history(db: Session):
#     logger.info(">>> Running populate_simulated_history...")
#     try:
#         logger.info("Checking existing history count...")
#         history_count = db.query(StockPriceHistory.id).limit(1).scalar()
#         logger.info(f"History count: {history_count if history_count is not None else 'None (or 0)'}")
#         if history_count is not None and history_count > 0:
#             logger.info("Skipping population."); logger.info("<<< populate_simulated_history finished (skipped)."); return

#         logger.info(f"Populating for {SYMBOLS_TO_POPULATE} (Period: {HISTORY_PERIOD})...")
#         total_added_count = 0
#         logger.info(f"Checking sector ID: {DEFAULT_SECTOR_ID}")
#         default_sector = db.query(Sector).get(DEFAULT_SECTOR_ID)
#         if not default_sector:
#             logger.warning(f"Creating default sector 'Technology'..."); default_sector = Sector(id=DEFAULT_SECTOR_ID, sector_name="Technology"); db.add(default_sector); db.flush()
#         for symbol in SYMBOLS_TO_POPULATE:
#             logger.info(f"--- Processing: {symbol} ---")
#             stock_obj = None
#             try:
#                 logger.info(f"Fetching Ticker info..."); ticker = yf.Ticker(symbol); info = ticker.info; logger.info(f"Ticker info fetched.")
#                 stock_name = info.get("longName", info.get("shortName", f"{symbol} N/A"))
#                 current_price_val = info.get("currentPrice", info.get("regularMarketPrice", info.get("previousClose")))
#                 current_price = Decimal("0.00")
#                 if current_price_val is not None:
#                     try: current_price = Decimal(str(current_price_val)).quantize(Decimal("0.01"))
#                     except Exception: logger.error(f"Err converting price '{current_price_val}' for {symbol}.")
#                 stock_obj = db.query(Stock).filter(Stock.symbol == symbol).first()
#                 if not stock_obj:
#                     stock_obj = Stock(symbol=symbol, name=stock_name, current_price=current_price, sector_id=DEFAULT_SECTOR_ID)
#                     db.add(stock_obj); db.flush(); logger.info(f"Stock {symbol} CREATED (ID:{stock_obj.id}).")
#                 else: stock_obj.current_price = current_price; db.flush()
#                 logger.info(f"Fetching history (Period: {HISTORY_PERIOD})..."); hist = ticker.history(period=HISTORY_PERIOD); logger.info(f"Fetched {len(hist)} points.")
#                 if hist.empty: logger.warning(f"No yfinance history for {symbol}. Skipping."); continue
#                 entries_to_add = [StockPriceHistory(stock_id=stock_obj.id, timestamp=pd.to_datetime(ts).to_pydatetime().replace(tzinfo=None), price=Decimal(str(row.get('Close'))).quantize(Decimal("0.01"))) for ts, row in hist.iterrows() if row.get('Close') is not None and stock_obj and stock_obj.id]
#                 if entries_to_add: db.add_all(entries_to_add); total_added_count += len(entries_to_add); logger.info(f"Added {len(entries_to_add)} history entries.")
#             except Exception as ticker_err: logger.error(f"ERROR processing {symbol}: {ticker_err}", exc_info=True); continue
#         if total_added_count > 0: logger.info(f"\nAttempting COMMIT ({total_added_count} entries)..."); db.commit(); logger.info("COMMIT successful!")
#         else: logger.info("\nNo new entries added.")
#     except Exception as e: logger.error(f"DB ERROR POPULATION: {e}", exc_info=True); logger.warning("ROLLBACK..."); db.rollback()
#     finally: logger.info("<<< populate_simulated_history finished.")

# def init_db_tables():
#     logger.info("--- init_db_tables called ---")
#     try:
#         from .models.user import User
#         from .models.stock import Stock
#         from .models.sector import Sector
#         from .models.transaction import StockTransaction
#         from .models.stock_price_history import StockPriceHistory
#         from .models.portfolio_item import PortfolioItemDB
#     except ImportError as import_err:
#         logger.error(f"ERROR importing models: {import_err}", exc_info=True)
#         return

#     try:
#         logger.info("Creating tables if needed...")
#         SQLModel.metadata.create_all(bind=engine)
#         logger.info("Tables created successfully.")
#     except Exception as e:
#         logger.error(f"ERROR during DB init: {e}", exc_info=True)
#     finally:
#         logger.info("--- init_db_tables finished ---")

# def drop_all_tables():
#     logger.info("--- drop_all_tables called ---")
#     try:
#         SQLModel.metadata.drop_all(bind=engine)
#         logger.info("Tables dropped successfully.")
#     except Exception as e:
#         logger.error(f"ERROR during table drop: {e}", exc_info=True)
#     finally:
#         logger.info("--- drop_all_tables finished ---")
# tradesim/tradesim/database.py
import os
from sqlmodel import create_engine, SQLModel, Session
from dotenv import load_dotenv
import logging

# Importa todos tus modelos aquí para que SQLModel los conozca al crear tablas
# Esto es crucial
from .models.user import User
from .models.sector import Sector
from .models.stock import Stock
from .models.portfolio_item import PortfolioItemDB # Asegúrate que este archivo y clase existen
from .models.transaction import StockTransaction # Asegúrate que este archivo y clase existen
from .models.stock_price_history import StockPriceHistory

logger = logging.getLogger(__name__)
load_dotenv()

DATABASE_URL_KEY = "DATABASE_URL"
DEFAULT_DATABASE_URL = "sqlite:///./data/tradesim.db" # Asegúrate que la carpeta data existe o se crea
DATABASE_URL = os.getenv(DATABASE_URL_KEY, DEFAULT_DATABASE_URL)

# Crear directorio si no existe (para SQLite)
if DATABASE_URL.startswith("sqlite:///"):
    db_path = DATABASE_URL.split("sqlite:///")[1]
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        logger.info(f"Directorio de base de datos creado: {db_dir}")

engine = create_engine(DATABASE_URL, echo=False) # echo=True para debug de SQL

DEFAULT_SECTOR_NAME = "Tecnología" # O el que prefieras como por defecto
DEFAULT_SECTOR_ID = 1 # Asumir que el ID 1 será el sector por defecto

def create_db_and_tables():
    logger.info("--- create_db_and_tables llamada ---")
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Tablas creadas (o ya existían) exitosamente.")
        
        # Crear sector por defecto si no existe
        with Session(engine) as session:
            default_sector = session.get(Sector, DEFAULT_SECTOR_ID)
            if not default_sector:
                default_sector_obj = Sector(id=DEFAULT_SECTOR_ID, sector_name=DEFAULT_SECTOR_NAME)
                session.add(default_sector_obj)
                session.commit()
                logger.info(f"Sector por defecto '{DEFAULT_SECTOR_NAME}' creado con ID {DEFAULT_SECTOR_ID}.")
            else:
                logger.info(f"Sector por defecto '{default_sector.sector_name}' ya existe.")
                # Actualizar el nombre si es diferente (opcional)
                if default_sector.sector_name != DEFAULT_SECTOR_NAME:
                    default_sector.sector_name = DEFAULT_SECTOR_NAME
                    session.add(default_sector)
                    session.commit()
                    logger.info(f"Sector por defecto actualizado a '{DEFAULT_SECTOR_NAME}'.")

    except Exception as e:
        logger.error(f"Error durante create_db_and_tables: {e}", exc_info=True)
        raise # Relanzar para que el error sea visible
    logger.info("--- create_db_and_tables finalizada ---")


def init_db_tables():
    logger.info("Usando Database URL: %s", DATABASE_URL)
    logger.info("--- init_db_tables llamada ---")
    try:
        create_db_and_tables()
        logger.info("Creando tablas si es necesario...") # Este log ya estaba
        # La siguiente línea es redundante si create_db_and_tables ya lo hace
        # SQLModel.metadata.create_all(engine) 
        logger.info("Tablas creadas exitosamente.") # Este log ya estaba
    except Exception as e:
        logger.error(f"FATAL ERROR durante init_db_tables call en database.py: {e}", exc_info=True)
        # Considera si quieres que la app falle aquí o intente continuar
    logger.info("--- init_db_tables finalizada ---")


# Dependencia para FastAPI (si usas FastAPI, si no, no es necesaria aquí)
def get_db():
    with Session(engine) as session:
        yield session

# Para usar con with SessionLocal() as session:
SessionLocal = lambda: Session(engine)
