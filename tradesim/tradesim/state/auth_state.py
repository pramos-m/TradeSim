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
from decimal import Decimal
import asyncio
import json # Necesario para open_url_script
import random
from sqlmodel import SQLModel 
from datetime import datetime, timedelta, timezone
from ..database import SessionLocal
from sqlalchemy import select, func
from ..controller.user import get_user_by_id
# tradesim/state/auth_state.py
# ... (otros imports de yfinance, os, logging, etc.)
from decimal import Decimal, InvalidOperation
import asyncio
from datetime import datetime, timezone # Asegúrate que timezone está aquí
from sqlalchemy.orm import Session
from ..models.stock import Stock
from ..models.stock_price_history import StockPriceHistory
from ..models.transaction import StockTransaction, TransactionType
from ..models.portfolio_item import PortfolioItemDB

from ..models.user import User 
from ..models.stock import Stock as StockModel 
from ..models.sector import Sector as SectorModel 
from ..controller.transaction import get_transaction_history_with_profit_loss # Para el historial

logger = logging.getLogger(__name__)
# ... (resto de constantes y clases base como NewsArticle, PortfolioItem, etc.)

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO)

SECRET_KEY = os.getenv("SECRET_KEY", "a-very-secret-key-here-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
DEFAULT_AVATAR = "/default_avatar.png"
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "f767bfe6df4f747e6b77c0178e8cc0d8") 
GNEWS_API_URL = "https://gnews.io/api/v4/search"
DEFAULT_SEARCH_QUERY = "mercado acciones finanzas" 
COMPANY_MAP = {
    "APPLE": "AAPL", "MICROSOFT": "MSFT", "GOOGLE": "GOOGL", "ALPHABET": "GOOGL",
    "AMAZON": "AMZN", "META": "META", "FACEBOOK": "META", "TESLA": "TSLA",
    "NVIDIA": "NVDA", "BERKSHIRE HATHAWAY": "BRK.B", "JPMORGAN": "JPM",
    "VISA": "V", "UNITEDHEALTH": "UNH", "HOME DEPOT": "HD",
    "PROCTER & GAMBLE": "PG", "MASTERCARD": "MA", "ELI LILLY": "LLY",
    "BROADCOM": "AVGO", "EXXON MOBIL": "XOM", "COSTCO": "COST",
    "ABBVIE": "ABBV", "PEPSICO": "PEP", "COCA-COLA": "KO", "COCA COLA": "KO",
    "MERCK": "MRK", "WALMART": "WMT", "BANK OF AMERICA": "BAC",
    "DISNEY": "DIS", "ADOBE": "ADBE", "PFIZER": "PFE", "CISCO": "CSCO",
    "ORACLE": "ORCL", "AT&T": "T", "INTEL": "INTC", "NETFLIX": "NFLX",
    "SALESFORCE": "CRM", "ABBOTT": "ABT", "MCDONALD'S": "MCD",
    "NIKE": "NKE", "QUALCOMM": "QCOM", "VERIZON": "VZ",
    "THERMO FISHER": "TMO", "DANAHER": "DHR", "ACCENTURE": "ACN",
}

class NewsArticle(rx.Base):
    title: str; url: str; publisher: str; date: str; summary: str; image: str
class PortfolioItem(rx.Base):
    symbol: str
    name: str
    quantity: int
    current_price: float
    current_value: float
    logo_url: str
class SearchResultItem(rx.Base):
    Symbol: str = ""; Name: str = "No encontrado"; Current_Price: str = "N/A"; Logo: str = "/default_logo.png"
class TransactionDisplayItem(rx.Base):
    timestamp: str; symbol: str; quantity: int; price: float; type: str 
    @property
    def formatted_quantity(self) -> str:
        sign = "+" if self.type.lower() == TransactionType.COMPRA.value.lower() else "-"
        return f"{sign}{abs(self.quantity)}"

class AuthState(rx.State):
    """Estado GLOBAL combinado."""
    # --- Variables ---
    is_authenticated: bool = False
    user_id: Optional[int] = None
    username: str = ""
    email: str = ""
    password: str = ""
    confirm_password: str = ""  # For password confirmation in registration
    profile_image_url: str = DEFAULT_AVATAR  # For user profile picture
    account_balance: float = 0.0
    active_tab: str = "login"  # Default to login tab
    error_message: str = ""  # For displaying error messages in forms
    loading: bool = False  # For tracking loading states in forms
    auth_token: str = ""  # For storing JWT token
    processed_token: bool = False  # For tracking if token has been processed
    last_path: str = "/"  # For storing last visited path
    
    # Portfolio
    portfolio_items: List[PortfolioItem] = []
    total_portfolio_value: float = 0.0
    portfolio_chart_hover_info: Optional[Dict] = None
    portfolio_show_absolute_change: bool = False
    selected_period: str = "1M"  # Default to 1 month view
    recent_transactions: List[TransactionDisplayItem] = []
    portfolio_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'total_value'])
    is_loading_portfolio_chart: bool = False
    
    # Stock Details
    viewing_stock_symbol: str = ""
    current_stock_info: dict = {}
    current_stock_shares_owned: int = 0
    buy_sell_quantity: int = 1
    transaction_message: str = ""
    current_stock_history: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
    current_stock_selected_period: str = "1M"
    stock_detail_chart_hover_info: Optional[Dict] = None
    is_loading_current_stock_details: bool = False
    current_stock_metrics: Dict[str, str] = {}
    
    # News
    processed_news: List[NewsArticle] = []
    is_loading_news: bool = False
    has_news: bool = False
    news_page: int = 1
    max_articles: int = 10
    SEARCH_QUERY: str = DEFAULT_SEARCH_QUERY
    
    # PNL Data
    daily_pnl: float = 0.0
    monthly_pnl: float = 0.0
    yearly_pnl: float = 0.0
    daily_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
    monthly_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
    yearly_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
    
    # Chart Data
    stock_chart_data: List[dict] = []
    stock_chart_layout: dict = {}
    
    # ... (resto de las variables de la clase AuthState)

    def _create_access_token(self, user_id: int) -> Optional[str]:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        data = {"sub": str(user_id), "exp": expire}
        try: return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
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
        self.is_authenticated = True; self.username = user.username; self.email = user.email
        self.user_id = user.id; self.account_balance = float(user.account_balance or 0.0)
        # self.profile_image_url = getattr(user, 'profile_image_url', DEFAULT_AVATAR) or DEFAULT_AVATAR # Comentado si User no tiene este campo

    def _clear_auth_state(self):
        self.auth_token = ""; self.is_authenticated = False; self.username = ""
        self.email = ""; self.user_id = None; self.account_balance = 0.0; self.profile_image_url = DEFAULT_AVATAR
        self.password = ""; self.confirm_password = ""

    def set_username(self, username_in: str): self.username = username_in.strip()
    def set_email(self, email_in: str): self.email = email_in.strip().lower()
    def set_password(self, password_in: str): self.password = password_in
    def set_confirm_password(self, confirm_password_in: str): self.confirm_password = confirm_password_in
    
    @rx.event
    def set_active_tab(self, tab: str):
        self.active_tab = tab; self.error_message = ""
        self.email = ""; self.password = ""; self.username = ""; self.confirm_password = ""

    @rx.event
    async def login(self):
        logger.info(f"Login attempt for email: {self.email}")
        self.error_message = ""
        self.loading = True
        if not self.email or not self.password:
            logger.warning("Login attempt with empty fields")
            self.error_message = "Por favor complete todos los campos"
            self.loading = False
            return

        db = None
        try:
            db = SessionLocal()
            # Buscar usuario por email
            logger.info(f"Searching for user with email: {self.email}")
            user = db.query(User).filter(User.email.ilike(self.email.strip().lower())).first()
            
            if not user:
                logger.warning(f"No user found with email: {self.email}")
                self.error_message = "Email o contraseña incorrectos"
                self.loading = False
                self.password = ""
                return

            # Verificar contraseña
            logger.info(f"Verifying password for user: {user.username}")
            if not user.verify_password(self.password):
                logger.warning(f"Invalid password for user: {user.username}")
                self.error_message = "Email o contraseña incorrectos"
                self.loading = False
                self.password = ""
                return

            # Establecer estado del usuario
            logger.info(f"Setting user state for: {user.username}")
            self._set_user_state(user)

            # Generar token
            logger.info(f"Generating token for user: {user.username}")
            token = self._create_access_token(user.id)
            if not token:
                logger.error(f"Failed to generate token for user: {user.username}")
                self.error_message = "Error al generar token"
                self._clear_auth_state()
                self.loading = False
                return

            # Actualizar estado
            self.auth_token = token
            self.last_path = "/dashboard"
            self.processed_token = False
            self.loading = False
            logger.info(f"User {self.email} logged in successfully")
            self.password = ""

            return rx.redirect(self.last_path)

        except Exception as e:
            logger.error(f"Login error: {e}", exc_info=True)
            self.error_message = "Error inesperado al iniciar sesión"
            self._clear_auth_state()
            self.loading = False
            self.password = ""
        finally:
            if db and db.is_active:
                db.close()

    @rx.event
    def set_buy_sell_quantity(self, value: str):
        """Set the quantity for buy/sell operations."""
        try:
            quantity = int(value) if value else 1
            self.buy_sell_quantity = max(1, quantity)
        except (ValueError, TypeError):
            self.buy_sell_quantity = 1

    @rx.event
    def open_url_script(self, url_string: str): # Acepta un string
        logger.info(f"Attempting to open URL via call_script: {url_string}")
        js_safe_url_string = json.dumps(url_string)
        js_command = f"""
        let urlToOpen = {js_safe_url_string}; 
        if (typeof urlToOpen === 'string' && (urlToOpen.startsWith('http://') || urlToOpen.startsWith('https://'))) {{
            window.open(urlToOpen, '_blank');
        }} else {{
            console.warn('Frontend (from open_url_script): Invalid URL or type for window.open:', urlToOpen, typeof urlToOpen);
        }}
        """
        return rx.call_script(js_command)

    @rx.event
    async def set_period(self, period: str):
        """Set the selected period for portfolio chart."""
        self.selected_period = period
        self.portfolio_chart_hover_info = None
        logger.info(f"Dashboard portfolio period changed to {period}. Triggering chart updates.")
        await self._update_portfolio_chart_data()

    @rx.event
    async def set_portfolio_period(self, period: str): # <--- Nombre correcto aquí
        self.selected_period = period 
        self.portfolio_chart_hover_info = None 
        logger.info(f"Dashboard portfolio period changed to {self.selected_period}. Triggering chart updates.")
        await self._update_portfolio_chart_data()

    @rx.event
    async def register(self):
        self.error_message = ""; self.loading = True
        if not self.username or not self.email or not self.password or not self.confirm_password:
            self.error_message = "Por favor complete todos los campos"; self.loading = False; return
        if self.password != self.confirm_password:
            self.error_message = "Las contraseñas no coinciden"; self.loading = False; self.password = ""; self.confirm_password = ""; return
        db = None
        try:
            db = SessionLocal()
            existing_user = await asyncio.to_thread(db.query(User).filter((User.email.ilike(self.email)) | (User.username.ilike(self.username))).first)
            if existing_user:
                self.error_message = "Usuario o email ya están registrados"; self.loading = False; return
            new_user = User(username=self.username, email=self.email); new_user.set_password(self.password)
            db.add(new_user); db.commit(); db.refresh(new_user)
            logger.info(f"User created: {new_user.username}")
            self._set_user_state(new_user)
            token = self._create_access_token(new_user.id)
            if not token:
                self.error_message = "Error al generar token post-registro."; self._clear_auth_state(); self.loading = False; return
            self.auth_token = token; self.last_path = "/dashboard"; self.processed_token = False
            self.loading = False; logger.info(f"User {self.email} registered."); self.password = ""; self.confirm_password = ""
            return rx.redirect(self.last_path)
        except Exception as e:
            logger.error(f"Registration error: {e}", exc_info=True); self.error_message = "Error inesperado."
            self._clear_auth_state(); self.loading = False; self.password = ""; self.confirm_password = ""
        finally:
            if db and db.is_active: db.close()
            
    @rx.event
    async def logout(self):
        logger.info(f"User {self.username} logging out.")
        self._clear_auth_state() 
        self.portfolio_items = []; self.total_portfolio_value = 0.0; self.processed_news = []
        self.recent_transactions = []; self.error_message = ""; self.loading = False
        self.active_tab = "login"; self.processed_token = False; self.last_path = "/"
        self.password = ""; self.confirm_password = "" 
        return rx.redirect("/")

    @rx.event
    async def on_load(self):
        current_path = self.router.page.path
        logger.info(f"on_load: Path='{current_path}', Token? {'Yes' if self.auth_token else 'No'}, Processed? {self.processed_token}, Auth? {self.is_authenticated}")
        if current_path == "/login" and self.active_tab != "login": self.active_tab = "login"
        elif current_path == "/registro" and self.active_tab != "register": self.active_tab = "register"
        if self.processed_token and self.last_path == current_path and self.is_authenticated == (self._get_user_id_from_token(self.auth_token) > 0) :
            logger.info(f"on_load: Already processed for '{current_path}'.")
            return
        self.last_path = current_path 
        if self.auth_token:
            user_id_from_token = self._get_user_id_from_token(self.auth_token)
            if user_id_from_token > 0:
                db = SessionLocal()
                try:
                    user = await asyncio.to_thread(get_user_by_id, db, user_id_from_token)
                    if user:
                        if not self.is_authenticated or self.user_id != user.id: self._set_user_state(user)
                        logger.info(f"on_load: User {self.email} authenticated via token.")
                        if current_path in ["/login", "/registro", "/"]:
                            self.processed_token = True; return rx.redirect("/dashboard")
                    else: 
                        logger.warning(f"on_load: User ID {user_id_from_token} not in DB. Clearing."); self._clear_auth_state()
                except Exception as e: 
                    logger.error(f"on_load DB Error: {e}", exc_info=True); self._clear_auth_state()
                finally:
                    if db and db.is_active: db.close()
            else: 
                logger.info("on_load: Invalid/expired token. Clearing."); self._clear_auth_state()
        else: 
             logger.info("on_load: No auth token."); self.is_authenticated = False
        protected_route_prefixes = ["/dashboard", "/profile", "/noticias", "/detalles_accion"]
        is_on_protected_route = any(current_path.startswith(p) for p in protected_route_prefixes)
        if not self.is_authenticated and is_on_protected_route:
            self.processed_token = True; return rx.redirect("/login")
        self.processed_token = True
        logger.info(f"on_load: Done for '{current_path}'. Auth: {self.is_authenticated}")

    # Dentro de la clase AuthState:
    async def _load_current_stock_shares_owned(self):
        self.current_stock_shares_owned = 0 # Resetear por si acaso
        if not self.user_id or not self.viewing_stock_symbol:
            return

        db = None
        try:
            db = SessionLocal()
            stock_db_entry = await asyncio.to_thread(
                db.query(StockModel).filter(StockModel.symbol == self.viewing_stock_symbol).first
            )
            if not stock_db_entry:
                logger.info(f"No stock entry found for {self.viewing_stock_symbol} while loading shares owned.")
                return

            # Sumar todas las transacciones de compra para esta acción
            buys_result = await asyncio.to_thread(
                db.query(func.sum(StockTransaction.quantity))
                .filter(
                    StockTransaction.user_id == self.user_id,
                    StockTransaction.stock_id == stock_db_entry.id,
                    StockTransaction.transaction_type == TransactionType.COMPRA # Usa tu enum
                ).scalar
            )
            sells_result = await asyncio.to_thread(
                db.query(func.sum(StockTransaction.quantity))
                .filter(
                    StockTransaction.user_id == self.user_id,
                    StockTransaction.stock_id == stock_db_entry.id,
                    StockTransaction.transaction_type == TransactionType.VENTA # Usa tu enum
                ).scalar
            )

            buys_quantity = buys_result or 0
            sells_quantity = sells_result or 0

            # La cantidad en StockTransaction es siempre positiva.
            # El tipo (COMPRA/VENTA) indica la operación.
            self.current_stock_shares_owned = int(buys_quantity - sells_quantity)
            logger.info(f"Shares owned for {self.viewing_stock_symbol} (Stock ID: {stock_db_entry.id}): {self.current_stock_shares_owned} (Buys: {buys_quantity}, Sells: {sells_quantity})")

        except Exception as e:
            logger.error(f"Error loading current stock shares for {self.viewing_stock_symbol}: {e}", exc_info=True)
            self.current_stock_shares_owned = 0 # Fallback
        finally:
            if db and db.is_active:
                await asyncio.to_thread(db.close)

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
        df = self.portfolio_chart_data; default = {"last_price": self.total_portfolio_value, "change": 0.0, "percent_change": 0.0, "is_positive": None}
        if not isinstance(df, pd.DataFrame) or df.empty or 'total_value' not in df.columns or len(df['total_value'].dropna()) < 1: return default
        prices = df['total_value'].dropna(); last_f = float(prices.iloc[-1])
        if len(prices) < 2: return {"last_price": last_f, "change": 0.0, "percent_change": 0.0, "is_positive": None}
        try: first_f = float(prices.iloc[0])
        except: return {"last_price": last_f, "change": 0.0, "percent_change": 0.0, "is_positive": None}
        change_f = last_f - first_f; percent_f = (change_f / first_f * 100) if first_f != 0 else 0.0
        is_positive = change_f > 0 if change_f != 0 else (None if change_f == 0 else False)
        return {"last_price": last_f, "change": change_f, "percent_change": percent_f, "is_positive": is_positive}
    @rx.var
    def is_portfolio_value_change_positive(self) -> Optional[bool]: return self.portfolio_change_info["is_positive"]
    @rx.var
    def formatted_portfolio_value_percent_change(self) -> str: return f"{abs(self.portfolio_change_info['percent_change']):.2f}%"
    @rx.var
    def formatted_portfolio_value_change_abs(self) -> str: return f"{self.portfolio_change_info['change']:+.2f}"
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
        return float(self.portfolio_change_info.get("last_price", 0.0))
    @rx.var
    def portfolio_display_time(self) -> str:
        hover_info = self.portfolio_chart_hover_info
        if hover_info and "x" in hover_info:
            x_data = hover_info["x"]; x_value = x_data[0] if isinstance(x_data, list) and x_data else x_data
            if x_value is not None:
                try:
                    if isinstance(x_value, (str, datetime, pd.Timestamp)): return pd.to_datetime(x_value).strftime('%d %b %Y')
                    return str(x_value)
                except Exception as e: logger.warning(f"Err format portfolio time: {e}"); return str(x_value) if x_value else "--"
        period_map_display = {"1D":"24h","5D":"5d","1M":"1m","6M":"6m","YTD":"Aquest Any","1Y":"1a","5Y":"5a","MAX":"Màx"}
        return period_map_display.get(self.selected_period.upper(), f"Període: {self.selected_period}")
    @rx.var
    def main_portfolio_chart_figure(self) -> go.Figure:
        loading_fig=go.Figure().update_layout(height=300,annotations=[dict(text="Calculant...",showarrow=False)],paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis=dict(visible=False),yaxis=dict(visible=False))
        error_fig=go.Figure().update_layout(height=300,annotations=[dict(text="Sense dades.",showarrow=False)],paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis=dict(visible=False),yaxis=dict(visible=False))
        if self.is_loading_portfolio_chart:return loading_fig
        df=self.portfolio_chart_data
        if not isinstance(df,pd.DataFrame)or df.empty or'total_value'not in df.columns or'time'not in df.columns:return error_fig
        try:
            df_chart=df.copy();df_chart['time']=pd.to_datetime(df_chart['time'],errors='coerce',utc=True);df_chart['total_value']=pd.to_numeric(df_chart['total_value'],errors='coerce');df_chart=df_chart.dropna(subset=['time','total_value']).sort_values(by='time')
            if df_chart.empty or len(df_chart)<2:return error_fig
            fig=go.Figure();fig.add_trace(go.Scatter(x=df_chart['time'],y=df_chart['total_value'],mode='lines',line=dict(width=0),fill='tozeroy',fillcolor=self.portfolio_chart_area_color,hoverinfo='skip'));fig.add_trace(go.Scatter(x=df_chart['time'],y=df_chart['total_value'],mode='lines',line=dict(color=self.portfolio_chart_color,width=2.5,shape='spline'),name='Valor Total',hovertemplate='<b>Valor:</b> $%{y:,.2f}<br><b>Fecha:</b> %{x|%d %b %Y, %H:%M}<extra></extra>'))
            min_v,max_v=df_chart['total_value'].min(),df_chart['total_value'].max();padding=(max_v-min_v)*0.1 if(max_v!=min_v)else abs(min_v)*0.1 or 1000;range_min,range_max=min_v-padding,max_v+padding
            fig.update_layout(height=300,margin=dict(l=50,r=10,t=10,b=30),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis=dict(showgrid=False,zeroline=False,tickmode='auto',nticks=6,showline=True,linewidth=1,linecolor='var(--gray-a6)',tickangle=-30,tickfont=dict(color="var(--gray-11)")),yaxis=dict(title=None,showgrid=True,gridcolor='var(--gray-a4)',zeroline=False,showline=False,side='left',tickformat="$,.0f",range=[range_min,range_max],tickfont=dict(color="var(--gray-11)")),hovermode='x unified',showlegend=False);return fig
        except Exception as e:logger.error(f"Err portfolio chart: {e}");return error_fig
    @rx.var
    def stock_detail_chart_change_info(self)->Dict[str,Any]:
        df=self.current_stock_history;default_info={"last_price":self.current_stock_info.get("currentPrice",0.0),"change":0.0,"percent_change":0.0,"is_positive":None,"first_price_time":None,"last_price_time":None}
        if self.current_stock_info.get("currentPrice")is not None:
            try:default_info["last_price"]=float(self.current_stock_info.get("currentPrice"))
            except:pass
        if not isinstance(df,pd.DataFrame)or df.empty or'price'not in df.columns or'time'not in df.columns:return default_info
        prices=df['price'].dropna();times=df['time'].dropna()
        if prices.empty or times.empty or len(prices)!=len(times)or len(prices)<1:return default_info
        last_f=float(prices.iloc[-1]);last_t=pd.to_datetime(times.iloc[-1]);default_info["last_price"]=last_f;default_info["last_price_time"]=last_t
        if len(prices)<2:return default_info
        first_f=float(prices.iloc[0]);first_t=pd.to_datetime(times.iloc[0]);change_f=last_f-first_f
        percent_f=(change_f/first_f*100)if first_f!=0 else 0.0;is_positive=change_f>0 if change_f!=0 else None
        return{"last_price":last_f,"change":change_f,"percent_change":percent_f,"is_positive":is_positive,"first_price_time":first_t,"last_price_time":last_t}
    @rx.var
    def stock_detail_display_price(self)->str:
        hover_info=self.stock_detail_chart_hover_info;change_info=self.stock_detail_chart_change_info;price_to_display=change_info.get("last_price",0.0);currency_symbol=self.current_stock_info.get("currencySymbol","$")
        if hover_info and"y"in hover_info:
            hover_y_data=hover_info["y"];y_to_convert=hover_y_data[0]if isinstance(hover_y_data,list)and hover_y_data else hover_y_data
            if y_to_convert is not None:
                try:price_to_display=float(y_to_convert)
                except:pass
        return f"{currency_symbol}{price_to_display:,.2f}"
    @rx.var
    def is_current_stock_info_empty(self)->bool:return not self.current_stock_info or"error"in self.current_stock_info or not self.current_stock_info.get("symbol")
    @rx.var
    def current_stock_metrics_list(self)->List[Tuple[str,str]]:return list(self.current_stock_metrics.items())
    @rx.var
    def stock_detail_display_time_or_change(self)->str:
        hover_info=self.stock_detail_chart_hover_info;change_info=self.stock_detail_chart_change_info
        if hover_info and"x"in hover_info:
            x_data=hover_info["x"];x_value=x_data[0]if isinstance(x_data,list)and x_data else x_data
            if x_value is not None:
                try:
                    dt_obj=pd.to_datetime(x_value)
                    if self.current_stock_selected_period.upper()in["1D","5D"]or(change_info.get("last_price_time")and change_info.get("first_price_time")and isinstance(change_info["last_price_time"],pd.Timestamp)and isinstance(change_info["first_price_time"],pd.Timestamp)and(change_info["last_price_time"]-change_info["first_price_time"]).days<2):return dt_obj.strftime('%d %b, %H:%M')
                    return dt_obj.strftime('%d %b %Y')
                except:return str(x_value)if x_value else"--"
        change_val=change_info.get("change",0.0);percent_change_val=change_info.get("percent_change",0.0);currency_symbol=self.current_stock_info.get("currencySymbol","$")
        period_map_display={"1D":"Avui","5D":"5 Dies","1M":"1 Mes","6M":"6 Mesos","YTD":"Aquest Any","1A":"1 Any","ENG":"Aquest Any","5A":"5 Anys","MAX":"Màxim"}
        period_display_name=period_map_display.get(self.current_stock_selected_period.upper(),self.current_stock_selected_period)
        return f"{currency_symbol}{change_val:+.2f} ({percent_change_val:+.2f}%) {period_display_name}"
    @rx.var
    def stock_detail_change_color(self)->str:
        is_positive=self.stock_detail_chart_change_info.get("is_positive")
        if self.stock_detail_chart_hover_info and"x"in self.stock_detail_chart_hover_info:return"var(--gray-11)"
        if is_positive is True:return"var(--green-10)"
        if is_positive is False:return"var(--red-10)"
        return"var(--gray-11)"
    @rx.var
    def current_stock_change_color(self) -> str:
        change = self.current_stock_info.get('change', 0)
        if change > 0:
            return "green"
        elif change < 0:
            return "red"
        return "gray"
    @rx.var
    def stock_detail_chart_figure(self)->go.Figure:
        df=self.current_stock_history;fig=go.Figure();error_fig=go.Figure().update_layout(height=350,annotations=[dict(text="Dades no disponibles",showarrow=False)],paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis=dict(visible=False),yaxis=dict(visible=False))
        if df.empty or not all(c in df.columns for c in['time','price']):logger.warning("Stock detail chart: Invalid df.");return error_fig
        prices=df["price"].dropna();times=pd.to_datetime(df.loc[prices.index,"time"],utc=True).dropna();prices=prices.loc[times.index]
        if prices.empty or len(prices)<1:logger.warning("Stock detail chart: Empty after NaN drop.");return error_fig
        line_color="var(--gray-9)";fill_color_base='128,128,128'
        if len(prices)>1:
            if prices.iloc[-1]>prices.iloc[0]:line_color="var(--green-9)";fill_color_base='34,197,94'
            elif prices.iloc[-1]<prices.iloc[0]:line_color="var(--red-9)";fill_color_base='239,68,68'
        fill_color_rgba=f"rgba({fill_color_base},0.1)"
        fig.add_trace(go.Scatter(x=times,y=prices,mode="lines",line=dict(color=line_color,width=2,shape='spline'),fill='tozeroy',fillcolor=fill_color_rgba,hovertemplate='<b>Preu:</b> %{y:,.2f}<br><b>Data:</b> %{x|%d %b %Y, %H:%M}<extra></extra>'))
        fig.update_layout(height=350,margin=dict(l=50,r=10,t=10,b=30),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",xaxis=dict(showgrid=False,zeroline=False,tickmode="auto",nticks=6,showline=True,linewidth=1,linecolor="var(--gray-a6)",tickangle=-30,tickfont=dict(color="var(--gray-11)")),yaxis=dict(title=None,showgrid=True,gridcolor="var(--gray-a4)",zeroline=False,showline=False,side="left",tickformat="$,.2f",tickfont=dict(color="var(--gray-11)")),hovermode="x unified",showlegend=False)
        return fig

    # --- Event Handlers de UI ---
    def portfolio_chart_handle_hover(self, event_data: List):
        new_hover_info = None; points = None
        if event_data and isinstance(event_data, list) and event_data[0] and isinstance(event_data[0], dict):
            points = event_data[0].get('points')
        if points and isinstance(points, list) and points[0] and isinstance(points[0], dict):
            new_hover_info = points[0]
        if self.portfolio_chart_hover_info != new_hover_info: self.portfolio_chart_hover_info = new_hover_info
    def portfolio_chart_handle_unhover(self, _):
        if self.portfolio_chart_hover_info is not None: self.portfolio_chart_hover_info = None
    def portfolio_toggle_change_display(self):
        self.portfolio_show_absolute_change = not self.portfolio_show_absolute_change
    def stock_detail_chart_handle_hover(self, event_data: List):
        new_hover_info = None
        if event_data and isinstance(event_data, list) and event_data[0] and isinstance(event_data[0], dict):
            points = event_data[0].get('points')
            if points and isinstance(points, list) and points[0] and isinstance(points[0], dict):
                new_hover_info = points[0]
        if self.stock_detail_chart_hover_info != new_hover_info: self.stock_detail_chart_hover_info = new_hover_info
    def stock_detail_chart_handle_unhover(self, _):
        if self.stock_detail_chart_hover_info is not None: self.stock_detail_chart_hover_info = None
    def change_style(self, style: str): self.selected_style = style; logger.info(f"Theme style to {style}")

    # --- Métodos de Noticias ---
    def _create_fallback_news(self):
        logger.warning("Creating fallback news item.")
        self.processed_news = [NewsArticle(title="Error al cargar noticias", url="#", publisher="Sistema", date=datetime.now().strftime("%d %b %Y, %H:%M"), summary="No se pudieron obtener las noticias.", image="")]
        self.has_news = True
    @rx.event
    async def get_news(self, new_query: Optional[str] = None):
        if self.is_loading_news: return
        self.is_loading_news = True
        if new_query is not None:
            self.SEARCH_QUERY = new_query.strip() if new_query.strip() else DEFAULT_SEARCH_QUERY
            self.news_page = 1; self.processed_news = []; self.has_news = False
        logger.info(f"Fetching news: '{self.SEARCH_QUERY}', page: {self.news_page}")
        try:
            params = {"q": self.SEARCH_QUERY, "token": GNEWS_API_KEY, "lang": "es", "country": "any", "max": self.max_articles, "sortby": "publishedAt", "page": self.news_page}
            response = await asyncio.to_thread(requests.get, GNEWS_API_URL, params=params)
            response.raise_for_status(); data = response.json(); articles = data.get("articles", [])
            if not articles:
                if self.news_page == 1: self._create_fallback_news()
                else: self.has_news = False 
                self.is_loading_news = False; return
            page_articles = []
            for article in articles:
                try:
                    dt_obj = datetime.strptime(article.get("publishedAt",""), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) if article.get("publishedAt") else datetime.now(timezone.utc)
                    page_articles.append(NewsArticle(title=article.get("title","S/T"), url=article.get("url","#"), publisher=article.get("source",{}).get("name","N/A"), date=dt_obj.strftime("%d %b %Y, %H:%M %Z"), summary=article.get("description","N/A."), image=article.get("image","")))
                except Exception as e_art: logger.error(f"Error processing article: {e_art}", exc_info=True)
            if self.news_page == 1: self.processed_news = page_articles
            else: self.processed_news.extend(page_articles)
            self.has_news = bool(self.processed_news)
            if articles: self.news_page += 1
            else: self.has_news = False 
        except Exception as e: logger.error(f"Error fetching news: {e}", exc_info=True);
        finally: self.is_loading_news = False
    @rx.event
    async def load_more_news(self):
        if not self.is_loading_news and self.has_news: await self.get_news()
    @rx.event
    async def set_news_search_query_and_fetch(self, query: str): await self.get_news(new_query=query)

    # --- Métodos para Búsqueda de Acciones (en AuthState) ---
    def set_search_term(self, term: str): self.search_term = term; self.search_error = ""
    @rx.event
    async def search_stock_global(self): # Renombrado para evitar conflicto con SearchState.search_stock si se usaran juntos
        if not self.search_term: self.search_error = "Introduce símbolo/nombre."; self.search_result = SearchResultItem(); return
        self.is_searching = True; self.search_error = ""; self.search_result = SearchResultItem()
        query_upper = self.search_term.strip().upper(); symbol_to_fetch = COMPANY_MAP.get(query_upper, query_upper)
        logger.info(f"AuthState global search: '{self.search_term}', ticker '{symbol_to_fetch}'")
        try:
            ticker_obj = await asyncio.to_thread(yf.Ticker, symbol_to_fetch)
            info = await asyncio.to_thread(getattr, ticker_obj, 'info')
            if not info or (info.get("regularMarketPrice") is None and info.get("currentPrice") is None and ("longName" not in info and "shortName" not in info)):
                self.search_error = f"No info para '{self.search_term}' ({symbol_to_fetch})."; self.is_searching = False; return
            price_val = info.get("currentPrice", info.get("regularMarketPrice", info.get("previousClose",0.0)))
            price_str = f"{info.get('currencySymbol','$')}{float(price_val):,.2f}" if isinstance(price_val,(int,float)) else "N/A"
            self.search_result = SearchResultItem(Symbol=info.get("symbol",symbol_to_fetch), Name=info.get("longName",info.get("shortName",symbol_to_fetch)), Current_Price=price_str, Logo=info.get("logo_url", f"/assets/{symbol_to_fetch.upper()}.png"))
        except Exception as e: logger.error(f"Error search_stock_global {symbol_to_fetch}: {e}", exc_info=True); self.search_error = f"Error buscando '{self.search_term}'."
        finally: self.is_searching = False
    @rx.event
    def go_to_stock_detail_global(self, symbol: str):
        if symbol and symbol != "No encontrado" and not symbol.startswith("Error"): return rx.redirect(f"/detalles_accion/{symbol.upper()}")
        return rx.window_alert("No se puede navegar para este resultado.")

    # --- Métodos para Detalles de Acción ---
    @rx.event
    async def set_current_stock_period(self, period: str): 
        self.current_stock_selected_period = period
        self.stock_detail_chart_hover_info = None
        logger.info(f"Stock detail period changed to {period}. Triggering chart update for {self.viewing_stock_symbol}.")
        await self._update_current_stock_chart_data_internal()
        
    def _fetch_stock_history_data(self, symbol: str, period: str) -> pd.DataFrame:
        db = SessionLocal(); df_result = pd.DataFrame(columns=['time', 'price'])
        try:
            stock = db.query(StockModel).filter(StockModel.symbol == symbol).first()
            if not stock: logger.warning(f"Stock '{symbol}' not in DB for history."); return df_result
            end_date = datetime.now(timezone.utc); start_date = None
            days_map = {"1D":1,"5D":5,"1M":30,"6M":180,"YTD":None,"1A":365,"1Y":365,"5A":365*5,"5Y":365*5,"MAX":None}
            period_upper = period.upper()
            if period_upper in days_map and days_map[period_upper] is not None: start_date = end_date - timedelta(days=days_map[period_upper])
            elif period_upper == "YTD": start_date = datetime(end_date.year,1,1,tzinfo=timezone.utc)
            elif period_upper != "MAX": logger.warning(f"Unrecognized period '{period}', defaulting to 1M."); start_date = end_date - timedelta(days=30)
            query_stmt = select(StockPriceHistory.timestamp, StockPriceHistory.price).where(StockPriceHistory.stock_id == stock.id)
            if start_date: query_stmt = query_stmt.where(StockPriceHistory.timestamp >= start_date)
            query_stmt = query_stmt.order_by(StockPriceHistory.timestamp.asc())
            with SessionLocal() as session: df = pd.read_sql(query_stmt, session.bind)
            if not df.empty:
                df = df.rename(columns={"timestamp":"time"}); df['price'] = pd.to_numeric(df['price'],errors='coerce')
                df['time'] = pd.to_datetime(df['time'],errors='coerce',utc=True)
                df_result = df.dropna(subset=['price','time']).sort_values(by='time')
        except Exception as e: logger.error(f"Error fetching DB history for {symbol} ({period}): {e}", exc_info=True)
        finally:
            if db and db.is_active: db.close()
        return df_result

    async def _update_portfolio_chart_data(self):
        if not self.is_authenticated:
            return
        
        db = SessionLocal()
        try:
            # Obtener todas las transacciones del usuario
            transactions = db.query(StockTransaction).filter(StockTransaction.user_id == self.user_id).all()
            
            # Crear un diccionario para almacenar el historial de precios por acción
            stock_history = {}
            
            for trans in transactions:
                stock = db.query(Stock).filter(Stock.id == trans.stock_id).first()
                if not stock:
                    continue
                
                if stock.symbol not in stock_history:
                    stock_history[stock.symbol] = []
                
                # Obtener historial de precios para esta acción
                history = db.query(StockPriceHistory).filter(
                    StockPriceHistory.stock_id == stock.id
                ).order_by(StockPriceHistory.timestamp.asc()).all()
                
                if history:
                    for entry in history:
                        stock_history[stock.symbol].append({
                            'time': entry.timestamp,
                            'price': float(entry.price)
                        })
            
            # Calcular el valor total del portafolio para cada punto en el tiempo
            portfolio_values = []
            for symbol, history in stock_history.items():
                for entry in history:
                    portfolio_values.append({
                        'time': entry['time'],
                        'value': entry['price']  # Aquí deberías multiplicar por la cantidad de acciones
                    })
            
            if portfolio_values:
                df = pd.DataFrame(portfolio_values)
                df = df.groupby('time')['value'].sum().reset_index()
                df = df.sort_values('time')
                self.portfolio_chart_data = df
            else:
                self.portfolio_chart_data = pd.DataFrame(columns=['time', 'total_value'])
            
        except Exception as e:
            logger.error(f"Error updating portfolio chart: {e}")
            self.portfolio_chart_data = pd.DataFrame(columns=['time', 'total_value'])
        finally:
            db.close()

    async def _load_recent_transactions(self):
        logger.info(f"Loading Recent Transactions for user_id: {self.user_id}")
        if not self.user_id:
            self.recent_transactions = []
            return

        db = None
        new_trans_list = []
        try:
            db = SessionLocal()
            # get_transaction_history_with_profit_loss es síncrona
            raw_transactions_data = await asyncio.to_thread(
                get_transaction_history_with_profit_loss, db, self.user_id, limit=10
            )

            for t_data_dict in raw_transactions_data:
                # Convertir timestamp ISO string a formato dd/mm/yy HH:MM
                dt_obj = datetime.fromisoformat(t_data_dict["timestamp"])
                formatted_timestamp = dt_obj.strftime("%d/%m/%y %H:%M")

                # Determinar el tipo de transacción y formatear el mensaje
                trans_type = t_data_dict["type"].capitalize()
                quantity = int(t_data_dict["quantity"])
                symbol = t_data_dict["stock_symbol"]
                price = float(t_data_dict["price"])
                total = quantity * price

                new_trans_list.append(TransactionDisplayItem(
                    timestamp=formatted_timestamp,
                    symbol=symbol,
                    quantity=quantity,
                    price=price,
                    type=trans_type
                ))
            self.recent_transactions = new_trans_list
            logger.info(f"Loaded {len(self.recent_transactions)} recent transactions using CRUD function.")
        except Exception as e:
            logger.error(f"Error loading recent transactions via CRUD: {e}", exc_info=True)
            self.recent_transactions = [] # Fallback
        finally:
            if db:
                await asyncio.to_thread(db.close)

    async def _fetch_stock_history_data_detail(self, symbol: str, period: str) -> pd.DataFrame:
        logger.info(f"Fetching yfinance history for DETAIL: {symbol}, period {period}")
        try:
            ticker = yf.Ticker(symbol)
            yf_map={"1D":"1d","5D":"5d","1M":"1mo","6M":"6mo","YTD":"ytd","1A":"1y","1Y":"1y","5A":"5y","5Y":"5y","ENG":"ytd","MAX":"max"}
            yf_p=yf_map.get(period.upper(),"1mo"); interval="1d"
            if yf_p=="1d":interval="1m"
            elif yf_p=="5d":interval="5m"
            hist=await asyncio.to_thread(ticker.history,period=yf_p,interval=interval,auto_adjust=True,prepost=False)
            if not hist.empty:
                hist=hist.reset_index(); date_col=next((c for c in ['Datetime','Date'] if c in hist.columns),None)
                if not date_col: logger.error(f"Date col not found for {symbol}"); return pd.DataFrame(columns=['time','price'])
                hist=hist.rename(columns={date_col:'time','Close':'price'}); hist['time']=pd.to_datetime(hist['time'],utc=True)
                return hist[['time','price']]
            logger.warning(f"YF empty history for {symbol} ({yf_p}, {interval})"); return pd.DataFrame(columns=['time','price'])
        except Exception as e: logger.error(f"Error YF history {symbol}: {e}",exc_info=True); return pd.DataFrame(columns=['time','price'])

    async def _update_current_stock_chart_data_internal(self):
        if not self.viewing_stock_symbol: self.current_stock_history=pd.DataFrame(columns=['time','price']); return
        df=await self._fetch_stock_history_data_detail(self.viewing_stock_symbol,self.current_stock_selected_period)
        if isinstance(df,pd.DataFrame) and not df.empty and 'time' in df.columns and 'price' in df.columns:
            self.current_stock_history=df.sort_values(by='time')
        else: logger.warning(f"Could not load chart for {self.viewing_stock_symbol}"); self.current_stock_history=pd.DataFrame(columns=['time','price'])

    @rx.event
    async def load_stock_page_data(self, symbol: str):
        """Load stock data for the details page."""
        if not self.is_authenticated:
            return

        self.viewing_stock_symbol = symbol.upper()
        self.current_stock_info = {}
        self.current_stock_shares_owned = 0
        self.transaction_message = ""
        
        try:
            session = SessionLocal()
            
            # Get stock info
            stock = session.query(Stock).filter(Stock.symbol == symbol.upper()).first()
            if not stock:
                self.current_stock_info = {"error": "Acción no encontrada"}
                return
                
            self.current_stock_info = {
                "name": stock.name,
                "sector": stock.sector,
                "current_price": float(stock.current_price),
                "change": float(stock.price_change_percent),
            }
            
            # Get shares owned
            portfolio = session.query(PortfolioItemDB).filter(
                PortfolioItemDB.user_id == self.user_id,
                PortfolioItemDB.stock_symbol == symbol.upper()
            ).first()
            
            if portfolio:
                self.current_stock_shares_owned = portfolio.quantity
            
            # Get historical prices for chart
            history = session.query(StockPriceHistory).filter(
                StockPriceHistory.stock_symbol == symbol.upper()
            ).order_by(StockPriceHistory.timestamp).all()
            
            if history:
                self.stock_chart_data = [{
                    "x": [h.timestamp for h in history],
                    "y": [float(h.price) for h in history],
                    "type": "scatter",
                    "mode": "lines",
                    "name": symbol.upper()
                }]
                
                self.stock_chart_layout = {
                    "title": f"Precio Histórico - {symbol.upper()}",
                    "xaxis": {"title": "Fecha"},
                    "yaxis": {"title": "Precio (USD)"}
                }
            
        except Exception as e:
            logger.error(f"Error loading stock data: {str(e)}")
            self.current_stock_info = {"error": f"Error al cargar datos: {str(e)}"}
        finally:
            session.close()

    @rx.event
    async def buy_stock(self):
        """Buy stock shares."""
        if not self.is_authenticated or not self.viewing_stock_symbol:
            return
            
        try:
            session = SessionLocal()
            
            # Get stock and user
            stock = session.query(Stock).filter(Stock.symbol == self.viewing_stock_symbol).first()
            user = session.query(User).filter(User.id == self.user_id).first()
            
            if not stock or not user:
                self.transaction_message = "Error: Acción o usuario no encontrado"
                return
                
            total_cost = float(stock.current_price) * self.buy_sell_quantity
            
            if float(user.account_balance) < total_cost:
                self.transaction_message = "Error: Saldo insuficiente"
                return
                
            # Update user balance
            user.account_balance = float(user.account_balance) - total_cost
            self.account_balance = float(user.account_balance)
            
            # Update portfolio
            portfolio = session.query(PortfolioItemDB).filter(
                PortfolioItemDB.user_id == self.user_id,
                PortfolioItemDB.stock_symbol == self.viewing_stock_symbol
            ).first()
            
            if portfolio:
                portfolio.quantity += self.buy_sell_quantity
            else:
                portfolio = PortfolioItemDB(
                    user_id=self.user_id,
                    stock_symbol=self.viewing_stock_symbol,
                    quantity=self.buy_sell_quantity
                )
                session.add(portfolio)
            
            # Record transaction
            transaction = StockTransaction(
                user_id=self.user_id,
                stock_id=stock.id,
                quantity=self.buy_sell_quantity,
                price=float(stock.current_price),
                transaction_type="BUY"
            )
            session.add(transaction)
            
            session.commit()
            self.current_stock_shares_owned = portfolio.quantity
            self.transaction_message = f"Transacción realizada con éxito: {self.buy_sell_quantity} acciones de {self.viewing_stock_symbol}"
            
        except Exception as e:
            logger.error(f"Error buying stock: {str(e)}")
            self.transaction_message = f"Error compra: {str(e)[:100]}"
            session.rollback()
        finally:
            session.close()

    @rx.event
    async def sell_stock(self):
        """Sell stock shares."""
        if not self.is_authenticated or not self.viewing_stock_symbol:
            return
            
        try:
            session = SessionLocal()
            
            # Get stock and portfolio
            stock = session.query(Stock).filter(Stock.symbol == self.viewing_stock_symbol).first()
            portfolio = session.query(PortfolioItemDB).filter(
                PortfolioItemDB.user_id == self.user_id,
                PortfolioItemDB.stock_symbol == self.viewing_stock_symbol
            ).first()
            
            if not stock or not portfolio:
                self.transaction_message = "Error: Acción o portfolio no encontrado"
                return
                
            if portfolio.quantity < self.buy_sell_quantity:
                self.transaction_message = "Error: No tienes suficientes acciones"
                return
                
            total_value = float(stock.current_price) * self.buy_sell_quantity
            
            # Update user balance
            user = session.query(User).filter(User.id == self.user_id).first()
            user.account_balance = float(user.account_balance) + total_value
            self.account_balance = float(user.account_balance)
            
            # Update portfolio
            portfolio.quantity -= self.buy_sell_quantity
            if portfolio.quantity == 0:
                session.delete(portfolio)
            
            # Record transaction
            transaction = StockTransaction(
                user_id=self.user_id,
                stock_id=stock.id,
                quantity=self.buy_sell_quantity,
                price=float(stock.current_price),
                transaction_type="SELL"
            )
            session.add(transaction)
            
            session.commit()
            self.current_stock_shares_owned = portfolio.quantity if portfolio.quantity > 0 else 0
            self.transaction_message = f"Transacción realizada con éxito: {self.buy_sell_quantity} acciones de {self.viewing_stock_symbol}"
            
        except Exception as e:
            logger.error(f"Error selling stock: {str(e)}")
            self.transaction_message = f"Error venta: {str(e)[:100]}"
            session.rollback()
        finally:
            session.close()

    @rx.event
    async def dashboard_on_mount(self): 
        logger.info(f"Dashboard on_mount: Loading for user {self.username} (ID: {self.user_id}).")
        if not self.is_authenticated or not self.user_id:
            logger.warning("User not authenticated on dashboard_on_mount, redirecting to login.")
            return rx.redirect("/login")

        # Cargar datos desde la BD
        await self._load_recent_transactions()
        await self._update_portfolio_chart_data()

        # Simulación de PNLs si no tienes lógica real aún
        self.daily_pnl = random.uniform(-500, 500) 
        self.monthly_pnl = random.uniform(-2000, 2000)
        self.yearly_pnl = random.uniform(-10000, 10000)

        logger.info("Dashboard on_mount: Data loading complete.")

    @rx.event
    async def news_page_on_mount(self):
        logger.info("NewsPage on_mount.")
        if not self.processed_news and not self.is_loading_news:
            await self.get_news(new_query=self.SEARCH_QUERY or DEFAULT_SEARCH_QUERY)

    @rx.event
    async def stock_detail_page_on_mount(self):
        logger.info(f"StockDetailPage on_mount. Current viewing: {self.viewing_stock_symbol}, Router params: {self.router.page.params}")
        route_symbol = self.router.page.params.get("symbol") # Símbolo de la URL
        if not route_symbol:
            self.current_stock_info = {"error": "Símbolo de acción no especificado en la URL."}
            self.is_loading_current_stock_details = False
            return

        # Limpiar estado anterior si el símbolo es diferente
        if self.viewing_stock_symbol.upper() != route_symbol.upper():
            self.current_stock_info = {}
            self.current_stock_metrics = {}
            self.current_stock_history = pd.DataFrame(columns=['time','price'])
            self.current_stock_shares_owned = 0
            self.buy_sell_message = ""
            self.buy_sell_quantity = 1

        self.viewing_stock_symbol = route_symbol.upper() # Actualizar el símbolo que estamos viendo

        # Solo recargar si el símbolo es nuevo o si la información está vacía/errónea
        # O si no se está ya cargando para evitar llamadas múltiples
        if not self.is_loading_current_stock_details:
            if not self.current_stock_info or self.current_stock_info.get("symbol","").upper() != self.viewing_stock_symbol:
                await self.load_stock_page_data(symbol=self.viewing_stock_symbol)
            elif self.is_authenticated and self.user_id : # Si la info es la correcta, solo recargar shares_owned
                await self._load_current_stock_shares_owned()
        else:
            logger.info(f"Stock details for {self.viewing_stock_symbol} are already loading.")

    @rx.event
    async def profile_page_on_mount(self):
        logger.info("INSIDE AuthState.profile_page_on_mount method")
        if not self.is_authenticated: logger.warning("ProfilePage: Unauthenticated (on_load should handle).")
        else: logger.info(f"ProfilePage: User {self.username} authenticated.")
    @rx.event
    async def buscador_page_on_mount(self):
        logger.info("BuscadorPage on_mount.")

    def get_transaction_message(self, transaction: StockTransaction) -> str:
        action = "Compra" if transaction.transaction_type == TransactionType.COMPRA else "Venta"
        stock = self.get_stock_by_id(transaction.stock_id)
        symbol = stock.symbol if stock else "Desconocido"
        total = transaction.quantity * transaction.price
        return f"{action} de {transaction.quantity} acciones de {symbol} a ${transaction.price:.2f} (Total: ${total:.2f})"

    async def load_portfolio(self):
        if not self.is_authenticated:
            return
        
        db = SessionLocal()
        try:
            # Cargar el portafolio del usuario
            portfolio_items = db.query(PortfolioItemDB).filter(PortfolioItemDB.user_id == self.user_id).all()
            self.portfolio_items = []
            
            for item in portfolio_items:
                stock = db.query(Stock).filter(Stock.id == item.stock_id).first()
                if stock:
                    current_price = float(stock.current_price)
                    quantity = item.quantity
                    current_value = current_price * quantity
                    
                    self.portfolio_items.append(
                        PortfolioItem(
                            symbol=stock.symbol,
                            name=stock.name,
                            quantity=quantity,
                            current_price=current_price,
                            current_value=current_value,
                            logo_url=stock.logo_url or ""
                        )
                    )
            
            # Calcular el valor total del portafolio
            self.total_portfolio_value = sum(item.current_value for item in self.portfolio_items)
            
        except Exception as e:
            logger.error(f"Error loading portfolio: {e}")
            self.portfolio_items = []
            self.total_portfolio_value = 0.0
        finally:
            db.close()

    async def load_transactions(self):
        if not self.is_authenticated:
            return
        
        db = SessionLocal()
        try:
            transactions = db.query(StockTransaction).filter(StockTransaction.user_id == self.user_id).order_by(StockTransaction.timestamp.desc()).all()
            self.transactions = []
            
            for trans in transactions:
                stock = db.query(Stock).filter(Stock.id == trans.stock_id).first()
                if stock:
                    self.transactions.append({
                        "id": trans.id,
                        "symbol": stock.symbol,
                        "type": trans.transaction_type.value,
                        "quantity": trans.quantity,
                        "price": float(trans.price),
                        "total": float(trans.quantity * trans.price),
                        "timestamp": trans.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    })
        except Exception as e:
            logger.error(f"Error loading transactions: {e}")
        finally:
            db.close()
