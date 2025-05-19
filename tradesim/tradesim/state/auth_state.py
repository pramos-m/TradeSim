# # tradesim/tradesim/state/auth_state.py
# import reflex as rx
# import yfinance as yf
# import os
# import logging
# import requests
# from typing import List, Dict, Any, Optional, Tuple # Any ya estaba aquí
# import pandas as pd
# import plotly.graph_objects as go
# from jose import JWTError, jwt
# from decimal import Decimal
# import asyncio
# import json # Necesario para open_url_script (y para la versión corregida)
# import random
# from sqlmodel import SQLModel
# from datetime import datetime, timedelta, timezone
# from ..database import SessionLocal
# from sqlalchemy import select, func
# from ..controller.user import get_user_by_id
# # tradesim/state/auth_state.py
# # ... (otros imports de yfinance, os, logging, etc.)
# from decimal import Decimal, InvalidOperation # Ya estaba
# # import asyncio # Ya estaba
# # from datetime import datetime, timezone # Ya estaba
# from sqlalchemy.orm import Session # Ya estaba
# from ..models.stock import Stock # Ya estaba
# from ..models.stock_price_history import StockPriceHistory # Ya estaba
# from ..models.transaction import StockTransaction, TransactionType # Ya estaba
# from ..models.portfolio_item import PortfolioItemDB # Ya estaba

# from ..models.user import User # Ya estaba
# from ..models.stock import Stock as StockModel # Ya estaba
# from ..models.sector import Sector as SectorModel # Ya estaba
# from ..controller.transaction import get_transaction_history_with_profit_loss # Ya estaba

# logger = logging.getLogger(__name__)
# # ... (resto de constantes y clases base como NewsArticle, PortfolioItem, etc.)

# # Esta configuración de logger ya estaba, la dejo por si acaso
# # logger = logging.getLogger(__name__) # Duplicado, pero no daña
# if not logger.hasHandlers():
#     logging.basicConfig(level=logging.INFO)

# SECRET_KEY = os.getenv("SECRET_KEY", "a-very-secret-key-here-change-me")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
# DEFAULT_AVATAR = "/default_avatar.png"
# GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "f767bfe6df4f747e6b77c0178e8cc0d8")
# GNEWS_API_URL = "https://gnews.io/api/v4/search"
# DEFAULT_SEARCH_QUERY = "mercado acciones finanzas"
# COMPANY_MAP = {
#     "APPLE": "AAPL", "MICROSOFT": "MSFT", "GOOGLE": "GOOGL", "ALPHABET": "GOOGL",
#     "AMAZON": "AMZN", "META": "META", "FACEBOOK": "META", "TESLA": "TSLA",
#     "NVIDIA": "NVDA", "BERKSHIRE HATHAWAY": "BRK.B", "JPMORGAN": "JPM",
#     "VISA": "V", "UNITEDHEALTH": "UNH", "HOME DEPOT": "HD",
#     "PROCTER & GAMBLE": "PG", "MASTERCARD": "MA", "ELI LILLY": "LLY",
#     "BROADCOM": "AVGO", "EXXON MOBIL": "XOM", "COSTCO": "COST",
#     "ABBVIE": "ABBV", "PEPSICO": "PEP", "COCA-COLA": "KO", "COCA COLA": "KO",
#     "MERCK": "MRK", "WALMART": "WMT", "BANK OF AMERICA": "BAC",
#     "DISNEY": "DIS", "ADOBE": "ADBE", "PFIZER": "PFE", "CISCO": "CSCO",
#     "ORACLE": "ORCL", "AT&T": "T", "INTEL": "INTC", "NETFLIX": "NFLX",
#     "SALESFORCE": "CRM", "ABBOTT": "ABT", "MCDONALD'S": "MCD",
#     "NIKE": "NKE", "QUALCOMM": "QCOM", "VERIZON": "VZ",
#     "THERMO FISHER": "TMO", "DANAHER": "DHR", "ACCENTURE": "ACN",
# }

# class NewsArticle(rx.Base):
#     title: str; url: str; publisher: str; date: str; summary: str; image: str
# class PortfolioItem(rx.Base):
#     symbol: str
#     name: str
#     quantity: int
#     current_price: float
#     current_value: float
#     logo_url: str
# class SearchResultItem(rx.Base):
#     Symbol: str = ""; Name: str = "No encontrado"; Current_Price: str = "N/A"; Logo: str = "/default_logo.png"
# class TransactionDisplayItem(rx.Base):
#     timestamp: str; symbol: str; quantity: int; price: float; type: str
#     @property
#     def formatted_quantity(self) -> str:
#         sign = "+" if self.type.lower() == TransactionType.COMPRA.value.lower() else "-"
#         return f"{sign}{abs(self.quantity)}"

# class AuthState(rx.State):
#     """Estado GLOBAL combinado."""
#     # --- Variables ---
#     is_authenticated: bool = False
#     user_id: Optional[int] = None
#     username: str = ""
#     email: str = ""
#     password: str = ""
#     confirm_password: str = ""
#     profile_image_url: str = DEFAULT_AVATAR
#     account_balance: float = 0.0
#     active_tab: str = "login"
#     error_message: str = ""
#     loading: bool = False
#     auth_token: str = ""
#     processed_token: bool = False
#     last_path: str = "/"

#     # Portfolio
#     portfolio_items: List[PortfolioItem] = []
#     total_portfolio_value: float = 0.0
#     portfolio_chart_hover_info: Optional[Dict] = None
#     portfolio_show_absolute_change: bool = False
#     selected_period: str = "1M"
#     recent_transactions: List[TransactionDisplayItem] = []
#     portfolio_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'total_value'])
#     is_loading_portfolio_chart: bool = False

#     # Stock Details
#     viewing_stock_symbol: str = ""
#     current_stock_info: dict = {}
#     current_stock_shares_owned: int = 0
#     buy_sell_quantity: int = 1
#     transaction_message: str = ""
#     current_stock_history: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
#     current_stock_selected_period: str = "1M"
#     stock_detail_chart_hover_info: Optional[Dict] = None
#     is_loading_current_stock_details: bool = False
#     current_stock_metrics: Dict[str, str] = {}

#     # News
#     processed_news: List[NewsArticle] = []
#     is_loading_news: bool = False
#     has_news: bool = False
#     news_page: int = 1
#     max_articles: int = 10
#     SEARCH_QUERY: str = DEFAULT_SEARCH_QUERY # Nota: puede causar confusión con SearchState.search_query

#     # Search (global, para diferenciarlo de SearchState si se usa)
#     search_term: str = "" # Para la búsqueda global en AuthState
#     # search_result: SearchResultItem = SearchResultItem() # Ya definido arriba
#     is_searching: bool = False # Para la búsqueda global en AuthState
#     # search_error: str = "" # Ya está error_message, pero podría ser específico para la búsqueda.

#     # PNL Data
#     daily_pnl: float = 0.0
#     monthly_pnl: float = 0.0
#     yearly_pnl: float = 0.0
#     daily_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
#     monthly_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
#     yearly_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])

#     # Chart Data (Genérico, no sé si lo usas, ya tienes otros específicos)
#     stock_chart_data: List[dict] = []
#     stock_chart_layout: dict = {}


#     def _create_access_token(self, user_id: int) -> Optional[str]:
#         expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#         data = {"sub": str(user_id), "exp": expire}
#         try: return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
#         except Exception as e: logger.error(f"Error _create_access_token: {e}"); return None

#     def _get_user_id_from_token(self, token: Optional[str]) -> int:
#         if not token: return -1
#         try:
#             payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#             user_id_str = payload.get("sub")
#             if user_id_str is None: logger.warning("Token 'sub' claim missing."); return -1
#             return int(user_id_str)
#         except JWTError as e: logger.warning(f"Token decoding error: {e}"); return -1
#         except (ValueError, TypeError): logger.warning("Token 'sub' not valid int."); return -1

#     def _set_user_state(self, user: User):
#         self.is_authenticated = True; self.username = user.username; self.email = user.email
#         self.user_id = user.id; self.account_balance = float(user.account_balance or 0.0)
#         # self.profile_image_url = getattr(user, 'profile_image_url', DEFAULT_AVATAR) or DEFAULT_AVATAR

#     def _clear_auth_state(self):
#         self.auth_token = ""; self.is_authenticated = False; self.username = ""
#         self.email = ""; self.user_id = None; self.account_balance = 0.0; self.profile_image_url = DEFAULT_AVATAR
#         self.password = ""; self.confirm_password = ""

#     def set_username(self, username_in: str): self.username = username_in.strip()
#     def set_email(self, email_in: str): self.email = email_in.strip().lower()
#     def set_password(self, password_in: str): self.password = password_in
#     def set_confirm_password(self, confirm_password_in: str): self.confirm_password = confirm_password_in

#     @rx.event
#     def set_active_tab(self, tab: str):
#         self.active_tab = tab; self.error_message = ""
#         self.email = ""; self.password = ""; self.username = ""; self.confirm_password = ""

#     @rx.event
#     async def login(self):
#         logger.info(f"Login attempt for email: {self.email}")
#         self.error_message = ""
#         self.loading = True
#         if not self.email or not self.password:
#             logger.warning("Login attempt with empty fields")
#             self.error_message = "Por favor complete todos los campos"
#             self.loading = False
#             return

#         db = None
#         try:
#             db = SessionLocal()
#             logger.info(f"Searching for user with email: {self.email}")
#             user = await asyncio.to_thread( # Usar asyncio.to_thread para llamadas síncronas a BD
#                 db.query(User).filter(User.email.ilike(self.email.strip().lower())).first
#             )

#             if not user:
#                 logger.warning(f"No user found with email: {self.email}")
#                 self.error_message = "Email o contraseña incorrectos"
#                 self.loading = False; self.password = ""; return

#             logger.info(f"Verifying password for user: {user.username}")
#             # La verificación de contraseña puede ser intensiva, considera to_thread si es muy lenta
#             if not await asyncio.to_thread(user.verify_password, self.password):
#                 logger.warning(f"Invalid password for user: {user.username}")
#                 self.error_message = "Email o contraseña incorrectos"
#                 self.loading = False; self.password = ""; return

#             logger.info(f"Setting user state for: {user.username}")
#             self._set_user_state(user)

#             logger.info(f"Generating token for user: {user.username}")
#             token = self._create_access_token(user.id)
#             if not token:
#                 logger.error(f"Failed to generate token for user: {user.username}")
#                 self.error_message = "Error al generar token"; self._clear_auth_state(); self.loading = False; return

#             self.auth_token = token; self.last_path = "/dashboard"; self.processed_token = False
#             self.loading = False; logger.info(f"User {self.email} logged in successfully"); self.password = ""
#             return rx.redirect(self.last_path)
#         except Exception as e:
#             logger.error(f"Login error: {e}", exc_info=True)
#             self.error_message = "Error inesperado al iniciar sesión"; self._clear_auth_state()
#             self.loading = False; self.password = ""
#         finally:
#             if db and db.is_active: await asyncio.to_thread(db.close)


#     @rx.event
#     def set_buy_sell_quantity(self, value: str):
#         try:
#             quantity = int(value) if value else 1
#             self.buy_sell_quantity = max(1, quantity)
#         except (ValueError, TypeError): self.buy_sell_quantity = 1

#     # --- MÉTODO CORREGIDO ---
#     @rx.event
#     def open_url_script(self, url_to_open: str): # Espera un string
#         logger.info(f"open_url_script: Recibida URL: '{url_to_open}' (tipo: {type(url_to_open)})")

#         if isinstance(url_to_open, str) and (url_to_open.startswith("http://") or url_to_open.startswith("https://")):
#             try:
#                 js_safe_url_string = json.dumps(url_to_open) # json.dumps necesita que json esté importado
#                 js_command = f"window.open({js_safe_url_string}, '_blank');"
#                 return rx.call_script(js_command)
#             except Exception as e:
#                 logger.error(f"Error al procesar URL con json.dumps: {url_to_open}, Error: {e}")
#                 return # Opcional: rx.window_alert("Error al procesar URL.")
#         else:
#             logger.error(f"URL inválida para script: '{url_to_open}' no es un string http/https URL válido.")
#             # return rx.window_alert("URL de noticia inválida.") # Opcional
#             return
#     # --- FIN MÉTODO CORREGIDO ---

#     @rx.event
#     async def set_period(self, period: str): # Para gráfico de portfolio
#         self.selected_period = period
#         self.portfolio_chart_hover_info = None
#         logger.info(f"Dashboard portfolio period changed to {period}. Triggering chart updates.")
#         # Aquí deberías llamar a la función que actualiza los datos del GRÁFICO DE PORTFOLIO
#         await self._update_portfolio_chart_data() # Asumiendo que esta es la función correcta

#     # Esta función parece un duplicado de set_period. Si es para el mismo gráfico, elimina una.
#     # Si es para otro gráfico con su propio 'selected_period', renombra la variable de estado.
#     # @rx.event
#     # async def set_portfolio_period(self, period: str):
#     #     self.selected_period = period
#     #     self.portfolio_chart_hover_info = None
#     #     logger.info(f"Dashboard portfolio period changed to {self.selected_period}. Triggering chart updates.")
#     #     await self._update_portfolio_chart_data()

#     async def _load_recent_transactions(self):
#         # Implementación de _load_recent_transactions
#         # Ejemplo (debe estar completo en tu archivo real):
#         logger.info(f"AuthState._load_recent_transactions para user_id: {self.user_id}")
#         if not self.user_id:
#             self.recent_transactions = []
#             return
#         # ... (lógica para cargar transacciones)
#         # self.recent_transactions = ...
#         pass # Reemplaza con tu lógica real
#     async def _update_portfolio_chart_data(self):
#         # Implementación de _update_portfolio_chart_data
#         # Esta función es la que debe poblar self.portfolio_chart_data
#         # Ejemplo (debe estar completo en tu archivo real):
#         logger.info(f"AuthState._update_portfolio_chart_data para user_id: {self.user_id}")
#         if not self.user_id:
#             self.portfolio_chart_data = pd.DataFrame(columns=['time', 'total_value'])
#             return
#         # ... (lógica para calcular y asignar a self.portfolio_chart_data)
#         # self.portfolio_chart_data = ... (un DataFrame de Pandas)
#         # Ejemplo de DataFrame vacío si la lógica no está lista:
#         # self.portfolio_chart_data = pd.DataFrame(columns=['time', 'total_value'])
#         pass # Reemplaza con tu lógica real

#     async def load_portfolio(self):
#         # Implementación de load_portfolio
#         # Ejemplo (debe estar completo en tu archivo real):
#         logger.info(f"AuthState.load_portfolio para user_id: {self.user_id}")
#         if not self.user_id:
#             self.portfolio_items = []
#             self.total_portfolio_value = 0.0
#             return
#         # ... (lógica para cargar self.portfolio_items y self.total_portfolio_value)
#         pass # Reemplaza con tu lógica real
#     # --- FIN DE MÉTODOS QUE DEBEN EXISTIR ---

#     @rx.event
#     async def register(self):
#         self.error_message = ""; self.loading = True
#         if not self.username or not self.email or not self.password or not self.confirm_password:
#             self.error_message = "Por favor complete todos los campos"; self.loading = False; return
#         if self.password != self.confirm_password:
#             self.error_message = "Las contraseñas no coinciden"; self.loading = False; self.password = ""; self.confirm_password = ""; return

#         db = None
#         try:
#             db = SessionLocal()
#             existing_user = await asyncio.to_thread(
#                 db.query(User).filter((User.email.ilike(self.email)) | (User.username.ilike(self.username))).first
#             )
#             if existing_user:
#                 self.error_message = "Usuario o email ya están registrados"; self.loading = False; return

#             new_user = User(username=self.username, email=self.email)
#             # set_password puede ser intensivo, considera to_thread si es necesario
#             await asyncio.to_thread(new_user.set_password, self.password)

#             db.add(new_user); await asyncio.to_thread(db.commit)
#             # db.refresh(new_user) # db.refresh debe correr en el mismo thread que la sesión o pasarse el objeto
#             await asyncio.to_thread(db.refresh, new_user) # Opción 1
#             # new_user_id = new_user.id # Opción 2: obtener el ID antes de cerrar el thread

#             logger.info(f"User created: {new_user.username} (ID: {new_user.id})") # ID podría ser None si refresh falla
#             self._set_user_state(new_user) # Asegúrate que new_user tiene el ID

#             token = self._create_access_token(new_user.id) # Necesita new_user.id
#             if not token:
#                 self.error_message = "Error al generar token post-registro."; self._clear_auth_state(); self.loading = False; return

#             self.auth_token = token; self.last_path = "/dashboard"; self.processed_token = False
#             self.loading = False; logger.info(f"User {self.email} registered."); self.password = ""; self.confirm_password = ""
#             return rx.redirect(self.last_path)
#         except Exception as e:
#             logger.error(f"Registration error: {e}", exc_info=True); self.error_message = "Error inesperado al registrar."
#             self._clear_auth_state(); self.loading = False; self.password = ""; self.confirm_password = ""
#         finally:
#             if db and db.is_active: await asyncio.to_thread(db.close)


#     @rx.event
#     async def logout(self):
#         logger.info(f"User {self.username} logging out.")
#         self._clear_auth_state()
#         self.portfolio_items = []; self.total_portfolio_value = 0.0; self.processed_news = []
#         self.recent_transactions = []; self.error_message = ""; self.loading = False
#         self.active_tab = "login"; self.processed_token = False; self.last_path = "/"
#         self.password = ""; self.confirm_password = ""
#         return rx.redirect("/")

#     @rx.event
#     async def on_load(self):
#         current_path = self.router.page.path
#         logger.info(f"on_load: Path='{current_path}', Token? {'Yes' if self.auth_token else 'No'}, Processed? {self.processed_token}, Auth? {self.is_authenticated}")

#         if current_path == "/login" and self.active_tab != "login": self.active_tab = "login"
#         elif current_path == "/registro" and self.active_tab != "register": self.active_tab = "register"

#         # Optimización: si ya estamos autenticados y el token no ha cambiado, y el path es el mismo, no reprocesar.
#         user_id_from_token_check = self._get_user_id_from_token(self.auth_token)
#         if self.processed_token and self.last_path == current_path and \
#            self.is_authenticated == (user_id_from_token_check > 0 and self.user_id == user_id_from_token_check) :
#             logger.info(f"on_load: Already processed for '{current_path}'. Current auth state seems valid.")
#             return

#         self.last_path = current_path
#         db = None # Definir db fuera del try para el finally
#         try:
#             if self.auth_token:
#                 user_id_from_token = self._get_user_id_from_token(self.auth_token)
#                 if user_id_from_token > 0:
#                     db = SessionLocal()
#                     user = await asyncio.to_thread(get_user_by_id, db, user_id_from_token)
#                     if user:
#                         if not self.is_authenticated or self.user_id != user.id: # Si no está autenticado o es otro user
#                             self._set_user_state(user)
#                         logger.info(f"on_load: User {self.email} (ID: {self.user_id}) authenticated via token.")
#                         if current_path in ["/login", "/registro", "/"]:
#                             self.processed_token = True; return rx.redirect("/dashboard")
#                     else:
#                         logger.warning(f"on_load: User ID {user_id_from_token} from token not found in DB. Clearing auth state."); self._clear_auth_state()
#                 else:
#                     logger.info("on_load: Invalid or expired token. Clearing auth state."); self._clear_auth_state()
#             else:
#                 logger.info("on_load: No auth token found. Ensuring logged out state.")
#                 if self.is_authenticated: self._clear_auth_state() # Limpiar si no hay token pero estaba autenticado
#                 self.is_authenticated = False


#             protected_route_prefixes = ["/dashboard", "/profile", "/noticias", "/detalles_accion"] # Añadir más rutas protegidas si es necesario
#             is_on_protected_route = any(current_path.startswith(p) for p in protected_route_prefixes)

#             if not self.is_authenticated and is_on_protected_route:
#                 logger.info(f"on_load: Not authenticated but on protected route '{current_path}'. Redirecting to /login.")
#                 self.processed_token = True # Marcar como procesado para evitar bucles de redirección
#                 return rx.redirect("/login")

#         except Exception as e:
#             logger.error(f"on_load general error: {e}", exc_info=True)
#             self._clear_auth_state() # En caso de error, limpiar para evitar estado inconsistente
#         finally:
#             if db and db.is_active: await asyncio.to_thread(db.close)

#         self.processed_token = True
#         logger.info(f"on_load: Processing finished for '{current_path}'. Authenticated: {self.is_authenticated}")


#     async def _load_current_stock_shares_owned(self):
#         self.current_stock_shares_owned = 0
#         if not self.user_id or not self.viewing_stock_symbol: return

#         db = None
#         try:
#             db = SessionLocal()
#             stock_db_entry = await asyncio.to_thread(
#                 db.query(StockModel).filter(StockModel.symbol == self.viewing_stock_symbol).first
#             )
#             if not stock_db_entry:
#                 logger.info(f"No stock entry found for {self.viewing_stock_symbol} while loading shares owned."); return

#             # Usar transaction_type para calcular acciones, asumiendo quantity siempre positiva
#             transactions = await asyncio.to_thread(
#                 db.query(StockTransaction.transaction_type, StockTransaction.quantity)
#                 .filter(
#                     StockTransaction.user_id == self.user_id,
#                     StockTransaction.stock_id == stock_db_entry.id
#                 ).all
#             )
            
#             buys_quantity = sum(t.quantity for t in transactions if t.transaction_type == TransactionType.COMPRA)
#             sells_quantity = sum(t.quantity for t in transactions if t.transaction_type == TransactionType.VENTA)

#             self.current_stock_shares_owned = int(buys_quantity - sells_quantity)
#             logger.info(f"Shares owned for {self.viewing_stock_symbol} (Stock ID: {stock_db_entry.id}): {self.current_stock_shares_owned} (Buys: {buys_quantity}, Sells: {sells_quantity})")

#         except Exception as e:
#             logger.error(f"Error loading current stock shares for {self.viewing_stock_symbol}: {e}", exc_info=True)
#             self.current_stock_shares_owned = 0
#         finally:
#             if db and db.is_active: await asyncio.to_thread(db.close)


#     @rx.var
#     def balance_date(self) -> str: return datetime.now().strftime("%d %b %Y")
#     @rx.var
#     def formatted_user_balance(self) -> str: return f"${self.account_balance:,.2f}"
#     @rx.var
#     def formatted_user_balance_with_currency(self) -> str: return f"${self.account_balance:,.2f} USD"
#     @rx.var
#     def can_load_more_news(self) -> bool: return bool(self.processed_news) and not self.is_loading_news and self.has_news # Ok
#     @rx.var
#     def featured_stock_page_news(self) -> List[NewsArticle]: return self.processed_news[:3] # Ok

#     @rx.var
#     def portfolio_change_info(self) -> Dict[str, Any]:
#         df = self.portfolio_chart_data
#         # Usar self.total_portfolio_value como el último precio si el df está vacío o es inválido
#         last_price_fallback = self.total_portfolio_value if self.total_portfolio_value is not None else 0.0
#         default = {"last_price": last_price_fallback, "change": 0.0, "percent_change": 0.0, "is_positive": None}

#         if not isinstance(df, pd.DataFrame) or df.empty or 'total_value' not in df.columns: return default
        
#         prices = df['total_value'].dropna()
#         if prices.empty: return default # Si después de dropear NaNs no hay precios

#         last_f = float(prices.iloc[-1])
#         if len(prices) < 2: # No hay suficientes datos para calcular el cambio
#             return {"last_price": last_f, "change": 0.0, "percent_change": 0.0, "is_positive": None}
        
#         try:
#             first_f = float(prices.iloc[0])
#         except IndexError: # Debería ser cubierto por len(prices) < 2, pero por si acaso
#              return {"last_price": last_f, "change": 0.0, "percent_change": 0.0, "is_positive": None}

#         change_f = last_f - first_f
#         percent_f = (change_f / first_f * 100) if first_f != 0 else 0.0
#         is_positive = change_f > 0 if change_f != 0 else (None if change_f == 0 else False) # True, False, o None
#         return {"last_price": last_f, "change": change_f, "percent_change": percent_f, "is_positive": is_positive}

#     @rx.var
#     def is_portfolio_value_change_positive(self) -> Optional[bool]: return self.portfolio_change_info.get("is_positive") # Usar .get para seguridad
#     @rx.var
#     def formatted_portfolio_value_percent_change(self) -> str: return f"{abs(self.portfolio_change_info.get('percent_change', 0.0)):.2f}%"
#     @rx.var
#     def formatted_portfolio_value_change_abs(self) -> str: return f"{self.portfolio_change_info.get('change', 0.0):+.2f}"

#     @rx.var
#     def portfolio_chart_color(self) -> str:
#         is_positive = self.is_portfolio_value_change_positive
#         if is_positive is True: return "var(--green-9)"
#         if is_positive is False: return "var(--red-9)"
#         return "var(--gray-9)" # Color neutro

#     @rx.var
#     def portfolio_chart_area_color(self) -> str:
#         is_positive = self.is_portfolio_value_change_positive
#         if is_positive is True: return "rgba(34,197,94,0.2)"
#         if is_positive is False: return "rgba(239,68,68,0.2)"
#         return "rgba(107,114,128,0.2)" # Neutro

#     @rx.var
#     def portfolio_display_value(self) -> float:
#         hover_info = self.portfolio_chart_hover_info
#         if hover_info and "y" in hover_info:
#             hover_y_data = hover_info["y"]
#             y_to_convert = hover_y_data[0] if isinstance(hover_y_data, list) and hover_y_data else hover_y_data
#             if y_to_convert is not None:
#                 try: return float(y_to_convert)
#                 except (ValueError, TypeError): pass # Ignorar si no se puede convertir
#         # Fallback al último precio conocido si no hay hover o el hover es inválido
#         return float(self.portfolio_change_info.get("last_price", self.total_portfolio_value if self.total_portfolio_value is not None else 0.0))


#     @rx.var
#     def portfolio_display_time(self) -> str:
#         hover_info = self.portfolio_chart_hover_info
#         if hover_info and "x" in hover_info:
#             x_data = hover_info["x"]; x_value = x_data[0] if isinstance(x_data, list) and x_data else x_data
#             if x_value is not None:
#                 try:
#                     # Asegurarse que es un timestamp o string convertible antes de formatear
#                     if isinstance(x_value, (str, int, float, datetime, pd.Timestamp)):
#                         return pd.to_datetime(x_value).strftime('%d %b %Y')
#                     return str(x_value) # Fallback si no es un tipo conocido
#                 except Exception as e: logger.warning(f"Error al formatear tiempo de portfolio: {e}"); return str(x_value) if x_value else "--"
#         # Si no hay hover, mostrar el período seleccionado
#         period_map_display = {"1D":"Últimas 24h","5D":"Últimos 5d","1M":"Último Mes","6M":"Últimos 6m","YTD":"Este Año","1Y":"Último Año","5Y":"Últimos 5a","MAX":"Máximo"}
#         return period_map_display.get(self.selected_period.upper(), f"Período: {self.selected_period}")


#     @rx.var
#     def main_portfolio_chart_figure(self) -> go.Figure:
#         # Figuras para estados de carga y error
#         loading_fig=go.Figure().update_layout(height=300,annotations=[dict(text="Calculando gráfico del portfolio...",showarrow=False)],paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis=dict(visible=False),yaxis=dict(visible=False))
#         error_fig=go.Figure().update_layout(height=300,annotations=[dict(text="Sin datos para mostrar en el gráfico del portfolio.",showarrow=False)],paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis=dict(visible=False),yaxis=dict(visible=False))

#         if self.is_loading_portfolio_chart: return loading_fig

#         df = self.portfolio_chart_data
#         if not isinstance(df, pd.DataFrame) or df.empty or 'total_value' not in df.columns or 'time' not in df.columns:
#             logger.warning("Gráfico de portfolio: DataFrame inválido o vacío.")
#             return error_fig

#         try:
#             df_chart = df.copy()
#             df_chart['time'] = pd.to_datetime(df_chart['time'], errors='coerce', utc=True)
#             df_chart['total_value'] = pd.to_numeric(df_chart['total_value'], errors='coerce')
#             df_chart = df_chart.dropna(subset=['time', 'total_value']).sort_values(by='time')

#             if df_chart.empty or len(df_chart) < 2 : # Se necesitan al menos 2 puntos para una línea
#                 logger.warning(f"Gráfico de portfolio: DataFrame vacío después de procesar o menos de 2 puntos. Puntos: {len(df_chart)}")
#                 return error_fig

#             fig = go.Figure()
#             # Area fill trace (sin hover)
#             fig.add_trace(go.Scatter(x=df_chart['time'], y=df_chart['total_value'], mode='lines',
#                                      line=dict(width=0), # Sin línea visible, solo para el área
#                                      fill='tozeroy', fillcolor=self.portfolio_chart_area_color,
#                                      hoverinfo='skip')) # Desactivar hover para esta traza de área
#             # Line trace (con hover)
#             fig.add_trace(go.Scatter(x=df_chart['time'], y=df_chart['total_value'], mode='lines',
#                                      line=dict(color=self.portfolio_chart_color, width=2.5, shape='spline'),
#                                      name='Valor Total',
#                                      hovertemplate='<b>Valor:</b> $%{y:,.2f}<br><b>Fecha:</b> %{x|%d %b %Y, %H:%M}<extra></extra>'))

#             min_v, max_v = df_chart['total_value'].min(), df_chart['total_value'].max()
#             padding = (max_v - min_v) * 0.1 if (max_v != min_v) else abs(min_v) * 0.1 or 1000 # Padding mínimo de 1000 si todo es 0 o igual
#             range_min = min_v - padding
#             range_max = max_v + padding

#             fig.update_layout(
#                 height=300, margin=dict(l=50,r=10,t=10,b=30), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
#                 xaxis=dict(showgrid=False, zeroline=False, tickmode='auto', nticks=6, showline=True, linewidth=1, linecolor='var(--gray-a6)', tickangle=-30, tickfont=dict(color="var(--gray-11)")),
#                 yaxis=dict(title=None, showgrid=True, gridcolor='var(--gray-a4)', zeroline=False, showline=False, side='left', tickformat="$,.0f", range=[range_min, range_max], tickfont=dict(color="var(--gray-11)")),
#                 hovermode='x unified', showlegend=False
#             )
#             return fig
#         except Exception as e:
#             logger.error(f"Error al generar gráfico de portfolio: {e}", exc_info=True)
#             return error_fig

#     async def _load_recent_transactions(self):
#         logger.info(f"Loading Recent Transactions for user_id: {self.user_id}")
#         if not self.user_id:
#             self.recent_transactions = []
#             return

#         db = None # Muy importante definirla fuera del try para el finally
#         new_trans_list = []
#         try:
#             db = SessionLocal()
#             # get_transaction_history_with_profit_loss es síncrona
#             raw_transactions_data = await asyncio.to_thread(
#                 get_transaction_history_with_profit_loss, db, self.user_id, limit=10
#             )

#             for t_data_dict in raw_transactions_data:
#                 # Convertir timestamp ISO string a formato dd/mm/yy HH:MM
#                 dt_obj = datetime.fromisoformat(t_data_dict["timestamp"])
#                 formatted_timestamp = dt_obj.strftime("%d/%m/%y %H:%M")

#                 trans_type = t_data_dict["type"].capitalize() # 'compra' -> 'Compra'
#                 quantity = int(t_data_dict["quantity"]) # Ya debería ser positivo
#                 symbol = t_data_dict["stock_symbol"]
#                 price = float(t_data_dict["price"])
#                 # total = quantity * price # No necesario para TransactionDisplayItem

#                 new_trans_list.append(TransactionDisplayItem(
#                     timestamp=formatted_timestamp,
#                     symbol=symbol,
#                     quantity=quantity, # Cantidad absoluta
#                     price=price,
#                     type=trans_type # 'Compra' o 'Venta'
#                 ))
#             self.recent_transactions = new_trans_list
#             logger.info(f"Loaded {len(self.recent_transactions)} recent transactions using CRUD function.")
#         except Exception as e:
#             logger.error(f"Error loading recent transactions via CRUD: {e}", exc_info=True)
#             self.recent_transactions = [] # Fallback
#         finally:
#             if db and db.is_active: # Comprobar que db se asignó
#                 await asyncio.to_thread(db.close)
#     @rx.var
#     def stock_detail_chart_change_info(self)->Dict[str,Any]:
#         df = self.current_stock_history
#         current_price_from_info = self.current_stock_info.get("currentPrice", self.current_stock_info.get("regularMarketPrice", 0.0))
#         try: # Asegurar que el precio de fallback sea float
#             last_price_fallback = float(current_price_from_info)
#         except (ValueError, TypeError):
#             last_price_fallback = 0.0

#         default_info = {"last_price": last_price_fallback, "change": 0.0, "percent_change": 0.0, "is_positive": None, "first_price_time": None, "last_price_time": None}

#         if not isinstance(df, pd.DataFrame) or df.empty or 'price' not in df.columns or 'time' not in df.columns:
#             return default_info
        
#         prices_series = df['price'].dropna()
#         times_series = df.loc[prices_series.index, 'time'].dropna() # Alinea times con precios no nulos

#         # Re-indexar prices_series para asegurar que coincide con times_series después de dropear NaNs de tiempos
#         prices_series = prices_series.loc[times_series.index]

#         if prices_series.empty or len(prices_series) < 1: return default_info

#         last_f = float(prices_series.iloc[-1])
#         last_t = pd.to_datetime(times_series.iloc[-1])
#         # Actualizar default_info con los últimos valores conocidos del DF
#         default_info["last_price"] = last_f
#         default_info["last_price_time"] = last_t

#         if len(prices_series) < 2: return default_info # No hay suficientes datos para calcular cambio

#         first_f = float(prices_series.iloc[0])
#         first_t = pd.to_datetime(times_series.iloc[0])
#         change_f = last_f - first_f
#         percent_f = (change_f / first_f * 100) if first_f != 0 else 0.0
#         is_positive = change_f > 0 if change_f != 0 else (None if change_f == 0 else False)

#         return {"last_price": last_f, "change": change_f, "percent_change": percent_f, "is_positive": is_positive, "first_price_time": first_t, "last_price_time": last_t}


#     @rx.var
#     def stock_detail_display_price(self)->str:
#         hover_info = self.stock_detail_chart_hover_info
#         change_info = self.stock_detail_chart_change_info # Llama al @rx.var
        
#         price_to_display = change_info.get("last_price", 0.0)
#         currency_symbol = self.current_stock_info.get("currencySymbol", "$") # Obtener de current_stock_info

#         if hover_info and "y" in hover_info:
#             hover_y_data = hover_info["y"]
#             y_to_convert = hover_y_data[0] if isinstance(hover_y_data, list) and hover_y_data else hover_y_data
#             if y_to_convert is not None:
#                 try: price_to_display = float(y_to_convert)
#                 except (ValueError, TypeError): pass # Mantener el precio de change_info si falla la conversión

#         return f"{currency_symbol}{price_to_display:,.2f}"


#     @rx.var
#     def is_current_stock_info_empty(self)->bool:
#         return not self.current_stock_info or "error" in self.current_stock_info or not self.current_stock_info.get("symbol")

#     @rx.var
#     def current_stock_metrics_list(self)->List[Tuple[str,str]]: # Ok
#         return list(self.current_stock_metrics.items()) if self.current_stock_metrics else []


#     @rx.var
#     def stock_detail_display_time_or_change(self)->str:
#         hover_info = self.stock_detail_chart_hover_info
#         change_info = self.stock_detail_chart_change_info # Llama al @rx.var

#         if hover_info and "x" in hover_info: # Si hay hover, mostrar la fecha/hora del hover
#             x_data = hover_info["x"]; x_value = x_data[0] if isinstance(x_data, list) and x_data else x_data
#             if x_value is not None:
#                 try:
#                     dt_obj = pd.to_datetime(x_value)
#                     # Lógica para determinar formato de fecha/hora basado en el período
#                     last_t = change_info.get("last_price_time")
#                     first_t = change_info.get("first_price_time")
#                     show_time = self.current_stock_selected_period.upper() in ["1D", "5D"]
#                     if not show_time and last_t and first_t and isinstance(last_t, pd.Timestamp) and isinstance(first_t, pd.Timestamp):
#                         if (last_t - first_t).days < 2: # Si el rango total es menos de 2 días
#                             show_time = True
#                     return dt_obj.strftime('%d %b, %H:%M') if show_time else dt_obj.strftime('%d %b %Y')
#                 except Exception as e:
#                     logger.warning(f"Error al formatear tiempo de detalle de stock: {e}")
#                     return str(x_value) if x_value else "--"
        
#         # Si no hay hover, mostrar el cambio del período
#         change_val = change_info.get("change", 0.0)
#         percent_change_val = change_info.get("percent_change", 0.0)
#         currency_symbol = self.current_stock_info.get("currencySymbol", "$") # Obtener de current_stock_info
        
#         period_map_display = {"1D":"Hoy","5D":"5 Días","1M":"1 Mes","6M":"6 Meses","YTD":"Este Año","1A":"1 Año","1Y":"1 Año","5A":"5 Anys","5Y":"5 Años","MAX":"Máximo"}
#         period_display_name = period_map_display.get(self.current_stock_selected_period.upper(), self.current_stock_selected_period) # Fallback al propio período

#         return f"{currency_symbol}{change_val:+.2f} ({percent_change_val:+.2f}%) {period_display_name}"

#     @rx.var
#     def stock_detail_change_color(self)->str: # Color para el texto de cambio
#         # Si hay hover, el color del texto de "cambio" (que ahora muestra fecha/hora) debe ser neutro
#         if self.stock_detail_chart_hover_info and "x" in self.stock_detail_chart_hover_info:
#             return "var(--gray-11)" # Color de texto normal

#         is_positive = self.stock_detail_chart_change_info.get("is_positive")
#         if is_positive is True: return "var(--green-10)"
#         if is_positive is False: return "var(--red-10)"
#         return "var(--gray-11)" # Neutro

#     @rx.var
#     def current_stock_change_color(self) -> str: # Color para el cambio diario de la acción (no del gráfico)
#         # Este color debería basarse en el cambio diario de current_stock_info, no del gráfico de período.
#         # Asumiendo que 'change' en current_stock_info es el cambio numérico.
#         change = self.current_stock_info.get('change', 0.0) # Asegúrate que esto es el cambio numérico
#         if not isinstance(change, (int, float)): # Si no es un número, no podemos determinar color
#             change = 0.0
        
#         if change > 0: return "var(--green-10)" # Verde si es positivo
#         elif change < 0: return "var(--red-10)" # Rojo si es negativo
#         return "var(--gray-11)" # Gris si es cero o no numérico


#     @rx.var
#     def stock_detail_chart_figure(self) -> go.Figure:
#         df = self.current_stock_history
#         loading_fig = go.Figure().update_layout(height=350, annotations=[dict(text="Cargando gráfico...", showarrow=False)], paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))
#         error_fig = go.Figure().update_layout(height=350, annotations=[dict(text="Datos de gráfico no disponibles.", showarrow=False)], paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))

#         if self.is_loading_current_stock_details and (not isinstance(df, pd.DataFrame) or df.empty):
#             return loading_fig

#         if not isinstance(df, pd.DataFrame) or df.empty or not all(c in df.columns for c in ['time', 'price']):
#             logger.warning(f"Stock detail chart: DataFrame inválido para {self.viewing_stock_symbol}. Columnas: {df.columns if isinstance(df, pd.DataFrame) else 'No es DF'}")
#             return error_fig

#         # Procesamiento robusto de datos para el gráfico
#         try:
#             prices_series = df["price"].dropna()
#             if prices_series.empty:
#                 logger.warning(f"Stock detail chart: No hay precios después de dropna para {self.viewing_stock_symbol}.")
#                 return error_fig

#             times_series = pd.to_datetime(df.loc[prices_series.index, "time"], utc=True, errors='coerce').dropna()
            
#             # Re-alinear prices_series con times_series que no son NaT
#             valid_indices = times_series.index
#             final_prices = prices_series.loc[valid_indices]
#             final_times = times_series # Ya filtrado de NaT

#             if final_prices.empty or len(final_prices) < 1: # Necesitamos al menos un punto
#                 logger.warning(f"Stock detail chart: Series vacías después de alineación para {self.viewing_stock_symbol}.")
#                 return error_fig
            
#             fig = go.Figure()
#             line_color = "var(--gray-9)"; fill_color_base = '128,128,128' # Default neutro

#             if len(final_prices) >= 2: # Necesitamos al menos dos puntos para determinar tendencia por color
#                 if final_prices.iloc[-1] > final_prices.iloc[0]: line_color = "var(--green-9)"; fill_color_base = '34,197,94'
#                 elif final_prices.iloc[-1] < final_prices.iloc[0]: line_color = "var(--red-9)"; fill_color_base = '239,68,68'
            
#             fill_color_rgba = f"rgba({fill_color_base},0.1)"
#             fig.add_trace(go.Scatter(x=final_times, y=final_prices, mode="lines", line=dict(color=line_color, width=2, shape='spline'), fill='tozeroy', fillcolor=fill_color_rgba, hovertemplate='<b>Precio:</b> $%{y:,.2f}<br><b>Fecha:</b> %{x|%d %b %Y, %H:%M}<extra></extra>'))
            
#             # Ajuste de rango del eje Y para mejor visualización
#             min_p, max_p = final_prices.min(), final_prices.max()
#             y_padding = (max_p - min_p) * 0.1 if (max_p != min_p) else abs(min_p) * 0.1 or 1.0 # Padding mínimo de 1 si todo es 0 o igual
#             y_range = [min_p - y_padding, max_p + y_padding]

#             fig.update_layout(
#                 height=350, margin=dict(l=50, r=10, t=10, b=30), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
#                 xaxis=dict(showgrid=False, zeroline=False, tickmode="auto", nticks=6, showline=True, linewidth=1, linecolor="var(--gray-a6)", tickangle=-30, tickfont=dict(color="var(--gray-11)")),
#                 yaxis=dict(title=None, showgrid=True, gridcolor="var(--gray-a4)", zeroline=False, showline=False, side="left", tickformat="$,.2f", tickfont=dict(color="var(--gray-11)"), range=y_range),
#                 hovermode="x unified", showlegend=False
#             )
#             return fig

#         except Exception as e:
#             logger.error(f"Excepción al generar gráfico de detalle de stock para {self.viewing_stock_symbol}: {e}", exc_info=True)
#             return error_fig


#     # --- Event Handlers de UI ---
#     def portfolio_chart_handle_hover(self, event_data: List): # Ok
#         new_hover_info = None; points = None
#         if event_data and isinstance(event_data, list) and event_data[0] and isinstance(event_data[0], dict):
#             points = event_data[0].get('points')
#         if points and isinstance(points, list) and points[0] and isinstance(points[0], dict):
#             new_hover_info = points[0]
#         if self.portfolio_chart_hover_info != new_hover_info: self.portfolio_chart_hover_info = new_hover_info

#     def portfolio_chart_handle_unhover(self, _): # Ok
#         if self.portfolio_chart_hover_info is not None: self.portfolio_chart_hover_info = None

#     def portfolio_toggle_change_display(self): # Ok
#         self.portfolio_show_absolute_change = not self.portfolio_show_absolute_change

#     def stock_detail_chart_handle_hover(self, event_data: List): # Ok
#         new_hover_info = None
#         if event_data and isinstance(event_data, list) and event_data[0] and isinstance(event_data[0], dict):
#             points = event_data[0].get('points')
#             if points and isinstance(points, list) and points[0] and isinstance(points[0], dict):
#                 new_hover_info = points[0]
#         if self.stock_detail_chart_hover_info != new_hover_info: self.stock_detail_chart_hover_info = new_hover_info

#     def stock_detail_chart_handle_unhover(self, _): # Ok
#         if self.stock_detail_chart_hover_info is not None: self.stock_detail_chart_hover_info = None

#     # selected_style no parece usarse en el código provisto, pero lo dejo si es parte de tu lógica de tema
#     # def change_style(self, style: str): self.selected_style = style; logger.info(f"Theme style to {style}")


#     # --- Métodos de Noticias ---
#     def _create_fallback_news(self): # Ok
#         logger.warning("Creating fallback news item.")
#         self.processed_news = [NewsArticle(title="Error al cargar noticias", url="#", publisher="Sistema", date=datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M"), summary="No se pudieron obtener las noticias.", image="")]
#         self.has_news = True # Para que se muestre el fallback

#     @rx.event
#     async def get_news(self, new_query: Optional[str] = None): # Ok
#         if self.is_loading_news: return
#         self.is_loading_news = True
#         if new_query is not None: # Si se provee una nueva query, resetear paginación y noticias
#             self.SEARCH_QUERY = new_query.strip() if new_query.strip() else DEFAULT_SEARCH_QUERY
#             self.news_page = 1; self.processed_news = []; self.has_news = False # Resetear
        
#         logger.info(f"Fetching news: '{self.SEARCH_QUERY}', page: {self.news_page}")
#         try:
#             params = {"q": self.SEARCH_QUERY, "token": GNEWS_API_KEY, "lang": "es", "country": "any", "max": self.max_articles, "sortby": "publishedAt", "page": self.news_page}
#             response = await asyncio.to_thread(requests.get, GNEWS_API_URL, params=params, timeout=10) # Añadir timeout
#             response.raise_for_status(); data = response.json(); articles = data.get("articles", [])

#             if not articles:
#                 if self.news_page == 1: self._create_fallback_news() # Si es la primera página y no hay nada, mostrar fallback
#                 else: self.has_news = False # Si no es la primera página, simplemente no hay más noticias
#                 self.is_loading_news = False; return

#             page_articles = []
#             for article in articles:
#                 try:
#                     # Usar datetime.fromisoformat si las fechas de GNews son ISO 8601 completas con Z
#                     dt_obj = datetime.fromisoformat(article.get("publishedAt","").replace("Z", "+00:00")) if article.get("publishedAt") else datetime.now(timezone.utc)
#                     # Convertir a la zona horaria local del servidor si es necesario (o mantener UTC)
#                     # dt_obj = dt_obj.astimezone(None) # Zona horaria local del sistema
#                     page_articles.append(NewsArticle(
#                         title=article.get("title","S/T"),
#                         url=article.get("url","#"),
#                         publisher=article.get("source",{}).get("name","N/A"),
#                         date=dt_obj.strftime("%d %b %Y, %H:%M"), # Quitar %Z si no es relevante o causa problemas
#                         summary=article.get("description","N/A."),
#                         image=article.get("image","") # Usar imagen por defecto si está vacía
#                     ))
#                 except Exception as e_art: logger.error(f"Error processing article: {article.get('title')}, Error: {e_art}", exc_info=True)

#             if self.news_page == 1: self.processed_news = page_articles
#             else: self.processed_news.extend(page_articles)
            
#             self.has_news = bool(self.processed_news) # Hay noticias si la lista procesada no está vacía
#             if articles and len(articles) == self.max_articles : # Si GNews devuelve el máximo, es probable que haya más
#                  self.news_page += 1
#             else: # Si devuelve menos del máximo, o nada, asumimos que no hay más.
#                  self.has_news = bool(self.processed_news) # Mantener has_news si ya teníamos algunas
#                  # No incrementar news_page si no hay más artículos que cargar.

#         except requests.exceptions.RequestException as e_req: # Manejar errores de red específicos
#             logger.error(f"Network error fetching news: {e_req}", exc_info=True)
#             if not self.processed_news: self._create_fallback_news() # Mostrar fallback si no hay nada cargado
#         except Exception as e: # Otros errores
#             logger.error(f"General error fetching news: {e}", exc_info=True)
#             if not self.processed_news: self._create_fallback_news()
#         finally:
#             self.is_loading_news = False

#     @rx.event
#     async def load_more_news(self): # Ok
#         # Permitir cargar más solo si 'has_news' es True (lo que implica que podría haber más)
#         # y no estamos ya cargando.
#         # La lógica de 'has_news' en get_news determina si hay más páginas.
#         # Esta comprobación aquí es más para la UI (ej. deshabilitar botón "cargar más")
#         # if not self.is_loading_news and self.has_news: # 'has_news' podría ser engañoso aquí
#         if not self.is_loading_news: # Simplificar: intentar cargar si no se está cargando
#             await self.get_news()

#     @rx.event
#     async def set_news_search_query_and_fetch(self, query: str): await self.get_news(new_query=query) # Ok


#     # --- Métodos para Búsqueda de Acciones (Global en AuthState) ---
#     # search_term, search_result, is_searching, search_error ya están definidos como variables de estado.
#     def set_search_term(self, term: str): # Ok
#         self.search_term = term
#         self.error_message = "" # Usar self.error_message para errores generales, o definir self.search_error

#     @rx.event
#     async def search_stock_global(self):
#         if not self.search_term:
#             self.error_message = "Introduce un símbolo o nombre de empresa para buscar." # Usar error_message
#             # self.search_result = SearchResultItem() # Limpiar/resetear resultado
#             return
        
#         self.is_searching = True; self.error_message = ""; # self.search_result = SearchResultItem()
#         query_upper = self.search_term.strip().upper()
#         symbol_to_fetch = COMPANY_MAP.get(query_upper, query_upper) # Usar el mapa
#         logger.info(f"AuthState global search: Term '{self.search_term}', effective ticker '{symbol_to_fetch}'")

#         try:
#             ticker_obj = await asyncio.to_thread(yf.Ticker, symbol_to_fetch)
#             # Acceder a 'info' puede ser una operación de red/bloqueante
#             info = await asyncio.to_thread(lambda: ticker_obj.info) # Usar getattr es más para cuando el atributo es dinámico
            
#             # Comprobación más robusta de si 'info' es útil
#             if not info or ("price" not in info and "currentPrice" not in info and "regularMarketPrice" not in info and "previousClose" not in info):
#                 self.error_message = f"No se encontró información de mercado para '{self.search_term}' (Símbolo: {symbol_to_fetch})."
#                 logger.warning(f"No market data in yfinance info for {symbol_to_fetch}. Info keys: {list(info.keys()) if info else 'No info'}")
#                 self.search_result = SearchResultItem(Name=f"No encontrado: {symbol_to_fetch}") # Indicar no encontrado
#                 return # No continuar si no hay datos de precio

#             price_val = info.get("currentPrice", info.get("regularMarketPrice", info.get("previousClose")))
#             price_str = "N/A"
#             if price_val is not None:
#                 try:
#                     price_str = f"{info.get('currencySymbol','$')}{float(price_val):,.2f}"
#                 except (ValueError, TypeError):
#                     logger.warning(f"No se pudo formatear el precio '{price_val}' para {symbol_to_fetch}")

#             # Logo: yfinance info.logo_url. Para local, buscar en assets/SYMBOL.png
#             logo_url = info.get("logo_url", f"/{symbol_to_fetch.upper()}.png") # Fallback a logo local si yfinance no lo da
#             # (Asegúrate que tienes esos logos en /assets/ o una lógica para manejarlos)

#             self.search_result = SearchResultItem(
#                 Symbol=info.get("symbol", symbol_to_fetch), # Usar el símbolo real de yfinance si es diferente
#                 Name=info.get("longName", info.get("shortName", symbol_to_fetch)),
#                 Current_Price=price_str,
#                 Logo=logo_url
#             )

#         except Exception as e:
#             logger.error(f"Error en search_stock_global para {symbol_to_fetch}: {e}", exc_info=True)
#             self.error_message = f"Error al buscar '{self.search_term}'. Intenta con el símbolo ticker."
#             self.search_result = SearchResultItem(Name=f"Error buscando {self.search_term}")
#         finally:
#             self.is_searching = False

#     @rx.event
#     def go_to_stock_detail_global(self, symbol: str): # Ok
#         if symbol and symbol != "No encontrado" and not symbol.startswith("Error"):
#             return rx.redirect(f"/detalles_accion/{symbol.upper().strip()}") # Añadir strip
#         return rx.window_alert("No se puede navegar a los detalles para este resultado.")


#     # --- Métodos para Detalles de Acción ---
#     @rx.event
#     async def set_current_stock_period(self, period: str): # Ok
#         self.current_stock_selected_period = period
#         self.stock_detail_chart_hover_info = None # Resetear hover info al cambiar período
#         logger.info(f"Período de detalle de acción cambiado a {period}. Actualizando gráfico para {self.viewing_stock_symbol}.")
#         await self._update_current_stock_chart_data_internal() # Llama a la función que realmente carga los datos


#     # _fetch_stock_history_data (de DB local) ya está, no se usa directamente para el gráfico de detalle si _update_current_stock_chart_data_internal usa yfinance
#     # _fetch_stock_history_data_detail (de yfinance) ya está, es usado por _update_current_stock_chart_data_internal
#     # _update_current_stock_chart_data_internal ya está, usa _fetch_stock_history_data_detail


#     @rx.event
#     async def load_stock_page_data(self, symbol: str):
#         """Carga datos para la página de detalles de la acción: info básica de yfinance y acciones del usuario."""
#         self.viewing_stock_symbol = symbol.upper()
#         self.is_loading_current_stock_details = True # Indicar inicio de carga
#         self.transaction_message = ""
#         self.current_stock_info = {} # Resetear para nueva acción
#         self.current_stock_metrics = {} # Resetear
#         # self.current_stock_history se actualiza por _update_current_stock_chart_data_internal

#         logger.info(f"load_stock_page_data: Cargando info para {self.viewing_stock_symbol}")
#         try:
#             # 1. Obtener info de yfinance (más actualizada para precio, etc.)
#             ticker = await asyncio.to_thread(yf.Ticker, self.viewing_stock_symbol)
#             info = await asyncio.to_thread(getattr, ticker, 'info') # Usar getattr para seguridad

#             if not info or not info.get("symbol"): # Si yfinance no devuelve nada útil
#                 logger.warning(f"No se pudo obtener info de yfinance para {self.viewing_stock_symbol}. Intentando DB local.")
#                 # Fallback a la base de datos local para nombre y sector si yfinance falla
#                 db_fallback = SessionLocal()
#                 try:
#                     stock_db = await asyncio.to_thread(db_fallback.query(StockModel).filter(StockModel.symbol == self.viewing_stock_symbol).first)
#                     if stock_db:
#                         self.current_stock_info = {
#                             "symbol": stock_db.symbol,
#                             "name": stock_db.name,
#                             "currentPrice": float(stock_db.current_price), # Usar el precio de la BD como fallback
#                             "sector": stock_db.sector.sector_name if stock_db.sector else "N/A",
#                             "currencySymbol": "$", # Asumir USD o definirlo
#                             # Otros campos que quieras mostrar de tu BD
#                         }
#                         logger.info(f"Info básica para {self.viewing_stock_symbol} cargada de DB local como fallback.")
#                     else: # No encontrado ni en yfinance ni en BD
#                         self.current_stock_info = {"error": f"Acción {self.viewing_stock_symbol} no encontrada."}
#                         self.is_loading_current_stock_details = False; return
#                 finally:
#                     if db_fallback: await asyncio.to_thread(db_fallback.close)
#             else: # Si yfinance sí devuelve información
#                 self.current_stock_info = {
#                     "symbol": info.get("symbol", self.viewing_stock_symbol), # Símbolo real de yf
#                     "name": info.get("longName", info.get("shortName", "Nombre no disponible")),
#                     "currentPrice": float(info.get("currentPrice", info.get("regularMarketPrice", 0.0))),
#                     "previousClose": float(info.get("previousClose", 0.0)),
#                     "open": float(info.get("open", 0.0)),
#                     "dayHigh": float(info.get("dayHigh", 0.0)),
#                     "dayLow": float(info.get("dayLow", 0.0)),
#                     "volume": info.get("volume"),
#                     "marketCap": info.get("marketCap"),
#                     "fiftyTwoWeekHigh": float(info.get("fiftyTwoWeekHigh", 0.0)),
#                     "fiftyTwoWeekLow": float(info.get("fiftyTwoWeekLow", 0.0)),
#                     "sector": info.get("sector", "N/A"),
#                     "industry": info.get("industry", "N/A"),
#                     "currencySymbol": info.get("currencySymbol", "$"), # Símbolo de moneda
#                     "logo_url": info.get("logo_url"), # URL del logo de yfinance
#                     # Otros campos relevantes para 'metrics'
#                 }
#                 # Calcular cambio simple si es posible
#                 if self.current_stock_info.get("currentPrice") and self.current_stock_info.get("previousClose"):
#                     cp = self.current_stock_info["currentPrice"]
#                     pc = self.current_stock_info["previousClose"]
#                     change_val = cp - pc
#                     change_percent_val = (change_val / pc * 100) if pc != 0 else 0.0
#                     self.current_stock_info["change"] = change_val # Cambio numérico
#                     self.current_stock_info["changePercent"] = change_percent_val # Cambio porcentual

#                 logger.info(f"Info de yfinance cargada para {self.viewing_stock_symbol}: {self.current_stock_info.get('name')}")
                
#                 # Poblar self.current_stock_metrics (ejemplo)
#                 self.current_stock_metrics = {
#                     "Capitalización Bursátil": f"{self.current_stock_info.get('currencySymbol','')}{self.current_stock_info.get('marketCap', 0):,}" if self.current_stock_info.get('marketCap') else "N/A",
#                     "Volumen": f"{self.current_stock_info.get('volume', 0):,}" if self.current_stock_info.get('volume') else "N/A",
#                     "Apertura": f"{self.current_stock_info.get('currencySymbol','')}{self.current_stock_info.get('open', 0.0):.2f}",
#                     "Máx. Diario": f"{self.current_stock_info.get('currencySymbol','')}{self.current_stock_info.get('dayHigh', 0.0):.2f}",
#                     "Mín. Diario": f"{self.current_stock_info.get('currencySymbol','')}{self.current_stock_info.get('dayLow', 0.0):.2f}",
#                     "Máx. 52 Semanas": f"{self.current_stock_info.get('currencySymbol','')}{self.current_stock_info.get('fiftyTwoWeekHigh', 0.0):.2f}",
#                     "Mín. 52 Semanas": f"{self.current_stock_info.get('currencySymbol','')}{self.current_stock_info.get('fiftyTwoWeekLow', 0.0):.2f}",
#                 }


#             # 2. Cargar acciones poseídas (si el usuario está autenticado)
#             if self.is_authenticated and self.user_id:
#                 await self._load_current_stock_shares_owned()

#             # Los datos del gráfico (current_stock_history) se cargarán explícitamente
#             # por _update_current_stock_chart_data_internal, llamado desde stock_detail_page_on_mount
#             # o set_current_stock_period. No es necesario aquí.

#         except Exception as e:
#             logger.error(f"Error en load_stock_page_data para {self.viewing_stock_symbol}: {e}", exc_info=True)
#             self.current_stock_info = {"error": f"Error al cargar datos para {self.viewing_stock_symbol}."}
#             self.current_stock_metrics = {} # Limpiar métricas en error
#         finally:
#             self.is_loading_current_stock_details = False # Indicar fin de carga de info básica
#             logger.info(f"load_stock_page_data finalizado para {self.viewing_stock_symbol}. Cargando detalles: {self.is_loading_current_stock_details}")


#     @rx.event
#     async def buy_stock(self):
#         if not self.is_authenticated or not self.user_id or not self.viewing_stock_symbol:
#             self.transaction_message = "Error: Usuario no autenticado o acción no seleccionada."
#             return
#         if self.buy_sell_quantity <= 0:
#             self.transaction_message = "Error: La cantidad debe ser mayor que cero."
#             return

#         self.loading = True # Indicar operación en curso
#         self.transaction_message = ""
#         db = None
#         try:
#             db = SessionLocal()
#             user = await asyncio.to_thread(db.query(User).filter(User.id == self.user_id).first)
#             stock = await asyncio.to_thread(db.query(StockModel).filter(StockModel.symbol == self.viewing_stock_symbol).first)

#             if not user or not stock:
#                 self.transaction_message = "Error: Usuario o acción no encontrados en la base de datos."
#                 self.loading = False; return

#             # Usar el precio actual de current_stock_info (que viene de yfinance y es más fresco)
#             price_to_use = self.current_stock_info.get("currentPrice")
#             if price_to_use is None: # Fallback al precio en BD si no hay de yf
#                 price_to_use = float(stock.current_price)
#                 logger.warning(f"Usando precio de BD para {stock.symbol} en compra: {price_to_use}")
#             else:
#                 price_to_use = float(price_to_use)


#             total_cost = Decimal(str(price_to_use)) * Decimal(self.buy_sell_quantity)

#             if user.account_balance < total_cost:
#                 self.transaction_message = f"Error: Saldo insuficiente ({user.account_balance:,.2f} disponible, {total_cost:,.2f} necesario)."
#                 self.loading = False; return
            
#             # Actualizar saldo del usuario
#             user.account_balance -= total_cost
            
#             # Crear la transacción de COMPRA (usando el controlador)
#             # El controlador create_transaction ya hace db.add y db.commit
#             # ¡ASEGÚRATE QUE TU CRUD 'create_transaction' NO HACE COMMIT SI ESTA FUNCIÓN HACE COMMIT AL FINAL!
#             # Es mejor que esta función haga el commit final después de todas las operaciones de BD.
#             # Por ahora, asumiré que create_transaction hace su propio commit.
#             # O mejor, llamar a la función de alto nivel del controlador/transaction.py si existe
#             # from ..controller.transaction import buy_stock as crud_buy_stock # Si tienes una función así
#             # transaction_record, summary = await asyncio.to_thread(crud_buy_stock, db, self.user_id, stock.id, self.buy_sell_quantity)
#             # Si no, replicar la lógica del CRUD aquí:
#             new_transaction = StockTransaction(
#                 user_id=self.user_id,
#                 stock_id=stock.id,
#                 transaction_type=TransactionType.COMPRA,
#                 quantity=self.buy_sell_quantity, # Siempre positivo
#                 price_per_share=Decimal(str(price_to_use)),
#                 timestamp=datetime.now(timezone.utc)
#             )
#             db.add(new_transaction)
#             # db.add(user) # SQLAlchemy rastrea cambios en user, no necesita re-add explícito si está en sesión
            
#             await asyncio.to_thread(db.commit)
#             # await asyncio.to_thread(db.refresh, user) # No necesario si solo actualizas account_balance en AuthState
#             # await asyncio.to_thread(db.refresh, new_transaction) # No necesario si no usas el obj transaction después

#             # Actualizar estado local
#             self.account_balance = float(user.account_balance)
#             await self._load_current_stock_shares_owned() # Recalcular acciones poseídas
#             await self._load_recent_transactions() # Refrescar transacciones recientes
#             await self._update_portfolio_chart_data() # Refrescar gráfico de portfolio
            
#             self.transaction_message = f"Compra exitosa: {self.buy_sell_quantity} acciones de {self.viewing_stock_symbol} a ${price_to_use:,.2f} c/u."
#             logger.info(self.transaction_message)

#         except ValueError as ve: # Errores de validación (ej. saldo insuficiente desde CRUD)
#              logger.error(f"Error de validación al comprar {self.viewing_stock_symbol}: {ve}", exc_info=True)
#              self.transaction_message = str(ve)
#              if db and db.is_active: await asyncio.to_thread(db.rollback)
#         except Exception as e:
#             logger.error(f"Error inesperado al comprar {self.viewing_stock_symbol}: {e}", exc_info=True)
#             self.transaction_message = "Error inesperado durante la compra."
#             if db and db.is_active: await asyncio.to_thread(db.rollback)
#         finally:
#             self.loading = False
#             if db and db.is_active: await asyncio.to_thread(db.close)


#     @rx.event
#     async def sell_stock(self):
#         if not self.is_authenticated or not self.user_id or not self.viewing_stock_symbol:
#             self.transaction_message = "Error: Usuario no autenticado o acción no seleccionada."
#             return
#         if self.buy_sell_quantity <= 0:
#             self.transaction_message = "Error: La cantidad debe ser mayor que cero."
#             return
#         if self.current_stock_shares_owned < self.buy_sell_quantity:
#              self.transaction_message = f"Error: No tienes suficientes acciones ({self.current_stock_shares_owned}) para vender."
#              return

#         self.loading = True
#         self.transaction_message = ""
#         db = None
#         try:
#             db = SessionLocal()
#             user = await asyncio.to_thread(db.query(User).filter(User.id == self.user_id).first)
#             stock = await asyncio.to_thread(db.query(StockModel).filter(StockModel.symbol == self.viewing_stock_symbol).first)

#             if not user or not stock:
#                 self.transaction_message = "Error: Usuario o acción no encontrados en la base de datos."
#                 self.loading = False; return
            
#             # Usar precio actual de yfinance
#             price_to_use = self.current_stock_info.get("currentPrice")
#             if price_to_use is None:
#                 price_to_use = float(stock.current_price) # Fallback
#                 logger.warning(f"Usando precio de BD para {stock.symbol} en venta: {price_to_use}")
#             else:
#                 price_to_use = float(price_to_use)

#             total_value = Decimal(str(price_to_use)) * Decimal(self.buy_sell_quantity)
            
#             # Actualizar saldo
#             user.account_balance += total_value
            
#             # Crear transacción de VENTA
#             new_transaction = StockTransaction(
#                 user_id=self.user_id,
#                 stock_id=stock.id,
#                 transaction_type=TransactionType.VENTA,
#                 quantity=self.buy_sell_quantity, # Siempre positivo
#                 price_per_share=Decimal(str(price_to_use)),
#                 timestamp=datetime.now(timezone.utc)
#             )
#             db.add(new_transaction)
#             # db.add(user) # No necesario
            
#             await asyncio.to_thread(db.commit)

#             # Actualizar estado local
#             self.account_balance = float(user.account_balance)
#             await self._load_current_stock_shares_owned() # Recalcular
#             await self._load_recent_transactions()
#             await self._update_portfolio_chart_data()

#             self.transaction_message = f"Venta exitosa: {self.buy_sell_quantity} acciones de {self.viewing_stock_symbol} a ${price_to_use:,.2f} c/u."
#             logger.info(self.transaction_message)

#         except ValueError as ve:
#              logger.error(f"Error de validación al vender {self.viewing_stock_symbol}: {ve}", exc_info=True)
#              self.transaction_message = str(ve)
#              if db and db.is_active: await asyncio.to_thread(db.rollback)
#         except Exception as e:
#             logger.error(f"Error inesperado al vender {self.viewing_stock_symbol}: {e}", exc_info=True)
#             self.transaction_message = "Error inesperado durante la venta."
#             if db and db.is_active: await asyncio.to_thread(db.rollback)
#         finally:
#             self.loading = False
#             if db and db.is_active: await asyncio.to_thread(db.close)


#     @rx.event
#     async def dashboard_on_mount(self):
#         logger.info(f"Dashboard on_mount: Loading for user {self.username} (ID: {self.user_id}).")
#         if not self.is_authenticated or not self.user_id:
#             logger.warning("Usuario no autenticado en dashboard_on_mount, redirigiendo a login.")
#             return rx.redirect("/login")

#         self.is_loading_portfolio_chart = True # Indicar carga del gráfico de portfolio
#         try:
#             # Cargar datos del portfolio y transacciones
#             # Usar asyncio.gather para ejecutar tareas de carga en "paralelo" (concurrente)
            
#             # Primero, asegúrate de que los métodos existen
#             if not hasattr(self, '_load_recent_transactions'):
#                 logger.error("CRITICAL: AuthState no tiene el método _load_recent_transactions.")
#                 # Puedes crear un estado de error o simplemente no continuar
#                 self.is_loading_portfolio_chart = False
#                 return
#             if not hasattr(self, '_update_portfolio_chart_data'):
#                 logger.error("CRITICAL: AuthState no tiene el método _update_portfolio_chart_data.")
#                 self.is_loading_portfolio_chart = False
#                 return
#             if not hasattr(self, 'load_portfolio'):
#                 logger.error("CRITICAL: AuthState no tiene el método load_portfolio.")
#                 self.is_loading_portfolio_chart = False
#                 return

#             await asyncio.gather(
#                 self._load_recent_transactions(),
#                 self._update_portfolio_chart_data(), # Esta es la función clave para el gráfico
#                 self.load_portfolio()
#             )

#             # --- DEBUG LOGS AÑADIDOS ---
#             logger.info(f"Dashboard: DEBUG - Después de _update_portfolio_chart_data()")
#             if isinstance(self.portfolio_chart_data, pd.DataFrame):
#                 logger.info(f"Dashboard: DEBUG - portfolio_chart_data es un DataFrame.")
#                 logger.info(f"Dashboard: DEBUG - portfolio_chart_data está vacío? {self.portfolio_chart_data.empty}")
#                 if not self.portfolio_chart_data.empty:
#                     logger.info(f"Dashboard: DEBUG - Columnas de portfolio_chart_data: {self.portfolio_chart_data.columns.tolist()}")
#                     logger.info(f"Dashboard: DEBUG - Primeras filas de portfolio_chart_data:\n{self.portfolio_chart_data.head().to_string()}")
#                 else:
#                     logger.warning("Dashboard: DEBUG - portfolio_chart_data está vacío después de la actualización.")
#             else:
#                 logger.error(f"Dashboard: DEBUG - portfolio_chart_data NO es un DataFrame. Tipo actual: {type(self.portfolio_chart_data)}")
#             # --- FIN DEBUG LOGS ---

#             # Simulación de PNLs (reemplazar con lógica real si la tienes)
#             # Estas líneas son de tu código original, las mantengo.
#             self.daily_pnl = random.uniform(-500, 500)
#             self.monthly_pnl = random.uniform(-2000, 2000)
#             self.yearly_pnl = random.uniform(-10000, 10000)

#             logger.info("Dashboard on_mount: Carga de datos completada (o intentada).")

#         except AttributeError as ae: # Capturar específicamente el AttributeError que estabas viendo
#             logger.error(f"Error de Atributo durante dashboard_on_mount: {ae}", exc_info=True)
#             # Aquí podrías establecer un mensaje de error para la UI si lo deseas
#             # self.error_message = "Error al cargar datos del dashboard."
#         except Exception as e:
#             logger.error(f"Error general durante dashboard_on_mount: {e}", exc_info=True)
#             # self.error_message = "Error inesperado al cargar el dashboard."
#         finally:
#              self.is_loading_portfolio_chart = False

#     @rx.event
#     async def news_page_on_mount(self): # Ok
#         logger.info("NewsPage on_mount.")
#         # Cargar noticias solo si no hay ya, y no se están cargando.
#         if not self.processed_news and not self.is_loading_news:
#             await self.get_news(new_query=self.SEARCH_QUERY or DEFAULT_SEARCH_QUERY)


#     @rx.event
#     async def stock_detail_page_on_mount(self):
#         route_symbol = self.router.page.params.get("symbol")
#         logger.info(f"StockDetailPage on_mount. Router symbol: '{route_symbol}', Current viewing: '{self.viewing_stock_symbol}'")

#         if not route_symbol:
#             self.current_stock_info = {"error": "Símbolo de acción no especificado en la URL."}
#             self.is_loading_current_stock_details = False; return

#         self.is_loading_current_stock_details = True # Iniciar estado de carga

#         is_new_symbol = self.viewing_stock_symbol.upper() != route_symbol.upper()

#         if is_new_symbol: # Si es un símbolo diferente, limpiar todo lo relacionado con el anterior
#             logger.info(f"Nuevo símbolo detectado: '{route_symbol.upper()}'. Limpiando datos anteriores de '{self.viewing_stock_symbol}'.")
#             self.current_stock_info = {}
#             self.current_stock_metrics = {}
#             self.current_stock_history = pd.DataFrame(columns=['time','price']) # Resetear historial
#             self.current_stock_shares_owned = 0
#             self.transaction_message = ""
#             self.buy_sell_quantity = 1
#             self.stock_detail_chart_hover_info = None # Limpiar hover del gráfico anterior
        
#         self.viewing_stock_symbol = route_symbol.upper() # Actualizar al nuevo símbolo

#         try:
#             # Cargar info básica de la acción (de yfinance, con fallback a BD)
#             await self.load_stock_page_data(symbol=self.viewing_stock_symbol)
            
#             # Después de cargar la info básica (que incluye current_stock_info),
#             # cargar el historial del gráfico para el período seleccionado por defecto.
#             if not self.current_stock_info.get("error"): # Solo si la info básica se cargó bien
#                 await self._update_current_stock_chart_data_internal()
#             else: # Si hubo error cargando info básica, el gráfico también fallará o mostrará error
#                  self.current_stock_history = pd.DataFrame(columns=['time','price']) # Asegurar que está vacío
#                  logger.warning(f"No se cargará el gráfico para {self.viewing_stock_symbol} debido a error previo en carga de info.")

#         except Exception as e:
#             logger.error(f"Error crítico durante stock_detail_page_on_mount para {self.viewing_stock_symbol}: {e}", exc_info=True)
#             self.current_stock_info = {"error": f"Error al cargar página de {self.viewing_stock_symbol}."}
#             self.current_stock_history = pd.DataFrame(columns=['time','price']) # Resetear en error
#         finally:
#             self.is_loading_current_stock_details = False # Finalizar estado de carga
#             logger.info(f"StockDetailPage on_mount finalizado para {self.viewing_stock_symbol}. Tiene datos de historial: {not self.current_stock_history.empty if isinstance(self.current_stock_history, pd.DataFrame) else 'No es DF'}")


#     @rx.event
#     async def profile_page_on_mount(self): # Ok
#         logger.info("AuthState.profile_page_on_mount: Verificando autenticación.")
#         if not self.is_authenticated:
#             logger.warning("ProfilePage: Usuario no autenticado. on_load debería haber redirigido.")
#             # return rx.redirect("/login") # on_load debería manejar esto, pero como doble seguro.
#         else:
#             logger.info(f"ProfilePage: Usuario {self.username} (ID: {self.user_id}) autenticado.")
#             # Aquí podrías cargar datos específicos del perfil si es necesario
#             # await self._load_user_profile_data() # Ejemplo


#     @rx.event
#     async def buscador_page_on_mount(self): # Ok (aunque la búsqueda es manejada por SearchState)
#         logger.info("BuscadorPage (desde AuthState) on_mount.")
#         # Podrías resetear el término de búsqueda global de AuthState si lo deseas
#         # self.search_term = ""
#         # self.search_result = SearchResultItem()


#     # get_transaction_message parece no usarse, pero si la necesitas:
#     # def get_transaction_message(self, transaction: StockTransaction) -> str:
#     #     action = "Compra" if transaction.transaction_type == TransactionType.COMPRA else "Venta"
#     #     # Necesitarías una forma de obtener el símbolo del stock desde stock_id
#     #     # Esto podría implicar una consulta a BD o tener los stocks cargados en el estado.
#     #     # Para simplificar, si no la usas, puedes comentarla o eliminarla.
#     #     # Ejemplo (requiere self.stocks_map o similar):
#     #     # stock_symbol = self.stocks_map.get(transaction.stock_id, {}).get("symbol", "Desconocido")
#     #     stock_symbol = "SÍMBOLO_DESCONOCIDO" # Placeholder
#     #     total = Decimal(transaction.quantity) * transaction.price_per_share
#     #     return f"{action} de {transaction.quantity} acciones de {stock_symbol} a ${transaction.price_per_share:,.2f} (Total: ${total:,.2f})"


#     async def load_portfolio(self): # Carga self.portfolio_items y self.total_portfolio_value
#         if not self.is_authenticated or not self.user_id:
#             self.portfolio_items = []
#             self.total_portfolio_value = 0.0
#             return

#         db = None
#         new_portfolio_items = []
#         new_total_value = Decimal("0.0")
#         try:
#             db = SessionLocal()
#             # Usar la función del controlador que ya calcula esto es más DRY
#             # from ..controller.user import get_user_stocks # Importar dentro o globalmente
#             # user_stocks_data = await asyncio.to_thread(get_user_stocks, db, self.user_id)
            
#             # O si prefieres la lógica aquí:
#             # Obtener las posiciones actuales (símbolo -> {shares, stock_object, avg_price})
#             # Esto es complejo y ya lo tienes en get_user_portfolio en el controller.
#             # Es mejor llamar a una función consolidada del controlador.
#             # Por ahora, replicando la lógica que tenías antes aquí:

#             # 1. Obtener todas las acciones únicas en las que el usuario ha transaccionado.
#             user_stock_transactions = await asyncio.to_thread(
#                 db.query(StockTransaction.stock_id).filter(StockTransaction.user_id == self.user_id).distinct().all
#             )
#             stock_ids = [st_id[0] for st_id in user_stock_transactions]

#             if not stock_ids:
#                 self.portfolio_items = []; self.total_portfolio_value = 0.0; return

#             # 2. Obtener la información de esas acciones y sus precios actuales
#             stocks_in_portfolio_db = await asyncio.to_thread(
#                 db.query(StockModel).filter(StockModel.id.in_(stock_ids)).all
#             )
#             stocks_map = {s.id: s for s in stocks_in_portfolio_db} # Mapa de ID a objeto StockModel

#             # 3. Calcular las tenencias actuales para cada acción
#             for stock_id in stock_ids:
#                 stock_model = stocks_map.get(stock_id)
#                 if not stock_model: continue

#                 # Calcular acciones poseídas para este stock_id
#                 transactions_for_stock = await asyncio.to_thread(
#                     db.query(StockTransaction.transaction_type, StockTransaction.quantity)
#                     .filter(StockTransaction.user_id == self.user_id, StockTransaction.stock_id == stock_id)
#                     .all
#                 )
#                 buys = sum(t.quantity for t in transactions_for_stock if t.transaction_type == TransactionType.COMPRA)
#                 sells = sum(t.quantity for t in transactions_for_stock if t.transaction_type == TransactionType.VENTA)
#                 current_quantity = buys - sells

#                 if current_quantity > 0:
#                     current_price = float(stock_model.current_price)
#                     current_value_for_item = current_price * current_quantity
#                     new_total_value += Decimal(str(current_value_for_item))
                    
#                     # Asumir que StockModel tiene logo_url
#                     logo_url_val = getattr(stock_model, 'logo_url', None) or f"/{stock_model.symbol.upper()}.png"

#                     new_portfolio_items.append(
#                         PortfolioItem( # Usar el Pydantic model rx.Base
#                             symbol=stock_model.symbol,
#                             name=stock_model.name,
#                             quantity=current_quantity,
#                             current_price=current_price,
#                             current_value=current_value_for_item,
#                             logo_url=logo_url_val
#                         )
#                     )
            
#             self.portfolio_items = new_portfolio_items
#             self.total_portfolio_value = float(new_total_value)
#             logger.info(f"Portfolio cargado para user {self.user_id}: {len(self.portfolio_items)} items, valor total {self.total_portfolio_value:.2f}")

#         except Exception as e:
#             logger.error(f"Error al cargar portfolio para user {self.user_id}: {e}", exc_info=True)
#             self.portfolio_items = []
#             self.total_portfolio_value = 0.0
#         finally:
#             if db and db.is_active: await asyncio.to_thread(db.close)

#     # load_transactions ya estaba, revisa si la usas y si su lógica es correcta
#     # con el cambio de quantity siempre positiva y transaction_type.
#     async def load_transactions(self): # Carga self.transactions (lista de dicts)
#         if not self.is_authenticated or not self.user_id:
#             # self.transactions = [] # Asumiendo que tienes self.transactions como variable de estado
#             return
        
#         db = None
#         new_transactions_list = []
#         try:
#             db = SessionLocal()
#             # Usar get_transaction_history_with_profit_loss que ya formatea bien
#             raw_transactions_data = await asyncio.to_thread(
#                 get_transaction_history_with_profit_loss, db, self.user_id, limit=20 # O el límite que quieras
#             )
#             # La variable de estado es recent_transactions, que es List[TransactionDisplayItem]
#             # Así que necesitamos convertir raw_transactions_data a eso.
#             # O renombrar esta función y la variable de estado si es para un historial completo.
            
#             # Por ahora, vamos a asumir que esta función es para poblar self.recent_transactions
#             # y que get_transaction_history_with_profit_loss ya devuelve un formato compatible
#             # con TransactionDisplayItem o se adapta aquí.

#             # El código de _load_recent_transactions ya hace esto, así que esta función
#             # load_transactions() es redundante o tiene otro propósito.
#             # Si es para self.recent_transactions, usa _load_recent_transactions.
#             # Si es para otra variable self.all_transactions (List[Dict]), entonces:

#             # self.all_transactions = raw_transactions_data # Si el formato es el deseado
#             logger.info(f"Función load_transactions ejecutada, {len(raw_transactions_data)} transacciones obtenidas del CRUD.")


#         except Exception as e:
#             logger.error(f"Error al cargar transacciones (load_transactions): {e}", exc_info=True)
#             # self.transactions = []
#         finally:
#             if db and db.is_active: await asyncio.to_thread(db.close)

# tradesim/tradesim/state/auth_state.py
import reflex as rx
import yfinance as yf
import os
import logging
import requests
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import plotly.graph_objects as go
from jose import JWTError, jwt
from decimal import Decimal, InvalidOperation
import asyncio
import json
import random
from sqlmodel import SQLModel 
from datetime import datetime, timedelta, timezone

from ..database import SessionLocal, DEFAULT_SECTOR_ID # Importar DEFAULT_SECTOR_ID
from sqlalchemy import select, func 
from ..controller.user import get_user_by_id
from ..models.user import User
from ..models.stock import Stock, Stock as StockModel 
from ..models.stock_price_history import StockPriceHistory
from ..models.transaction import StockTransaction, TransactionType
from ..models.portfolio_item import PortfolioItemDB
from ..models.sector import Sector as SectorModel # Asegúrate que SectorModel está importado
from ..controller.transaction import get_transaction_history_with_profit_loss 


logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO)

# --- CONSTANTES ---
SECRET_KEY = os.getenv("SECRET_KEY", "a-very-secret-key-here-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
DEFAULT_AVATAR = "/default_avatar.png" 
GNEWS_API_KEY = "46ad3b8bbfa80ad174197e906e265525" # TU API KEY ACTUALIZADA
GNEWS_API_URL = "https://gnews.io/api/v4/search"
DEFAULT_SEARCH_QUERY = "mercado acciones finanzas"
COMPANY_MAP = {
    "APPLE": "AAPL", "MICROSOFT": "MSFT", "GOOGLE": "GOOGL", "ALPHABET": "GOOGL",
    "AMAZON": "AMZN", "META": "META", "FACEBOOK": "META", "TESLA": "TSLA",
}

# --- MODELOS Pydantic/rx.Base para el Estado ---
class NewsArticle(rx.Base):
    title: str; url: str; publisher: str; date: str; summary: str; image: str

class PortfolioItem(rx.Base): 
    symbol: str; name: str; quantity: int; current_price: float; current_value: float; logo_url: str

class SearchResultItem(rx.Base): 
    Symbol: str = "N/A"; Name: str = "No encontrado"; Current_Price: str = "N/A"; Logo: str = "/default_logo.png"

class TransactionDisplayItem(rx.Base): 
    timestamp: str; symbol: str; quantity: int; price: float; type: str
    @property
    def formatted_quantity(self) -> str:
        sign = "+" if self.type.lower() == TransactionType.COMPRA.value.lower() else "-"
        return f"{sign}{abs(self.quantity)}"

class AuthState(rx.State):
    # --- Variables de Autenticación y Usuario ---
    is_authenticated: bool = False
    user_id: Optional[int] = None
    username: str = ""
    email: str = "" 
    password: str = "" 
    confirm_password: str = "" 
    profile_image_url: str = DEFAULT_AVATAR
    account_balance: float = 100000.0 
    active_tab: str = "login" 
    error_message: str = "" 
    loading: bool = False 
    auth_token: Optional[str] = None 
    processed_token: bool = False 
    last_path: str = "/" 

    # --- Portfolio ---
    portfolio_items: List[PortfolioItem] = []
    total_portfolio_value: float = 0.0
    portfolio_chart_hover_info: Optional[Dict] = None
    portfolio_show_absolute_change: bool = False 
    selected_period: str = "1M" 
    recent_transactions: List[TransactionDisplayItem] = []
    portfolio_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'total_value'])
    is_loading_portfolio_chart: bool = False

    # --- Detalles de Acción ---
    viewing_stock_symbol: str = "" 
    current_stock_info: Dict[str, Any] = {} 
    current_stock_shares_owned: int = 0 
    buy_sell_quantity: int = 1 
    transaction_message: str = "" 
    current_stock_history: pd.DataFrame = pd.DataFrame(columns=['time', 'price']) 
    current_stock_selected_period: str = "1M" 
    stock_detail_chart_hover_info: Optional[Dict] = None
    is_loading_current_stock_details: bool = False 
    current_stock_metrics: Dict[str, str] = {} 

    # --- Noticias ---
    processed_news: List[NewsArticle] = []
    is_loading_news: bool = False
    has_news: bool = False 
    news_page: int = 1
    max_articles: int = 10 
    SEARCH_QUERY: str = DEFAULT_SEARCH_QUERY 

    # --- Búsqueda Global (si la usas desde AuthState) ---
    search_term: str = ""
    search_result: SearchResultItem = SearchResultItem() 
    is_searching: bool = False 

    # --- PNL Data ---
    daily_pnl: float = 0.0
    monthly_pnl: float = 0.0
    yearly_pnl: float = 0.0
    daily_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
    monthly_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
    yearly_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])

    # --- Métodos de Autenticación ---
    def _create_access_token(self, user_id: int) -> Optional[str]:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"sub": str(user_id), "exp": expire}
        try: return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        except Exception as e: logger.error(f"Error _create_access_token: {e}"); return None

    def _get_user_id_from_token(self, token: Optional[str]) -> int:
        if not token: return -1
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id_str = payload.get("sub")
            if user_id_str is None: logger.warning("Token 'sub' claim missing."); return -1
            return int(user_id_str)
        except JWTError as e: logger.warning(f"Token decoding error: {e}"); return -1
        except (ValueError, TypeError): logger.warning("Token 'sub' not valid int."); return -1

    def _set_user_state(self, user: User):
        self.is_authenticated = True; self.user_id = user.id; self.username = user.username; self.email = user.email
        self.account_balance = float(user.account_balance or 0.0)
        self.profile_image_url = getattr(user, 'profile_picture', DEFAULT_AVATAR) or DEFAULT_AVATAR

    def _clear_auth_state(self):
        self.is_authenticated = False; self.user_id = None; self.username = ""; self.email = ""
        self.profile_image_url = DEFAULT_AVATAR; self.account_balance = 0.0; self.auth_token = None
        self.portfolio_items = []; self.total_portfolio_value = 0.0; self.recent_transactions = []
        self.password = ""; self.confirm_password = ""
        logger.info("Estado de autenticación limpiado.")

    def set_username(self, username_in: str): self.username = username_in.strip()
    def set_email(self, email_in: str): self.email = email_in.strip().lower()
    def set_password(self, password_in: str): self.password = password_in
    def set_confirm_password(self, confirm_password_in: str): self.confirm_password = confirm_password_in

    @rx.event
    def set_active_tab(self, tab: str):
        self.active_tab = tab; self.error_message = ""; self.email = ""; self.password = ""; self.username = ""; self.confirm_password = ""

    @rx.event
    async def login(self):
        logger.info(f"Intento de login para email: {self.email}")
        self.error_message = ""; self.loading = True
        if not self.email or not self.password:
            self.error_message = "Por favor, complete todos los campos."; self.loading = False; return 
        db = None
        try:
            db = SessionLocal()
            user = await asyncio.to_thread(db.query(User).filter(User.email.ilike(self.email.strip().lower())).first)
            if not user or not await asyncio.to_thread(user.verify_password, self.password):
                self.error_message = "Email o contraseña incorrectos."; self.loading = False; self.password = ""; return
            self._set_user_state(user)
            token = self._create_access_token(user.id)
            if not token: self.error_message = "Error al generar token."; self._clear_auth_state(); self.loading = False; return
            self.auth_token = token; self.last_path = "/dashboard"; self.processed_token = False; self.loading = False
            logger.info(f"Usuario {self.email} logueado."); self.password = ""
            return rx.redirect(self.last_path) 
        except Exception as e:
            logger.error(f"Error en login: {e}", exc_info=True); self.error_message = "Error inesperado en login."; self._clear_auth_state(); self.loading = False; self.password = ""
        finally:
            if db: await asyncio.to_thread(db.close)

    @rx.event
    async def register(self):
        logger.info(f"Intento de registro para: {self.email}, Username: {self.username}")
        self.error_message = ""; self.loading = True
        if not self.username or not self.email or not self.password or not self.confirm_password:
            self.error_message = "Complete todos los campos."; self.loading = False; return
        if self.password != self.confirm_password:
            self.error_message = "Las contraseñas no coinciden."; self.loading = False; self.password = ""; self.confirm_password = ""; return
        db = None
        try:
            db = SessionLocal()
            existing_user = await asyncio.to_thread(db.query(User).filter((User.email.ilike(self.email)) | (User.username.ilike(self.username))).first)
            if existing_user: self.error_message = "Usuario o email ya registrados."; self.loading = False; return
            new_user = User(username=self.username.strip(), email=self.email.strip().lower())
            await asyncio.to_thread(new_user.set_password, self.password)
            db.add(new_user); await asyncio.to_thread(db.commit); await asyncio.to_thread(db.refresh, new_user)
            logger.info(f"Usuario creado: {new_user.username} (ID: {new_user.id})")
            self._set_user_state(new_user)
            token = self._create_access_token(new_user.id)
            if not token: self.error_message = "Error al generar token post-registro."; self._clear_auth_state(); self.loading = False; return
            self.auth_token = token; self.last_path = "/dashboard"; self.processed_token = False; self.loading = False
            logger.info(f"Usuario {self.email} registrado y logueado."); self.password = ""; self.confirm_password = ""; self.username = ""; self.email = ""
            return rx.redirect(self.last_path) 
        except Exception as e:
            logger.error(f"Error en registro: {e}", exc_info=True); self.error_message = "Error inesperado en registro."; self._clear_auth_state(); self.loading = False; self.password = ""; self.confirm_password = ""
        finally:
            if db: await asyncio.to_thread(db.close)

    @rx.event
    async def logout(self): 
        logger.info(f"Usuario {self.username} cerrando sesión."); self._clear_auth_state()
        self.active_tab = "login"; self.processed_token = False; self.last_path = "/"; return rx.redirect("/")

    @rx.var
    def stock_symbol_first_letter_for_avatar(self) -> str:
        symbol = self.current_stock_info.get("symbol") 
        if symbol and isinstance(symbol, str) and len(symbol) > 0:
            return symbol[0].upper()
        return "?"

    @rx.event
    async def on_load(self): 
        current_path = self.router.page.path
        logger.info(f"AuthState.on_load: Path='{current_path}', Token? {'Yes' if self.auth_token else 'No'}, Processed? {self.processed_token}, Auth? {self.is_authenticated}")
        if current_path == "/login" and self.active_tab != "login": self.active_tab = "login"
        elif current_path == "/registro" and self.active_tab != "register": self.active_tab = "register"
        user_id_from_token_check = self._get_user_id_from_token(self.auth_token)
        if self.processed_token and self.last_path == current_path and self.is_authenticated == (user_id_from_token_check > 0 and self.user_id == user_id_from_token_check) :
            logger.info(f"AuthState.on_load: Ya procesado para '{current_path}'."); return
        self.last_path = current_path
        db = None
        try:
            if self.auth_token:
                user_id_from_token = self._get_user_id_from_token(self.auth_token)
                if user_id_from_token > 0:
                    db = SessionLocal()
                    user = await asyncio.to_thread(get_user_by_id, db, user_id_from_token)
                    if user:
                        if not self.is_authenticated or self.user_id != user.id: self._set_user_state(user)
                        logger.info(f"AuthState.on_load: User {self.email} (ID: {self.user_id}) autenticado vía token.")
                        if current_path in ["/login", "/registro", "/"]: self.processed_token = True; return rx.redirect("/dashboard")
                    else: logger.warning(f"AuthState.on_load: User ID {user_id_from_token} del token no en BD. Limpiando."); self._clear_auth_state()
                else: logger.info("AuthState.on_load: Token inválido/expirado. Limpiando."); self._clear_auth_state()
            else: 
                logger.info("AuthState.on_load: No hay token. Asegurando no autenticado."); 
                if self.is_authenticated: self._clear_auth_state()
            protected_route_prefixes = ["/dashboard", "/profile", "/noticias", "/detalles_accion", "/aprender"]
            is_on_protected_route = any(current_path.startswith(p) for p in protected_route_prefixes)
            if not self.is_authenticated and is_on_protected_route:
                logger.info(f"AuthState.on_load: No autenticado en ruta protegida '{current_path}'. Redirigiendo a /login.")
                self.processed_token = True; return rx.redirect("/login")
        except Exception as e: logger.error(f"AuthState.on_load: Error: {e}", exc_info=True); self._clear_auth_state()
        finally:
            if db: await asyncio.to_thread(db.close)
        self.processed_token = True
        logger.info(f"AuthState.on_load: Finalizado para '{current_path}'. Autenticado: {self.is_authenticated}")

    @rx.event
    def set_buy_sell_quantity(self, value: str):
        try: self.buy_sell_quantity = max(1, int(value) if value else 1)
        except (ValueError, TypeError): self.buy_sell_quantity = 1

    @rx.event
    def open_url_script(self, url_to_open: str):
        logger.info(f"open_url_script: URL: '{url_to_open}' (tipo: {type(url_to_open)})")
        if isinstance(url_to_open, str) and (url_to_open.startswith("http://") or url_to_open.startswith("https://")):
            try: js_command = f"window.open({json.dumps(url_to_open)}, '_blank');"; return rx.call_script(js_command)
            except Exception as e: logger.error(f"Error json.dumps URL: {url_to_open}, Error: {e}")
        else: logger.error(f"URL inválida para script: '{url_to_open}'")
        return

    @rx.event
    async def set_period(self, period: str): # Para gráfico de portfolio
        self.selected_period = period; self.portfolio_chart_hover_info = None
        logger.info(f"Periodo portfolio cambiado a {period}. Actualizando gráfico.")
        await self._update_portfolio_chart_data()

    @rx.event
    async def set_current_stock_period(self, period: str): # Para gráfico de detalle de acción
        self.current_stock_selected_period = period
        self.stock_detail_chart_hover_info = None 
        logger.info(f"Período de detalle de acción cambiado a {period}. Actualizando gráfico para {self.viewing_stock_symbol}.")
        await self._update_current_stock_chart_data_internal()

    async def _load_current_stock_shares_owned(self):
        self.current_stock_shares_owned = 0
        if not self.user_id or not self.viewing_stock_symbol: return
        db = None
        try:
            db = SessionLocal()
            stock_db = await asyncio.to_thread(db.query(StockModel).filter(StockModel.symbol == self.viewing_stock_symbol).first)
            if not stock_db: logger.info(f"Stock {self.viewing_stock_symbol} no en BD (shares)."); return
            txs = await asyncio.to_thread(db.query(StockTransaction.transaction_type, StockTransaction.quantity).filter(StockTransaction.user_id == self.user_id, StockTransaction.stock_id == stock_db.id).all)
            buys = sum(t.quantity for t in txs if t.transaction_type == TransactionType.COMPRA)
            sells = sum(t.quantity for t in txs if t.transaction_type == TransactionType.VENTA)
            self.current_stock_shares_owned = int(buys - sells)
            logger.info(f"Acciones de {self.viewing_stock_symbol}: {self.current_stock_shares_owned} (B:{buys},S:{sells})")
        except Exception as e: logger.error(f"Error cargando shares de {self.viewing_stock_symbol}: {e}", exc_info=True); self.current_stock_shares_owned = 0
        finally:
            if db: await asyncio.to_thread(db.close)

    async def _generate_mock_stock_data(self, num_points=30) -> pd.DataFrame:
        end_date = datetime.now(timezone.utc); start_date = end_date - timedelta(days=num_points -1)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        prices = [max(10, random.uniform(100,200) + i*random.uniform(-2,2) + random.choice([-1,1])*i*random.uniform(0.1,0.5)) for i in range(len(dates))]
        return pd.DataFrame({'time': dates, 'price': prices})

    async def _generate_mock_portfolio_data(self, num_points=30) -> pd.DataFrame:
        end_date = datetime.now(timezone.utc); start_date = end_date - timedelta(days=num_points -1)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        values = [max(1000, random.uniform(10000,20000) + i*random.uniform(-200,200) + random.choice([-1,1])*i*random.uniform(10,50)) for i in range(len(dates))]
        return pd.DataFrame({'time': dates, 'total_value': values})

    async def _update_portfolio_chart_data(self): 
        logger.info(f"AuthState._update_portfolio_chart_data para user_id: {self.user_id}")
        if not self.is_authenticated or not self.user_id:
            self.portfolio_chart_data = pd.DataFrame(columns=['time', 'total_value']); logger.warning("UPD PORTF CHART: No auth, DF vacío."); return
        db = None
        try:
            db = SessionLocal()
            transactions = await asyncio.to_thread(
                db.query(StockTransaction)
                .filter(StockTransaction.user_id == self.user_id)
                .order_by(StockTransaction.timestamp) 
                .all
            )
            if not transactions:
                logger.info(f"No hay transacciones para user_id {self.user_id} para el gráfico de portfolio. Usando MOCK.")
                self.portfolio_chart_data = await self._generate_mock_portfolio_data()
                return 

            stock_ids_in_transactions = list(set(tx.stock_id for tx in transactions))
            if not stock_ids_in_transactions: 
                logger.warning("No stock_ids found in transactions. Using MOCK for portfolio chart.")
                self.portfolio_chart_data = await self._generate_mock_portfolio_data(); 
                return

            all_price_history_df_list = []
            for stock_id_val in stock_ids_in_transactions:
                history_query = select(StockPriceHistory.timestamp, StockPriceHistory.price).where(StockPriceHistory.stock_id == stock_id_val).order_by(StockPriceHistory.timestamp)
                df_hist_stock = await asyncio.to_thread(pd.read_sql, history_query, db.bind)
                if not df_hist_stock.empty:
                    df_hist_stock = df_hist_stock.rename(columns={"timestamp": "time", "price": f"price_{stock_id_val}"})
                    df_hist_stock['time'] = pd.to_datetime(df_hist_stock['time'], utc=True)
                    df_hist_stock = df_hist_stock.set_index('time') 
                    all_price_history_df_list.append(df_hist_stock)
            
            if not all_price_history_df_list:
                logger.warning("No se encontró historial de precios en BD para las acciones del portfolio. Usando MOCK DATA.")
                self.portfolio_chart_data = await self._generate_mock_portfolio_data()
                return

            combined_prices_df = pd.concat(all_price_history_df_list, axis=1)
            combined_prices_df = combined_prices_df.sort_index().ffill().bfill() 

            portfolio_value_over_time = []
            current_holdings = {} 

            all_relevant_timestamps = set(pd.to_datetime(tx.timestamp, utc=True) for tx in transactions)
            for df_h in all_price_history_df_list: 
                all_relevant_timestamps.update(df_h.index.tolist())
            
            if not all_relevant_timestamps:
                logger.warning("No hay timestamps relevantes para el gráfico de portfolio. Usando MOCK DATA.")
                self.portfolio_chart_data = await self._generate_mock_portfolio_data()
                return

            sorted_unique_timestamps = sorted(list(all_relevant_timestamps))
            
            transaction_idx = 0
            for ts_eval_dt in sorted_unique_timestamps:
                while transaction_idx < len(transactions) and pd.to_datetime(transactions[transaction_idx].timestamp, utc=True) <= ts_eval_dt:
                    tx = transactions[transaction_idx]
                    if tx.transaction_type == TransactionType.COMPRA:
                        current_holdings[tx.stock_id] = current_holdings.get(tx.stock_id, 0) + tx.quantity
                    elif tx.transaction_type == TransactionType.VENTA:
                        current_holdings[tx.stock_id] = current_holdings.get(tx.stock_id, 0) - tx.quantity
                    transaction_idx += 1
                
                current_ts_portfolio_value = Decimal("0.0")
                for stock_id_held, quantity_held in current_holdings.items():
                    if quantity_held > 0:
                        price_col_name = f"price_{stock_id_held}"
                        if price_col_name in combined_prices_df.columns and not combined_prices_df[price_col_name].asof(ts_eval_dt) is pd.NaT and pd.notna(combined_prices_df[price_col_name].asof(ts_eval_dt)):
                            price_at_ts_scalar = combined_prices_df[price_col_name].asof(ts_eval_dt)
                            current_ts_portfolio_value += Decimal(str(price_at_ts_scalar)) * Decimal(quantity_held)
                
                portfolio_value_over_time.append({'time': ts_eval_dt, 'total_value': float(current_ts_portfolio_value)})

            if portfolio_value_over_time:
                self.portfolio_chart_data = pd.DataFrame(portfolio_value_over_time)
                logger.info(f"Datos REALES del gráfico de portfolio cargados. {len(self.portfolio_chart_data)} puntos.")
            else:
                logger.warning("No se pudieron calcular valores de portfolio (lista vacía). Usando MOCK DATA.")
                self.portfolio_chart_data = await self._generate_mock_portfolio_data()
        except Exception as e_real_data:
            logger.error(f"Error al calcular datos reales del gráfico de portfolio: {e_real_data}", exc_info=True)
            logger.warning("Cayendo a MOCK DATA para gráfico de portfolio debido a excepción en lógica real.")
            self.portfolio_chart_data = await self._generate_mock_portfolio_data()
        finally:
            if db: await asyncio.to_thread(db.close)


    async def _fetch_stock_history_data_detail(self, symbol: str, period: str) -> pd.DataFrame:
        logger.info(f"Fetching yfinance history: {symbol}, period {period}")
        try:
            ticker = yf.Ticker(symbol)
            yf_map={"1D":"1d","5D":"5d","1M":"1mo","6M":"6mo","YTD":"ytd","1A":"1y","1Y":"1y","5A":"5y","5Y":"5y","MAX":"max"}
            yf_p = yf_map.get(period.upper(),"1mo")
            interval="1d"
            if yf_p == "1d": interval = "5m"
            elif yf_p == "5d": interval = "15m"
            elif yf_p == "1mo": interval = "1h"
            hist = await asyncio.to_thread(ticker.history, period=yf_p, interval=interval, auto_adjust=True, prepost=False)
            if not hist.empty:
                hist = hist.reset_index(); date_col = next((c for c in ['Datetime','Date','index'] if c in hist.columns),None)
                if not date_col: logger.error(f"Col fecha no en yf hist {symbol}. Cols: {hist.columns.tolist()}"); return await self._generate_mock_stock_data()
                hist = hist.rename(columns={date_col:'time','Close':'price'}); hist['time']=pd.to_datetime(hist['time'],utc=True,errors='coerce'); hist['price']=pd.to_numeric(hist['price'],errors='coerce'); hist=hist.dropna(subset=['time','price'])
                if not hist.empty: logger.info(f"YF hist {symbol} ({period}): {len(hist)} pts."); return hist[['time','price']]
            logger.warning(f"YF hist vacío {symbol} ({yf_p},{interval}). Usando MOCK."); return await self._generate_mock_stock_data()
        except Exception as e: logger.error(f"Error YF hist {symbol}: {e}",exc_info=True); return await self._generate_mock_stock_data()

    async def _update_current_stock_chart_data_internal(self):
        logger.info(f"_update_current_stock_chart_data_internal: {self.viewing_stock_symbol} P:{self.current_stock_selected_period}")
        if not self.viewing_stock_symbol: self.current_stock_history=pd.DataFrame(columns=['time','price']); return
        df = await self._fetch_stock_history_data_detail(self.viewing_stock_symbol, self.current_stock_selected_period)
        if isinstance(df,pd.DataFrame) and not df.empty: self.current_stock_history=df.sort_values(by='time'); logger.info(f"Chart data {self.viewing_stock_symbol}: {len(df)} pts.")
        else: self.current_stock_history=await self._generate_mock_stock_data(60); logger.warning(f"Fallback MOCK chart data {self.viewing_stock_symbol}.")

    @rx.event
    async def load_stock_page_data(self, symbol: str): 
        self.viewing_stock_symbol = symbol.upper(); self.is_loading_current_stock_details = True; self.transaction_message = ""; self.current_stock_info = {}; self.current_stock_metrics = {}
        logger.info(f"load_stock_page_data: Iniciando para {self.viewing_stock_symbol}")
        db_session = None 
        try:
            ticker = await asyncio.to_thread(yf.Ticker, self.viewing_stock_symbol)
            info = await asyncio.to_thread(getattr, ticker, 'info')

            if not info or not info.get("symbol"):
                logger.warning(f"No yf info para {self.viewing_stock_symbol}. Intentando DB local.")
                db_session = SessionLocal() 
                stock_db = await asyncio.to_thread(db_session.query(StockModel).filter(StockModel.symbol == self.viewing_stock_symbol).first)
                if stock_db:
                    self.current_stock_info = {"symbol":stock_db.symbol,"name":stock_db.name,"currentPrice":float(stock_db.current_price),"sector":stock_db.sector.sector_name if stock_db.sector else "N/A","currencySymbol":"$"}
                    logger.info(f"Info básica para {self.viewing_stock_symbol} cargada de DB local.")
                else:
                    self.current_stock_info = {"error": f"Acción {self.viewing_stock_symbol} no encontrada en yfinance ni en BD."}
                    # No hacer return aquí, el finally se encargará de db_session
            else:
                self.current_stock_info = {
                    "symbol": info.get("symbol", self.viewing_stock_symbol), "name": info.get("longName", info.get("shortName", "N/A")),
                    "currentPrice": float(info.get("currentPrice", info.get("regularMarketPrice", 0.0))),
                    "previousClose": float(info.get("previousClose", 0.0)), "open": float(info.get("open", 0.0)),
                    "dayHigh": float(info.get("dayHigh", 0.0)), "dayLow": float(info.get("dayLow", 0.0)),
                    "volume": info.get("volume"), "marketCap": info.get("marketCap"),
                    "fiftyTwoWeekHigh": float(info.get("fiftyTwoWeekHigh", 0.0)), "fiftyTwoWeekLow": float(info.get("fiftyTwoWeekLow", 0.0)),
                    "sector": info.get("sector", "N/A"), "industry": info.get("industry", "N/A"),
                    "currencySymbol": info.get("currencySymbol", "$"), "logo_url": info.get("logo_url"),
                    "longBusinessSummary": info.get("longBusinessSummary", "Resumen no disponible.")
                }
                if self.current_stock_info.get("currentPrice") and self.current_stock_info.get("previousClose"): cp=self.current_stock_info["currentPrice"];pc=self.current_stock_info["previousClose"];self.current_stock_info["change"]=cp-pc;self.current_stock_info["changePercent"]=((cp-pc)/pc*100)if pc else 0.0
                
                self.current_stock_metrics={
                    "Cap. Bursátil":f"{self.current_stock_info.get('currencySymbol','')}{self.current_stock_info.get('marketCap',0):,}" if self.current_stock_info.get('marketCap')else"N/A",
                    "Volumen":f"{self.current_stock_info.get('volume',0):,}" if self.current_stock_info.get('volume')else"N/A",
                    "Apertura": f"{self.current_stock_info.get('currencySymbol','')}{self.current_stock_info.get('open', 0.0):.2f}",
                    "Máx. Diario": f"{self.current_stock_info.get('currencySymbol','')}{self.current_stock_info.get('dayHigh', 0.0):.2f}",
                    "Mín. Diario": f"{self.current_stock_info.get('currencySymbol','')}{self.current_stock_info.get('dayLow', 0.0):.2f}",
                }
                logger.info(f"Info de yfinance cargada para {self.viewing_stock_symbol}: {self.current_stock_info.get('name')}")

                # --- AÑADIR/ACTUALIZAR STOCK EN BD LOCAL ---
                db_op_session = SessionLocal() # Sesión separada para esta operación
                try:
                    stock_symbol_from_yf = self.current_stock_info["symbol"] 
                    stock_name_from_yf = self.current_stock_info["name"]
                    current_price_from_yf = Decimal(str(self.current_stock_info["currentPrice"]))
                    logo_url_from_yf = self.current_stock_info.get("logo_url")
                    sector_name_from_yf = self.current_stock_info.get("sector", "Desconocido") 

                    existing_stock_in_db = await asyncio.to_thread(
                        db_op_session.query(StockModel).filter(StockModel.symbol == stock_symbol_from_yf).first
                    )
                    if not existing_stock_in_db:
                        logger.info(f"Stock {stock_symbol_from_yf} no encontrado en BD local. Creando entrada...")
                        sector_obj = await asyncio.to_thread(db_op_session.query(SectorModel).filter(SectorModel.sector_name == sector_name_from_yf).first)
                        if not sector_obj:
                            logger.info(f"Sector '{sector_name_from_yf}' no encontrado. Creando nuevo sector.")
                            sector_obj = SectorModel(sector_name=sector_name_from_yf)
                            db_op_session.add(sector_obj)
                            await asyncio.to_thread(db_op_session.flush) 
                        
                        new_stock_db_entry = StockModel(
                            symbol=stock_symbol_from_yf, name=stock_name_from_yf,
                            current_price=current_price_from_yf,
                            logo_url=logo_url_from_yf, 
                            sector_id=sector_obj.id if sector_obj else DEFAULT_SECTOR_ID 
                        )
                        db_op_session.add(new_stock_db_entry)
                        await asyncio.to_thread(db_op_session.commit) # Commit para la nueva acción
                        logger.info(f"Stock {stock_symbol_from_yf} añadido a BD local con ID: {new_stock_db_entry.id}, Sector ID: {new_stock_db_entry.sector_id}")
                    elif existing_stock_in_db.current_price != current_price_from_yf or existing_stock_in_db.logo_url != logo_url_from_yf or existing_stock_in_db.name != stock_name_from_yf:
                        logger.info(f"Actualizando stock {stock_symbol_from_yf} en BD local.")
                        existing_stock_in_db.current_price = current_price_from_yf
                        existing_stock_in_db.name = stock_name_from_yf 
                        if logo_url_from_yf: existing_stock_in_db.logo_url = logo_url_from_yf
                        sector_obj = await asyncio.to_thread(db_op_session.query(SectorModel).filter(SectorModel.sector_name == sector_name_from_yf).first)
                        if not sector_obj and sector_name_from_yf != "Desconocido": 
                            sector_obj = SectorModel(sector_name=sector_name_from_yf)
                            db_op_session.add(sector_obj)
                            await asyncio.to_thread(db_op_session.flush)
                        if sector_obj : existing_stock_in_db.sector_id = sector_obj.id
                        
                        await asyncio.to_thread(db_op_session.commit) # Commit para la actualización
                        logger.info(f"Stock {stock_symbol_from_yf} actualizado en BD local.")
                except Exception as e_db_op:
                    logger.error(f"Error al añadir/actualizar stock {self.viewing_stock_symbol} en BD: {e_db_op}", exc_info=True)
                    if db_op_session: await asyncio.to_thread(db_op_session.rollback) 
                finally:
                    if db_op_session: await asyncio.to_thread(db_op_session.close)
                # --- FIN AÑADIR/ACTUALIZAR STOCK ---
            
            if self.is_authenticated and self.user_id: await self._load_current_stock_shares_owned()

        except Exception as e: 
            logger.error(f"Error en load_stock_page_data para {self.viewing_stock_symbol}: {e}", exc_info=True)
            self.current_stock_info={"error":f"Error al cargar datos para {self.viewing_stock_symbol}."} 
        finally:
            if db_session: await asyncio.to_thread(db_session.close) 
            self.is_loading_current_stock_details=False

    @rx.event
    async def buy_stock(self):
        logger.info(f"AUTHSTATE: Intento de COMPRA para {self.viewing_stock_symbol} por user {self.user_id}, cantidad: {self.buy_sell_quantity}")
        if not self.is_authenticated or not self.user_id or not self.viewing_stock_symbol: 
            self.transaction_message="Err:Auth/Acción"; logger.warning("BUY_STOCK: Auth o símbolo no válido."); return
        if self.buy_sell_quantity <= 0: 
            self.transaction_message = "Cantidad debe ser positiva."; logger.warning("BUY_STOCK: Cantidad no positiva."); return
        
        self.loading = True; self.transaction_message = ""
        logger.info(f"BUY_STOCK: Iniciando transacción para {self.viewing_stock_symbol}")
        db = None
        try:
            db = SessionLocal()
            user = await asyncio.to_thread(db.query(User).get, self.user_id)
            stock_m = await asyncio.to_thread(db.query(StockModel).filter(StockModel.symbol == self.viewing_stock_symbol).first)
            
            if not user: logger.error("BUY_STOCK: Usuario no encontrado en BD."); self.transaction_message="Error: Usuario no encontrado."; self.loading=False; return
            if not stock_m: 
                logger.error(f"BUY_STOCK: Stock {self.viewing_stock_symbol} NO encontrado en BD local. No se puede comprar.")
                self.transaction_message=f"Error: Acción {self.viewing_stock_symbol} no encontrada en sistema para transacciones."; self.loading=False; return

            price_to_use = float(self.current_stock_info.get("currentPrice", stock_m.current_price)) 
            logger.info(f"BUY_STOCK: Usando precio {price_to_use} para {stock_m.symbol}")
            cost = Decimal(str(price_to_use)) * Decimal(self.buy_sell_quantity)

            logger.info(f"BUY_STOCK: Costo total: {cost}, Saldo usuario: {user.account_balance}")
            if user.account_balance < cost:
                self.transaction_message = f"Saldo insuficiente. Necesario: {cost:,.2f}, Disponible: {user.account_balance:,.2f}"; self.loading = False; return
            
            user.account_balance -= cost
            logger.info(f"BUY_STOCK: Saldo actualizado usuario: {user.account_balance}")
            
            tx = StockTransaction(
                user_id=self.user_id, stock_id=stock_m.id, transaction_type=TransactionType.COMPRA,
                quantity=self.buy_sell_quantity, price_per_share=Decimal(str(price_to_use)),
                timestamp=datetime.now(timezone.utc)
            )
            db.add(tx)
            await asyncio.to_thread(db.commit)
            logger.info(f"BUY_STOCK: Transacción COMMIT para {stock_m.symbol}, ID: {tx.id if tx.id else 'NO ID'}")
            
            self.account_balance = float(user.account_balance) 
            await asyncio.gather(
                self._load_current_stock_shares_owned(),
                self._load_recent_transactions(),
                self._update_portfolio_chart_data(), 
                self.load_portfolio() 
            )
            self.transaction_message = f"Compra OK: {self.buy_sell_quantity} de {self.viewing_stock_symbol}"
            logger.info(self.transaction_message)

        except Exception as e:
            logger.error(f"Err buy_stock: {e}", exc_info=True)
            self.transaction_message = "Error durante la compra."
            if db: await asyncio.to_thread(db.rollback)
        finally:
            self.loading = False
            if db: await asyncio.to_thread(db.close)


    @rx.event
    async def sell_stock(self):
        logger.info(f"AUTHSTATE: Intento de VENTA para {self.viewing_stock_symbol} por user {self.user_id}, cantidad: {self.buy_sell_quantity}")
        if not self.is_authenticated or not self.user_id or not self.viewing_stock_symbol: 
            self.transaction_message="Err:Auth/Acción"; logger.warning("SELL_STOCK: Auth o símbolo no válido."); return
        if self.buy_sell_quantity <= 0: 
            self.transaction_message = "Cantidad debe ser positiva."; logger.warning("SELL_STOCK: Cantidad no positiva."); return
        
        await self._load_current_stock_shares_owned() 
        if self.current_stock_shares_owned < self.buy_sell_quantity:
            self.transaction_message = f"No tienes suficientes acciones ({self.current_stock_shares_owned}) para vender {self.buy_sell_quantity}."; logger.warning(self.transaction_message); return

        self.loading = True; self.transaction_message = ""
        logger.info(f"SELL_STOCK: Iniciando transacción para {self.viewing_stock_symbol}")
        db = None
        try:
            db = SessionLocal()
            user = await asyncio.to_thread(db.query(User).get, self.user_id)
            stock_m = await asyncio.to_thread(db.query(StockModel).filter(StockModel.symbol == self.viewing_stock_symbol).first)

            if not user: logger.error("SELL_STOCK: Usuario no encontrado en BD."); self.transaction_message="Error: Usuario no encontrado."; self.loading=False; return
            if not stock_m: 
                logger.error(f"SELL_STOCK: Stock {self.viewing_stock_symbol} NO encontrado en BD local. No se puede vender.")
                self.transaction_message=f"Error: Acción {self.viewing_stock_symbol} no encontrada en sistema para transacciones."; self.loading=False; return

            price_to_use = float(self.current_stock_info.get("currentPrice", stock_m.current_price))
            logger.info(f"SELL_STOCK: Usando precio {price_to_use} para {stock_m.symbol}")
            value_of_sale = Decimal(str(price_to_use)) * Decimal(self.buy_sell_quantity)

            user.account_balance += value_of_sale
            logger.info(f"SELL_STOCK: Saldo actualizado usuario: {user.account_balance}")

            tx = StockTransaction(
                user_id=self.user_id, stock_id=stock_m.id, transaction_type=TransactionType.VENTA,
                quantity=self.buy_sell_quantity, price_per_share=Decimal(str(price_to_use)),
                timestamp=datetime.now(timezone.utc)
            )
            db.add(tx)
            await asyncio.to_thread(db.commit)
            logger.info(f"SELL_STOCK: Transacción COMMIT para {stock_m.symbol}, ID: {tx.id if tx.id else 'NO ID'}")

            self.account_balance = float(user.account_balance)
            await asyncio.gather(
                self._load_current_stock_shares_owned(),
                self._load_recent_transactions(),
                self._update_portfolio_chart_data(),
                self.load_portfolio()
            )
            self.transaction_message = f"Venta OK: {self.buy_sell_quantity} de {self.viewing_stock_symbol}"
            logger.info(self.transaction_message)

        except Exception as e:
            logger.error(f"Err sell_stock: {e}", exc_info=True); self.transaction_message = "Error durante la venta."
            if db: await asyncio.to_thread(db.rollback)
        finally:
            self.loading = False
            if db: await asyncio.to_thread(db.close)


    @rx.event
    async def dashboard_on_mount(self):
        logger.info(f"Dashboard on_mount: User {self.username} (ID: {self.user_id}).")
        if not self.is_authenticated or not self.user_id: logger.warning("Dashboard: No auth, redirect login."); return rx.redirect("/login")
        self.is_loading_portfolio_chart = True
        try:
            if not all(hasattr(self,m)for m in['_load_recent_transactions','_update_portfolio_chart_data','load_portfolio']):
                logger.error("CRITICAL: Faltan métodos de carga en AuthState."); self.is_loading_portfolio_chart=False; return
            await asyncio.gather(self._load_recent_transactions(),self._update_portfolio_chart_data(),self.load_portfolio())
            logger.info(f"Dashboard DEBUG: portfolio_chart_data empty? {self.portfolio_chart_data.empty if isinstance(self.portfolio_chart_data,pd.DataFrame)else 'NotDF'}")
            if isinstance(self.portfolio_chart_data,pd.DataFrame)and not self.portfolio_chart_data.empty:logger.info(f"Cols:{self.portfolio_chart_data.columns.tolist()} Head:\n{self.portfolio_chart_data.head().to_string()}")
            else:logger.warning("Dashboard DEBUG: portfolio_chart_data vacío/inválido post-update.")
            self.daily_pnl=random.uniform(-100,100);self.monthly_pnl=random.uniform(-500,500);self.yearly_pnl=random.uniform(-1000,1000)
            logger.info("Dashboard on_mount: Carga completada (o mock).")
        except AttributeError as ae:logger.error(f"AttrErr dashboard_on_mount:{ae}",exc_info=True)
        except Exception as e:logger.error(f"Err dashboard_on_mount:{e}",exc_info=True)
        finally:self.is_loading_portfolio_chart=False

    @rx.event
    async def news_page_on_mount(self):
        logger.info("NewsPage on_mount.")
        if not self.processed_news and not self.is_loading_news: await self.get_news(new_query=self.SEARCH_QUERY or DEFAULT_SEARCH_QUERY)

    @rx.event
    async def stock_detail_page_on_mount(self): 
        route_symbol = self.router.page.params.get("symbol")
        logger.info(f"StockDetail on_mount. Route:{route_symbol}, Current viewing symbol: '{self.viewing_stock_symbol}'")
        if not route_symbol:
            self.current_stock_info = {"error": "Símbolo de acción no especificado en la URL."}; self.is_loading_current_stock_details = False; return
        self.is_loading_current_stock_details = True
        if self.viewing_stock_symbol.upper() != route_symbol.upper() or not self.current_stock_info or self.current_stock_info.get("symbol", "").upper() != route_symbol.upper():
            logger.info(f"Nuevo símbolo para detalles: '{route_symbol.upper()}'. Limpiando datos anteriores de '{self.viewing_stock_symbol}'.")
            self.viewing_stock_symbol = route_symbol.upper() 
            self.current_stock_info = {}; self.current_stock_metrics = {}; self.current_stock_history = pd.DataFrame(columns=['time','price']); self.current_stock_shares_owned = 0; self.transaction_message = ""; self.stock_detail_chart_hover_info = None; self.processed_news = []; self.has_news = False; self.news_page = 1
        else: logger.info(f"Refrescando datos para el mismo símbolo: {self.viewing_stock_symbol}")
        try:
            # Encadenar las llamadas para asegurar el orden
            await self.load_stock_page_data(symbol=self.viewing_stock_symbol) 
            if not self.current_stock_info.get("error"):
                await self._update_current_stock_chart_data_internal()
                if GNEWS_API_KEY and GNEWS_API_KEY != "YOUR_GNEWS_API_KEY_HERE": 
                    await self.get_news(new_query=self.viewing_stock_symbol) 
                else:
                    logger.warning("GNEWS_API_KEY no configurada o es placeholder. Saltando carga de noticias para detalles de acción.")
                    self._create_fallback_news() 
            else:
                self.current_stock_history = pd.DataFrame(columns=['time','price']); self.processed_news = []; self.has_news = False
                logger.warning(f"No se cargarán gráfico/noticias para {self.viewing_stock_symbol} debido a error previo en carga de info.")
        except Exception as e:
            logger.error(f"Error crítico durante stock_detail_page_on_mount para {self.viewing_stock_symbol}: {e}", exc_info=True)
            self.current_stock_info = {"error": f"Error al cargar página de {self.viewing_stock_symbol}."}; self.current_stock_history = pd.DataFrame(columns=['time','price'])
        finally:
            self.is_loading_current_stock_details = False
            logger.info(f"StockDetail on_mount finalizado para {self.viewing_stock_symbol}. Hist. datos:{not self.current_stock_history.empty if isinstance(self.current_stock_history,pd.DataFrame)else 'NoDF'}")


    @rx.event
    async def profile_page_on_mount(self):
        logger.info("AuthState.profile_page_on_mount.");
        if not self.is_authenticated:logger.warning("ProfilePage: No auth.")
        else:logger.info(f"ProfilePage: User {self.username} (ID:{self.user_id}) auth.")

    @rx.event
    async def buscador_page_on_mount(self): logger.info("BuscadorPage (AuthState) on_mount.")

    async def _load_recent_transactions(self):
        logger.info(f"AuthState._load_recent_transactions para user_id: {self.user_id}")
        if not self.user_id: self.recent_transactions = []; return
        db = None; new_trans_list = []
        try:
            db = SessionLocal()
            raw_transactions_data = await asyncio.to_thread(get_transaction_history_with_profit_loss, db, self.user_id, limit=10)
            for t_data_dict in raw_transactions_data:
                dt_obj = datetime.fromisoformat(t_data_dict["timestamp"]); formatted_timestamp = dt_obj.strftime("%d/%m/%y %H:%M")
                trans_type = t_data_dict["type"].capitalize(); quantity = int(t_data_dict["quantity"]); symbol = t_data_dict["stock_symbol"]; price = float(t_data_dict["price"])
                new_trans_list.append(TransactionDisplayItem(timestamp=formatted_timestamp, symbol=symbol, quantity=quantity, price=price, type=trans_type))
            self.recent_transactions = new_trans_list
            logger.info(f"Loaded {len(self.recent_transactions)} recent transactions.")
        except Exception as e: logger.error(f"Error en _load_recent_transactions: {e}", exc_info=True); self.recent_transactions = []
        finally:
            if db: await asyncio.to_thread(db.close)

    async def load_portfolio(self):
        logger.info(f"AuthState.load_portfolio para user_id: {self.user_id}")
        if not self.is_authenticated or not self.user_id: self.portfolio_items = []; self.total_portfolio_value = 0.0; return
        db = None; new_portfolio_items = []; new_total_value = Decimal("0.0")
        try:
            db = SessionLocal()
            user_stock_transactions = await asyncio.to_thread(db.query(StockTransaction.stock_id).filter(StockTransaction.user_id == self.user_id).distinct().all)
            stock_ids = [st_id[0] for st_id in user_stock_transactions]
            if not stock_ids: self.portfolio_items = []; self.total_portfolio_value = 0.0; return
            stocks_in_portfolio_db = await asyncio.to_thread(db.query(StockModel).filter(StockModel.id.in_(stock_ids)).all)
            stocks_map = {s.id: s for s in stocks_in_portfolio_db}
            for stock_id in stock_ids:
                stock_model = stocks_map.get(stock_id)
                if not stock_model: continue
                transactions_for_stock = await asyncio.to_thread(db.query(StockTransaction.transaction_type, StockTransaction.quantity).filter(StockTransaction.user_id == self.user_id, StockTransaction.stock_id == stock_id).all)
                buys = sum(t.quantity for t in transactions_for_stock if t.transaction_type == TransactionType.COMPRA)
                sells = sum(t.quantity for t in transactions_for_stock if t.transaction_type == TransactionType.VENTA)
                current_quantity = buys - sells
                if current_quantity > 0:
                    current_price = float(stock_model.current_price); current_value_for_item = current_price * current_quantity
                    new_total_value += Decimal(str(current_value_for_item))
                    logo_url_val = getattr(stock_model, 'logo_url', None) or f"/{stock_model.symbol.upper()}.png"
                    new_portfolio_items.append(PortfolioItem(symbol=stock_model.symbol, name=stock_model.name, quantity=current_quantity, current_price=current_price, current_value=current_value_for_item, logo_url=logo_url_val))
            self.portfolio_items = new_portfolio_items; self.total_portfolio_value = float(new_total_value)
            logger.info(f"Portfolio cargado user {self.user_id}: {len(self.portfolio_items)} items, valor {self.total_portfolio_value:.2f}")
        except Exception as e: logger.error(f"Error cargar portfolio user {self.user_id}: {e}", exc_info=True); self.portfolio_items = []; self.total_portfolio_value = 0.0
        finally:
            if db: await asyncio.to_thread(db.close)

    @rx.var
    def balance_date(self) -> str: return datetime.now().strftime("%d %b %Y")
    @rx.var
    def formatted_user_balance(self) -> str: return f"${self.account_balance:,.2f}"
    @rx.var
    def formatted_user_balance_with_currency(self) -> str: return f"${self.account_balance:,.2f} USD"
    @rx.var
    def can_load_more_news(self) -> bool: return bool(self.processed_news) and not self.is_loading_news and self.has_news
    @rx.var
    def featured_stock_page_news(self) -> List[NewsArticle]: return self.processed_news[:3]
    @rx.var
    def portfolio_change_info(self) -> Dict[str, Any]:
        df = self.portfolio_chart_data; last_price_fallback = self.total_portfolio_value if self.total_portfolio_value is not None else 0.0
        default = {"last_price": last_price_fallback, "change": 0.0, "percent_change": 0.0, "is_positive": None}
        if not isinstance(df, pd.DataFrame) or df.empty or 'total_value' not in df.columns: return default
        prices = df['total_value'].dropna();
        if prices.empty: return default
        last_f = float(prices.iloc[-1])
        if len(prices) < 2: return {"last_price": last_f, "change": 0.0, "percent_change": 0.0, "is_positive": None}
        try: first_f = float(prices.iloc[0])
        except IndexError: return {"last_price": last_f, "change": 0.0, "percent_change": 0.0, "is_positive": None}
        change_f = last_f - first_f; percent_f = (change_f / first_f * 100) if first_f != 0 else 0.0
        is_positive = change_f > 0 if change_f != 0 else (None if change_f == 0 else False)
        return {"last_price": last_f, "change": change_f, "percent_change": percent_f, "is_positive": is_positive}
    @rx.var
    def is_portfolio_value_change_positive(self) -> Optional[bool]: return self.portfolio_change_info.get("is_positive")
    @rx.var
    def formatted_portfolio_value_percent_change(self) -> str: return f"{abs(self.portfolio_change_info.get('percent_change', 0.0)):.2f}%"
    @rx.var
    def formatted_portfolio_value_change_abs(self) -> str: return f"{self.portfolio_change_info.get('change', 0.0):+.2f}"
    @rx.var
    def portfolio_chart_color(self) -> str:
        is_positive = self.is_portfolio_value_change_positive
        if is_positive is True: return "var(--green-9)"
        if is_positive is False: return "var(--red-9)"
        return "var(--gray-9)"
    @rx.var
    def portfolio_chart_area_color(self) -> str:
        is_positive = self.is_portfolio_value_change_positive
        if is_positive is True: return "rgba(34,197,94,0.2)"
        if is_positive is False: return "rgba(239,68,68,0.2)"
        return "rgba(107,114,128,0.2)"
    @rx.var
    def portfolio_display_value(self) -> float:
        hover_info = self.portfolio_chart_hover_info
        if hover_info and "y" in hover_info:
            hover_y_data = hover_info["y"]; y_to_convert = hover_y_data[0] if isinstance(hover_y_data, list) and hover_y_data else hover_y_data
            if y_to_convert is not None:
                try: return float(y_to_convert)
                except: pass
        return float(self.portfolio_change_info.get("last_price", self.total_portfolio_value if self.total_portfolio_value is not None else 0.0))
    @rx.var
    def portfolio_display_time(self) -> str:
        hover_info = self.portfolio_chart_hover_info
        if hover_info and "x" in hover_info:
            x_data = hover_info["x"]; x_value = x_data[0] if isinstance(x_data, list) and x_data else x_data
            if x_value is not None:
                try:
                    if isinstance(x_value, (str, int, float, datetime, pd.Timestamp)): return pd.to_datetime(x_value).strftime('%d %b %Y')
                    return str(x_value)
                except Exception as e: logger.warning(f"Err format portfolio time: {e}"); return str(x_value) if x_value else "--"
        period_map_display = {"1D":"24h","5D":"5d","1M":"1m","6M":"6m","YTD":"Aquest Any","1Y":"1a","5Y":"5a","MAX":"Màx"}
        return period_map_display.get(self.selected_period.upper(), f"Període: {self.selected_period}")
    @rx.var
    def main_portfolio_chart_figure(self) -> go.Figure:
        loading_fig=go.Figure().update_layout(height=300,annotations=[dict(text="Calculant gráfico...",showarrow=False)],paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis=dict(visible=False),yaxis=dict(visible=False))
        error_fig=go.Figure().update_layout(height=300,annotations=[dict(text="Sense dades portfolio.",showarrow=False)],paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis=dict(visible=False),yaxis=dict(visible=False))
        if self.is_loading_portfolio_chart and (not isinstance(self.portfolio_chart_data, pd.DataFrame) or self.portfolio_chart_data.empty): return loading_fig
        df=self.portfolio_chart_data
        if not isinstance(df,pd.DataFrame)or df.empty or'total_value'not in df.columns or'time'not in df.columns: logger.warning(f"main_portfolio_chart: Invalid DF. Cols:{df.columns if isinstance(df,pd.DataFrame)else 'NoDF'}"); return error_fig
        try:
            df_chart=df.copy();df_chart['time']=pd.to_datetime(df_chart['time'],errors='coerce',utc=True);df_chart['total_value']=pd.to_numeric(df_chart['total_value'],errors='coerce');df_chart=df_chart.dropna(subset=['time','total_value']).sort_values(by='time')
            if df_chart.empty or len(df_chart)<1: logger.warning(f"main_portfolio_chart: DF vacío post-proc. Pts:{len(df_chart)}"); return error_fig
            fig=go.Figure();fig.add_trace(go.Scatter(x=df_chart['time'],y=df_chart['total_value'],mode='lines',line=dict(width=0),fill='tozeroy',fillcolor=self.portfolio_chart_area_color,hoverinfo='skip'));fig.add_trace(go.Scatter(x=df_chart['time'],y=df_chart['total_value'],mode='lines',line=dict(color=self.portfolio_chart_color,width=2.5,shape='spline'),name='Valor Total',hovertemplate='<b>Valor:</b> $%{y:,.2f}<br><b>Fecha:</b> %{x|%d %b %Y, %H:%M}<extra></extra>'))
            min_v,max_v=df_chart['total_value'].min(),df_chart['total_value'].max();padding=(max_v-min_v)*0.1 if(max_v!=min_v)else abs(min_v)*0.1 or 1000;range_min,range_max=min_v-padding,max_v+padding
            fig.update_layout(height=300,margin=dict(l=50,r=10,t=10,b=30),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis=dict(showgrid=False,zeroline=False,tickmode='auto',nticks=6,showline=True,linewidth=1,linecolor='var(--gray-a6)',tickangle=-30,tickfont=dict(color="var(--gray-11)")),yaxis=dict(title=None,showgrid=True,gridcolor='var(--gray-a4)',zeroline=False,showline=False,side='left',tickformat="$,.0f",range=[range_min,range_max],tickfont=dict(color="var(--gray-11)")),hovermode='x unified',showlegend=False);return fig
        except Exception as e:logger.error(f"Err main_portfolio_chart_figure: {e}", exc_info=True);return error_fig

    @rx.var
    def stock_detail_chart_change_info(self)->Dict[str,Any]:
        df=self.current_stock_history; current_price_from_info = self.current_stock_info.get("currentPrice", self.current_stock_info.get("regularMarketPrice", 0.0))
        try: last_price_fallback = float(current_price_from_info)
        except (ValueError, TypeError): last_price_fallback = 0.0
        default_info={"last_price":last_price_fallback,"change":0.0,"percent_change":0.0,"is_positive":None,"first_price_time":None,"last_price_time":None}
        if not isinstance(df,pd.DataFrame)or df.empty or'price'not in df.columns or'time'not in df.columns:return default_info
        prices_series=df['price'].dropna(); times_series=df.loc[prices_series.index,'time'].dropna(); prices_series=prices_series.loc[times_series.index]
        if prices_series.empty or len(prices_series)<1:return default_info
        last_f=float(prices_series.iloc[-1]);last_t=pd.to_datetime(times_series.iloc[-1]);default_info["last_price"]=last_f;default_info["last_price_time"]=last_t
        if len(prices_series)<2:return default_info
        first_f=float(prices_series.iloc[0]);first_t=pd.to_datetime(times_series.iloc[0]);change_f=last_f-first_f
        percent_f=(change_f/first_f*100)if first_f!=0 else 0.0;is_positive=change_f>0 if change_f!=0 else (None if change_f==0 else False)
        return{"last_price":last_f,"change":change_f,"percent_change":percent_f,"is_positive":is_positive,"first_price_time":first_t,"last_price_time":last_t}

    @rx.var
    def stock_detail_display_price(self)->str:
        hover_info=self.stock_detail_chart_hover_info;change_info=self.stock_detail_chart_change_info
        price_to_display=change_info.get("last_price",0.0);currency_symbol=self.current_stock_info.get("currencySymbol","$")
        if hover_info and"y"in hover_info:
            hover_y_data=hover_info["y"];y_to_convert=hover_y_data[0]if isinstance(hover_y_data,list)and hover_y_data else hover_y_data
            if y_to_convert is not None:
                try:price_to_display=float(y_to_convert)
                except:pass
        return f"{currency_symbol}{price_to_display:,.2f}"
    @rx.var
    def is_current_stock_info_empty(self)->bool: return not self.current_stock_info or"error"in self.current_stock_info or not self.current_stock_info.get("symbol")
    @rx.var
    def current_stock_metrics_list(self)->List[Tuple[str,str]]: return list(self.current_stock_metrics.items()) if self.current_stock_metrics else []
    @rx.var
    def stock_detail_display_time_or_change(self)->str:
        hover_info=self.stock_detail_chart_hover_info;change_info=self.stock_detail_chart_change_info
        if hover_info and"x"in hover_info:
            x_data=hover_info["x"];x_value=x_data[0]if isinstance(x_data,list)and x_data else x_data
            if x_value is not None:
                try:
                    dt_obj=pd.to_datetime(x_value);last_t=change_info.get("last_price_time");first_t=change_info.get("first_price_time")
                    show_time=self.current_stock_selected_period.upper()in["1D","5D"]
                    if not show_time and last_t and first_t and isinstance(last_t,pd.Timestamp)and isinstance(first_t,pd.Timestamp):
                        if(last_t-first_t).days<2:show_time=True
                    return dt_obj.strftime('%d %b, %H:%M')if show_time else dt_obj.strftime('%d %b %Y')
                except:return str(x_value)if x_value else"--"
        change_val=change_info.get("change",0.0);percent_change_val=change_info.get("percent_change",0.0);currency_symbol=self.current_stock_info.get("currencySymbol","$")
        period_map_display={"1D":"Avui","5D":"5 Dies","1M":"1 Mes","6M":"6 Mesos","YTD":"Aquest Any","1A":"1 Any","1Y":"1 Any","5A":"5 Anys","5Y":"5 Anys","MAX":"Màxim"}
        period_display_name=period_map_display.get(self.current_stock_selected_period.upper(),self.current_stock_selected_period)
        return f"{currency_symbol}{change_val:+.2f} ({percent_change_val:+.2f}%) {period_display_name}"
    @rx.var
    def stock_detail_change_color(self)->str:
        if self.stock_detail_chart_hover_info and"x"in self.stock_detail_chart_hover_info:return"var(--gray-11)"
        is_positive=self.stock_detail_chart_change_info.get("is_positive")
        if is_positive is True:return"var(--green-10)"
        if is_positive is False:return"var(--red-10)"
        return"var(--gray-11)"
    @rx.var
    def current_stock_change_color(self) -> str:
        change = self.current_stock_info.get('change', 0.0);
        if not isinstance(change, (int, float)): change = 0.0
        if change > 0: return "var(--green-10)"
        elif change < 0: return "var(--red-10)"
        return "var(--gray-11)"
    @rx.var
    def stock_detail_chart_figure(self) -> go.Figure:
        df = self.current_stock_history
        loading_fig = go.Figure().update_layout(height=350, annotations=[dict(text="Cargando gráfico...", showarrow=False)], paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))
        error_fig = go.Figure().update_layout(height=350, annotations=[dict(text="Datos de gráfico no disponibles.", showarrow=False)], paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))
        if self.is_loading_current_stock_details and (not isinstance(df, pd.DataFrame) or df.empty): return loading_fig
        if not isinstance(df, pd.DataFrame) or df.empty or not all(c in df.columns for c in ['time', 'price']):
            logger.warning(f"stock_detail_chart_figure: Invalid DF for {self.viewing_stock_symbol}. Cols:{df.columns if isinstance(df,pd.DataFrame)else 'NoDF'}")
            return error_fig
        try:
            prices_series = df["price"].dropna()
            if prices_series.empty: logger.warning(f"stock_detail_chart_figure: No prices after dropna for {self.viewing_stock_symbol}."); return error_fig
            times_series = pd.to_datetime(df.loc[prices_series.index, "time"], utc=True, errors='coerce').dropna()
            valid_indices = times_series.index; final_prices = prices_series.loc[valid_indices]; final_times = times_series
            if final_prices.empty or len(final_prices) < 1: logger.warning(f"stock_detail_chart_figure: Empty series after align for {self.viewing_stock_symbol}."); return error_fig
            fig = go.Figure(); line_color = "var(--gray-9)"; fill_color_base = '128,128,128'
            if len(final_prices) >= 2:
                if final_prices.iloc[-1] > final_prices.iloc[0]: line_color = "var(--green-9)"; fill_color_base = '34,197,94'
                elif final_prices.iloc[-1] < final_prices.iloc[0]: line_color = "var(--red-9)"; fill_color_base = '239,68,68'
            fill_color_rgba = f"rgba({fill_color_base},0.1)"
            fig.add_trace(go.Scatter(x=final_times, y=final_prices, mode="lines", line=dict(color=line_color, width=2, shape='spline'), fill='tozeroy', fillcolor=fill_color_rgba, hovertemplate='<b>Precio:</b> $%{y:,.2f}<br><b>Fecha:</b> %{x|%d %b %Y, %H:%M}<extra></extra>'))
            min_p, max_p = final_prices.min(), final_prices.max(); y_padding = (max_p - min_p) * 0.1 if (max_p != min_p) else abs(min_p) * 0.1 or 1.0; y_range = [min_p - y_padding, max_p + y_padding]
            fig.update_layout(height=350, margin=dict(l=50, r=10, t=10, b=30), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False, zeroline=False, tickmode="auto", nticks=6, showline=True, linewidth=1, linecolor="var(--gray-a6)", tickangle=-30, tickfont=dict(color="var(--gray-11)")), yaxis=dict(title=None, showgrid=True, gridcolor="var(--gray-a4)", zeroline=False, showline=False, side="left", tickformat="$,.2f", tickfont=dict(color="var(--gray-11)"), range=y_range), hovermode='x unified', showlegend=False)
            return fig
        except Exception as e: logger.error(f"Exception gen stock_detail_chart_figure for {self.viewing_stock_symbol}: {e}", exc_info=True); return error_fig

    # --- Event Handlers de UI ---
    def portfolio_chart_handle_hover(self, event_data: List):
        new_hover_info = None; points = None
        if event_data and isinstance(event_data, list) and event_data[0] and isinstance(event_data[0], dict): points = event_data[0].get('points')
        if points and isinstance(points, list) and points[0] and isinstance(points[0], dict): new_hover_info = points[0]
        if self.portfolio_chart_hover_info != new_hover_info: self.portfolio_chart_hover_info = new_hover_info
    def portfolio_chart_handle_unhover(self, _):
        if self.portfolio_chart_hover_info is not None: self.portfolio_chart_hover_info = None
    def portfolio_toggle_change_display(self):
        self.portfolio_show_absolute_change = not self.portfolio_show_absolute_change
    def stock_detail_chart_handle_hover(self, event_data: List):
        new_hover_info = None
        if event_data and isinstance(event_data, list) and event_data[0] and isinstance(event_data[0], dict):
            points = event_data[0].get('points')
            if points and isinstance(points, list) and points[0] and isinstance(points[0], dict): new_hover_info = points[0]
        if self.stock_detail_chart_hover_info != new_hover_info: self.stock_detail_chart_hover_info = new_hover_info
    def stock_detail_chart_handle_unhover(self, _):
        if self.stock_detail_chart_hover_info is not None: self.stock_detail_chart_hover_info = None

    # --- Métodos de Noticias ---
    def _create_fallback_news(self):
        logger.warning("Creating fallback news item.")
        self.processed_news = [NewsArticle(title="Error al cargar noticias", url="#", publisher="Sistema", date=datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M"), summary="No se pudieron obtener las noticias.", image="")]
        self.has_news = True

    @rx.event
    async def get_news(self, new_query: Optional[str] = None):
        if self.is_loading_news: return
        self.is_loading_news = True
        if new_query is not None:
            self.SEARCH_QUERY = new_query.strip() if new_query.strip() else DEFAULT_SEARCH_QUERY
            self.news_page = 1; self.processed_news = []; self.has_news = False
        
        if not GNEWS_API_KEY or GNEWS_API_KEY == "YOUR_GNEWS_API_KEY_HERE": 
            logger.error("CRÍTICO: GNEWS_API_KEY no está configurada o es el placeholder.")
            self._create_fallback_news()
            self.is_loading_news = False
            return

        logger.info(f"Fetching news: '{self.SEARCH_QUERY}', page: {self.news_page}")
        try:
            params = {"q": self.SEARCH_QUERY, "token": GNEWS_API_KEY, "lang": "es", "country": "any", "max": self.max_articles, "sortby": "publishedAt", "page": self.news_page}
            response = await asyncio.to_thread(requests.get, GNEWS_API_URL, params=params, timeout=10)
            response.raise_for_status(); data = response.json(); articles = data.get("articles", [])
            if not articles:
                if self.news_page == 1: self._create_fallback_news()
                else: self.has_news = False 
                self.is_loading_news = False; return
            page_articles = []
            for article in articles:
                try:
                    dt_obj = datetime.fromisoformat(article.get("publishedAt","").replace("Z", "+00:00")) if article.get("publishedAt") else datetime.now(timezone.utc)
                    page_articles.append(NewsArticle(title=article.get("title","S/T"), url=article.get("url","#"), publisher=article.get("source",{}).get("name","N/A"), date=dt_obj.strftime("%d %b %Y, %H:%M"), summary=article.get("description","N/A."), image=article.get("image","")))
                except Exception as e_art: logger.error(f"Error processing article: {article.get('title')}, Error: {e_art}", exc_info=True)
            if self.news_page == 1: self.processed_news = page_articles
            else: self.processed_news.extend(page_articles)
            self.has_news = bool(self.processed_news)
            if articles and len(articles) == self.max_articles : self.news_page += 1
            else: self.has_news = bool(self.processed_news) 
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error fetching news: {http_err.response.status_code} - {http_err.response.text}", exc_info=False) 
            if not self.processed_news: self._create_fallback_news()
        except requests.exceptions.RequestException as e_req: 
            logger.error(f"Network error fetching news: {e_req}", exc_info=False)
            if not self.processed_news: self._create_fallback_news()
        except Exception as e: 
            logger.error(f"General error fetching news: {e}", exc_info=True)
            if not self.processed_news: self._create_fallback_news()
        finally: 
            self.is_loading_news = False
            if not self.processed_news and self.news_page == 1: self._create_fallback_news()

    @rx.event
    async def load_more_news(self):
        if not self.is_loading_news : await self.get_news()

    @rx.event
    async def set_news_search_query_and_fetch(self, query: str): await self.get_news(new_query=query)
    
    # --- MÉTODOS DE BÚSQUEDA GLOBAL ---
    def set_search_term(self, term: str):
        self.search_term = term; self.error_message = ""

    @rx.event
    async def search_stock_global(self):
        if not self.search_term: self.error_message = "Introduce símbolo/nombre."; return
        self.is_searching = True; self.error_message = ""
        query_upper = self.search_term.strip().upper(); symbol_to_fetch = COMPANY_MAP.get(query_upper, query_upper)
        logger.info(f"AuthState global search: '{self.search_term}', ticker '{symbol_to_fetch}'")
        sri = SearchResultItem() 
        try:
            ticker_obj = await asyncio.to_thread(yf.Ticker, symbol_to_fetch)
            info = await asyncio.to_thread(lambda: ticker_obj.info)
            if not info or ("price" not in info and "currentPrice" not in info and "regularMarketPrice" not in info):
                self.error_message = f"No info para '{self.search_term}' ({symbol_to_fetch})."; sri.Name=f"No encontrado: {symbol_to_fetch}"; self.search_result=sri; return
            price_val = info.get("currentPrice", info.get("regularMarketPrice", info.get("previousClose",0.0)))
            price_str = f"{info.get('currencySymbol','$')}{float(price_val):,.2f}" if isinstance(price_val,(int,float)) else "N/A"
            sri.Symbol=info.get("symbol",symbol_to_fetch); sri.Name=info.get("longName",info.get("shortName",symbol_to_fetch)); sri.Current_Price=price_str; sri.Logo=info.get("logo_url", f"/{symbol_to_fetch.upper()}.png")
            self.search_result = sri 
        except Exception as e: logger.error(f"Error search_stock_global {symbol_to_fetch}: {e}", exc_info=True); self.error_message = f"Error buscando '{self.search_term}'."; sri.Name=f"Error buscando {self.search_term}"; self.search_result=sri
        finally: self.is_searching = False
        
    @rx.event
    def go_to_stock_detail_global(self, symbol: str):
        if symbol and symbol != "N/A" and symbol != "No encontrado" and not symbol.startswith("Error"): return rx.redirect(f"/detalles_accion/{symbol.upper().strip()}")
        return rx.window_alert("No se puede navegar para este resultado.")

print("AuthState CLASS DEFINITION PARSED AT END OF FILE (v11 - GNews Key updated, buy/sell logs)")
