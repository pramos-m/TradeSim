# tradesim/state/auth_state.py (FINAL FUNCIONAL v10 - CORREGIDO)
import reflex as rx
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from jose import jwt, JWTError
import os
import requests
import traceback
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf # Importar yfinance
from ..database import SessionLocal
from ..models.user import User
from ..models.stock import Stock
from ..models.stock_price_history import StockPriceHistory
import logging
from decimal import Decimal
import random
import asyncio

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# --- Modelos Pydantic/Base ---
class NewsArticle(rx.Base):
    title: str
    url: str
    publisher: str
    date: str
    summary: str
    image: str = ""

class PortfolioItem(rx.Base):
    symbol: str
    name: str
    quantity: int
    current_price: float
    current_value: float
    logo_url: str

class AuthState(rx.State):
    """Estado GLOBAL combinado."""
    # --- Variables ---
    is_authenticated: bool = False
    auth_token: str = rx.Cookie(name="auth_token", max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60)
    processed_token: bool = False
    loading: bool = False
    active_tab: str = "login"
    error_message: str = ""
    username: str = ""
    email: str = ""
    password: str = ""
    confirm_password: str = ""
    account_balance: float = 0.0
    user_id: int | None = None
    last_path: str = ""

    processed_news: List[NewsArticle] = []
    is_loading_news: bool = False
    has_news: bool = False
    news_page: int = 1
    max_articles: int = 10
    selected_style: str = "panel"
    GNEWS_API_KEY = "f767bfe6df4f747e6b77c0178e8cc0d8"
    GNEWS_API_URL = "https://gnews.io/api/v4/search"
    SEARCH_QUERY = "bolsa acciones"

    balance_date: str = datetime.now().strftime("%d/%m/%Y")
    daily_pnl: float = 0.0
    monthly_pnl: float = 0.0
    yearly_pnl: float = 0.0
    daily_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
    monthly_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
    yearly_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])

    portfolio_items: List[PortfolioItem] = []
    total_portfolio_value: float = 0.0

    selected_period: str = "1M"
    portfolio_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'total_value'])
    portfolio_chart_hover_info: Dict | None = None
    portfolio_show_absolute_change: bool = False
    is_loading_portfolio_chart: bool = False

    # --- Métodos Autenticación y Noticias (Sin cambios) ---
    def create_access_token(self, user_id: int) -> str:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        data = {"sub": str(user_id), "exp": expire}
        try:
            return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        except Exception as e:
            logger.error(f"Err token: {e}")
            return ""

    def verify_token(self, token: str | None) -> int:
        if not token:
            return -1
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id_str = payload.get("sub")
            if user_id_str:
                 return int(user_id_str)
            return -1 # No sub claim
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired.")
            return -1
        except (JWTError, ValueError, TypeError) as e:
            logger.error(f"Token verification error: {e}")
            return -1

    @rx.var
    def is_on_auth_page(self) -> bool:
        return self.router.page.path == "/login"

    @rx.event
    async def on_load(self): # Simplificado
        current_path = self.router.page.path
        if self.processed_token and self.last_path == current_path:
            return
        self.processed_token = True
        self.last_path = current_path
        if current_path == "/":
            return
        user_id_from_token = self.verify_token(self.auth_token)
        if user_id_from_token <= 0:
            if self.is_authenticated:
                self.is_authenticated = False
                self.username = ""
                self.email = ""
                self.account_balance = 0.0
                self.user_id = None
            if self.auth_token:
                self.auth_token = ""
            return # @require_auth maneja el redirect
        db = SessionLocal()
        user_valid = False
        try:
            user = db.query(User).filter(User.id == user_id_from_token).first()
            if user:
                if not self.is_authenticated or self.user_id != user.id:
                    self.username = user.username
                    self.email = user.email
                    self.account_balance = float(user.account_balance or 0.0)
                    self.user_id = user.id
                    self.is_authenticated = True
                    logger.info(f"User {self.user_id} loaded.")
                user_valid = True
                if current_path == "/login":
                    yield rx.redirect("/dashboard")
                    return
            else:
                logger.warning(f"User ID {user_id_from_token} not found.")
                self.is_authenticated = False
                self.username = ""
                self.email = ""
                self.account_balance = 0.0
                self.user_id = None
                self.auth_token = ""
        except Exception as e:
            logger.error(f"on_load DB Error: {e}")
            self.is_authenticated = False
            self.account_balance = 0.0
            self.user_id = None
            self.auth_token = ""
        finally:
             if db and db.is_active:
                 db.close()
        if self.is_authenticated and current_path == "/noticias" and not self.processed_news:
            self.get_news()

    @rx.event
    async def login(self): # ... (igual) ...
        self.error_message = ""
        self.loading = True
        if not self.email or not self.password:
            self.error_message = "Complete campos"
            self.loading = False
            return
        db = None
        try:
            db = SessionLocal()
            user = db.query(User).filter(User.email.ilike(self.email.strip().lower())).first()
            if not user or not user.verify_password(self.password):
                self.error_message = "Credenciales inválidas"
                self.loading = False
                return
            self.is_authenticated = True
            self.username = user.username
            self.email = user.email
            self.account_balance = float(user.account_balance or 0.0)
            self.user_id = user.id
            token = self.create_access_token(user.id)
            if not token:
                logger.error("Login fail: No token.")
                self.error_message = "Error token."
                self.loading = False
                return
            self.auth_token = token
            self.last_path = "/dashboard"
            self.processed_token = True
            self.loading = False
            return rx.redirect("/dashboard")
        except Exception as e:
            logger.error(f"Login fail: Exception: {e}")
            self.error_message = "Error inesperado."
            self.loading = False
        finally:
            if db and db.is_active:
                db.close()

    @rx.event
    async def register(self): # ... (igual) ...
        self.error_message = ""
        self.loading = True
        if not self.username or not self.email or not self.password:
            self.error_message = "Complete campos"
            self.loading = False
            return
        if self.password != self.confirm_password:
            self.error_message = "Contraseñas no coinciden"
            self.loading = False
            return
        db = None
        try:
            db = SessionLocal()
            existing_user = db.query(User).filter( (User.email.ilike(self.email.strip().lower())) | (User.username.ilike(self.username.strip())) ).first()
            if existing_user:
                self.error_message = "Usuario/email ya existen"
                self.loading = False
                return
            new_user = User(username=self.username.strip(), email=self.email.strip().lower())
            new_user.set_password(self.password)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            logger.info(f"User created: {new_user.username}, Balance: {new_user.account_balance}")
            self.is_authenticated = True
            self.username = new_user.username
            self.email = new_user.email
            self.account_balance = float(new_user.account_balance or 0.0)
            self.user_id = new_user.id
            token = self.create_access_token(new_user.id)
            if not token:
                logger.error("Register fail: No token.")
                self.error_message = "Error token."
                self.loading = False
                return
            self.auth_token = token
            self.last_path = "/dashboard"
            self.processed_token = True
            self.loading = False
            return rx.redirect("/dashboard")
        except Exception as e:
            logger.error(f"Register fail: Exception: {e}")
            self.error_message = "Error inesperado."
            self.loading = False
        finally:
            if db and db.is_active:
                db.close()

    @rx.event
    def logout(self): # ... (igual) ...
        self.is_authenticated = False
        self.username = ""
        self.email = ""
        self.password = ""
        self.confirm_password = ""
        self.account_balance = 0.0
        self.auth_token = ""
        self.user_id = None
        self.processed_token = True
        self.last_path = "/"
        self.processed_news = []
        self.portfolio_items = []
        self.total_portfolio_value = 0.0
        self.daily_pnl = 0.0
        self.monthly_pnl = 0.0
        self.yearly_pnl = 0.0
        self.portfolio_chart_data = pd.DataFrame(columns=['time', 'total_value'])
        return rx.redirect("/")

    # Setters...
    def set_active_tab(self, tab: str):
        self.active_tab = tab
        self.error_message = ""

    def set_username(self, username: str):
        self.username = username

    def set_email(self, email: str):
        self.email = email

    def set_password(self, password: str):
        self.password = password

    def set_confirm_password(self, confirm_password: str):
        self.confirm_password = confirm_password

    # --- Métodos Noticias ---
    @rx.var
    def featured_news(self) -> Optional[NewsArticle]:
        return self.processed_news[0] if self.processed_news else None

    @rx.var
    def recent_news_list(self) -> List[NewsArticle]:
        return self.processed_news[1:min(4, len(self.processed_news))] if len(self.processed_news) > 1 else []

    @rx.var
    def can_load_more(self) -> bool:
        return len(self.processed_news) > 0 and not self.is_loading_news

    @rx.event
    def change_style(self, style: str):
        self.selected_style = style

    @rx.event
    def open_url_script(self, url: str): # ... (igual) ...
        if isinstance(url, str) and url.startswith(("http://", "https://")):
            safe_url = url.replace("\\", "\\\\").replace("'", "\\'")
            js_command = f"window.open('{safe_url}', '_blank')"
            return rx.call_script(js_command)
        else:
            logger.warning(f"URL inv\u00E1lida para script: '{url}'.")
            return rx.console_log(f"URL inv\u00E1lida para script: {url}")

    @rx.event
    def get_news(self): # ... (igual) ...
        if self.is_loading_news:
            return
        self.is_loading_news = True
        self.has_news = False
        self.processed_news = []
        self.news_page = 1
        try:
            params = {"q": self.SEARCH_QUERY, "token": self.GNEWS_API_KEY, "lang": "es", "country": "any", "max": self.max_articles, "sortby": "publishedAt", "from": "30d"}
            response = requests.get(self.GNEWS_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])
            if articles:
                processed_articles = []
                for article in articles:
                    try:
                        title = article.get("title", "?")
                        url = article.get("url", "#")
                        src = article.get("source", {})
                        pub = src.get("name", "?")
                        dt_str = article.get("publishedAt", "")
                        sumry = article.get("description", "")
                        img = article.get("image", "")
                        dt_formatted = "?"
                        if dt_str:
                            try:
                                dt_formatted = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%d %b %Y, %H:%M")
                            except ValueError:
                                dt_formatted = "?"
                        processed_articles.append(NewsArticle(title=title, url=url, publisher=pub, date=dt_formatted, summary=sumry, image=img))
                    except Exception as e:
                        logger.error(f"Error procesando article: {e}")
                if processed_articles:
                    self.processed_news = processed_articles
                    self.has_news = True
                else:
                    self._create_fallback_news()
            else:
                self._create_fallback_news()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error red news: {e}")
            self._create_fallback_news()
        except Exception as e:
            logger.error(f"Error get_news: {e}")
            self._create_fallback_news()
        finally:
            self.is_loading_news = False

    @rx.event
    def load_more_news(self): # ... (igual) ...
        if not self.can_load_more or self.is_loading_news:
            return
        self.is_loading_news = True
        self.news_page += 1
        try:
            params = {"q": self.SEARCH_QUERY, "token": self.GNEWS_API_KEY, "lang": "es", "country": "any", "max": self.max_articles, "page": self.news_page, "sortby": "publishedAt", "from": "30d"}
            response = requests.get(self.GNEWS_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])
            if articles:
                new_articles = []
                current_titles = {news.title for news in self.processed_news}
                for article in articles:
                    try:
                        title = article.get("title", "?")
                        if title in current_titles:
                            continue
                        url = article.get("url", "#")
                        src = article.get("source", {})
                        pub = src.get("name", "?")
                        dt_str = article.get("publishedAt", "")
                        sumry = article.get("description", "")
                        img = article.get("image", "")
                        dt_formatted = "?"
                        if dt_str:
                            try:
                                dt_formatted = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%d %b %Y, %H:%M")
                            except ValueError:
                                dt_formatted = "?"
                        news_article = NewsArticle(title=title, url=url, publisher=pub, date=dt_formatted, summary=sumry, image=img)
                        new_articles.append(news_article)
                        current_titles.add(title)
                    except Exception as e:
                        logger.error(f"Error procesando art extra: {e}")
                if new_articles:
                    self.processed_news.extend(new_articles)
                    logger.info(f"Añadidas {len(new_articles)} noticias.")
                else:
                    logger.info("No más noticias nuevas.")
            else:
                logger.info("No más páginas API.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error red load_more: {e}")
        except Exception as e:
            logger.error(f"Error load_more: {e}")
        finally:
            self.is_loading_news = False

    def _create_fallback_news(self):
        logger.warning("Generando fallback news...")
        # ... (lógica igual - assuming correct indentation inside)

    def _add_more_fallback_news(self):
        logger.warning("Añadiendo fallback news...")
        # ... (lógica igual - assuming correct indentation inside)

    # --- Métodos / Variables Computadas del Dashboard y Portfolio ---

    # PNL (calculado para AAPL para las PNL cards)
    def _calculate_stock_pnl(self, symbol: str, period: str, quantity: int) -> Tuple[Optional[float], pd.DataFrame]:
        df_history = self._fetch_stock_history_data(symbol, period)
        pnl: Optional[float] = None
        if not df_history.empty and len(df_history) >= 2:
            try:
                prices = df_history['price'].dropna()
                if len(prices) >= 2:
                    start_price = float(prices.iloc[0])
                    end_price = float(prices.iloc[-1])
                    pnl = (end_price - start_price) * quantity
            except Exception as e:
                logger.error(f"Error PNL {symbol} ({period}): {e}")
                pnl = None
        return pnl, df_history

    # Carga Portfolio (Usa Precios Reales API)
    def _load_simulated_portfolio_with_api_prices(self):
        logger.info("--- Loading Portfolio with API Prices START ---")
        symbols_hardcoded = ['MSFT', 'AAPL', 'NVDA', 'GOOGL', 'TSLA']
        quantities_hardcoded = {'MSFT': 15, 'AAPL': 25, 'NVDA': 5, 'GOOGL': 30, 'TSLA': 10}
        logo_placeholders = { "MSFT": "/microsoft_logo.png", "AAPL": "/apple_logo.png", "NVDA": "/default_logo.png", "GOOGL": "/google_logo.png", "TSLA": "/tesla_logo.png", "DEFAULT": "/default_logo.png" }
        portfolio_list = []
        calculated_total_value = 0.0
        db = SessionLocal()
        try:
            for symbol in symbols_hardcoded:
                current_price = 0.0
                stock_name = symbol
                try:
                    # logger.info(f"Fetching current price for {symbol}...") # Log reducido
                    ticker = yf.Ticker(symbol)
                    hist_1d = ticker.history(period="1d")
                    if not hist_1d.empty:
                        current_price = float(hist_1d['Close'].iloc[-1])
                    else: # Fallback a info si history falla
                        info = ticker.info
                        price_val = info.get("currentPrice", info.get("regularMarketPrice"))
                        if price_val:
                            current_price = float(price_val)
                        else:
                            logger.warning(f"Could not fetch price for {symbol}. Using 0.")
                    # Obtener nombre de la DB como fuente principal si existe
                    stock_db = db.query(Stock.name).filter(Stock.symbol == symbol).first()
                    stock_name = stock_db.name if stock_db else ticker.info.get("longName", symbol) # Nombre API como fallback

                except Exception as api_err:
                    logger.error(f"yfinance error for {symbol}: {api_err}")
                    stock_db = db.query(Stock.name).filter(Stock.symbol == symbol).first()
                    stock_name = stock_db.name if stock_db else symbol # Fallback nombre DB

                simulated_quantity = quantities_hardcoded.get(symbol, 0)
                current_value = simulated_quantity * current_price
                logo_url = logo_placeholders.get(symbol, logo_placeholders["DEFAULT"])
                portfolio_list.append( PortfolioItem( symbol=symbol, name=stock_name, quantity=simulated_quantity, current_price=current_price, current_value=current_value, logo_url=logo_url ) )
                calculated_total_value += current_value
            self.portfolio_items = sorted(portfolio_list, key=lambda x: x.current_value, reverse=True)
            self.total_portfolio_value = calculated_total_value
            logger.info(f"Portfolio state updated: items={len(self.portfolio_items)}, total_value={self.total_portfolio_value:.2f}")
        except Exception as e:
            logger.error(f"Error loading portfolio: {e}", exc_info=True)
            self.portfolio_items = []
            self.total_portfolio_value = 0.0
        finally:
            if db and db.is_active:
                db.close()
            # logger.info("--- Loading Portfolio with API Prices END ---") # Log reducido

    # Fetcher de historial (igual)
    def _fetch_stock_history_data(self, symbol: str, period: str) -> pd.DataFrame:
        db = SessionLocal()
        df_result = pd.DataFrame(columns=['time', 'price'])
        try:
            stock = db.query(Stock).filter(Stock.symbol == symbol).first()
            if not stock:
                return df_result
            end_date = datetime.utcnow()
            start_date = None
            days_map = {"1D": 1, "5D": 5, "1M": 30, "6M": 180, "1A": 365, "5A": 365 * 5}
            if period in days_map:
                start_date = end_date - timedelta(days=days_map[period])
            elif period == "ENG":
                start_date = datetime(end_date.year, 1, 1)
            elif period == "MAX":
                start_date = None
            else:
                start_date = end_date - timedelta(days=1) # Default to 1D

            query = db.query(StockPriceHistory.timestamp, StockPriceHistory.price).filter(StockPriceHistory.stock_id == stock.id)
            if start_date:
                query = query.filter(StockPriceHistory.timestamp >= start_date)
            query = query.order_by(StockPriceHistory.timestamp.asc())
            df = pd.read_sql(query.statement, db.bind)
            if not df.empty:
                df = df.rename(columns={"timestamp": "time"})
                df['price'] = pd.to_numeric(df['price'], errors='coerce')
                df['time'] = pd.to_datetime(df['time'], errors='coerce')
                df = df.dropna(subset=['price', 'time'])
                df_result = df
        except Exception as e:
            logger.error(f"Err _fetch {symbol} {period}: {e}")
        finally:
            if db and db.is_active:
                db.close()
        return df_result

    # --- Lógica Gráfico Portfolio ---
    # QUITAR @rx.background -> Usaremos asyncio.create_task
    async def _update_portfolio_chart_data(self):
        """Calcula valor total portfolio para gráfico."""
        async with self:
            self.is_loading_portfolio_chart = True # Indicar carga
        logger.info(f"--- Updating Portfolio Chart Data START (Period: {self.selected_period}) ---")
        if not self.portfolio_items:
            async with self:
                self.portfolio_chart_data = pd.DataFrame(columns=['time', 'total_value'])
                self.is_loading_portfolio_chart = False
            logger.warning("No portfolio items for chart.")
            return

        db_session = SessionLocal()
        try:
            db_symbols = {s.symbol for s in db_session.query(Stock.symbol).all()}
        finally:
            db_session.close()

        symbols_to_chart = [item.symbol for item in self.portfolio_items if item.symbol in db_symbols]
        quantities = {item.symbol: item.quantity for item in self.portfolio_items if item.symbol in symbols_to_chart}
        period = self.selected_period

        if not symbols_to_chart:
            logger.warning("No symbols with history found for chart.")
            async with self:
                self.portfolio_chart_data = pd.DataFrame(columns=['time', 'total_value'])
                self.is_loading_portfolio_chart = False
            return

        all_history_dict = {}
        # logger.info(f"Fetching history for portfolio chart: {symbols_to_chart}") # Log reducido
        loop = asyncio.get_running_loop()
        fetch_tasks = [loop.run_in_executor(None, self._fetch_stock_history_data, symbol, period) for symbol in symbols_to_chart]
        try:
            results = await asyncio.gather(*fetch_tasks)
        except Exception as e:
            logger.error(f"Error fetching histories: {e}")
            results = []

        for symbol, df in zip(symbols_to_chart, results):
            if isinstance(df, pd.DataFrame) and not df.empty:
                df['time'] = pd.to_datetime(df['time'], errors='coerce')
                df = df.set_index('time')
                all_history_dict[symbol] = df['price'].dropna()
            # else: logger.warning(f"No history for {symbol} ({period})") # Log reducido

        if not all_history_dict:
            logger.warning("No history fetched.")
            async with self:
                self.portfolio_chart_data = pd.DataFrame(columns=['time', 'total_value'])
                self.is_loading_portfolio_chart = False
            return

        try:
            combined_df = pd.DataFrame(all_history_dict)
            combined_df = combined_df.interpolate(method='time', limit_area='inside').bfill(limit=5).ffill(limit=5)
            combined_df = combined_df.dropna(how='all')
            if combined_df.empty:
                logger.warning("Combined history empty.")
                async with self:
                    self.portfolio_chart_data = pd.DataFrame(columns=['time', 'total_value'])
                    self.is_loading_portfolio_chart = False
                return
            total_value_series = pd.Series(0.0, index=combined_df.index)
            for symbol, quantity in quantities.items():
                if symbol in combined_df.columns:
                    total_value_series += combined_df[symbol].fillna(0.0) * quantity
            final_df = pd.DataFrame({'total_value': total_value_series}).reset_index()
            # Actualizar estado DENTRO del async with
            async with self:
                self.portfolio_chart_data = final_df
                # logger.info(f"Portfolio chart data calculated. Rows: {len(self.portfolio_chart_data)}")
        except Exception as e:
            logger.error(f"Error processing history: {e}")
            async with self:
                self.portfolio_chart_data = pd.DataFrame(columns=['time', 'total_value'])
        finally:
            async with self:
                self.is_loading_portfolio_chart = False # Indicar fin de carga
        # logger.info("--- Updating Portfolio Chart Data END ---") # Log reducido

    # --- dashboard_on_mount (Llama a PNL, Portfolio y Gráfico Portfolio) ---
    async def dashboard_on_mount(self):
        logger.info("--- Dashboard on_mount START ---")
        try:
            # Calcular PNL para las cards (ej. AAPL)
            pnl_symbol = "AAPL"
            quantity = 10 # Usar 10 acciones de AAPL como ejemplo para PNL
            if quantity > 0:
                daily_pnl_val, daily_df = self._calculate_stock_pnl(pnl_symbol, "1D", quantity)
                self.daily_pnl = daily_pnl_val if daily_pnl_val is not None else 0.0
                self.daily_pnl_chart_data = daily_df

                monthly_pnl_val, monthly_df = self._calculate_stock_pnl(pnl_symbol, "1M", quantity)
                self.monthly_pnl = monthly_pnl_val if monthly_pnl_val is not None else 0.0
                self.monthly_pnl_chart_data = monthly_df

                yearly_pnl_val, yearly_df = self._calculate_stock_pnl(pnl_symbol, "1A", quantity)
                self.yearly_pnl = yearly_pnl_val if yearly_pnl_val is not None else 0.0
                self.yearly_pnl_chart_data = yearly_df
            else:
                self.daily_pnl, self.monthly_pnl, self.yearly_pnl = 0.0, 0.0, 0.0
                empty_df = pd.DataFrame(columns=['time', 'price'])
                self.daily_pnl_chart_data = empty_df
                self.monthly_pnl_chart_data = empty_df
                self.yearly_pnl_chart_data = empty_df

            # Cargar portfolio simulado (con precios reales API)
            # Esta función es síncrona, así que se ejecuta y termina aquí
            self._load_simulated_portfolio_with_api_prices()

            # Lanzar cálculo del gráfico del portfolio en background
            # Usamos asyncio.create_task para no esperar aquí
            asyncio.create_task(self._update_portfolio_chart_data())

        except Exception as e:
            logger.error(f"Error on_mount: {e}", exc_info=True)
        logger.info("--- Dashboard on_mount END ---")

    # --- set_period (Ahora actualiza gráfico portfolio) ---
    @rx.event
    async def set_period(self, period: str): # Debe ser async
        """Updates selected period and triggers portfolio chart update."""
        self.selected_period = period
        self.portfolio_chart_hover_info = None
        # Lanzar la actualización en background
        asyncio.create_task(self._update_portfolio_chart_data())
        logger.info(f"Period changed to {period}. Portfolio chart update task created.")
        # No necesitamos devolver nada

    # --- Variables Computadas Gráfico Portfolio ---
    @rx.var
    def portfolio_change_info(self) -> Dict[str, Any]: # Renombrado
        df = self.portfolio_chart_data
        default = {"last_price": 0.0, "change": 0.0, "percent_change": 0.0, "is_positive": True}
        if not isinstance(df, pd.DataFrame) or df.empty or 'total_value' not in df.columns:
            return default
        prices = df['total_value'].dropna()
        if len(prices) < 2:
            last_price = float(prices.iloc[-1]) if len(prices) == 1 else 0.0
            return {"last_price": last_price, "change": 0.0, "percent_change": 0.0, "is_positive": True}
        try:
            last_f = float(prices.iloc[-1])
            first_f = float(prices.iloc[0])
        except Exception:
            return default
        change_f = last_f - first_f
        percent_f = (change_f / first_f * 100) if first_f != 0 else 0.0
        return {"last_price": last_f, "change": change_f, "percent_change": percent_f, "is_positive": change_f >= 0}

    @rx.var
    def is_portfolio_value_change_positive(self) -> bool:
        return self.portfolio_change_info["is_positive"]

    @rx.var
    def formatted_portfolio_value_percent_change(self) -> str:
        return f"{abs(self.portfolio_change_info['percent_change']):.2f}"

    @rx.var
    def formatted_portfolio_value_change_abs(self) -> str:
        return f"{self.portfolio_change_info['change']:+.2f}"

    @rx.var
    def portfolio_chart_color(self) -> str:
        return "#22c55e" if self.is_portfolio_value_change_positive else "#ef4444"

    @rx.var
    def portfolio_chart_area_color(self) -> str:
        rgb_color = '34,197,94' if self.is_portfolio_value_change_positive else '239,68,68'
        return f"rgba({rgb_color},0.2)"

    @rx.var
    def portfolio_display_value(self) -> float: # ... (igual) ...
        last_value = float(self.portfolio_change_info.get("last_price", 0.0))
        hover_y = self.portfolio_chart_hover_info.get("y") if self.portfolio_chart_hover_info else None
        y = hover_y[0] if isinstance(hover_y, list) and hover_y else hover_y
        try:
            if isinstance(y, (int, float, str, Decimal)) and y is not None:
                return float(y)
            else:
                return last_value
        except (ValueError, TypeError):
            return last_value

    @rx.var
    def portfolio_display_time(self) -> str: # ... (igual) ...
        if self.portfolio_chart_hover_info and "x" in self.portfolio_chart_hover_info:
            x_data = self.portfolio_chart_hover_info.get("x")
            x = x_data[0] if isinstance(x_data, list) and x_data else x_data
            try:
                time_obj = pd.to_datetime(x)
                return time_obj.strftime('%Y-%m-%d')
            except Exception:
                return str(x) if x else "--"
        return "--"

    @rx.var
    def main_portfolio_chart_figure(self) -> go.Figure: # ... (igual, usa portfolio_chart_data y flag loading) ...
        df = self.portfolio_chart_data
        loading_fig = go.Figure().update_layout(
            height=300, annotations=[dict(text="Calculando gráfico portfolio...", showarrow=False)],
            paper_bgcolor='white', plot_bgcolor='white', xaxis=dict(visible=False), yaxis=dict(visible=False)
        )
        error_fig = go.Figure().update_layout(
            height=300, annotations=[dict(text="Sin datos para gráfico.", showarrow=False)],
            paper_bgcolor='white', plot_bgcolor='white', xaxis=dict(visible=False), yaxis=dict(visible=False)
        )
        if self.is_loading_portfolio_chart:
            return loading_fig
        if not isinstance(df, pd.DataFrame) or df.empty or 'total_value' not in df.columns or 'time' not in df.columns:
            return error_fig
        try:
            df_chart = df.copy()
            df_chart['time'] = pd.to_datetime(df_chart['time'], errors='coerce')
            df_chart['total_value'] = pd.to_numeric(df_chart['total_value'], errors='coerce')
            df_chart = df_chart.dropna(subset=['time', 'total_value'])
            if df_chart.empty or len(df_chart) < 2:
                return error_fig
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_chart['time'], y=df_chart['total_value'], mode='lines',
                line=dict(width=0), fill='tozeroy', fillcolor=self.portfolio_chart_area_color, hoverinfo='skip'
            ))
            fig.add_trace(go.Scatter(
                x=df_chart['time'], y=df_chart['total_value'], mode='lines',
                line=dict(color=self.portfolio_chart_color, width=2.5, shape='spline'), name='Valor Total',
                hovertemplate='<b>Valor:</b> $%{y:,.2f}<br><b>Fecha:</b> %{x|%Y-%m-%d}<extra></extra>'
            ))
            min_v, max_v = df_chart['total_value'].min(), df_chart['total_value'].max()
            padding = (max_v - min_v) * 0.1 if (max_v != min_v) else abs(min_v) * 0.1 or 1000
            range_min, range_max = min_v - padding, max_v + padding
            fig.update_layout(
                height=300, margin=dict(l=50, r=10, t=10, b=30),
                paper_bgcolor='white', plot_bgcolor='white',
                xaxis=dict(showgrid=False, zeroline=False, tickmode='auto', nticks=6, showline=True, linewidth=1, linecolor='lightgrey', tickangle=-30),
                yaxis=dict(title=None, showgrid=True, gridcolor='rgba(230,230,230,0.5)', zeroline=False, showline=False, side='left', tickformat="$,.0f", range=[range_min, range_max]),
                hovermode='x unified', showlegend=False
            )
            return fig
        except Exception as e:
            logger.error(f"Err portfolio chart figure: {e}")
            return error_fig

    # --- Event Handlers Gráfico Portfolio ---
    def portfolio_chart_handle_hover(self, event_data): # Renombrado
        new_hover_info = None
        points = None
        if event_data and isinstance(event_data, list) and event_data[0] and isinstance(event_data[0], dict):
            points = event_data[0].get('points')
        if points and isinstance(points, list) and points[0] and isinstance(points[0], dict):
            new_hover_info = points[0]
        if self.portfolio_chart_hover_info != new_hover_info:
            self.portfolio_chart_hover_info = new_hover_info

    def portfolio_chart_handle_unhover(self, _): # Renombrado
        if self.portfolio_chart_hover_info is not None:
            self.portfolio_chart_hover_info = None

    def portfolio_toggle_change_display(self): # Renombrado
        self.portfolio_show_absolute_change = not self.portfolio_show_absolute_change