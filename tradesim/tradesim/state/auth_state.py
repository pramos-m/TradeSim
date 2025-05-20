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
import traceback # Para traceback.print_exc()
import httpx

from ..database import SessionLocal, DEFAULT_SECTOR_ID 
from sqlalchemy import select, func 
from ..controller.user import get_user_by_id
from ..models.user import User
from ..models.stock import Stock, Stock as StockModel 
from ..models.stock_price_history import StockPriceHistory
from ..models.transaction import StockTransaction, TransactionType
from ..models.portfolio_item import PortfolioItemDB
from ..models.sector import Sector as SectorModel 
from ..controller.transaction import get_transaction_history_with_profit_loss 


logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO)

# --- CONSTANTES ---
SECRET_KEY = os.getenv("SECRET_KEY", "a-very-secret-key-here-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
DEFAULT_AVATAR = "/default_avatar.png" 
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "46ad3b8bbfa80ad174197e906e265525") 
GNEWS_API_URL = "https://gnews.io/api/v4/search"
DEFAULT_SEARCH_QUERY = "mercado acciones finanzas"

# Mapeo de nombres de empresas a símbolos
company_map = {
    "APPLE": "AAPL", "MICROSOFT": "MSFT", "GOOGLE": "GOOG", "ALPHABET": "GOOG",
    "AMAZON": "AMZN", "META": "META", "FACEBOOK": "META", "TESLA": "TSLA",
    "NVIDIA": "NVDA", "BERKSHIRE HATHAWAY": "BRK.B", "JPMORGAN": "JPM",
    "VISA": "V", "UNITEDHEALTH": "UNH", "HOME DEPOT": "HD",
    "PROCTER & GAMBLE": "PG", "MASTERCARD": "MA", "ELI LILLY": "LLY",
}

# Mapeo de símbolos a URLs de logos locales
STOCK_LOGOS = {
    "AAPL": "/AAPL.png",
    "MSFT": "/MSFT.png",
    "GOOG": "/GOOGL.png",
    "AMZN": "/AMZN.png",
    "META": "/META.png",
    "TSLA": "/TSLA.png",
    "NVDA": "/NVDA.png",
    "BRK.B": "/BRK.B.png",
    "JPM": "/JPM.png",
    "V": "/V.png",
    "UNH": "/UNH.png",
    "HD": "/HD.png",
    "PG": "/PG.png",
    "MA": "/MA.png",
    "LLY": "/LLY.png",
}

def get_stock_logo_url(symbol: str) -> str:
    """Obtiene la URL del logo de una acción usando el mapeo local o Clearbit."""
    if not symbol:
        return "/assets/default_logo.png"
    
    # Primero intentar con el mapeo local
    symbol_upper = symbol.upper()
    local_logo = STOCK_LOGOS.get(symbol_upper)
    if local_logo:
        # Ensure the local_logo path does not already start with /assets/ before adding it
        if local_logo.startswith('/assets/'):
            return local_logo
        elif local_logo.startswith('/'):
            # If it starts with '/' but not '/assets/', add '/assets' before it
            return f"/assets{local_logo}"
        else:
            # If it's just a filename, prepend /assets/
            return f"/assets/{local_logo}"

    # Si no está en el mapeo local, intentar con Clearbit
    try:
        # Limpiar el símbolo para el dominio
        domain_symbol = symbol_upper.split('.')[0]  # Quitar sufijos como .B
        clearbit_domain = f"{domain_symbol.lower()}.com"
        clearbit_url = f"https://logo.clearbit.com/{clearbit_domain}"
        return clearbit_url
    except Exception as e:
        logger.warning(f"Error getting Clearbit logo for {symbol}: {e}")
        # Fallback to a default logo path, ensuring it's correctly formatted
        return f"/assets/{symbol_upper.lower()}.png" # Use lowercase symbol for potential asset filename consistency, ensure /assets/


# --- MODELOS Pydantic/rx.Base para el Estado ---
class NewsArticle(rx.Base):
    title: str; url: str; publisher: str; date: str; summary: str; image: str = "/assets/default_news.png"  # Valor por defecto para imágenes de noticias

class PortfolioItem(rx.Base): 
    symbol: str; name: str; quantity: int; current_price: float; current_value: float; logo_url: str

class SearchResultItem(rx.Base): 
    Symbol: str = "N/A"; Name: str = "No encontrado"; Current_Price: str = "N/A"; Logo: str = "/assets/default_logo.png"

class TransactionDisplayItem(rx.Base): 
    timestamp: str; symbol: str; quantity: int; price: float; type: str
    @property
    def formatted_quantity(self) -> str:
        sign = "+" if self.type.lower() == TransactionType.COMPRA.value.lower() else "-"
        return f"{sign}{abs(self.quantity)}"

class AuthState(rx.State):
    # Variables de estado esenciales
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
    show_password: bool = False
    password_field_type: str = "password"

    # Variables del portfolio y transacciones
    portfolio_items: List[PortfolioItem] = []
    total_portfolio_value: float = 0.0
    portfolio_chart_hover_info: Optional[Dict] = None
    portfolio_chart_change_info: Optional[Dict] = None
    portfolio_show_absolute_change: bool = False
    selected_period: str = "1M"
    recent_transactions: List[TransactionDisplayItem] = []
    portfolio_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'total_value'])
    is_loading_portfolio_chart: bool = False
    pnl: float = 0.0
    daily_pnl: float = 0.0
    monthly_pnl: float = 0.0
    yearly_pnl: float = 0.0
    daily_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
    monthly_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
    yearly_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
    total_invested: float = 0.0
    portfolio_value: float = 0.0

    # Variables de detalle de acción
    viewing_stock_symbol: str = ""
    current_stock_info: Dict[str, Any] = {}
    current_stock_metrics: Dict[str, str] = {}
    current_stock_history: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
    current_stock_shares_owned: int = 0
    stock_detail_chart_hover_info: Optional[Dict] = None
    current_stock_selected_period: str = "1M"
    transaction_message: str = ""
    buy_sell_quantity: int = 0
    is_loading_current_stock_details: bool = False

    # Variables de noticias
    processed_news: List[NewsArticle] = []
    recent_news_list: List[NewsArticle] = []
    featured_news: Optional[NewsArticle] = None
    is_loading_news: bool = False
    selected_news_style: str = "panel"
    can_load_more: bool = True
    news_page: int = 1
    SEARCH_QUERY: str = DEFAULT_SEARCH_QUERY

    # Variables de búsqueda
    search_term: str = ""
    search_results: List[SearchResultItem] = []
    is_searching: bool = False

    def toggle_password_visibility(self):
        self.show_password = not self.show_password
        self.password_field_type = "text" if self.show_password else "password"

    @rx.event
    def change_news_style(self, style: str):
        """Cambia el estilo de visualización de noticias ('panel' o 'publicaciones')."""
        if style in ["panel", "publicaciones"]:
            self.selected_news_style = style
            logger.info(f"News display style changed to: {self.selected_news_style}")
        else:
            logger.warning(f"Invalid news display style requested: {style}. Keeping current style: {self.selected_news_style}")

    # --- Métodos de Autenticación (sin cambios respecto a v13) ---
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
        self.portfolio_chart_data = pd.DataFrame(columns=['time', 'total_value']) # Limpiar datos del gráfico también
        self.portfolio_value = 0.0 # Limpiar portfolio_value
        self.total_invested = 0.0 # Limpiar total_invested
        self.pnl = 0.0 # Limpiar pnl
        self.daily_pnl = 0.0; self.monthly_pnl = 0.0; self.yearly_pnl = 0.0 # Limpiar PnLs por período
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
            # Después del login exitoso, cargar datos del portfolio y otros
            await asyncio.gather(
                self._update_portfolio_value(),
                self._update_total_invested(),
                self._update_pnl(),
                self._update_portfolio_chart_data(),
                # await self._update_yearly_pnl_chart_data() # Si este método existe y lo necesitas
                self._load_recent_transactions(),
                self.load_portfolio()
            )
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
            # Después del registro exitoso, cargar datos del portfolio y otros
            await asyncio.gather(
                self._update_portfolio_value(),
                self._update_total_invested(),
                self._update_pnl(),
                self._update_portfolio_chart_data(),
                # await self._update_yearly_pnl_chart_data() # Si este método existe y lo necesitas
                self._load_recent_transactions(),
                self.load_portfolio()
            )
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
        """Event to run when the page loads."""
        current_path = self.router.page.path
        logger.info(f"AuthState.on_load: Path='{current_path}', Token? {'Yes' if self.auth_token else 'No'}, Processed? {self.processed_token}, Auth? {self.is_authenticated}")
        
        # Establecer la pestaña activa en función de la ruta si no se ha procesado el token
        # Esto ayuda a que las pestañas de login/registro sean correctas al acceder directamente por URL
        if not self.processed_token:
            if current_path == "/login" and self.active_tab != "login": self.active_tab = "login"
            elif current_path == "/registro" and self.active_tab != "register": self.active_tab = "register"
        
        # Evitar procesamiento duplicado en el mismo path si ya se procesó el token y el estado de auth es el mismo
        # Se añade la verificación del user_id para evitar problemas si cambia de usuario con el mismo token (caso raro, pero seguro)
        user_id_from_token_check = self._get_user_id_from_token(self.auth_token)
        is_auth_consistent = self.is_authenticated == (user_id_from_token_check > 0 and self.user_id == user_id_from_token_check)
        if self.processed_token and self.last_path == current_path and is_auth_consistent:
             logger.info(f"AuthState.on_load: Ya procesado para '{current_path}' con estado de auth consistente."); return
        
        self.last_path = current_path # Actualizar el último path procesado
        db = None
        original_is_authenticated = self.is_authenticated # Guardar estado original por si hay redirección/logout durante el proceso

        try:
            # Lógica para validar token y establecer estado de autenticación
            if self.auth_token:
                user_id_from_token = self._get_user_id_from_token(self.auth_token)
                if user_id_from_token > 0:
                    db = SessionLocal()
                    user = await asyncio.to_thread(get_user_by_id, db, user_id_from_token)
                    if user:
                        if not self.is_authenticated or self.user_id != user.id:
                            self._set_user_state(user)
                        logger.info(f"AuthState.on_load: User {self.email} (ID: {self.user_id}) autenticado vía token.")
                        
                        # Si está autenticado e intenta acceder a login/registro o raíz, redirigir al dashboard
                        if current_path in ["/login", "/registro", "/"]: 
                            self.processed_token = True
                            # No retornar rx.redirect aquí, dejar que la lógica de carga de datos se ejecute
                            # y la redirección se manejará al final si es necesario.
                            return rx.redirect("/dashboard") # Redirigir explícitamente aquí
                            
                    else: 
                        logger.warning(f"AuthState.on_load: User ID {user_id_from_token} del token no en BD. Limpiando."); 
                        self._clear_auth_state()
                else: 
                    logger.info("AuthState.on_load: Token inválido/expirado. Limpiando."); 
                    self._clear_auth_state()
            else: 
                logger.info("AuthState.on_load: No hay token. Asegurando no autenticado."); 
                if self.is_authenticated: # Si previamente estaba autenticado (quizás por estado persistente sin token válido)
                    self._clear_auth_state()
            
            # Lógica de protección de rutas
            # Si NO está autenticado Y está en una ruta protegida, redirigir a login
            protected_route_prefixes = ["/dashboard", "/profile", "/noticias", "/detalles_accion", "/aprender"] # Ajusta según tus rutas
            is_on_protected_route = any(current_path.startswith(p) for p in protected_route_prefixes)
            
            # Verificar el estado de autenticación *después* de intentar validar el token
            if not self.is_authenticated and is_on_protected_route:
                 logger.info(f"AuthState.on_load: No autenticado en ruta protegida '{current_path}'. Redirigiendo a /login.")
                 self.processed_token = True
                 # No retornar rx.redirect aquí si quieres cargar datos incluso sin autenticación en rutas no protegidas
                 return rx.redirect("/login") # Redirigir explícitamente aquí

            # --- Lógica de carga de datos para usuarios AUTENTICADOS ---
            # Esta parte se ejecuta si el usuario *está* autenticado después de la verificación del token
            # y no fue redirigido por estar en login/registro estando autenticado.
            if self.is_authenticated and self.user_id:
                logger.info(f"AuthState.on_load: Usuario autenticado (ID: {self.user_id}). Intentando cargar datos del portfolio...")
                try:
                    # Cargar los datos necesarios para el dashboard y otras páginas autenticadas
                    await asyncio.gather(
                        self._update_portfolio_value(),
                        self._update_total_invested(),
                        self._update_pnl(),
                        self._update_portfolio_chart_data(),
                        # await self._update_yearly_pnl_chart_data(), # Descomentar si este método existe
                        self._load_recent_transactions(),
                        self.load_portfolio() # load_portfolio también actualiza total_portfolio_value
                    )
                    logger.info("Datos del portfolio y transacciones actualizados en on_load.")
                except Exception as e_portfolio:
                    logger.error(f"Error en on_load al actualizar datos del portfolio/transacciones: {e_portfolio}", exc_info=True)
            else:
                 # Este caso cubre:
                 # 1. Usuario no autenticado que accede a una ruta NO protegida.
                 # 2. Usuario que estaba autenticado (original_is_authenticated True) pero fue desautenticado en este on_load.
                 # En ambos casos, no cargamos datos específicos del portfolio de un usuario autenticado.
                 if original_is_authenticated and not self.is_authenticated:
                     logger.info("AuthState.on_load: El usuario estaba autenticado pero fue desautenticado. No se cargan datos del portfolio.")
                 else:
                     logger.info(f"AuthState.on_load: Usuario no autenticado o en ruta no protegida. No se cargan datos del portfolio de usuario en este paso.")

        except Exception as e: 
            logger.error(f"AuthState.on_load: Error general durante el procesamiento del token o redirección: {e}", exc_info=True); 
            # En caso de un error inesperado, limpiar estado y redirigir a login por seguridad.
            self._clear_auth_state()
            self.processed_token = True
            return rx.redirect("/login")
        finally:
            if db: await asyncio.to_thread(db.close)
        
        # Marcar el token como procesado solo si no hubo una redirección explícita ya manejada.
        # Si se llamó a rx.redirect, el estado se limpiará en la próxima carga de página.
        # Si no hubo redirección, entonces la carga fue exitosa o el usuario está en una página pública.
        self.processed_token = True
        logger.info(f"AuthState.on_load: Finalizado para '{current_path}'. Autenticado: {self.is_authenticated}. Token procesado: {self.processed_token}")


    @rx.event
    def set_buy_sell_quantity(self, value: str):
        try: self.buy_sell_quantity = max(1, int(value) if value else 1)
        except (ValueError, TypeError): self.buy_sell_quantity = 1

    @rx.event
    async def set_period(self, period: str):
        self.selected_period = period; self.portfolio_chart_hover_info = None
        logger.info(f"Periodo portfolio cambiado a {period}. Actualizando gráfico.")

    @rx.event
    async def set_current_stock_period(self, period: str):
        self.current_stock_selected_period = period
        self.stock_detail_chart_hover_info = None
        logger.info(f"Período de detalle de acción cambiado a {period}. Actualizando gráfico para {self.viewing_stock_symbol}.")
        await self._update_current_stock_chart_data_internal()

    async def _load_current_stock_shares_owned(self):
        logger.info(f"AuthState._load_current_stock_shares_owned para user {self.user_id} y symbol {self.viewing_stock_symbol}")
        self.current_stock_shares_owned = 0
        if not self.user_id or not self.viewing_stock_symbol:
            logger.info("_load_current_stock_shares_owned: No user_id o symbol. Shares 0.")
            return
        db = None
        try:
            db = SessionLocal()
            stock_db = await asyncio.to_thread(db.query(StockModel).filter(StockModel.symbol == self.viewing_stock_symbol).first)
            if not stock_db:
                logger.info(f"_load_current_stock_shares_owned: Stock {self.viewing_stock_symbol} no en BD local. Shares 0.")
                return
            
            # Calcular cantidad neta de transacciones para este usuario y stock
            txs_query = select(StockTransaction.transaction_type, StockTransaction.quantity).where(
                StockTransaction.user_id == self.user_id,
                StockTransaction.stock_id == stock_db.id
            )
            txs = await asyncio.to_thread(db.execute, txs_query)
            txs_results = txs.all()

            buys = sum(t.quantity for t in txs_results if t.transaction_type == TransactionType.COMPRA)
            sells = sum(t.quantity for t in txs_results if t.transaction_type == TransactionType.VENTA)
            
            self.current_stock_shares_owned = int(buys - sells)
            logger.info(f"_load_current_stock_shares_owned: Acciones de {self.viewing_stock_symbol} poseídas: {self.current_stock_shares_owned} (B:{buys}, S:{sells})")
        except Exception as e:
            logger.error(f"Error cargando shares de {self.viewing_stock_symbol}: {e}", exc_info=True);
            self.current_stock_shares_owned = 0
        finally:
            if db: await asyncio.to_thread(db.close)

    async def _generate_mock_stock_data(self, num_points=30) -> pd.DataFrame:
        logger.info("Generating mock stock data.")
        end_date = datetime.now(timezone.utc); start_date = end_date - timedelta(days=num_points -1)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        # Asegurar precios base más razonables para mock
        base_price = random.uniform(50, 500)
        prices = [max(1.0, base_price + i*random.uniform(-0.5,0.5) + random.choice([-1,1])*i*random.uniform(0.01,0.1)) for i in range(len(dates))]
        
        df = pd.DataFrame({'time': dates, 'price': prices})
        logger.info(f"Generated {len(df)} points of mock stock data.")
        return df

    async def _generate_mock_portfolio_data(self, num_points=30) -> pd.DataFrame:
        logger.info("Generating mock portfolio data.")
        end_date = datetime.now(timezone.utc); start_date = end_date - timedelta(days=num_points -1)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        # Asegurar valores base más altos para portfolio mock
        base_value = random.uniform(10000, 50000)
        values = [max(100.0, base_value + i*random.uniform(-100,100) + random.choice([-1,1])*i*random.uniform(5,20)) for i in range(len(dates))]
        
        df = pd.DataFrame({'time': dates, 'total_value': values})
        logger.info(f"Generated {len(df)} points of mock portfolio data.")
        return df

    async def _update_portfolio_chart_data(self):
        """
        Calcula el valor histórico del portfolio sumando el valor de las acciones poseídas
        en cada punto del tiempo, utilizando los precios históricos de la base de datos.
        """
        logger.info(f"AuthState._update_portfolio_chart_data para user_id: {self.user_id}")
        if not self.is_authenticated or not self.user_id:
            self.portfolio_chart_data = pd.DataFrame(columns=['time', 'total_value'])
            logger.warning("UPD PORTF CHART: No auth, DF vacío.")
            return

        def get_portfolio_chart_data_sync(user_id):
            db = SessionLocal()
            try:
                transactions = db.query(StockTransaction).filter(StockTransaction.user_id == user_id).order_by(StockTransaction.timestamp).all()

                if not transactions:
                    logger.info(f"No hay transacciones para user_id {user_id} para el gráfico. Retornando DF vacío.")
                    return pd.DataFrame(columns=['time', 'total_value'])

                current_net_holdings: Dict[int, int] = {}
                for tx in transactions:
                    if tx.stock_id not in current_net_holdings:
                        current_net_holdings[tx.stock_id] = 0
                    if tx.transaction_type == TransactionType.COMPRA:
                        current_net_holdings[tx.stock_id] += tx.quantity
                    elif tx.transaction_type == TransactionType.VENTA:
                        current_net_holdings[tx.stock_id] -= tx.quantity

                held_stock_ids = [stock_id for stock_id, qty in current_net_holdings.items() if qty > 0]

                if not held_stock_ids:
                    logger.info(f"Usuario {user_id} no tiene tenencias actuales > 0. Retornando DF vacío.")
                    return pd.DataFrame(columns=['time', 'total_value'])

                # --- CORRECTED PRICE HISTORY FETCH ---
                # Ensure we are executing the query and getting results within the sync function
                price_history_query_result = db.execute(
                    select(
                        StockPriceHistory.timestamp,
                        StockPriceHistory.stock_id,
                        StockPriceHistory.price
                    ).where(
                        StockPriceHistory.stock_id.in_(held_stock_ids)
                    ).order_by(StockPriceHistory.timestamp)
                ).all()

                # Convert the raw results to a list of dictionaries for DataFrame creation
                price_history_data = [{'timestamp': r.timestamp, 'stock_id': r.stock_id, 'price': r.price} for r in price_history_query_result]

                if not price_history_data:
                    logger.warning(f"No se encontró historial de precios en BD para los stocks {held_stock_ids}. Retornando DF vacío.")
                    return pd.DataFrame(columns=['time', 'total_value'])

                df_price_history = pd.DataFrame(price_history_data)

                # --- Rest of the DataFrame processing remains similar ---
                df_price_history['timestamp'] = pd.to_datetime(df_price_history['timestamp'], utc=True)
                df_price_history = df_price_history.rename(columns={'timestamp': 'time'})

                df_pivot = df_price_history.pivot_table(index='time', columns='stock_id', values='price')

                all_times = df_pivot.index
                portfolio_values_at_times = []

                for timestamp in all_times:
                    current_total_value = Decimal("0.0")
                    for stock_id in held_stock_ids:
                         price_at_ts = df_pivot.loc[:timestamp, stock_id].dropna().iloc[-1] if not df_pivot.loc[:timestamp, stock_id].dropna().empty else None
                         if price_at_ts is not None:
                             quantity = current_net_holdings[stock_id]
                             current_total_value += Decimal(str(price_at_ts)) * Decimal(str(quantity))
                    if current_total_value > 0:
                        portfolio_values_at_times.append({'time': timestamp, 'total_value': float(current_total_value)})

                if not portfolio_values_at_times:
                    logger.warning("No se pudieron calcular valores del portfolio a lo largo del tiempo. Retornando DF vacío.")
                    return pd.DataFrame(columns=['time', 'total_value'])

                df_portfolio_chart = pd.DataFrame(portfolio_values_at_times)
                df_portfolio_chart['time'] = pd.to_datetime(df_portfolio_chart['time'], utc=True)
                df_portfolio_chart['total_value'] = pd.to_numeric(df_portfolio_chart['total_value'], errors='coerce')
                df_portfolio_chart = df_portfolio_chart.dropna(subset=['time', 'total_value']).sort_values('time')

                logger.info(f"Datos REALES del gráfico de portfolio cargados para user {user_id}. {len(df_portfolio_chart)} puntos.")
                return df_portfolio_chart
            except Exception as e:
                logger.error(f"Error en get_portfolio_chart_data_sync para user {user_id}: {e}", exc_info=True)
                return pd.DataFrame(columns=['time', 'total_value']) # Return empty DF on error
            finally:
                db.close()

        df_chart = await asyncio.to_thread(get_portfolio_chart_data_sync, self.user_id)

        if isinstance(df_chart, pd.DataFrame) and not df_chart.empty:
             self.portfolio_chart_data = df_chart
        else:
             logger.warning("Fallback a MOCK DATA para gráfico de portfolio.")
             self.portfolio_chart_data = await self._generate_mock_portfolio_data()


    async def _fetch_stock_history_data_detail(self, symbol: str, period: str) -> pd.DataFrame:
        logger.info(f"Fetching yfinance history for stock detail: {symbol}, period {period}")
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
                if not date_col: logger.error(f"Columna de fecha no encontrada en yf history para {symbol}. Cols: {hist.columns.tolist()}"); return await self._generate_mock_stock_data(60) # Fallback a mock si falta columna clave
                
                hist = hist.rename(columns={date_col:'time','Close':'price'});
                hist['time']=pd.to_datetime(hist['time'],utc=True,errors='coerce');
                hist['price']=pd.to_numeric(hist['price'],errors='coerce');
                hist=hist.dropna(subset=['time','price']) # Eliminar filas con NaT o NaN en columnas clave

                if not hist.empty:
                    logger.info(f"YF history para {symbol} ({period}): {len(hist)} puntos.")
                    # Opcional: Guardar este historial en StockPriceHistory para uso futuro/portfolio chart
                    # Esta parte no se añade por defecto para no sobrecargar, pero es donde lo harías.
                    # await self._save_stock_history_to_db(symbol, hist[['time', 'price']])
                    return hist[['time','price']]
                    
            logger.warning(f"YF history vacío o con errores para {symbol} ({yf_p},{interval}). Usando MOCK.");
            return await self._generate_mock_stock_data(60) # Usar 60 puntos para mock de stock si falla la carga real
            
        except Exception as e:
            logger.error(f"Error fetching YF history para {symbol} ({period}): {e}",exc_info=True);
            return await self._generate_mock_stock_data(60) # Fallback a mock en caso de excepción

    # Nota: El método _save_stock_history_to_db() sería necesario si quieres persistir el historial de YFinance
    # en tu base de datos para usarlo en el gráfico del portfolio. Aquí no está implementado.


    async def _save_stock_history_to_db(self, symbol: str, history_df: pd.DataFrame):
        """Guarda el historial de precios de una acción en la base de datos."""
        logger.info(f"Attempting to save history for {symbol} to DB.")
        if history_df.empty or 'time' not in history_df.columns or 'price' not in history_df.columns:
             logger.warning(f"_save_stock_history_to_db: Empty or invalid history DF for {symbol}. Not saving.")
             return
        
        db = None
        try:
            db = SessionLocal()
            # Find the stock ID first
            stock_obj = await asyncio.to_thread(db.query(StockModel).filter(StockModel.symbol == symbol).first)
            if not stock_obj:
                 logger.error(f"_save_stock_history_to_db: Stock {symbol} not found in DB. Cannot save history.")
                 return
            
            stock_id = stock_obj.id

            # Prepare data for bulk insertion
            history_to_create = []
            # Ensure timestamps are timezone-aware and in UTC before saving
            history_df['time'] = pd.to_datetime(history_df['time'], utc=True, errors='coerce')
            history_df = history_df.dropna(subset=['time', 'price'])

            for index, row in history_df.iterrows():
                # Check if history for this timestamp and stock_id already exists to avoid duplicates
                # This check can be expensive. For large imports, consider bulk insert ignore or upsert logic.
                # For now, a simple check: retrieve count of existing entries for this timestamp and stock
                exists_count = await asyncio.to_thread(
                    lambda: db.query(StockPriceHistory)
                    .filter(
                        StockPriceHistory.stock_id == stock_id,
                        StockPriceHistory.timestamp == row['time']
                    )
                    .count()
                )
                
                if exists_count == 0:
                    # --- Debugging and Data Preparation for Bulk Insert ---
                    try:
                        price_val = row['price']
                        # logger.info(f"_save_stock_history_to_db: Processing row for {symbol} at time={row['time']}. Price value: {price_val} (Type: {type(price_val)}).")
                        
                        # Ensure price is not None or NaN before converting
                        if pd.isna(price_val) or price_val is None:
                             logger.warning(f"_save_stock_history_to_db: Skipping row for {symbol} at {row['time']} due to missing price.")
                             continue # Skip this iteration if price is missing

                        # Prepare dictionary for bulk insert
                        history_dict = {
                            "stock_id": stock_id,
                            "timestamp": row['time'],
                            "price": float(price_val) # Convert to float for insertion attempt
                        }
                        # logger.info(f"_save_stock_history_to_db: Prepared history dictionary: {history_dict}")
                        history_to_create.append(history_dict)
                        
                    except Exception as price_e:
                         logger.error(f"_save_stock_history_to_db: Error processing entry for {symbol} at {row['time']}: {price_e}", exc_info=True)
                         # Continue to the next row even if one fails
                    # --- End Debugging and Data Preparation for Bulk Insert ---

                # else: logger.debug(f"History for {symbol} at {row['time']} already exists.") # Optional: debug log for existing entries

            if history_to_create:
                logger.info(f"_save_stock_history_to_db: Adding {len(history_to_create)} new history entries for {symbol}.")
                # Use bulk_insert_mappings with dictionaries
                await asyncio.to_thread(db.bulk_insert_mappings, StockPriceHistory, history_to_create)
                await asyncio.to_thread(db.commit) # Commit the changes
                logger.info(f"_save_stock_history_to_db: Successfully saved {len(history_to_create)} history entries for {symbol}.")
            else:
                logger.info(f"_save_stock_history_to_db: No new history entries to save for {symbol}.")

        except Exception as e:
            logger.error(f"Error saving stock history for {symbol} to DB: {e}", exc_info=True)
            if db: await asyncio.to_thread(db.rollback) # Rollback on error
        finally:
            if db: await asyncio.to_thread(db.close) # Close the session

    async def _update_current_stock_chart_data_internal(self):
        logger.info(f"_update_current_stock_chart_data_internal: {self.viewing_stock_symbol} P:{self.current_stock_selected_period}")
        if not self.viewing_stock_symbol:
             self.current_stock_history=pd.DataFrame(columns=['time','price']);
             logger.info("_update_current_stock_chart_data_internal: No symbol. DF vacío.")
             return
        
        # Asegurarse de que tenemos info básica antes de intentar obtener historial
        if not self.current_stock_info or self.current_stock_info.get("symbol", "").upper() != self.viewing_stock_symbol.upper():
             logger.warning(f"_update_current_stock_chart_data_internal: Info básica para {self.viewing_stock_symbol} no cargada. Intentando cargarla...")
             # Intenta cargar info básica si no está disponible
             await self.load_stock_page_data(symbol=self.viewing_stock_symbol)
             # Si aún falla o hay error, no continuamos con el gráfico
             if not self.current_stock_info or self.current_stock_info.get("error"):
                 logger.error(f"_update_current_stock_chart_data_internal: Falló la carga de info básica para {self.viewing_stock_symbol}. No se cargará el gráfico.")
                 self.current_stock_history = pd.DataFrame(columns=['time','price']);
                 return

        df = await self._fetch_stock_history_data_detail(self.viewing_stock_symbol, self.current_stock_selected_period)
        
        # Save the fetched history data to the database
        if isinstance(df, pd.DataFrame) and not df.empty:
            await self._save_stock_history_to_db(self.viewing_stock_symbol, df)

        if isinstance(df,pd.DataFrame) and not df.empty:
             self.current_stock_history=df.sort_values(by='time');
             logger.info(f"Chart data {self.viewing_stock_symbol}: {len(df)} pts. cargados.")
        else:
             self.current_stock_history=await self._generate_mock_stock_data(60); # Fallback to mock if fetch or save failed or resulted in empty valid data
             logger.warning(f"Fallback MOCK chart data para {self.viewing_stock_symbol}.")


    @rx.event
    async def load_stock_page_data(self, symbol: str): 
        logger.info(f"load_stock_page_data: Iniciando para {symbol}")
        # Limpiar estado relacionado con la acción anterior
        self.viewing_stock_symbol = symbol.upper()
        self.is_loading_current_stock_details = True
        self.transaction_message = ""
        self.current_stock_info = {}
        self.current_stock_metrics = {}
        self.current_stock_history = pd.DataFrame(columns=['time', 'price'])
        self.current_stock_shares_owned = 0
        self.stock_detail_chart_hover_info = None
        # self.processed_news = [] # No limpiar noticias si queremos ver noticias relacionadas aunque falle la info
        # self.has_news = False
        # self.news_page = 1


        db_session_main = None 
        try:
            ticker = await asyncio.to_thread(yf.Ticker, self.viewing_stock_symbol)
            # Intentar obtener la información de varias formas si falla la primera
            info = None
            try: info = await asyncio.to_thread(getattr, ticker, 'info')
            except Exception as e_info: logger.warning(f"YF info error 1 para {self.viewing_stock_symbol}: {e_info}")

            if not info or not info.get("symbol"):
                logger.warning(f"No yf info completa para {self.viewing_stock_symbol}. Intentando .fast_info.")
                try: info = await asyncio.to_thread(getattr, ticker, 'fast_info')
                except Exception as e_fastinfo: logger.warning(f"YF fast_info error 2 para {self.viewing_stock_symbol}: {e_fastinfo}")
                
            if not info or not info.get("symbol"):
                 logger.warning(f"No yf info disponible para {self.viewing_stock_symbol}. Intentando DB local.")
                 db_session_main = SessionLocal() 
                 stock_db = await asyncio.to_thread(db_session_main.query(StockModel).filter(StockModel.symbol == self.viewing_stock_symbol).first)
                 if stock_db:
                     self.current_stock_info = {
                         "symbol": stock_db.symbol,
                         "name": stock_db.name,
                         "currentPrice": float(stock_db.current_price),
                         "sector": stock_db.sector.sector_name if stock_db.sector else "N/A",
                         "currencySymbol": "$", # Asumir USD por defecto si no hay info
                         "logo_url": stock_db.logo_url or get_stock_logo_url(stock_db.symbol) # Usar logo de DB o intentar Clearbit
                     }
                     logger.info(f"Info básica para {self.viewing_stock_symbol} cargada de DB local.")
                 else:
                     self.current_stock_info = {"error": f"Acción {self.viewing_stock_symbol} no encontrada en yfinance ni en BD."}
                     logger.error(f"load_stock_page_data: No info encontrada para {self.viewing_stock_symbol} en YF o DB.")
                     
            else: # Si se obtuvo info de yfinance
                self.current_stock_info = {
                    "symbol": info.get("symbol", self.viewing_stock_symbol),
                    # Usar longName o shortName, fallback al símbolo
                    "name": info.get("longName", info.get("shortName", info.get("symbol", self.viewing_stock_symbol))),
                    # Usar currentPrice, fallback a regularMarketPrice, luego previousClose
                    "currentPrice": float(info.get("currentPrice", info.get("regularMarketPrice", info.get("previousClose", 0.0)))),
                    "previousClose": float(info.get("previousClose", 0.0)), 
                    "open": float(info.get("open", 0.0)),
                    "dayHigh": float(info.get("dayHigh", 0.0)), 
                    "dayLow": float(info.get("dayLow", 0.0)),
                    "volume": info.get("volume", 0), 
                    "marketCap": info.get("marketCap", 0),
                    "fiftyTwoWeekHigh": float(info.get("fiftyTwoWeekHigh", 0.0)), 
                    "fiftyTwoWeekLow": float(info.get("fiftyTwoWeekLow", 0.0)),
                    "sector": info.get("sector", "N/A"), 
                    "industry": info.get("industry", "N/A"),
                    "currencySymbol": info.get("currency", "$"), # Usar 'currency' para el símbolo de moneda
                    "logo_url": info.get("logo_url", get_stock_logo_url(info.get("symbol", self.viewing_stock_symbol))), # Usar logo de YF o intentar Clearbit
                    "longBusinessSummary": info.get("longBusinessSummary", "Resumen no disponible.")
                }

                # Calcular el cambio diario si tenemos previousClose
                change = self.current_stock_info['currentPrice'] - self.current_stock_info['previousClose']
                percent_change = (change / self.current_stock_info['previousClose'] * 100) if self.current_stock_info['previousClose'] != 0 else 0.0

                # Añadir métricas clave
                self.current_stock_metrics = {
                    "Precio Actual": f"{self.current_stock_info['currencySymbol']}{self.current_stock_info['currentPrice']:,.2f}",
                    "Cambio Diario": f"{change:+.2f} ({percent_change:+.2f}%)", # Mostrar cambio absoluto y porcentual
                    "Apertura": f"{self.current_stock_info['currencySymbol']}{self.current_stock_info['open']:,.2f}",
                    "Máx. Diario": f"{self.current_stock_info['currencySymbol']}{self.current_stock_info['dayHigh']:,.2f}",
                    "Mín. Diario": f"{self.current_stock_info['currencySymbol']}{self.current_stock_info['dayLow']:,.2f}",
                    "Volumen": f"{self.current_stock_info['volume']:,}",
                    "Cap. de Mercado": f"{self.current_stock_info['currencySymbol']}{self.current_stock_info['marketCap']/1e9:.2f}B" if self.current_stock_info['marketCap'] else "N/A",
                    "Máx. 52 Sem.": f"{self.current_stock_info['currencySymbol']}{self.current_stock_info['fiftyTwoWeekHigh']:,.2f}",
                    "Mín. 52 Sem.": f"{self.current_stock_info['currencySymbol']}{self.current_stock_info['fiftyTwoWeekLow']:,.2f}",
                    "Sector": self.current_stock_info['sector'],
                    "Industria": self.current_stock_info['industry']
                }

                # --- Guardar/Actualizar Stock en BD local ---
                db_op_session = SessionLocal() 
                try:
                    stock_symbol_to_save = self.current_stock_info["symbol"]
                    stock_name_to_save = self.current_stock_info["name"]
                    current_price_to_save = Decimal(str(self.current_stock_info["currentPrice"]))
                    logo_url_to_save = self.current_stock_info.get("logo_url")
                    sector_name_to_save = self.current_stock_info.get("sector", "Desconocido")
                    
                    existing_stock_in_db = await asyncio.to_thread(
                        db_op_session.query(StockModel).filter(StockModel.symbol == stock_symbol_to_save).first
                    )
                    
                    sector_obj = await asyncio.to_thread(db_op_session.query(SectorModel).filter(SectorModel.sector_name == sector_name_to_save).first)
                    if not sector_obj:
                        logger.info(f"Sector '{sector_name_to_save}' no encontrado. Intentando usar sector por defecto o crear nuevo.")
                        sector_obj = await asyncio.to_thread(db_op_session.get, SectorModel, DEFAULT_SECTOR_ID)
                        if not sector_obj and sector_name_to_save != "Desconocido":
                             logger.info(f"Creando nuevo sector '{sector_name_to_save}'.")
                             sector_obj = SectorModel(sector_name=sector_name_to_save)
                             db_op_session.add(sector_obj)
                             await asyncio.to_thread(db_op_session.flush) # Obtener el ID antes de commit
                        elif not sector_obj:
                             logger.error(f"Sector por defecto ID {DEFAULT_SECTOR_ID} no existe y sector de YF es 'Desconocido'. No se puede asignar sector.")
                             # Asignar None o un ID de error si no se puede asignar un sector válido
                             sector_obj = None # No se asignará sector_id si es None

                    if not existing_stock_in_db:
                        logger.info(f"Stock {stock_symbol_to_save} no encontrado en BD local. Creando entrada...")
                        new_stock_db_entry = StockModel(
                            symbol=stock_symbol_to_save,
                            name=stock_name_to_save,
                            current_price=current_price_to_save,
                            logo_url=logo_url_to_save,
                            sector_id=sector_obj.id if sector_obj else None # Asignar ID del sector o None
                        )
                        db_op_session.add(new_stock_db_entry)
                        await asyncio.to_thread(db_op_session.commit)
                        await asyncio.to_thread(db_op_session.refresh, new_stock_db_entry) # Obtener el ID del nuevo stock
                        logger.info(f"Stock {stock_symbol_to_save} añadido a BD local con ID: {new_stock_db_entry.id}, Sector ID: {new_stock_db_entry.sector_id}")

                    elif (existing_stock_in_db.current_price != current_price_to_save or
                          existing_stock_in_db.logo_url != logo_url_to_save or
                          existing_stock_in_db.name != stock_name_to_save or
                          (sector_obj and existing_stock_in_db.sector_id != sector_obj.id)): # Actualizar también el sector si cambió
                        logger.info(f"Actualizando stock {stock_symbol_to_save} en BD local.")
                        existing_stock_in_db.current_price = current_price_to_save
                        existing_stock_in_db.name = stock_name_to_save
                        existing_stock_in_db.logo_url = logo_url_to_save
                        if sector_obj:
                             existing_stock_in_db.sector_id = sector_obj.id # Actualizar sector_id
                        await asyncio.to_thread(db_op_session.commit)
                        logger.info(f"Stock {stock_symbol_to_save} actualizado en BD local.")

                except Exception as e_db_op:
                    logger.error(f"Error al añadir/actualizar stock {self.viewing_stock_symbol} en BD: {e_db_op}", exc_info=True)
                    if db_op_session: await asyncio.to_thread(db_op_session.rollback)
                finally:
                    if db_op_session: await asyncio.to_thread(db_op_session.close)

            # Si el usuario está autenticado, cargar sus acciones poseídas de esta acción
            if self.is_authenticated and self.user_id:
                 await self._load_current_stock_shares_owned()

        except Exception as e: 
            logger.error(f"Error general en load_stock_page_data para {self.viewing_stock_symbol}: {e}", exc_info=True)
            self.current_stock_info={"error":f"Error al cargar datos para {self.viewing_stock_symbol}."} 
        finally:
            if db_session_main: await asyncio.to_thread(db_session_main.close) 
            self.is_loading_current_stock_details=False
            logger.info(f"load_stock_page_data finalizado para {self.viewing_stock_symbol}.")


    @rx.event
    async def buy_stock(self):
        logger.info(f"AUTHSTATE: Intento de COMPRA para {self.viewing_stock_symbol} por user {self.user_id}, cantidad: {self.buy_sell_quantity}")
        if not self.is_authenticated or not self.user_id or not self.viewing_stock_symbol: 
            self.transaction_message="Error: Autenticación o acción no válida."; logger.warning("BUY_STOCK: Auth o símbolo no válido."); return
        if self.buy_sell_quantity <= 0: 
            self.transaction_message = "Cantidad debe ser positiva."; logger.warning("BUY_STOCK: Cantidad no positiva."); return

        self.loading = True; self.transaction_message = ""
        db = None
        try:
            db = SessionLocal()
            user = await asyncio.to_thread(db.query(User).get, self.user_id)
            stock_m = await asyncio.to_thread(db.query(StockModel).filter(StockModel.symbol == self.viewing_stock_symbol).first)

            if not user: logger.error("BUY_STOCK: Usuario no encontrado en BD."); self.transaction_message="Error: Usuario no encontrado."; self.loading=False; return
            if not stock_m:
                logger.error(f"BUY_STOCK: Stock {self.viewing_stock_symbol} NO encontrado en BD local. No se puede comprar.")
                self.transaction_message=f"Error: Acción {self.viewing_stock_symbol} no encontrada en sistema para transacciones."; self.loading=False; return

            # Usar el precio actual del stock desde la base de datos si está disponible, sino desde current_stock_info
            price_to_use = float(stock_m.current_price if stock_m.current_price is not None else self.current_stock_info.get("currentPrice", 0.0))
            if price_to_use <= 0:
                 logger.error(f"BUY_STOCK: Precio de acción no válido ({price_to_use}) para {stock_m.symbol}. No se puede comprar.")
                 self.transaction_message = "Error: Precio de acción no disponible o inválido."; self.loading = False; return


            cost = Decimal(str(price_to_use)) * Decimal(self.buy_sell_quantity)

            logger.info(f"BUY_STOCK: Costo total: {cost:,.2f}, Saldo usuario: {user.account_balance:,.2f}")
            if user.account_balance < cost:
                self.transaction_message = f"Saldo insuficiente. Necesario: {cost:,.2f}, Disponible: {user.account_balance:,.2f}"; self.loading = False; return

            user.account_balance -= cost
            logger.info(f"BUY_STOCK: Saldo actualizado usuario: {user.account_balance:,.2f}")

            tx = StockTransaction(
                user_id=self.user_id, stock_id=stock_m.id, transaction_type=TransactionType.COMPRA,
                quantity=self.buy_sell_quantity, price_per_share=Decimal(str(price_to_use)), # Guardar el precio usado en la transacción
                timestamp=datetime.now(timezone.utc)
            )
            db.add(tx)
            await asyncio.to_thread(db.commit)
            await asyncio.to_thread(db.refresh, tx)
            await asyncio.to_thread(db.refresh, user)
            logger.info(f"BUY_STOCK: Transacción COMMIT para {stock_m.symbol}, ID: {tx.id}")

            self.account_balance = float(user.account_balance)
            self.transaction_message = f"Compra OK: {self.buy_sell_quantity} de {self.viewing_stock_symbol} a ${price_to_use:.2f} c/u."
            logger.info(self.transaction_message)

        except Exception as e:
            logger.error(f"Err buy_stock: {e}", exc_info=True)
            self.transaction_message = "Error durante la compra."
            if db: await asyncio.to_thread(db.rollback)
        finally:
            self.loading = False
            if db: await asyncio.to_thread(db.close)

        # Actualizar datos del portfolio y transacciones después de una compra exitosa
        await asyncio.gather(
            self._load_current_stock_shares_owned(), # Recargar acciones poseídas de la acción actual
            self._load_recent_transactions(),
            self._update_portfolio_value(), # Recalcular valor del portfolio
            self._update_total_invested(), # Recalcular total invertido
            self._update_pnl(), # Recalcular PnL
            self._update_portfolio_chart_data(), # Recalcular datos del gráfico
            self.load_portfolio() # Recargar lista de items en el portfolio
        )
        logger.info("BUY_STOCK: Actualización de estado post-compra finalizada.")


    @rx.event
    async def sell_stock(self):
        logger.info(f"AUTHSTATE: Intento de VENTA para {self.viewing_stock_symbol} por user {self.user_id}, cantidad: {self.buy_sell_quantity}")
        if not self.is_authenticated or not self.user_id or not self.viewing_stock_symbol: 
            self.transaction_message="Error: Autenticación o acción no válida."; logger.warning("SELL_STOCK: Auth o símbolo no válido."); return
        if self.buy_sell_quantity <= 0: 
            self.transaction_message = "Cantidad debe ser positiva."; logger.warning("SELL_STOCK: Cantidad no positiva."); return

        # Verificar acciones poseídas ANTES de iniciar la transacción
        await self._load_current_stock_shares_owned()
        if self.current_stock_shares_owned < self.buy_sell_quantity:
            self.transaction_message = f"No tienes suficientes acciones ({self.current_stock_shares_owned}) para vender {self.buy_sell_quantity}.";
            logger.warning(self.transaction_message);
            return

        self.loading = True; self.transaction_message = ""
        db = None
        try:
            db = SessionLocal()
            user = await asyncio.to_thread(db.query(User).get, self.user_id)
            stock_m = await asyncio.to_thread(db.query(StockModel).filter(StockModel.symbol == self.viewing_stock_symbol).first)

            if not user: logger.error("SELL_STOCK: Usuario no encontrado en BD."); self.transaction_message="Error: Usuario no encontrado."; self.loading=False; return
            if not stock_m:
                logger.error(f"SELL_STOCK: Stock {self.viewing_stock_symbol} NO encontrado en BD local. No se puede vender.")
                self.transaction_message=f"Error: Acción {self.viewing_stock_symbol} no encontrada en sistema para transacciones."; self.loading=False; return

            # Usar el precio actual del stock desde la base de datos si está disponible, sino desde current_stock_info
            price_to_use = float(stock_m.current_price if stock_m.current_price is not None else self.current_stock_info.get("currentPrice", 0.0))
            if price_to_use <= 0:
                 logger.error(f"SELL_STOCK: Precio de acción no válido ({price_to_use}) para {stock_m.symbol}. No se puede vender.")
                 self.transaction_message = "Error: Precio de acción no disponible o inválido."; self.loading = False; return

            value_of_sale = Decimal(str(price_to_use)) * Decimal(self.buy_sell_quantity)

            user.account_balance += value_of_sale
            logger.info(f"SELL_STOCK: Saldo actualizado usuario: {user.account_balance:,.2f}")

            tx = StockTransaction(
                user_id=self.user_id, stock_id=stock_m.id, transaction_type=TransactionType.VENTA,
                quantity=self.buy_sell_quantity, price_per_share=Decimal(str(price_to_use)), # Guardar el precio usado en la transacción
                timestamp=datetime.now(timezone.utc)
            )
            db.add(tx)
            await asyncio.to_thread(db.commit)
            await asyncio.to_thread(db.refresh, tx)
            await asyncio.to_thread(db.refresh, user)
            logger.info(f"SELL_STOCK: Transacción COMMIT para {stock_m.symbol}, ID: {tx.id}")

            self.account_balance = float(user.account_balance)
            self.transaction_message = f"Venta OK: {self.buy_sell_quantity} de {self.viewing_stock_symbol} a ${price_to_use:.2f} c/u."
            logger.info(self.transaction_message)

        except Exception as e:
            logger.error(f"Err sell_stock: {e}", exc_info=True); self.transaction_message = "Error durante la venta."
            if db: await asyncio.to_thread(db.rollback)
        finally:
            self.loading = False
            if db: await asyncio.to_thread(db.close)

        # Actualizar datos del portfolio y transacciones después de una venta exitosa
        await asyncio.gather(
            self._load_current_stock_shares_owned(), # Recargar acciones poseídas de la acción actual
            self._load_recent_transactions(),
            self._update_portfolio_value(), # Recalcular valor del portfolio
            self._update_total_invested(), # Recalcular total invertido
            self._update_pnl(), # Recalcular PnL
            self._update_portfolio_chart_data(), # Recalcular datos del gráfico
            self.load_portfolio() # Recargar lista de items en el portfolio
        )
        logger.info("SELL_STOCK: Actualización de estado post-venta finalizada.")


    @rx.event
    async def dashboard_on_mount(self):
        logger.info(f"Dashboard on_mount: User {self.username} (ID: {self.user_id}).")
        if not self.is_authenticated or not self.user_id:
             logger.warning("Dashboard: No auth, redirect login.");
             # return rx.redirect("/login") # La redirección se maneja en on_load ahora
             return # Solo salir si no autenticado, on_load se encargará de redirigir si es ruta protegida

        self.is_loading_portfolio_chart = True # Indicar que se están cargando los datos del gráfico
        logger.info("Dashboard on_mount: Iniciando carga de datos del dashboard.")

        try:
            # Asegurarse de que los métodos existen antes de llamarlos
            required_methods = [
                '_load_recent_transactions',
                '_update_portfolio_chart_data',
                '_update_portfolio_value', # Añadido
                '_update_total_invested', # Añadido
                '_update_pnl', # Añadido
                'load_portfolio'
            ]
            if not all(hasattr(self, m) for m in required_methods):
                missing = [m for m in required_methods if not hasattr(self, m)]
                logger.error(f"CRITICAL: Faltan métodos de carga en AuthState: {missing}. No se cargará el dashboard correctamente.")
                self.is_loading_portfolio_chart = False
                # Opcional: Mostrar un mensaje de error al usuario
                self.error_message = "Error interno al cargar el dashboard. Contacte al administrador."
                return

            # Cargar todos los datos necesarios para el dashboard
            await asyncio.gather(
                self._load_recent_transactions(),
                self._update_portfolio_chart_data(),
                self._update_portfolio_value(),
                self._update_total_invested(),
                self._update_pnl(),
                self.load_portfolio() # load_portfolio también actualiza total_portfolio_value
                # await self._update_yearly_pnl_chart_data(), # Descomentar si este método existe
            )

            logger.info(f"Dashboard on_mount: Carga de datos completada.")
            
            # Debugging del DataFrame del gráfico
            # logger.info(f"Dashboard DEBUG: portfolio_chart_data empty? {self.portfolio_chart_data.empty if isinstance(self.portfolio_chart_data,pd.DataFrame)else 'NotDF'}")
            # if isinstance(self.portfolio_chart_data, pd.DataFrame) and not self.portfolio_chart_data.empty:
            #     logger.info(f"Dashboard DEBUG: Cols:{self.portfolio_chart_data.columns.tolist()} Head:\n{self.portfolio_chart_data.head().to_string()}")
            # else:
            #     logger.warning("Dashboard DEBUG: portfolio_chart_data vacío/inválido post-update.")

            # Los PnL diario, mensual y anual ahora se calculan dentro de _update_pnl si hay datos de gráfico.
            # Si no hay datos de gráfico o transacciones, _update_pnl ya los pondrá a 0.0.

        except Exception as e:
            logger.error(f"Err dashboard_on_mount: {e}", exc_info=True)
            # En caso de error, asegurar que el gráfico se muestre vacío o con mock data
            self.portfolio_chart_data = pd.DataFrame(columns=['time', 'total_value'])
            self.error_message = f"Error al cargar datos del dashboard: {e}" # Mostrar un mensaje de error al usuario
        finally:
            self.is_loading_portfolio_chart = False
            logger.info("Dashboard on_mount: Finalizado.")


    @rx.event
    async def news_page_on_mount(self):
        logger.info("NewsPage on_mount.")
        # Solo cargar noticias si no se han cargado ya y no se está cargando actualmente
        if not self.processed_news and not self.is_loading_news:
             logger.info("NewsPage on_mount: No hay noticias cargadas. Iniciando get_news.")
             await self.get_news(new_query=self.SEARCH_QUERY or DEFAULT_SEARCH_QUERY)
        else:
             logger.info(f"NewsPage on_mount: Noticias ya cargadas ({len(self.processed_news)}) o cargando ({self.is_loading_news}). No se hace fetch.")


    @rx.event
    async def stock_detail_page_on_mount(self):
        route_symbol = self.router.page.params.get("symbol")
        logger.info(f"StockDetail on_mount. Route Symbol:{route_symbol}, Current viewing symbol: '{self.viewing_stock_symbol}'")

        if not route_symbol:
            self.current_stock_info = {"error": "Símbolo de acción no especificado en la URL."}
            self.is_loading_current_stock_details = False
            logger.error("StockDetail on_mount: No symbol in route.")
            return

        symbol_upper = route_symbol.upper()

        # Limpiar datos anteriores solo si el símbolo de la ruta es diferente al que se está viendo actualmente
        if self.viewing_stock_symbol.upper() != symbol_upper or not self.current_stock_info or self.current_stock_info.get("symbol", "").upper() != symbol_upper:
            logger.info(f"Nuevo símbolo para detalles: '{symbol_upper}'. Limpiando datos anteriores de '{self.viewing_stock_symbol}'.")
            self.viewing_stock_symbol = symbol_upper
            self.current_stock_info = {}
            self.current_stock_metrics = {}
            self.current_stock_history = pd.DataFrame(columns=['time','price'])
            self.current_stock_shares_owned = 0
            self.transaction_message = ""
            self.stock_detail_chart_hover_info = None
            self.processed_news = [] # Clean news when changing stock
            self.news_page = 1
        else:
            logger.info(f"Refrescando datos para el mismo símbolo: {self.viewing_stock_symbol}")

        self.is_loading_current_stock_details = True # Indicar que la carga ha comenzado

        try:
            # Cargar la información básica de la acción (esto también guarda/actualiza en BD local)
            await self.load_stock_page_data(symbol=self.viewing_stock_symbol)

            # Continuar solo si la carga de info básica fue exitosa (no hay error en current_stock_info)
            if not self.current_stock_info.get("error"):
                logger.info(f"StockDetail on_mount: Info básica para {self.viewing_stock_symbol} cargada. Cargando historial y noticias...")
                
                # Cargar datos del gráfico de historial para el período inicial (ej. 1M)
                # Asegurarse de que self.current_stock_selected_period tenga un valor inicial sensato
                if not self.current_stock_selected_period:
                     self.current_stock_selected_period = "1M"
                     logger.info("StockDetail on_mount: current_stock_selected_period no seteado, usando '1M'.")

                await self._update_current_stock_chart_data_internal()

                # Cargar noticias relacionadas con la acción
                # Use the stock symbol as the search query for news on this page
                logger.info(f"StockDetail on_mount: Loading news for {self.viewing_stock_symbol}.")
                # The get_news method handles API key check and fallback
                await self.get_news(new_query=self.viewing_stock_symbol)
                
            else:
                logger.warning(f"StockDetail on_mount: No se cargarán gráfico/noticias para {self.viewing_stock_symbol} debido a error previo en carga de info básica.")
                # Asegurarse de que el historial y las noticias estén vacíos si la carga de info falló
                self.current_stock_history = pd.DataFrame(columns=['time','price'])
                self.processed_news = []
                self.news_page = 1
            
        except Exception as e:
            logger.error(f"Error crítico durante stock_detail_page_on_mount para {self.viewing_stock_symbol}: {e}", exc_info=True)
            self.current_stock_info = {"error": f"Error al cargar página de {self.viewing_stock_symbol}."}
            self.current_stock_history = pd.DataFrame(columns=['time','price']) # Asegurar que el gráfico está vacío en caso de error
            self.processed_news = [] # Asegurar que las noticias están vacías
            self.news_page = 1
            self.transaction_message = "Error al cargar los detalles de la acción." # Mensaje de error para el usuario
        finally:
            self.is_loading_current_stock_details = False
            logger.info(f"StockDetail on_mount finalizado para {self.viewing_stock_symbol}. Hist. datos cargados: {not self.current_stock_history.empty if isinstance(self.current_stock_history,pd.DataFrame)else 'NoDF'}. Noticias cargadas: {bool(self.processed_news)}")


    @rx.event
    async def profile_page_on_mount(self):
        logger.info("AuthState.profile_page_on_mount.");
        # La autenticación y redirección se manejan en on_load.
        if not self.is_authenticated:
            logger.warning("ProfilePage: No auth.")
            # No redirigir aquí, on_load ya lo hizo si es necesario
        else:
            logger.info(f"ProfilePage: User {self.username} (ID:{self.user_id}) auth.")
            # Cargar datos específicos del perfil si los hay

    @rx.event
    async def buscador_page_on_mount(self):
         logger.info("BuscadorPage (AuthState) on_mount.")
         # No se carga nada por defecto, la búsqueda se activa con la interacción del usuario.

    async def _load_recent_transactions(self):
        logger.info(f"AuthState._load_recent_transactions para user_id: {self.user_id}")
        if not self.user_id:
            self.recent_transactions = [];
            logger.info("_load_recent_transactions: No user_id. Lista vacía.")
            return
        db = None; new_trans_list = []
        try:
            db = SessionLocal()
            # Obtener las últimas 10 transacciones con la info de stock
            # Asegurarse de que get_transaction_history_with_profit_loss devuelve lo esperado o ajustar la lógica aquí.
            # Basado en los logs anteriores, parece que esta función devuelve una lista de diccionarios.
            raw_transactions_data = await asyncio.to_thread(get_transaction_history_with_profit_loss, db, self.user_id, limit=10)

            for t_data_dict in raw_transactions_data:
                try:
                    # Validar y formatear los datos de cada transacción
                    timestamp_str = t_data_dict.get("timestamp", "")
                    dt_obj = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00")) if timestamp_str else datetime.now(timezone.utc)
                    formatted_timestamp = dt_obj.strftime("%d/%m/%y %H:%M")

                    trans_type_raw = t_data_dict.get("type", "").capitalize()
                    # Asegurarse de que el tipo es uno de los esperados o usar un valor por defecto
                    trans_type = trans_type_raw if trans_type_raw in ["Compra", "Venta"] else "Desconocido"

                    quantity_raw = t_data_dict.get("quantity", 0)
                    quantity = int(quantity_raw) if quantity_raw is not None else 0

                    symbol = t_data_dict.get("stock_symbol", "N/A") # Asegurarse de que la clave es correcta

                    price_raw = t_data_dict.get("price", 0.0) # Asegurarse de que la clave es correcta
                    price = float(price_raw) if price_raw is not None else 0.0

                    # Agregar otros campos si son necesarios para TransactionDisplayItem
                    # profit_loss = float(t_data_dict.get("profit_loss", 0.0)) # Si get_transaction_history_with_profit_loss lo devuelve

                    new_trans_list.append(TransactionDisplayItem(
                        timestamp=formatted_timestamp,
                        symbol=symbol,
                        quantity=quantity,
                        price=price, # O price_per_share si es diferente
                        type=trans_type
                        # Añadir profit_loss si se incluye en TransactionDisplayItem
                    ))
                except Exception as e_trans:
                    logger.error(f"Error procesando transacción en _load_recent_transactions: {t_data_dict}, Error: {e_trans}", exc_info=True)
                    # Opcional: añadir un item de transacción con error para depurar en la UI
                    # new_trans_list.append(TransactionDisplayItem(timestamp="Error", symbol="Error", quantity=0, price=0.0, type="Error"))

            self.recent_transactions = new_trans_list
            logger.info(f"Loaded {len(self.recent_transactions)} recent transactions.")

        except Exception as e:
            logger.error(f"Error general en _load_recent_transactions para user {self.user_id}: {e}", exc_info=True);
            self.recent_transactions = [] # Asegurar que la lista esté vacía en caso de error
        finally:
            if db: await asyncio.to_thread(db.close)


    async def load_portfolio(self):
        logger.info(f"AuthState.load_portfolio para user_id: {self.user_id}")
        
        def load_portfolio_sync(user_id):
            db = SessionLocal()
            try:
                # Obtener todas las transacciones del usuario
                transactions = db.query(StockTransaction).filter(StockTransaction.user_id == user_id).all()
                
                if not transactions:
                    logger.info(f"load_portfolio_sync: No hay transacciones para user_id {user_id}. Retornando listas vacías.")
                    return [], 0.0
                
                # Calcular el balance neto de acciones por stock
                current_net_holdings = {}
                for transaction in transactions:
                    stock_id = transaction.stock_id
                    if stock_id not in current_net_holdings:
                        current_net_holdings[stock_id] = 0
                    
                    if transaction.transaction_type == TransactionType.COMPRA:
                        current_net_holdings[stock_id] += transaction.quantity
                    elif transaction.transaction_type == TransactionType.VENTA:
                        current_net_holdings[stock_id] -= transaction.quantity
                
                # Filtrar solo las acciones con balance positivo
                held_stock_ids = [stock_id for stock_id, quantity in current_net_holdings.items() if quantity > 0]
                
                if not held_stock_ids:
                    logger.info(f"load_portfolio_sync: No hay acciones con balance positivo para user_id {user_id}.")
                    return [], 0.0
                
                # Obtener información de las acciones
                stocks = db.query(StockModel).filter(StockModel.id.in_(held_stock_ids)).all()
                stocks_map = {stock.id: stock for stock in stocks}
                
                new_portfolio_items = []
                new_total_value = Decimal("0.0")
                for stock_id in held_stock_ids:
                    stock_model = stocks_map.get(stock_id)
                    quantity = current_net_holdings[stock_id]
                    
                    if stock_model and quantity > 0:
                        current_price = float(stock_model.current_price) if stock_model.current_price is not None else 0.0
                        current_value_for_item = current_price * quantity
                        
                        # Prioritize logo URL from the DB if it exists and looks like an asset path or a full URL.
                        # Otherwise, use the helper function which handles Clearbit and local fallbacks.
                        logo_url_val = stock_model.logo_url if stock_model.logo_url and (stock_model.logo_url.startswith('/') or stock_model.logo_url.startswith('http')) else get_stock_logo_url(stock_model.symbol)
                        # Ensure local paths have the /assets/ prefix if missing
                        if logo_url_val and logo_url_val.startswith('/') and not logo_url_val.startswith('/assets/') and not logo_url_val.startswith('http'):
                            logo_url_val = f"/assets{logo_url_val}"
                        # Final fallback to default if everything else fails or is invalid
                        if not logo_url_val or (logo_url_val.startswith('/') and not logo_url_val.startswith('/assets/')):
                            logo_url_val = "/assets/default_logo.png"
                        
                        # Ensure logo_url_val is a string, fallback to default if None
                        final_logo_url = str(logo_url_val) if logo_url_val is not None else "/assets/default_logo.png"
                        
                        new_portfolio_items.append(PortfolioItem(
                            symbol=stock_model.symbol,
                            name=stock_model.name,
                            quantity=quantity,
                            current_price=current_price,
                            current_value=current_value_for_item,
                            logo_url=final_logo_url # Use the final, validated logo URL
                        ))
                        new_total_value += Decimal(str(current_value_for_item))
                
                logger.info(f"Portfolio cargado SYNC user {user_id}: {len(new_portfolio_items)} items, valor {new_total_value:,.2f}")
                return new_portfolio_items, float(new_total_value)
                
            except Exception as e:
                logger.error(f"Error en load_portfolio_sync: {e}", exc_info=True)
                return [], 0.0
            finally:
                db.close()
        
        try:
            portfolio_items, total_value = await asyncio.to_thread(load_portfolio_sync, self.user_id)
            self.portfolio_items = portfolio_items
            self.total_portfolio_value = total_value
            logger.info(f"Portfolio cargado: {len(portfolio_items)} items, valor total: {total_value:,.2f}")
        except Exception as e:
            logger.error(f"Error en load_portfolio: {e}", exc_info=True)
            self.portfolio_items = []
            self.total_portfolio_value = 0.0


    # Estas propiedades rx.var ya estaban formateadas a 2 decimales.
    # Si en la UI se ven más, el problema está en el componente del frontend que las muestra.
    @rx.var
    def balance_date(self) -> str: return datetime.now().strftime("%d %b %Y")
    @rx.var
    def formatted_user_balance(self) -> str: return f"${self.account_balance:,.2f}"
    @rx.var
    def formatted_user_balance_with_currency(self) -> str: return f"${self.account_balance:,.2f} USD"

    @rx.var
    def formatted_total_portfolio_value(self) -> str:
        """Formatted total portfolio value with 2 decimal places and currency."""
        # Asegurarse de que total_portfolio_value es numérico antes de formatear
        try:
            value = float(self.total_portfolio_value) if self.total_portfolio_value is not None else 0.0
        except (ValueError, TypeError):
            value = 0.0
            logger.error(f"Error converting total_portfolio_value to float: {self.total_portfolio_value}")
            
        # Puedes añadir lógica para determinar el símbolo de moneda si tu app soporta múltiples
        # Por ahora, asumimos USD como enformatted_user_balance_with_currency
        currency_symbol = "$"
        return f"{currency_symbol}{value:,.2f} USD"

    @rx.var
    def pnl_formatted(self) -> str:
        """Formatted PnL with sign and 2 decimal places."""
        return f"{self.pnl:+.2f}" # + para mostrar el signo positivo

    @rx.var
    def daily_pnl_formatted(self) -> str:
        """Formatted Daily PnL with sign and 2 decimal places."""
        return f"{self.daily_pnl:+.2f}"

    @rx.var
    def monthly_pnl_formatted(self) -> str:
        """Formatted Monthly PnL with sign and 2 decimal places."""
        return f"{self.monthly_pnl:+.2f}"

    @rx.var
    def yearly_pnl_formatted(self) -> str:
        """Formatted Yearly PnL with sign and 2 decimal places."""
        return f"{self.yearly_pnl:+.2f}"

    # Agregar propiedades para obtener el signo y color del PnL si es necesario para la UI
    @rx.var
    def pnl_is_positive(self) -> Optional[bool]:
        if self.pnl > 0: return True
        if self.pnl < 0: return False
        return None # None for zero

    @rx.var
    def daily_pnl_is_positive(self) -> Optional[bool]:
        if self.daily_pnl > 0: return True
        if self.daily_pnl < 0: return False
        return None

    @rx.var
    def monthly_pnl_is_positive(self) -> Optional[bool]:
        if self.monthly_pnl > 0: return True
        if self.monthly_pnl < 0: return False
        return None

    @rx.var
    def yearly_pnl_is_positive(self) -> Optional[bool]:
        if self.yearly_pnl > 0: return True
        if self.yearly_pnl < 0: return False
        return None # None for zero

    @rx.var
    def pnl_color(self) -> str:
        is_positive = self.pnl_is_positive
        if is_positive is True: return "var(--green-10)"
        if is_positive is False: return "var(--red-10)"
        return "var(--gray-11)" # Color neutro para 0

    @rx.var
    def daily_pnl_color(self) -> str:
        is_positive = self.daily_pnl_is_positive
        if is_positive is True: return "var(--green-10)"
        if is_positive is False: return "var(--red-10)"
        return "var(--gray-11)"

    @rx.var
    def monthly_pnl_color(self) -> str:
        is_positive = self.monthly_pnl_is_positive
        if is_positive is True: return "var(--green-10)"
        if is_positive is False: return "var(--red-10)"
        return "var(--gray-11)"

    @rx.var
    def yearly_pnl_color(self) -> str:
        is_positive = self.yearly_pnl_is_positive
        if is_positive is True: return "var(--green-10)"
        if is_positive is False: return "var(--red-10)"
        return "var(--gray-11)" # Color neutro para 0

    @rx.var
    def can_load_more_news(self) -> bool:
        """Indica si se pueden cargar más noticias (para la página de noticias principal)."""
        # En la página de detalle de acción, esta variable puede no ser relevante
        # pero se incluye para mantener la estructura original si era necesario.
        # La lógica aquí está pensada para la página principal de noticias.
        return bool(self.processed_news) and not self.is_loading_news # Simplified check

    @rx.var
    def featured_stock_page_news(self) -> List[NewsArticle]:
        """Devuelve las primeras 3 noticias procesadas para mostrar en la página de detalle de acción."""
        # Asegurarse de que processed_news es una lista antes de intentar rebanar
        if isinstance(self.processed_news, list):
            return self.processed_news[:3]
        return [] # Retornar lista vacía si processed_news no es una lista

    @rx.var
    def portfolio_change_info(self) -> Dict[str, Any]:
        df = self.portfolio_chart_data
        # Usar el valor total del portfolio calculado en load_portfolio como último precio si el gráfico está vacío
        last_price_fallback = self.total_portfolio_value if self.total_portfolio_value is not None else 0.0
        
        default = {"last_price": last_price_fallback, "change": 0.0, "percent_change": 0.0, "is_positive": None}
        
        if not isinstance(df, pd.DataFrame) or df.empty or 'total_value' not in df.columns or 'time' not in df.columns:
            logger.warning("portfolio_change_info: Invalid DF for calculating change. Using default.")
            return default

        # Asegurar que los datos son numéricos y están ordenados por tiempo
        df_sorted = df.copy()
        df_sorted['total_value'] = pd.to_numeric(df_sorted['total_value'], errors='coerce')
        df_sorted['time'] = pd.to_datetime(df_sorted['time'], utc=True, errors='coerce')
        df_sorted = df_sorted.dropna(subset=['time', 'total_value']).sort_values('time')

        prices = df_sorted['total_value']
        if prices.empty:
             logger.warning("portfolio_change_info: Prices series is empty after cleaning. Using default.")
             return default
        
        last_f = float(prices.iloc[-1])
        
        if len(prices) < 2:
             # Si solo hay un punto, el cambio es 0. El último precio es el valor de ese punto.
             return {"last_price": last_f, "change": 0.0, "percent_change": 0.0, "is_positive": None}

        try:
            first_f = float(prices.iloc[0])
            change_f = last_f - first_f
            percent_f = (change_f / first_f * 100) if first_f != 0 else 0.0
            is_positive = change_f > 0 if change_f != 0 else (None if change_f == 0 else False)

            return {"last_price": last_f, "change": change_f, "percent_change": percent_f, "is_positive": is_positive}

        except Exception as e:
            logger.error(f"Err calculating portfolio_change_info: {e}", exc_info=True)
            return default


    @rx.var
    def is_portfolio_value_change_positive(self) -> Optional[bool]: return self.portfolio_change_info.get("is_positive")
    
    @rx.var
    def formatted_portfolio_value_percent_change(self) -> str:
        """Formatted portfolio percentage change with sign and 2 decimal places."""
        percent_change = self.portfolio_change_info.get('percent_change', 0.0)
        return f"{percent_change:+.2f}%" # Usar + para mostrar signo positivo


    @rx.var
    def formatted_portfolio_value_change_abs(self) -> str:
        """Formatted portfolio absolute change with sign and 2 decimal places."""
        change = self.portfolio_change_info.get('change', 0.0)
        return f"{change:+.2f}" # Usar + para mostrar signo positivo


    @rx.var
    def portfolio_chart_color(self) -> str:
        is_positive = self.is_portfolio_value_change_positive
        if is_positive is True: return "var(--green-9)"
        if is_positive is False: return "var(--red-9)"
        return "var(--gray-9)" # Color neutro


    @rx.var
    def portfolio_chart_area_color(self) -> str:
        is_positive = self.is_portfolio_value_change_positive
        if is_positive is True: return "rgba(34,197,94,0.2)" # Verde con transparencia
        if is_positive is False: return "rgba(239,68,68,0.2)" # Rojo con transparencia
        return "rgba(107,114,128,0.2)" # Gris con transparencia


    @rx.var
    def portfolio_display_value(self) -> float:
        """Determina el valor a mostrar en el dashboard (hover o último)."""
        hover_info = self.portfolio_chart_hover_info
        
        # Acceder a portfolio_chart_change_info de forma segura, con un fallback adicional
        change_info = self.portfolio_change_info # Accedemos a la rx.var
        last_price_from_change = change_info.get("last_price") if isinstance(change_info, dict) else None

        # Usar el valor del hover si está disponible, sino el último valor del gráfico (si se obtuvo de change_info) o el valor total actual
        value_to_display = self.total_portfolio_value if self.total_portfolio_value is not None else 0.0
        if last_price_from_change is not None:
             value_to_display = last_price_from_change # Usar el last_price calculado en change_info si está disponible

        if hover_info and "y" in hover_info:
            hover_y_data = hover_info["y"]
            # Manejar si hover_y_data es una lista (e.g., de hovermode='x unified') o un solo valor
            y_to_convert = hover_y_data[0] if isinstance(hover_y_data, list) and hover_y_data else hover_y_data
            
            if y_to_convert is not None:
                try:
                    # Intentar convertir a float, si falla usar el valor_to_display por defecto
                    value_to_display = float(y_to_convert)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert hover y-value '{y_to_convert}' to float.")
                    pass # Si falla la conversión, mantener value_to_display por defecto

        return float(value_to_display) # Asegurar que el retorno es float


    @rx.var
    def portfolio_display_time(self) -> str:
        """Determina el tiempo/fecha a mostrar en el dashboard (hover o período)."""
        hover_info = self.portfolio_chart_hover_info
        if hover_info and "x" in hover_info:
            x_data = hover_info["x"]
            # Manejar si x_data es una lista o un solo valor
            x_value = x_data[0] if isinstance(x_data, list) and x_data else x_data

            if x_value is not None:
                try:
                    # Intentar parsear la fecha. Plotly envía timestamps o strings.
                    # Asumimos formato que pd.to_datetime pueda manejar.
                    dt_obj = pd.to_datetime(x_value, utc=True) # Asegurar que es aware y UTC
                    
                    # Decidir formato: con hora para períodos cortos (1D, 5D), sin hora para largos.
                    # Esto es una heurística, ajusta según cómo te gustaría que se viera.
                    # Podrías basarte en la diferencia entre el primer y último punto visible del gráfico si tuvieras esa info.
                    show_time = self.selected_period.upper() in ["1D", "5D"]
                    if not show_time and not self.portfolio_chart_data.empty and 'time' in self.portfolio_chart_data.columns:
                         # Heurística alternativa: mostrar hora si el rango de tiempo cubierto es < 2 días
                         df_times = pd.to_datetime(self.portfolio_chart_data['time'], utc=True, errors='coerce').dropna()
                         if len(df_times) >= 2 and (df_times.max() - df_times.min()).total_seconds() < 48 * 3600: # Menos de 48 horas
                              show_time = True

                    return dt_obj.strftime('%d %b, %H:%M') if show_time else dt_obj.strftime('%d %b %Y')

                except Exception as e:
                    logger.warning(f"Err formatting portfolio hover time: {e}. Raw value: '{x_value}'", exc_info=True)
                    # Si falla el parseo o formato de fecha, mostrar el valor crudo o un placeholder
                    return str(x_value) if x_value else "--"

        # Si no hay hover info, mostrar el nombre del período seleccionado
        period_map_display = {"1D":"24h","5D":"5d","1M":"1m","6M":"6m","YTD":"Aquest Any","1Y":"1a","5Y":"5a","MAX":"Màx"}
        return period_map_display.get(self.selected_period.upper(), f"Període: {self.selected_period}")

    @rx.var
    def main_portfolio_chart_figure(self) -> go.Figure:
        """Genera la figura de Plotly para el gráfico del portfolio."""
        # Figuras de carga y error para mostrar si no hay datos o hay error
        loading_fig=go.Figure().update_layout(height=300,annotations=[dict(text="Calculant gráfico...",showarrow=False, xref="paper", yref="paper",x=0.5,y=0.5)],paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis=dict(visible=False),yaxis=dict(visible=False))
        error_fig=go.Figure().update_layout(height=300,annotations=[dict(text="Sense dades portfolio.",showarrow=False, xref="paper", yref="paper",x=0.5,y=0.5)],paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis=dict(visible=False),yaxis=dict(visible=False))

        # Mostrar figura de carga si isLoading es True y no hay datos de gráfico
        if self.is_loading_portfolio_chart and (not isinstance(self.portfolio_chart_data, pd.DataFrame) or self.portfolio_chart_data.empty):
            logger.info("main_portfolio_chart_figure: Mostrando figura de carga.")
            return loading_fig

        df = self.portfolio_chart_data
        
        # Validar el DataFrame
        if not isinstance(df, pd.DataFrame) or df.empty or 'total_value' not in df.columns or 'time' not in df.columns:
            logger.warning(f"main_portfolio_chart_figure: Invalid DF. Cols:{df.columns.tolist() if isinstance(df,pd.DataFrame)else 'NoDF'}. Mostrando figura de error.")
            return error_fig

        try:
            # Limpiar y preparar datos para el gráfico
            df_chart = df.copy()
            df_chart['time'] = pd.to_datetime(df_chart['time'], errors='coerce', utc=True)
            df_chart['total_value'] = pd.to_numeric(df_chart['total_value'], errors='coerce')
            df_chart = df_chart.dropna(subset=['time', 'total_value']).sort_values(by='time')

            if df_chart.empty or len(df_chart) < 1:
                logger.warning(f"main_portfolio_chart: DF vacío post-procesamiento. Pts:{len(df_chart)}. Mostrando figura de error.")
                return error_fig

            # --- Filter data based on selected_period ---
            filtered_df = pd.DataFrame()
            latest_data_time = df_chart['time'].max() # Get the latest time in the data
            if self.selected_period.upper() == "MAX":
                filtered_df = df_chart # Use all data for MAX
            else:
                # Calculate start date based on the latest data time
                start_date = latest_data_time - pd.Timedelta(days=365 * 5) # Default to 5 years if period is not recognized
                if self.selected_period.upper() == "5D":
                    start_date = latest_data_time - pd.Timedelta(days=5)
                elif self.selected_period.upper() == "1M":
                    start_date = latest_data_time - pd.DateOffset(months=1)
                elif self.selected_period.upper() == "6M":
                    start_date = latest_data_time - pd.DateOffset(months=6)
                elif self.selected_period.upper() == "YTD":
                    # Start of the year of the latest data point
                    start_date = datetime(latest_data_time.year, 1, 1, tzinfo=timezone.utc)
                elif self.selected_period.upper() == "1A" or self.selected_period.upper() == "1Y":
                    start_date = latest_data_time - pd.DateOffset(years=1)
                elif self.selected_period.upper() == "5A" or self.selected_period.upper() == "5Y":
                    start_date = latest_data_time - pd.DateOffset(years=5)

                # No need for this check anymore as start_date is based on latest_data_time
                # However, ensure start_date is not *before* the earliest data point
                earliest_data_time = df_chart['time'].min()
                if start_date < earliest_data_time:
                    start_date = earliest_data_time
                    logger.warning(f"main_portfolio_chart_figure: Calculated start_date {start_date} is before earliest data point. Using earliest data point time.")
                
                # Filter the DataFrame
                filtered_df = df_chart[df_chart['time'] >= start_date].copy()

            if filtered_df.empty:
                 logger.warning(f"main_portfolio_chart: Filtered DF is empty for period {self.selected_period}. Showing error figure.")
                 return error_fig

            # Crear la figura de Plotly
            fig = go.Figure()

            # Añadir área bajo la curva (fill)
            fig.add_trace(
                go.Scatter(
                    x=filtered_df['time'],
                    y=filtered_df['total_value'],
                    mode='lines',
                    line=dict(width=0), # Línea invisible para definir el área
                    fill='tozeroy', # Rellenar hasta el eje Y=0
                    fillcolor=self.portfolio_chart_area_color, # Usar color con transparencia del estado
                    hoverinfo='skip' # No mostrar hover para esta traza
                )
            )

            # Añadir la línea principal del gráfico
            fig.add_trace(
                go.Scatter(
                    x=filtered_df['time'],
                    y=filtered_df['total_value'],
                    mode='lines',
                    line=dict(color=self.portfolio_chart_color, width=2.5, shape='spline'), # Usar color del estado
                    name='Valor Total',
                    # Definir el formato del hover tooltip
                    hovertemplate='<b>Valor:</b> $%{y:,.2f}<br><b>Fecha:</b> %{x|%d %b %Y, %H:%M}<extra></extra>'
                )
            )

            # Configurar el layout del gráfico
            # Calcular rango Y con padding
            min_v, max_v = filtered_df['total_value'].min(), filtered_df['total_value'].max()
            # Asegurar que el padding es sensible incluso si min/max son iguales o cercanos a cero
            value_range = max_v - min_v
            padding = value_range * 0.1 if value_range > 0 else abs(min_v) * 0.1 or 100 # 10% del rango o 100 si el rango es 0
            # Asegurar que el rango incluye 0 si todos los valores son positivos o negativos
            range_min = min(0, min_v - padding) if min_v >= 0 else min_v - padding
            range_max = max(0, max_v + padding) if max_v <= 0 else max_v + padding


            fig.update_layout(
                height=300,
                margin=dict(l=50, r=10, t=10, b=30),
                paper_bgcolor='rgba(0,0,0,0)', # Fondo transparente
                plot_bgcolor='rgba(0,0,0,0)', # Fondo del área de plot transparente
                xaxis=dict(
                    showgrid=False, # Ocultar gridlines verticales
                    zeroline=False,
                    tickmode='auto', # tickmode automático
                    nticks=6, # Sugerir 6 ticks en el eje X
                    showline=True, # Mostrar línea del eje X
                    linewidth=1,
                    linecolor='var(--gray-a6)', # Color de la línea del eje X
                    tickangle=-30, # Inclinar ticks para mejor legibilidad
                    tickfont=dict(color="var(--gray-11)") # Color de los ticks
                 ),
                 yaxis=dict(
                     title=None, # No mostrar título en el eje Y
                     showgrid=True, # Mostrar gridlines horizontales
                     gridcolor='var(--gray-a4)', # Color de las gridlines
                     zeroline=False,
                     showline=False,
                     side='left',
                     tickformat="$,.0f", # Formato de los ticks del eje Y (ej: $10,000)
                     # Asegurar formato correcto de ticks, ajusta si necesitas decimales aquí
                     # tickformat="$,.2f" # Con dos decimales
                     range=[range_min, range_max], # Usar rango calculado con padding
                     tickfont=dict(color="var(--gray-11)") # Color de los ticks
                 ),
                 hovermode='x unified', # Hover que muestra info de todas las trazas en un punto X
                 showlegend=False # No mostrar leyenda
             )

            logger.info(f"main_portfolio_chart_figure: Figura generada exitosamente para periodo {self.selected_period} con {len(filtered_df)} puntos.")
            return fig

        except Exception as e:
                logger.error(f"Err generating main_portfolio_chart_figure: {e}", exc_info=True);
        return error_fig

    @rx.var
    def stock_detail_chart_change_info(self)->Dict[str,Any]:
        """Calcula la información de cambio (absoluto y porcentual) para el gráfico de detalle de acción."""
        df = self.current_stock_history
        # Obtener el precio actual de la acción desde current_stock_info como fallback
        current_price_from_info = self.current_stock_info.get("currentPrice", self.current_stock_info.get("regularMarketPrice", 0.0))
        try: last_price_fallback = float(current_price_from_info)
        except (ValueError, TypeError): last_price_fallback = 0.0

        # Estructura por defecto de la información de cambio
        default_info={"last_price":last_price_fallback,"change":0.0,"percent_change":0.0,"is_positive":None,"first_price_time":None,"last_price_time":None}

        # Validar el DataFrame del historial
        if not isinstance(df,pd.DataFrame) or df.empty or 'price' not in df.columns or 'time' not in df.columns:
             logger.warning("stock_detail_chart_change_info: Invalid DF. Using default info.")
             return default_info

        try:
            # Limpiar y preparar los datos de precio y tiempo
            prices_series = df['price'].dropna()
            if prices_series.empty:
                 logger.warning("stock_detail_chart_change_info: Price series empty after dropna. Using default info.")
                 return default_info

            # Asegurarse de que las series de precio y tiempo estén alineadas por índice y sean DatetimeIndex
            times_series_raw = df.loc[prices_series.index,'time']
            times_series = pd.to_datetime(times_series_raw, utc=True, errors='coerce').dropna()
            
            # Alinear prices_series nuevamente con los timestamps válidos
            valid_indices = times_series.index
            final_prices = prices_series.loc[valid_indices]
            final_times = times_series

            if final_prices.empty or len(final_prices) < 1:
                 logger.warning("stock_detail_chart_change_info: Final series empty after time alignment. Using default info.")
                 return default_info

            # Calcular último precio y tiempo
            last_f = float(final_prices.iloc[-1])
            last_t = pd.to_datetime(final_times.iloc[-1], utc=True) # Asegurar que es Datetime con timezone

            # Actualizar el último precio y tiempo en la info por defecto
            default_info["last_price"] = last_f
            default_info["last_price_time"] = last_t

            # Si solo hay un punto, el cambio es 0
            if len(final_prices) < 2:
                 return default_info # Ya tiene el último precio y tiempo, cambio 0

            # Calcular primer precio y tiempo
            first_f = float(final_prices.iloc[0])
            first_t = pd.to_datetime(final_times.iloc[0], utc=True) # Asegurar que es Datetime con timezone

            # Calcular cambio absoluto y porcentual
            change_f = last_f - first_f
            percent_f = (change_f / first_f * 100) if first_f != 0 else 0.0

            # Determinar si el cambio es positivo, negativo o cero
            is_positive = change_f > 0 if change_f != 0 else (None if change_f == 0 else False)

            # Retornar la información calculada
            return {
                "last_price": last_f,
                "change": change_f,
                "percent_change": percent_f,
                "is_positive": is_positive,
                "first_price_time": first_t,
                "last_price_time": last_t
            }

        except Exception as e:
            logger.error(f"Err calculating stock_detail_chart_change_info: {e}", exc_info=True);
            return default_info # Retornar info por defecto en caso de excepción


    @rx.var
    def stock_detail_display_price(self)->str:
        """Determina el precio a mostrar en el detalle de acción (hover o último)."""
        hover_info = self.stock_detail_chart_hover_info
        change_info = self.stock_detail_chart_change_info # Obtener info de cambio para el último precio
        
        # Usar el último precio calculado en change_info como valor por defecto
        price_to_display = change_info.get("last_price", 0.0)
        currency_symbol = self.current_stock_info.get("currencySymbol","$")

        if hover_info and "y" in hover_info:
            hover_y_data = hover_info["y"]
            # Manejar si hover_y_data es una lista o un solo valor
            y_to_convert = hover_y_data[0] if isinstance(hover_y_data, list) and hover_y_data else hover_y_data

            if y_to_convert is not None:
                try:
                    # Intentar convertir a float, si falla usar el price_to_display por defecto
                    price_to_display = float(y_to_convert)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert stock detail hover y-value '{y_to_convert}' to float.")
                    pass # Si falla la conversión, mantener price_to_display por defecto

        # Formatear el precio a mostrar
        return f"{currency_symbol}{price_to_display:,.2f}"


    @rx.var
    def is_current_stock_info_empty(self)->bool:
        """Verifica si la información de la acción actual está vacía o contiene un error."""
        return not self.current_stock_info or "error" in self.current_stock_info or not self.current_stock_info.get("symbol")


    @rx.var
    def current_stock_metrics_list(self)->List[Tuple[str,str]]:
        """Convierte el diccionario de métricas de la acción actual en una lista de tuplas para fácil iteración en la UI."""
        # Asegurarse de que current_stock_metrics es un diccionario antes de convertirlo a lista
        if isinstance(self.current_stock_metrics, dict):
            return list(self.current_stock_metrics.items())
        return [] # Retornar lista vacía si no es un diccionario válido


    @rx.var
    def stock_detail_display_time_or_change(self)->str:
        """Determina el texto a mostrar debajo del precio en el detalle de acción (fecha del hover o info de cambio del período)."""
        hover_info = self.stock_detail_chart_hover_info
        change_info = self.stock_detail_chart_change_info # Obtener info de cambio del período
        
        # Si hay hover, mostrar la fecha/hora del punto del hover
        if hover_info and "x" in hover_info:
            x_data = hover_info["x"]
            x_value = x_data[0] if isinstance(x_data, list) and x_data else x_data # Manejar lista/single value

            if x_value is not None:
                try:
                    # Intentar parsear la fecha. Asegurarse de que sea Datetime con timezone.
                    dt_obj = pd.to_datetime(x_value, utc=True)
                    
                    # Decidir formato de fecha/hora: con hora para períodos cortos, sin hora para largos.
                    # Basado en la duración total del historial cargado si está disponible.
                    show_time = False
                    if not self.current_stock_history.empty and 'time' in self.current_stock_history.columns:
                         df_times = pd.to_datetime(self.current_stock_history['time'], utc=True, errors='coerce').dropna()
                         if len(df_times) >= 2 and (df_times.max() - df_times.min()).total_seconds() < 48 * 3600: # Menos de 48 horas
                             show_time = True
                    # O basado simplemente en el período seleccionado (heurística más simple)
                    # show_time = self.current_stock_selected_period.upper() in ["1D", "5D"]

                    return dt_obj.strftime('%d %b, %H:%M') if show_time else dt_obj.strftime('%d %b %Y')

                except Exception as e:
                    logger.warning(f"Err formatting stock detail hover time: {e}. Raw value: '{x_value}'", exc_info=True)
                    return str(x_value) if x_value else "--" # Fallback si el formato de fecha falla

        # Si no hay hover, mostrar la info de cambio del período
        change_val = change_info.get("change", 0.0)
        percent_change_val = change_info.get("percent_change", 0.0)
        currency_symbol = self.current_stock_info.get("currencySymbol","$")

        # Mapeo para nombres de períodos en español
        period_map_display={"1D":"Avui","5D":"5 Dies","1M":"1 Mes","6M":"6 Mesos","YTD":"Aquest Any","1A":"1 Any","1Y":"1 Any","5A":"5 Anys","5Y":"5 Anys","MAX":"Màxim"}
        period_display_name=period_map_display.get(self.current_stock_selected_period.upper(),self.current_stock_selected_period)

        # Formatear la cadena de cambio
        return f"{currency_symbol}{change_val:+.2f} ({percent_change_val:+.2f}%) {period_display_name}"


    @rx.var
    def stock_detail_change_color(self)->str:
        """Determina el color del texto de cambio en el detalle de acción (verde, rojo, gris)."""
        # Si hay hover, el color es gris (o el color del texto general)
        if self.stock_detail_chart_hover_info and "x" in self.stock_detail_chart_hover_info:
            return "var(--gray-11)" # Color neutro para el texto del hover

        # Si no hay hover, usar el color basado en si el cambio del período es positivo
        is_positive = self.stock_detail_chart_change_info.get("is_positive")
        if is_positive is True: return "var(--green-10)"
        if is_positive is False: return "var(--red-10)"
        return "var(--gray-11)" # Color neutro para cambio cero o no determinado


    # Esta propiedad parece estar duplicada o ser redundante con stock_detail_chart_change_info['is_positive']
    # Revisa dónde se usa current_stock_change_color en tu frontend y considera si stock_detail_change_color es más apropiado
    @rx.var
    def current_stock_change_color(self) -> str:
        """Determina el color del cambio diario (basado en current_stock_info)."""
        # Esto usa el cambio del current_stock_info, que es el cambio desde el cierre anterior
        # Es diferente del cambio calculado para el período seleccionado en el gráfico (stock_detail_chart_change_info)
        # Asegúrate de usar la propiedad correcta en tu frontend.
        
        change = self.current_stock_info.get('currentPrice', 0.0) - self.current_stock_info.get('previousClose', 0.0)
        
        # Asegurarse de que 'change' es numérico
        try:
            change = float(change)
        except (ValueError, TypeError):
            change = 0.0 # Usar 0 si no se puede convertir a float

        if change > 0: return "var(--green-10)"
        elif change < 0: return "var(--red-10)"
        return "var(--gray-11)" # Color neutro para cambio cero


    @rx.var
    def stock_detail_chart_figure(self) -> go.Figure:
        """Genera la figura de Plotly para el gráfico de detalle de acción."""
        df = self.current_stock_history
        # Figuras de carga y error
        loading_fig = go.Figure().update_layout(height=350, annotations=[dict(text="Cargando gráfico...", showarrow=False, xref="paper", yref="paper",x=0.5,y=0.5)], paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))
        error_fig = go.Figure().update_layout(height=350, annotations=[dict(text="Datos de gráfico no disponibles.", showarrow=False, xref="paper", yref="paper",x=0.5,y=0.5)], paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))

        # Mostrar figura de carga si isLoading es True y no hay datos de gráfico
        if self.is_loading_current_stock_details and (not isinstance(df, pd.DataFrame) or df.empty):
            logger.info("stock_detail_chart_figure: Mostrando figura de carga.")
            return loading_fig

        # Validar el DataFrame
        if not isinstance(df, pd.DataFrame) or df.empty or not all(c in df.columns for c in ['time', 'price']):
            logger.warning(f"stock_detail_chart_figure: Invalid DF for {self.viewing_stock_symbol}. Cols:{df.columns.tolist() if isinstance(df,pd.DataFrame)else 'NoDF'}. Mostrando figura de error.")
            return error_fig

        try:
            # Limpiar y preparar datos para el gráfico
            df_chart = df.copy()
            df_chart['time'] = pd.to_datetime(df_chart['time'], errors='coerce', utc=True)
            df_chart['price'] = pd.to_numeric(df_chart['price'], errors='coerce')
            df_chart = df_chart.dropna(subset=['time', 'price']).sort_values(by='time')

            if df_chart.empty or len(df_chart) < 1:
                logger.warning(f"stock_detail_chart_figure: DF vacío post-procesamiento para {self.viewing_stock_symbol}. Pts:{len(df_chart)}. Mostrando figura de error.")
                return error_fig

            prices_series = df_chart['price']
            final_times = df_chart['time']

            # Determinar color de la línea basado en el cambio del período mostrado en el gráfico
            line_color = "var(--gray-9)" # Color por defecto
            fill_color_base = '128,128,128' # RGB base para el relleno (gris)

            if len(prices_series) >= 2:
                first_price = prices_series.iloc[0]
                last_price = prices_series.iloc[-1]
                if last_price > first_price:
                    line_color = "var(--green-9)" # Verde si sube
                    fill_color_base = '34,197,94' # Verde RGB
                elif last_price < first_price:
                    line_color = "var(--red-9)" # Rojo si baja
                    fill_color_base = '239,68,68' # Rojo RGB

            fill_color_rgba = f"rgba({fill_color_base},0.1)" # Relleno con transparencia

            # Crear la figura de Plotly
            fig = go.Figure()

            # Añadir traza del gráfico de línea con relleno
            fig.add_trace(go.Scatter(
                x=final_times,
                y=prices_series,
                mode="lines",
                line=dict(color=line_color, width=2, shape='spline'), # Usar color determinado
                fill='tozeroy', # Rellenar hasta el eje Y=0
                fillcolor=fill_color_rgba, # Usar color de relleno determinado
                hovertemplate='<b>Precio:</b> $%{y:,.2f}<br><b>Fecha:</b> %{x|%d %b %Y, %H:%M}<extra></extra>'
            ))

            # Configurar el layout del gráfico
            # Calcular rango Y con padding
            min_p, max_p = prices_series.min(), prices_series.max()
            price_range = max_p - min_p
            y_padding = price_range * 0.1 if price_range > 0 else abs(min_p) * 0.1 or 1.0 # 10% del rango o 1.0
            # Asegurar que el rango incluye 0 si todos los valores son positivos o negativos
            y_range_min = min(0, min_p - y_padding) if min_p >= 0 else min_p - y_padding
            y_range_max = max(0, max_p + y_padding) if max_p <= 0 else max_p + y_padding

            fig.update_layout(
                height=350,
                margin=dict(l=50, r=10, t=10, b=30),
                paper_bgcolor="rgba(0,0,0,0)", # Fondo transparente
                plot_bgcolor="rgba(0,0,0,0)", # Fondo del área de plot transparente
                xaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    tickmode="auto",
                    nticks=6,
                    showline=True,
                    linewidth=1,
                    linecolor="var(--gray-a6)",
                    tickangle=-30,
                    tickfont=dict(color="var(--gray-11)")
                ),
                yaxis=dict(
                    title=None,
                    showgrid=True,
                    gridcolor="var(--gray-a4)",
                    zeroline=False,
                    showline=False,
                    side="left",
                    tickformat="$,.2f", # Formato de los ticks del eje Y con 2 decimales
                    tickfont=dict(color="var(--gray-11)"),
                    range=[y_range_min, y_range_max] # Usar rango calculado con padding
                ),
                hovermode='x unified', # Hover unificado
                showlegend=False # No mostrar leyenda
            )

            logger.info(f"stock_detail_chart_figure: Figura generada exitosamente para {self.viewing_stock_symbol} con {len(df_chart)} puntos.")
            return fig

        except Exception as e:
            logger.error(f"Exception generating stock_detail_chart_figure for {self.viewing_stock_symbol}: {e}", exc_info=True);
            # Retornar figura de error en caso de excepción
            return error_fig


    # --- Event Handlers de UI ---
    def portfolio_chart_handle_hover(self, event_data: List):
        """Maneja el evento hover en el gráfico del portfolio para actualizar la info mostrada."""
        new_hover_info = None
        # Plotly envía los datos del hover como una lista de puntos, incluso si solo hay uno en hovermode='x unified'
        if event_data and isinstance(event_data, list) and event_data:
            # En hovermode='x unified', event_data[0] contiene la info consolidada por punto X
            point_info = event_data[0]
            if isinstance(point_info, dict):
                 # point_info.get('x') y point_info.get('y') pueden ser listas o valores únicos
                 # Para hovermode='x unified', 'y' es una lista de los valores Y de todas las trazas en ese X
                 # Nos interesa el valor Y del primer (y único) Scatter trace de datos en este caso.
                 new_hover_info = point_info # Guardar la info completa

        # Solo actualizar si la nueva info es diferente para evitar re-renders innecesarios
        if self.portfolio_chart_hover_info != new_hover_info:
            # logger.debug(f"Portfolio hover: {new_hover_info}") # Log detallado si es necesario
            self.portfolio_chart_hover_info = new_hover_info


    def portfolio_chart_handle_unhover(self, _):
        """Maneja el evento unhover en el gráfico del portfolio para limpiar la info mostrada."""
        if self.portfolio_chart_hover_info is not None:
            self.portfolio_chart_hover_info = None
            # logger.debug("Portfolio unhover: Info limpiada.")


    def portfolio_toggle_change_display(self):
        """Alterna entre mostrar cambio absoluto y porcentual en el dashboard."""
        self.portfolio_show_absolute_change = not self.portfolio_show_absolute_change
        logger.info(f"Portfolio display change toggled. Show absolute: {self.portfolio_show_absolute_change}")


    def stock_detail_chart_handle_hover(self, event_data: List):
        """Maneja el evento hover en el gráfico de detalle de acción para actualizar la info mostrada."""
        new_hover_info = None
        if event_data and isinstance(event_data, list) and event_data:
            point_info = event_data[0] # En hovermode='x unified', info consolidada en el primer elemento
            if isinstance(point_info, dict):
                 new_hover_info = point_info # Guardar la info completa

        if self.stock_detail_chart_hover_info != new_hover_info:
            # logger.debug(f"Stock Detail hover: {new_hover_info}") # Log detallado si es necesario
            self.stock_detail_chart_hover_info = new_hover_info


    def stock_detail_chart_handle_unhover(self, _):
        """Maneja el evento unhover en el gráfico de detalle de acción para limpiar la info mostrada."""
        if self.stock_detail_chart_hover_info is not None:
            self.stock_detail_chart_hover_info = None
            # logger.debug("Stock Detail unhover: Info limpiada.")


    # --- Métodos de Noticias ---
    def _create_fallback_news(self):
        """Crea noticias de respaldo cuando no se pueden obtener noticias reales."""
        logger.warning("Creating fallback news items.")
        # Usar el símbolo o nombre de la acción actual si se está viendo una, sino un término general
        context_term = self.current_stock_info.get("name", self.viewing_stock_symbol if self.viewing_stock_symbol else "el mercado de valores")

        self.processed_news = [
            NewsArticle(
                title=f"Actualización sobre {context_term}", 
                url="#", 
                publisher="Tradesim Info",
                date=datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M"), 
                summary=f"Información general del mercado o noticias relacionadas con {context_term}. Verifica la configuración de tu API Key de GNews para obtener noticias en tiempo real.", 
                image="/assets/default_news.png"
            ),
            NewsArticle(
                title="Mercado de valores en movimiento", 
                url="#", 
                publisher="Tradesim Info", 
                date=datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M"), 
                summary="Análisis de las tendencias actuales del mercado y su impacto en las inversiones.", 
                image="/assets/default_news.png"
            ),
            NewsArticle(
                title="Consejos para inversores", 
                url="#", 
                publisher="Tradesim Info", 
                date=datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M"), 
                summary="Estrategias y recomendaciones para tomar decisiones informadas en el mercado de valores.", 
                image="/assets/default_news.png"
            )
        ]
        self.news_page = 1


    @rx.event
    async def get_news(self, new_query: Optional[str] = None):
        """Fetch news articles from GNews API."""
        if self.is_loading_news:
            logger.info("get_news: Ya hay una carga en progreso. Ignorando.")
            return

        if new_query:
            self.SEARCH_QUERY = new_query
            self.news_page = 1
            self.processed_news = []

        logger.info(f"get_news llamado con new_query: '{new_query}'. Current search_query: '{self.SEARCH_QUERY}'. Page: {self.news_page}. Loading: {self.is_loading_news}")
        
        if not GNEWS_API_KEY or GNEWS_API_KEY == "YOUR_GNEWS_API_KEY_HERE":
            logger.error("get_news: GNEWS_API_KEY no configurada.")
            self._create_fallback_news()
            return

        self.is_loading_news = True
        try:
            params = {
                "q": self.SEARCH_QUERY,
                "apikey": GNEWS_API_KEY,
                "page": self.news_page,
                "max": 10,
                "lang": "en",
                "country": "us",
                "sortby": "publishedAt"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(GNEWS_API_URL, params=params)
                response.raise_for_status()
                data = response.json()

            if "articles" not in data:
                logger.error(f"get_news: No articles in response. Data: {data}")
                self._create_fallback_news()
                return

            new_articles = []
            for article in data["articles"]:
                if not article.get("title") or not article.get("url"):
                    continue

                # Clean and validate the URL
                url = article["url"].strip()
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url

                # Clean and validate the image URL, fallback to default if needed
                image_url = article.get("image", "").strip()
                valid_image_url = "/assets/default_news.png" # Default fallback

                if image_url:
                    if not image_url.startswith(("http://", "https://")):
                        # Attempt to fix missing scheme, but still prioritize valid URLs
                        logger.warning(f"get_news: Image URL missing scheme, attempting to fix: {image_url}")
                        image_url = "https://" + image_url # Assume https
                    
                    # Simple check: if it's now a valid URL format, use it.
                    if image_url.startswith(("http://", "https://")):
                         valid_image_url = image_url
                    else:
                         logger.warning(f"get_news: Invalid image URL format after cleaning: {image_url}. Using default.")

                new_articles.append(NewsArticle(
                    title=article["title"],
                    url=url,
                    publisher=article.get("source", {}).get("name", "Unknown"),
                    date=article.get("publishedAt", ""),
                    summary=article.get("description", ""),
                    image=valid_image_url # Use the validated or default image URL
                ))

            if new_articles:
                self.processed_news.extend(new_articles)
                self.news_page = 1
                logger.info(f"get_news: {len(new_articles)} nuevos artículos añadidos. Total: {len(self.processed_news)}")
            else:
                logger.warning("get_news: No se encontraron artículos válidos en la respuesta.")
                if not self.processed_news:
                    self._create_fallback_news()

        except Exception as e:
            logger.error(f"Error en get_news: {e}", exc_info=True)
            if not self.processed_news:
                self._create_fallback_news()
        finally:
            self.is_loading_news = False


    @rx.event
    async def load_more_news(self):
        """Carga la siguiente página de noticias si hay más disponibles."""
        logger.info(f"load_more_news llamado. Can load: {self.can_load_more_news}, Loading: {self.is_loading_news}")
        if self.can_load_more_news: # Solo cargar si can_load_more_news es True (hay noticias y no está cargando)
            await self.get_news() # Llamar a get_news para la próxima página (news_page ya se actualizó)
        else:
             logger.info("load_more_news: No se pueden cargar más noticias en este momento.")


    @rx.event
    async def set_news_search_query_and_fetch(self, query: str):
        """Establece una nueva query de búsqueda de noticias y inicia la carga desde la página 1."""
        logger.info(f"set_news_search_query_and_fetch llamado con query: '{query}'.")
        # Llama a get_news con la nueva query, lo que reseteará la paginación
        await self.get_news(new_query=query)

    
    # --- MÉTODOS DE BÚSQUEDA GLOBAL ---
    def set_search_term(self, term: str):
        """Establece el término de búsqueda global."""
        self.search_term = term.strip(); # Eliminar espacios en blanco
        self.error_message = "" # Limpiar mensaje de error al cambiar el término
        logger.debug(f"Global search term set to: '{self.search_term}'")


    @rx.event
    async def search_stock_global(self):
        """Realiza una búsqueda global de acciones usando yfinance."""
        logger.info(f"search_stock_global llamado con term: '{self.search_term}'")
        
        if not self.search_term:
            self.error_message = "Introduce un símbolo o nombre de acción para buscar.";
            self.search_result = SearchResultItem() # Limpiar resultado anterior
            logger.warning("search_stock_global: Término de búsqueda vacío.")
            return

        self.is_searching = True; # Indicar que la búsqueda está en progreso
        self.error_message = "" # Limpiar mensajes de error previos
        self.search_result = SearchResultItem() # Limpiar resultado anterior

        # Usar el mapeo local primero, si no, usar el término directamente como símbolo potencial
        query_upper = self.search_term.upper()
        symbol_to_fetch = company_map.get(query_upper, query_upper)
        logger.info(f"search_stock_global: Buscando ticker para '{self.search_term}' -> '{symbol_to_fetch}'")

        try:
            ticker_obj = await asyncio.to_thread(yf.Ticker, symbol_to_fetch)
            # Intentar obtener la información de varias formas si falla la primera
            info = None
            try: info = await asyncio.to_thread(lambda: ticker_obj.info)
            except Exception as e_info: logger.warning(f"YF info error 1 para '{symbol_to_fetch}': {e_info}")

            if not info or not info.get("symbol"):
                logger.warning(f"No yf info completa para '{symbol_to_fetch}'. Intentando .fast_info.")
                try: info = await asyncio.to_thread(lambda: ticker_obj.fast_info)
                except Exception as e_fastinfo: logger.warning(f"YF fast_info error 2 para '{symbol_to_fetch}': {e_fastinfo}")

            # Si aún no hay info válida
            if not info or not info.get("symbol"):
                self.error_message = f"No se encontró información para '{self.search_term}' ({symbol_to_fetch}).";
                self.search_result = SearchResultItem(Name=f"No encontrado: {symbol_to_fetch}") # Mostrar que no se encontró
                logger.warning(f"search_stock_global: No info encontrada para '{symbol_to_fetch}' después de intentos.")
                return

            # Procesar la información encontrada
            symbol_found = info.get("symbol", symbol_to_fetch)
            name_found = info.get("longName", info.get("shortName", symbol_found)) # Usar longName o shortName
            price_val = info.get("currentPrice", info.get("regularMarketPrice", info.get("previousClose",0.0)))
            
            # Formatear el precio
            price_str = "N/A"
            if isinstance(price_val,(int,float)):
                 currency_symbol = info.get("currency", "$") # Usar 'currency' para el símbolo
                 price_str = f"{currency_symbol}{float(price_val):,.2f}" # Formato con 2 decimales y separador de miles

            # Obtener URL del logo, intentando con la de YF o Clearbit
            logo_url_found = info.get("logo_url", get_stock_logo_url(symbol_found)) or "/default_logo.png"

            # Construir el SearchResultItem
            self.search_result = SearchResultItem(
                Symbol=symbol_found,
                Name=name_found,
                Current_Price=price_str,
                Logo=logo_url_found
            )
            logger.info(f"search_stock_global: Resultado encontrado para '{self.search_term}': {self.search_result}")

        except Exception as e:
            logger.error(f"Error en search_stock_global para '{self.search_term}' ({symbol_to_fetch}): {e}", exc_info=True);
            self.error_message = f"Error al buscar '{self.search_term}'. Intenta de nuevo.";
            self.search_result = SearchResultItem(Name=f"Error buscando {self.search_term}") # Mostrar un mensaje de error en el resultado

        finally:
            self.is_searching = False # La búsqueda ha terminado


    @rx.event
    def go_to_stock_detail_global(self, symbol: str):
        """Navega a la página de detalle de acción para el símbolo dado desde la búsqueda global."""
        logger.info(f"go_to_stock_detail_global llamado con symbol: '{symbol}'")
        # Validar el símbolo antes de redirigir
        if symbol and symbol != "N/A" and not symbol.startswith("No encontrado") and not symbol.startswith("Error"):
             # Redirigir a la ruta de detalle de acción con el símbolo en mayúsculas y sin espacios
             return rx.redirect(f"/detalles_accion/{symbol.upper().strip()}")
        else:
             # Mostrar una alerta si el símbolo no es válido para navegar
             logger.warning(f"go_to_stock_detail_global: Símbolo '{symbol}' no válido para navegar.")
             return rx.window_alert("No se puede navegar para este resultado.")

    # --- Métodos de Actualización de Portfolio, Invertido y PnL ---
    # Estos métodos se llaman desde on_load, dashboard_on_mount y Buy/Sell Stock events

    async def _update_portfolio_value(self):
        """Calcula y actualiza el valor total actual del portfolio."""
        logger.info(f"AuthState._update_portfolio_value para user_id: {self.user_id}")
        if not self.is_authenticated or not self.user_id:
            self.portfolio_value = 0.0
            logger.warning("UPD PORTF VALUE: No auth, valor 0.")
            return

        def get_portfolio_value_sync(user_id):
            db = SessionLocal()
            try:
                transactions = db.query(StockTransaction).filter(StockTransaction.user_id == user_id).all()

                if not transactions:
                    logger.info(f"No hay transacciones para user_id {user_id}. Retornando valor 0.")
                    return 0.0

                current_net_holdings: Dict[int, int] = {}
                for tx in transactions:
                    if tx.stock_id not in current_net_holdings:
                        current_net_holdings[tx.stock_id] = 0
                    if tx.transaction_type == TransactionType.COMPRA:
                        current_net_holdings[tx.stock_id] += tx.quantity
                    elif tx.transaction_type == TransactionType.VENTA:
                        current_net_holdings[tx.stock_id] -= tx.quantity

                held_stock_ids = [stock_id for stock_id, qty in current_net_holdings.items() if qty > 0]

                if not held_stock_ids:
                    logger.info(f"Usuario {user_id} no tiene tenencias actuales > 0. Retornando valor 0.")
                    return 0.0

                # --- CORRECTED STOCK FETCH ---
                # Ensure we are executing the query within the sync function
                stocks_in_portfolio_db = db.query(StockModel).filter(StockModel.id.in_(held_stock_ids)).all()
                stocks_map = {s.id: s for s in stocks_in_portfolio_db}

                total_value = Decimal("0.0")
                for stock_id in held_stock_ids:
                    stock_model = stocks_map.get(stock_id)
                    quantity = current_net_holdings[stock_id]

                    if stock_model and stock_model.current_price is not None:
                        total_value += Decimal(str(stock_model.current_price)) * Decimal(str(quantity))
                    elif stock_model:
                        logger.warning(f"UPD PORTF VALUE SYNC: Stock {stock_model.symbol} (ID: {stock_id}) tiene precio actual None en BD.")
                    else:
                        logger.error(f"UPD PORTF VALUE SYNC: Stock ID {stock_id} en holdings no encontrado en BD StockModel.")

                logger.info(f"Valor total actual del portfolio calculado SYNC: {total_value:,.2f}")
                return float(total_value) # Convertir Decimal a float
            except Exception as e:
                logger.error(f"Error en get_portfolio_value_sync para user {user_id}: {e}", exc_info=True)
                return 0.0 # Return 0.0 on error
            finally:
                db.close()

        self.portfolio_value = await asyncio.to_thread(get_portfolio_value_sync, self.user_id)
        
    async def _update_total_invested(self):
        """Calcula y actualiza el total de dinero invertido (solo compras)."""
        logger.info(f"AuthState._update_total_invested para user_id: {self.user_id}")
        if not self.is_authenticated or not self.user_id:
            self.total_invested = 0.0
            logger.warning("UPD TOTAL INV: No auth, valor 0.")
            return

        def get_total_invested_sync(user_id):
            db = SessionLocal()
            try:
                # --- CORRECTED BUY TRANSACTIONS FETCH ---
                # Ensure we are executing the query within the sync function
                buy_transactions = db.query(StockTransaction).filter(
                    StockTransaction.user_id == user_id,
                    StockTransaction.transaction_type == TransactionType.COMPRA
                ).all()

                total_invested = Decimal("0.0")
                for tx in buy_transactions:
                    total_invested += Decimal(str(tx.price_per_share)) * Decimal(str(tx.quantity))

                logger.info(f"Valor total invertido calculado SYNC: {total_invested:,.2f}")
                return float(total_invested)
            except Exception as e:
                logger.error(f"Error en get_total_invested_sync para user {user_id}: {e}", exc_info=True)
                return 0.0
            finally:
                db.close()

        self.total_invested = await asyncio.to_thread(get_total_invested_sync, self.user_id)

    async def _update_pnl(self):
        """Calcula y actualiza el PnL total, diario, mensual y anual."""
        logger.info(f"AuthState._update_pnl para user_id: {self.user_id}")
        # Las verificaciones de autenticación se hacen al llamar a este método desde otros lugares (on_load, buy/sell)
        # pero se añaden aquí también por si acaso se llama directamente.
        if not self.is_authenticated or not self.user_id:
            self.pnl = 0.0
            self.daily_pnl = 0.0
            self.monthly_pnl = 0.0
            self.yearly_pnl = 0.0
            logger.warning("UPD PNL: No auth, valores 0.")
            return

        try:
            # Asegurarse de que portfolio_value y total_invested estén actualizados
            # Estos ya deberían estar actualizados si se llama desde on_load o buy/sell,
            # pero se pueden llamar aquí explícitamente si se necesita garantizar.
            # await self._update_portfolio_value()
            # await self._update_total_invested()
            
            # El PnL total es la diferencia entre el valor actual del portfolio y el total invertido
            # Usar los valores que ya están en el estado (actualizados por los métodos correspondientes)
            self.pnl = self.portfolio_value - self.total_invested
            
            logger.info(f"PnL TOTAL calculado: {self.pnl:+.2f} (Portfolio: {self.portfolio_value:,.2f}, Invertido: {self.total_invested:,.2f})")

            # Calcular PnL diario, mensual y anual basado en el portfolio_chart_data
            # Estos cálculos solo tienen sentido si el portfolio_chart_data está correctamente poblado
            if isinstance(self.portfolio_chart_data, pd.DataFrame) and not self.portfolio_chart_data.empty and 'time' in self.portfolio_chart_data.columns and 'total_value' in self.portfolio_chart_data.columns:
                
                df = self.portfolio_chart_data.copy()
                df['time'] = pd.to_datetime(df['time'], utc=True, errors='coerce')
                df['total_value'] = pd.to_numeric(df['total_value'], errors='coerce')
                df = df.dropna(subset=['time', 'total_value']).sort_values('time')

                if len(df) >= 2:
                    last_point_time = df['time'].iloc[-1]
                    last_point_value = df['total_value'].iloc[-1]

                    # PnL diario: Cambio desde el punto más cercano a 24 horas antes del último punto
                    day_ago_time_target = last_point_time - pd.Timedelta(days=1)
                    # Encontrar el punto más cercano en el pasado o igual a day_ago_time_target
                    closest_past_point_day_idx = df[df['time'] <= day_ago_time_target].index.max()
                    
                    if pd.notna(closest_past_point_day_idx):
                         prev_day_value = df.loc[closest_past_point_day_idx, 'total_value']
                         self.daily_pnl = last_point_value - prev_day_value
                    else:
                         # Si no hay un punto 24h antes, el cambio diario es el cambio total desde el inicio
                         # o 0 si solo hay un punto. Aquí usamos el cambio total desde el inicio.
                         # Opcional: poner a 0 si el primer punto es < 24h del último.
                         first_point_value = df['total_value'].iloc[0]
                         self.daily_pnl = last_point_value - first_point_value
                         logger.warning(f"UPD PNL: No se encontró punto exacto 24h antes. Usando cambio total desde el inicio ({self.daily_pnl:+.2f}) como daily PnL heurístico.")

                    # PnL mensual: Cambio desde el punto más cercano a 30 días antes del último punto
                    month_ago_time_target = last_point_time - pd.Timedelta(days=30)
                    closest_past_point_month_idx = df[df['time'] <= month_ago_time_target].index.max()

                    if pd.notna(closest_past_point_month_idx):
                        month_ago_value = df.loc[closest_past_point_month_idx, 'total_value']
                        self.monthly_pnl = last_point_value - month_ago_value
                    else:
                         # Si no hay un punto 30d antes, usar el cambio total desde el inicio como mensual heurístico
                         first_point_value = df['total_value'].iloc[0]
                         self.monthly_pnl = last_point_value - first_point_value
                         logger.warning(f"UPD PNL: No se encontró punto exacto 30d antes. Usando cambio total desde el inicio ({self.monthly_pnl:+.2f}) como monthly PnL heurístico.")


                    # PnL anual: Cambio desde el punto más cercano a 365 días antes del último punto
                    year_ago_time_target = last_point_time - pd.Timedelta(days=365)
                    closest_past_point_year_idx = df[df['time'] <= year_ago_time_target].index.max()

                    if pd.notna(closest_past_point_year_idx):
                        year_ago_value = df.loc[closest_past_point_year_idx, 'total_value']
                        self.yearly_pnl = last_point_value - year_ago_value
                    else:
                        # Si no hay un punto 365d antes, usar el cambio total desde el inicio como anual heurístico
                        first_point_value = df['total_value'].iloc[0]
                        self.yearly_pnl = last_point_value - first_point_value
                        logger.warning(f"UPD PNL: No se encontró punto exacto 365d antes. Usando cambio total desde el inicio ({self.yearly_pnl:+.2f}) como yearly PnL heurístico.")


                    logger.info(f"PnL diario: {self.daily_pnl:+.2f}, mensual: {self.monthly_pnl:+.2f}, anual: {self.yearly_pnl:+.2f}")

                else:
                    # Si solo hay un punto en el gráfico, los PnL por período son 0
                    self.daily_pnl = 0.0
                    self.monthly_pnl = 0.0
                    self.yearly_pnl = 0.0
                    logger.info("UPD PNL: Menos de 2 puntos en portfolio_chart_data. PnLs por período son 0.")

            else:
                 # Si el portfolio_chart_data no es válido o está vacío, los PnLs por período son 0
                 self.daily_pnl = 0.0
                 self.monthly_pnl = 0.0
                 self.yearly_pnl = 0.0
                 logger.warning("UPD PNL: portfolio_chart_data inválido o vacío. PnLs por período son 0.")


        except Exception as e:
            logger.error(f"Error al calcular PnL o PnLs por período: {e}", exc_info=True)
            # Asegurar que todos los valores de PnL se resetee en caso de error
            self.pnl = 0.0
            self.daily_pnl = 0.0
            self.monthly_pnl = 0.0
            self.yearly_pnl = 0.0

# --- Definición de STOCK_LOGOS si tienes logos locales ---
# Ejemplo (asegúrate de que las rutas sean correctas dentro de la carpeta assets)
# STOCK_LOGOS = {
#     "AAPL": "/logos/apple.png",
#     "MSFT": "/logos/microsoft.png",
#     "TSLA": "/logos/tesla.png",
#     # Añadir más logos aquí
# }


print("AuthState CLASS DEFINITION PARSED AT END OF FILE (v14 - Fixed PnL/Invested/Chart logic)")

