import yfinance as yf
from sqlalchemy.orm import Session
from tradesim.database import SessionLocal, engine, Base # Importa tu Sesión y Base
from tradesim.models.stock import Stock # Importa tu modelo Stock
from tradesim.models.sector import Sector # Importa tu modelo Sector (necesario si creas Stocks)
from tradesim.models.stock_price_history import StockPriceHistory # Importa el nuevo modelo
from datetime import datetime
from decimal import Decimal
import pandas as pd # yfinance devuelve DataFrames

# --- Configuración ---
# Define los símbolos de las acciones que quieres poblar
SYMBOLS_TO_POPULATE = ["AAPL", "GOOGL", "MSFT", "TSLA"]
# Define el período histórico a obtener (ej: "1y", "2y", "5y", "max")
HISTORY_PERIOD = "2y"
# Define un sector_id por defecto (¡IMPORTANTE: Asegúrate que este ID exista en tu tabla sectors!)
# O busca uno dinámicamente.
DEFAULT_SECTOR_ID = 1 # CAMBIA ESTO si es necesario

def get_or_create_stock(db: Session, symbol: str, name: str, current_price: Decimal) -> Stock:
    """Busca una acción por símbolo o la crea si no existe."""
    stock = db.query(Stock).filter(Stock.symbol == symbol).first()
    if not stock:
        print(f"Stock {symbol} not found, creating...")
        # Intenta obtener el sector por defecto
        default_sector = db.query(Sector).get(DEFAULT_SECTOR_ID)
        if not default_sector:
             # Si el sector por defecto no existe, crea uno genérico (o maneja el error)
             print(f"Default sector ID {DEFAULT_SECTOR_ID} not found. Creating a default 'Technology' sector.")
             default_sector = Sector(id=DEFAULT_SECTOR_ID, sector_name="Technology") # O elige otro nombre/id
             db.add(default_sector)
             # db.flush() # Podría ser necesario si quieres usar el ID inmediatamente, pero el commit al final debería bastar

        stock = Stock(
            symbol=symbol,
            name=name,
            current_price=current_price,
            sector_id=DEFAULT_SECTOR_ID # Asigna el ID del sector
        )
        db.add(stock)
        db.flush() # Para obtener el ID del stock recién creado antes del commit final
        print(f"Stock {symbol} created with ID {stock.id}.")
    else:
         # Actualizar precio actual si ya existe
         stock.current_price = current_price
         print(f"Stock {symbol} found with ID {stock.id}. Updating current price.")
    return stock

def populate_history():
    """Obtiene datos de yfinance y los guarda en la base de datos."""
    print(f"--- Starting history population for symbols: {SYMBOLS_TO_POPULATE} ---")
    db = SessionLocal()
    try:
        # Verificar si la tabla de historial ya tiene datos para estos símbolos
        existing_history_check = db.query(StockPriceHistory).join(Stock).filter(Stock.symbol.in_(SYMBOLS_TO_POPULATE)).count()

        if existing_history_check > 0:
            print("History table already contains data for the specified symbols. Skipping population.")
            print("To repopulate, delete tradesim.db or manually clear the history table.")
            return

        total_added_count = 0
        for symbol in SYMBOLS_TO_POPULATE:
            print(f"\nFetching data for {symbol}...")
            ticker = yf.Ticker(symbol)

            # Obtener info para nombre y precio actual
            info = ticker.info
            stock_name = info.get("longName", f"{symbol} Name Not Found")
            current_price = Decimal(str(info.get("currentPrice", "0.0"))).quantize(Decimal("0.01"))
            print(f"Current info: Name='{stock_name}', Price={current_price}")


            # Obtener o crear el registro del Stock en la BBDD
            stock_obj = get_or_create_stock(db, symbol, stock_name, current_price)
            if not stock_obj or not stock_obj.id:
                 print(f"ERROR: Could not get or create stock object for {symbol}. Skipping history.")
                 continue # Saltar al siguiente símbolo si no se pudo crear/obtener el stock

            # Obtener historial de precios
            hist = ticker.history(period=HISTORY_PERIOD)

            if hist.empty:
                print(f"No history found for {symbol} for period {HISTORY_PERIOD}. Skipping.")
                continue

            print(f"Fetched {len(hist)} historical data points for {symbol}.")

            entries_to_add = []
            # Iterar sobre el DataFrame de historial (el índice es la fecha/hora)
            for timestamp, row in hist.iterrows():
                # Asegurarse de que el timestamp sea timezone-naive y datetime object
                ts = pd.to_datetime(timestamp).to_pydatetime()
                if ts.tzinfo is not None:
                     ts = ts.replace(tzinfo=None) # Convertir a naive si tiene timezone

                price = Decimal(str(row['Close'])).quantize(Decimal("0.01")) # Usar precio de cierre

                entry = StockPriceHistory(
                    stock_id=stock_obj.id,
                    timestamp=ts,
                    price=price
                )
                entries_to_add.append(entry)

            if entries_to_add:
                db.add_all(entries_to_add)
                total_added_count += len(entries_to_add)
                print(f"Prepared {len(entries_to_add)} history entries for {symbol}.")

        # Commit todos los cambios al final
        if total_added_count > 0:
            print(f"\nCommitting {total_added_count} total entries to the database...")
            db.commit()
            print("Commit successful!")
        else:
            print("\nNo new history entries were added.")

    except Exception as e:
        print(f"\n--- ERROR DURING POPULATION ---")
        print(e)
        db.rollback() # Deshacer cambios en caso de error
    finally:
        db.close()
        print("--- History population script finished ---")

# Ejecutar la función principal si el script se corre directamente
if __name__ == "__main__":
    # Asegúrate de que las tablas existen antes de poblar
    # init_db_tables() # Descomenta si corres esto totalmente independiente
    print("Running population script...")
    populate_history()