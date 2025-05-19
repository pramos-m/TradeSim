# # # NOMBRE_DE_TU_APP_MODULO/state/search_state.py

# # import reflex as rx
# # import yfinance as yf
# # import os
# # import traceback
# # from sqlalchemy.orm import Session
# # from ..database import SessionLocal
# # from ..models.stock import Stock

# # class SearchState(rx.State):
# #     company_map = {
# #         "APPLE": "AAPL", "MICROSOFT": "MSFT", "GOOGLE": "GOOG", "ALPHABET": "GOOG",
# #         "AMAZON": "AMZN", "META": "META", "FACEBOOK": "META", "TESLA": "TSLA",
# #         "NVIDIA": "NVDA", "BERKSHIRE HATHAWAY": "BRK.B", "JPMORGAN": "JPM",
# #         "VISA": "V", "UNITEDHEALTH": "UNH", "HOME DEPOT": "HD",
# #         "PROCTER & GAMBLE": "PG", "MASTERCARD": "MA", "ELI LILLY": "LLY",
# #         "BROADCOM": "AVGO", "EXXON MOBIL": "XOM", "COSTCO": "COST",
# #         "ABBVIE": "ABBV", "PEPSICO": "PEP", "COCA-COLA": "KO", "COCA COLA": "KO",
# #         "MERCK": "MRK", "WALMART": "WMT", "BANK OF AMERICA": "BAC",
# #         "DISNEY": "DIS", "ADOBE": "ADBE", "PFIZER": "PFE", "CISCO": "CSCO",
# #         "ORACLE": "ORCL", "AT&T": "T", "INTEL": "INTC", "NETFLIX": "NFLX",
# #         "SALESFORCE": "CRM", "ABBOTT": "ABT", "MCDONALD'S": "MCD",
# #         "NIKE": "NKE", "QUALCOMM": "QCOM", "VERIZON": "VZ",
# #         "THERMO FISHER": "TMO", "DANAHER": "DHR", "ACCENTURE": "ACN",
# #     }

# #     search_query: str = ""
# #     search_result: dict = {}
# #     is_searching: bool = False
# #     search_error: str = ""

# #     def set_search_query(self, value: str):
# #         self.search_query = value

# #     def handle_input_key_down(self, key: str):
# #         if key == "Enter":
# #             return self.search_stock()

# #     @rx.event
# #     def search_stock(self):
# #         if not self.search_query:
# #             self.search_error = "Por favor ingrese un símbolo o nombre de acción"
# #             return
        
# #         self.is_searching = True
# #         self.search_error = ""
        
# #         db = SessionLocal()
# #         try:
# #             # Buscar en la base de datos
# #             stock = db.query(Stock).filter(
# #                 (Stock.symbol.ilike(f"%{self.search_query}%")) |
# #                 (Stock.name.ilike(f"%{self.search_query}%"))
# #             ).first()
            
# #             if stock:
# #                 self.search_result = {
# #                     "Symbol": stock.symbol,
# #                     "Name": stock.name,
# #                     "Price": float(stock.current_price),
# #                     "Change": 0.0  # TODO: Calcular cambio real
# #                 }
# #             else:
# #                 self.search_error = f"No se encontró la acción '{self.search_query}'"
# #                 self.search_result = {}
# #         except Exception as e:
# #             self.search_error = f"Error al buscar: {str(e)}"
# #             self.search_result = {}
# #         finally:
# #             db.close()
# #             self.is_searching = False

# #     @rx.event
# #     def go_to_stock_detail(self, symbol: str):
# #         if symbol and symbol != "No encontrado" and not symbol.startswith("Error"):
# #             return rx.redirect(f"/detalles_accion/{symbol.upper()}")
# #         return rx.window_alert("No se puede navegar para este resultado.")

# # NOMBRE_DE_TU_APP_MODULO/state/search_state.py

# import reflex as rx
# import logging # Para registrar errores si es necesario
# from sqlalchemy.orm import Session # No es necesario si usas SessionLocal directamente
# from ..database import SessionLocal # Ajusta la ruta si es necesario
# from ..models.stock import Stock # Ajusta la ruta si es necesario

# logger = logging.getLogger(__name__)

# class SearchState(rx.State):
#     # company_map no se usa actualmente en la función search_stock local,
#     # pero lo mantenemos si lo necesitas para otra lógica o es de tu código original.
#     company_map = {
#         "APPLE": "AAPL", "MICROSOFT": "MSFT", "GOOGLE": "GOOG", "ALPHABET": "GOOG",
#         "AMAZON": "AMZN", "META": "META", "FACEBOOK": "META", "TESLA": "TSLA",
#         "NVIDIA": "NVDA", "BERKSHIRE HATHAWAY": "BRK.B", "JPMORGAN": "JPM",
#         "VISA": "V", "UNITEDHEALTH": "UNH", "HOME DEPOT": "HD",
#         "PROCTER & GAMBLE": "PG", "MASTERCARD": "MA", "ELI LILLY": "LLY",
#         "BROADCOM": "AVGO", "EXXON MOBIL": "XOM", "COSTCO": "COST",
#         "ABBVIE": "ABBV", "PEPSICO": "PEP", "COCA-COLA": "KO", "COCA COLA": "KO",
#         "MERCK": "MRK", "WALMART": "WMT", "BANK OF AMERICA": "BAC",
#         "DISNEY": "DIS", "ADOBE": "ADBE", "PFIZER": "PFE", "CISCO": "CSCO",
#         "ORACLE": "ORCL", "AT&T": "T", "INTEL": "INTC", "NETFLIX": "NFLX",
#         "SALESFORCE": "CRM", "ABBOTT": "ABT", "MCDONALD'S": "MCD",
#         "NIKE": "NKE", "QUALCOMM": "QCOM", "VERIZON": "VZ",
#         "THERMO FISHER": "TMO", "DANAHER": "DHR", "ACCENTURE": "ACN",
#     }

#     search_query: str = ""
#     search_result: dict = {} # Guardará el resultado: {"Symbol": "...", "Name": "...", "Price": ..., "Logo": "..."}
#     is_searching: bool = False
#     search_error: str = "" # Para mensajes de error

#     def set_search_query(self, value: str):
#         self.search_query = value
#         # Opcional: limpiar resultados/errores anteriores cuando el usuario escribe
#         # self.search_result = {}
#         # self.search_error = ""

#     def handle_input_key_down(self, key: str):
#         """Maneja el evento de presionar una tecla en el input de búsqueda."""
#         if key == "Enter":
#             # Prevenir el comportamiento por defecto del Enter si es necesario
#             # (en este caso, rx.event lo maneja bien)
#             return self.search_stock()

#     @rx.event
#     def search_stock(self):
#         """Busca una acción en la base de datos local."""
#         self.is_searching = True
#         self.search_result = {} # Limpiar resultados previos
#         self.search_error = ""  # Limpiar errores previos

#         if not self.search_query.strip():
#             self.search_error = "Por favor, ingrese un símbolo o nombre de acción."
#             self.is_searching = False
#             return

#         db = None # Inicializar db a None
#         try:
#             db = SessionLocal()
#             query_term = self.search_query.strip()
            
#             # Buscar en la base de datos local.
#             # Usamos ilike para búsquedas insensibles a mayúsculas/minúsculas.
#             # El '%' actúa como comodín.
#             stock_found = db.query(Stock).filter(
#                 (Stock.symbol.ilike(f"%{query_term}%")) |
#                 (Stock.name.ilike(f"%{query_term}%"))
#             ).first()

#             if stock_found:
#                 self.search_result = {
#                     "Symbol": stock_found.symbol,
#                     "Name": stock_found.name,
#                     "Price": float(stock_found.current_price), # Asegurarse que es float
#                     # Asumimos que tu modelo Stock tiene 'logo_url'.
#                     # Si no, elimina esta línea o ajusta el modelo.
#                     "Logo": stock_found.logo_url if hasattr(stock_found, 'logo_url') and stock_found.logo_url else "/default_logo.png"
#                 }
#             else:
#                 self.search_error = f"No se encontró la acción '{query_term}' en la base de datos."
#         except Exception as e:
#             logger.error(f"Error durante la búsqueda de acciones en BD: {e}", exc_info=True)
#             self.search_error = "Ocurrió un error al buscar. Inténtalo de nuevo."
#         finally:
#             if db:
#                 db.close()
#             self.is_searching = False
        
#         return

#     @rx.event
#     def go_to_stock_detail(self, symbol: str | None):
#         """Navega a la página de detalles de la acción si el símbolo es válido."""
#         if symbol and isinstance(symbol, str) and symbol.strip():
#             # Limpiar búsqueda actual para la próxima vez
#             # self.search_query = ""
#             # self.search_result = {}
#             # self.search_error = ""
#             return rx.redirect(f"/detalles_accion/{symbol.upper().strip()}")
#         else:
#             # Podrías mostrar una alerta o log si el símbolo no es válido
#             logger.warning("Intento de navegar a detalles de acción con símbolo inválido.")
#             return rx.window_alert("No se puede navegar: símbolo de acción no válido.")

# tradesim/tradesim/state/search_state.py
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
        # ... (puedes añadir más si quieres)
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
