# tradesim/tradesim/state/search_state.py
import reflex as rx
import yfinance as yf
import os
import logging
from typing import Optional # <--- IMPORT AÑADIDO AQUÍ

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO)

class SearchState(rx.State):
    company_map = {
        "APPLE": "AAPL", "MICROSOFT": "MSFT", "GOOGLE": "GOOG", "ALPHABET": "GOOG",
        "AMAZON": "AMZN", "META": "META", "FACEBOOK": "META", "TESLA": "TSLA",
        "NVIDIA": "NVDA", "BERKSHIRE HATHAWAY": "BRK.B", "JPMORGAN": "JPM",
        "VISA": "V", "UNITEDHEALTH": "UNH", "HOME DEPOT": "HD",
        "PROCTER & GAMBLE": "PG", "MASTERCARD": "MA", "ELI LILLY": "LLY",
    }

    search_query: str = ""
    search_result: dict = {}
    is_searching: bool = False
    search_error: str = ""

    def set_search_query(self, value: str):
        self.search_query = value
        self.search_error = ""
        if not value.strip():
            self.search_result = {}

    @rx.event
    def search_stock(self):
        self.is_searching = True
        self.search_result = {}
        self.search_error = ""
        
        if not self.search_query.strip():
            self.search_error = "Por favor, introduce un símbolo o nombre de empresa."
            self.is_searching = False
            return

        try:
            query_cleaned = self.search_query.strip()
            query_for_map = query_cleaned.upper()
            symbol_to_fetch = self.company_map.get(query_for_map, query_cleaned) 
            
            logger.info(f"SearchState: Buscando con símbolo/query: '{symbol_to_fetch}' (original: '{query_cleaned}')")
            
            stock_ticker = yf.Ticker(symbol_to_fetch)
            info = stock_ticker.info 

            if not info or (info.get("regularMarketPrice") is None and info.get("currentPrice") is None and info.get("previousClose") is None):
                self.search_error = f"No se encontró información de mercado para '{query_cleaned}' (intentado: '{symbol_to_fetch}'). Intenta con un símbolo ticker válido."
                logger.warning(f"SearchState: No info o precio para {symbol_to_fetch}. Keys en info: {list(info.keys()) if isinstance(info, dict) else 'Info no es dict'}")
            else:
                actual_symbol = info.get("symbol", symbol_to_fetch.upper())
                logo_url_yf = info.get("logo_url")
                logo_path_on_server = f"/{actual_symbol}.png"

                price_val = info.get("currentPrice", info.get("regularMarketPrice", info.get("previousClose")))
                price_str = "N/A"
                if price_val is not None:
                    try:
                        price_str = f"{info.get('currencySymbol', '$')}{float(price_val):,.2f}"
                    except (ValueError, TypeError):
                        price_str = str(price_val) 

                self.search_result = {
                    "Symbol": actual_symbol,
                    "Name": info.get("longName", info.get("shortName", query_cleaned)),
                    "PriceString": price_str,
                    "Logo": logo_url_yf or logo_path_on_server,
                }
                logger.info(f"SearchState: Resultado encontrado para {actual_symbol}: {self.search_result.get('Name')}")
                self.search_error = "" 

        except requests.exceptions.RequestException as net_err:
            logger.error(f"SearchState: Error de red al buscar '{self.search_query}': {net_err}", exc_info=False)
            self.search_error = "Error de red al buscar. Verifica tu conexión o inténtalo más tarde."
        except Exception as e: 
            logger.error(f"SearchState: Excepción en search_stock para '{self.search_query}': {e}", exc_info=True)
            self.search_error = "Ocurrió un error inesperado al buscar."
        finally:
            self.is_searching = False
        return

    def handle_input_key_down(self, key: str):
        if key == "Enter":
            return self.search_stock()

    @rx.event
    def go_to_stock_detail(self, symbol: Optional[str]): # Optional[str] necesita el import
        if symbol and isinstance(symbol, str) and symbol.strip() and symbol != "N/A":
            return rx.redirect(f"/detalles_accion/{symbol.upper().strip()}")
        else:
            logger.warning("SearchState: Intento de navegar a detalles con símbolo inválido o None.")
            self.search_error = "No se puede navegar: símbolo no válido."
            return
