# tradesim/state/auth_state.py (FINAL v19 - SIN @rx.background)
import reflex as rx
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from jose import jwt, JWTError
import os
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from ..database import SessionLocal
from ..models.user import User
from ..models.stock import Stock
from ..models.stock_price_history import StockPriceHistory
from ..models.transaction import Transaction
import logging
from decimal import Decimal
import random
import asyncio
import requests

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


class TransactionDisplayItem(rx.Base):
    timestamp: str
    symbol: str
    quantity: int
    price: float
    type: str


class SearchResultItem(rx.Base):
    Symbol: str = ""
    Name: str = "No encontrado"
    Current_Price: str = "N/A"
    Logo: str = "/default_logo.png"


class AuthState(rx.State):
    """Estado GLOBAL combinado."""

    # --- Variables ---
    is_authenticated: bool = False
    portfolio_chart_hover_info: Dict | None = None
    auth_token: str = rx.Cookie(name="auth_token", max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
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
    GNEWS_API_KEY: str = "f767bfe6df4f747e6b77c0178e8cc0d8"
    GNEWS_API_URL: str = "https://gnews.io/api/v4/search"
    SEARCH_QUERY: str = "bolsa acciones"

    balance_date: str = datetime.now().strftime("%d/%m/%Y")
    daily_pnl: float = 0.0
    monthly_pnl: float = 0.0
    yearly_pnl: float = 0.0
    daily_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=["time", "price"])
    monthly_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=["time", "price"])
    yearly_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=["time", "price"])

    portfolio_items: List[PortfolioItem] = []
    total_portfolio_value: float = 0.0
    selected_period: str = "1M"
    portfolio_chart_data: pd.DataFrame = pd.DataFrame(columns=["time", "total_value"])
    # portfolio_chart_hover_info: Dict | None = None # This was duplicated, ensure only one definition
    portfolio_show_absolute_change: bool = False
    is_loading_portfolio_chart: bool = False
    recent_transactions: List[TransactionDisplayItem] = []

    # Variables para Buscador
    search_query: str = ""
    search_result: SearchResultItem = SearchResultItem()
    is_searching: bool = False
    search_error: str = ""

    # Variables for Stock Detail Page
    viewing_stock_symbol: str = ""
    current_stock_info: Dict[str, Any] = {}
    current_stock_metrics: Dict[str, str] = {}
    current_stock_history: pd.DataFrame = pd.DataFrame(columns=["time", "price"])
    current_stock_selected_period: str = "1M"
    is_loading_current_stock_details: bool = False
    stock_detail_chart_hover_info: Dict | None = None

    @rx.var
    def current_stock_metrics_list(self) -> List[Tuple[str, str]]:
        """
        Convierte el diccionario current_stock_metrics en una lista de tuplas (clave, valor)
        para ser usada con rx.foreach.
        """
        return list(self.current_stock_metrics.items())

    # --- Métodos Autenticación ---
    @rx.var
    def is_current_stock_info_empty(self) -> bool:
        """
        Devuelve True si current_stock_info está vacío, False en caso contrario.
        Un diccionario vacío se evalúa como Falsy en Python.
        """
        return not self.current_stock_info

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
            if user_id_str is None:
                logger.error("Token payload does not contain 'sub' (user_id).")
                return -1
            return int(user_id_str)
        except jwt.ExpiredSignatureError:
            logger.info("Token has expired.")
            return -1
        except (JWTError, ValueError, TypeError) as e:
            logger.error(f"Invalid token: {e}")
            return -1

    @rx.var
    def is_on_auth_page(self) -> bool:
        return self.router.page.path == "/login"

    @rx.event
    async def on_load(self):
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
            return
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id_from_token).first()
            if user:
                if not self.is_authenticated or self.user_id != user.id:
                    self.username = user.username
                    self.email = user.email
                    self.account_balance = float(user.account_balance or 0.0)
                    self.user_id = user.id
                    self.is_authenticated = True
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
            yield self.get_news()

    @rx.event
    async def login(self):
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
    async def register(self):
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
            existing_user = db.query(User).filter(
                (User.email.ilike(self.email.strip().lower())) |
                (User.username.ilike(self.username.strip()))
            ).first()
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
    def logout(self):
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
        self.portfolio_chart_data = pd.DataFrame(columns=['time','total_value'])
        self.recent_transactions = []
        self.search_query = ""
        self.search_result = SearchResultItem()
        self.search_error = ""
        self.is_searching = False
        return rx.redirect("/")

    # --- Setters for form fields ---
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
    def open_url_script(self, url: str):
        if isinstance(url, str) and url.startswith(("http://", "https://")):
            safe_url = url.replace("\\", "\\\\").replace("'", "\\'")
            js_command = f"window.open('{safe_url}', '_blank')"
            return rx.call_script(js_command)
        else:
            logger.warning(f"Invalid URL provided for opening: '{url}'.")
            return rx.console_log(f"Invalid URL for script: {url}")

    @rx.event
    def get_news(self):
        if self.is_loading_news: return
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
                        title = article.get("title", "Sin título")
                        url = article.get("url", "#")
                        source_info = article.get("source", {})
                        publisher = source_info.get("name", "Desconocido")
                        published_at_str = article.get("publishedAt", "")
                        summary = article.get("description", "No hay resumen disponible.")
                        image_url = article.get("image", "")
                        date_formatted = "Fecha desconocida"
                        if published_at_str:
                            try: 
                                dt_obj = datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%SZ")
                                date_formatted = dt_obj.strftime("%d %b %Y, %H:%M")
                            except ValueError: 
                                logger.warning(f"Could not parse date: {published_at_str}")
                        processed_articles.append(NewsArticle(
                            title=title, url=url, publisher=publisher, 
                            date=date_formatted, summary=summary, image=image_url
                        ))
                    except Exception as e: 
                        logger.error(f"Error processing individual news article: {e}", exc_info=True)
                if processed_articles: 
                    self.processed_news = processed_articles
                    self.has_news = True
                    logger.info(f"Successfully loaded {len(self.processed_news)} news articles.")
                else: 
                    logger.warning("API returned articles, but none could be processed.")
                    self._create_fallback_news()
            else: 
                logger.info("No news articles found for the query.")
                self._create_fallback_news()
        except requests.exceptions.RequestException as e: 
            logger.error(f"Network error fetching news: {e}", exc_info=True)
            self._create_fallback_news()
        except Exception as e: 
            logger.error(f"Unexpected error in get_news: {e}", exc_info=True)
            self._create_fallback_news()
        finally: 
            self.is_loading_news = False

    @rx.event
    def load_more_news(self):
        if not self.can_load_more or self.is_loading_news: return
        self.is_loading_news = True
        self.news_page += 1
        try:
            params = {
                "q": self.SEARCH_QUERY, "token": self.GNEWS_API_KEY, "lang": "es", 
                "country": "any", "max": self.max_articles, "page": self.news_page, 
                "sortby": "publishedAt", "from": "30d"
            }
            response = requests.get(self.GNEWS_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])
            if articles:
                new_articles_processed = []
                current_titles = {news.title for news in self.processed_news}
                for article in articles:
                    try: 
                        title = article.get("title", "Sin título")
                        if title in current_titles: continue
                        url = article.get("url", "#")
                        source_info = article.get("source", {})
                        publisher = source_info.get("name", "Desconocido")
                        published_at_str = article.get("publishedAt", "")
                        summary = article.get("description", "No hay resumen disponible.")
                        image_url = article.get("image", "")
                        date_formatted = "Fecha desconocida"
                        if published_at_str: 
                            try: 
                                dt_obj = datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%SZ")
                                date_formatted = dt_obj.strftime("%d %b %Y, %H:%M")
                            except ValueError: 
                                logger.warning(f"Could not parse date for additional news: {published_at_str}")
                        news_item = NewsArticle(
                            title=title, url=url, publisher=publisher, 
                            date=date_formatted, summary=summary, image=image_url
                        )
                        new_articles_processed.append(news_item)
                        current_titles.add(title)
                    except Exception as e: 
                        logger.error(f"Error processing additional news article: {e}", exc_info=True)
                if new_articles_processed: 
                    self.processed_news.extend(new_articles_processed)
                    logger.info(f"Added {len(new_articles_processed)} more news articles. Total: {len(self.processed_news)}")
                else: 
                    logger.info("No new, unique articles found in this batch.")
            else: 
                logger.info("No more articles returned from API.")
        except requests.exceptions.RequestException as e: 
            logger.error(f"Network error during load_more_news: {e}", exc_info=True)
        except Exception as e: 
            logger.error(f"Unexpected error in load_more_news: {e}", exc_info=True)
        finally: 
            self.is_loading_news = False

    def _create_fallback_news(self):
        logger.warning("Creating fallback news item due to error or no results.")
        self.processed_news = [NewsArticle(
            title="Error al cargar noticias", 
            url="#", 
            publisher="Sistema", 
            date="", 
            summary="No se pudieron obtener las noticias. Inténtelo de nuevo más tarde.", 
            image=""
        )]
        self.has_news = True

    # --- Métodos / Variables Computadas del Dashboard y Portfolio ---
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

    def _load_simulated_portfolio_with_api_prices(self):
        logger.info("--- Loading Simulated Portfolio with Real-Time API Prices START ---")
        symbols_hardcoded = ['MSFT', 'AAPL', 'NVDA', 'GOOGL', 'TSLA']
        quantities_hardcoded = {'MSFT': 15, 'AAPL': 25, 'NVDA': 5, 'GOOGL': 30, 'TSLA': 10}
        logo_placeholders = {
            "MSFT": "/microsoft_logo.png", 
            "AAPL": "/apple_logo.png", 
            "NVDA": "/default_logo.png", 
            "GOOGL": "/google_logo.png", 
            "TSLA": "/tesla_logo.png", 
            "DEFAULT": "/default_logo.png"
        }
        portfolio_list = []
        calculated_total_value = 0.0
        db = SessionLocal()
        try:
            for symbol in symbols_hardcoded:
                current_price = 0.0
                stock_name = symbol
                logo_url = logo_placeholders.get(symbol, logo_placeholders["DEFAULT"])
                try: 
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    price_val = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose") or info.get("bid")
                    stock_name_api = info.get("longName") or info.get("shortName", symbol)
                    logo_url_api = info.get("logo_url")
                    if price_val is not None: 
                        current_price = float(price_val)
                    else: 
                        hist_1d = ticker.history(period="1d")
                        if not hist_1d.empty and 'Close' in hist_1d.columns: 
                            current_price = float(hist_1d['Close'].iloc[-1])
                        else: 
                            logger.warning(f"Could not fetch price for {symbol}. Using 0.")
                            current_price = 0.0
                    stock_name = stock_name_api if stock_name_api else symbol
                    if logo_url_api: 
                        logo_url = logo_url_api
                    if not stock_name or stock_name == symbol: 
                        stock_db_entry = db.query(Stock.name).filter(Stock.symbol == symbol).first()
                        stock_name = stock_db_entry.name if stock_db_entry else symbol
                except Exception as api_err: 
                    logger.error(f"yfinance error for {symbol}: {api_err}. Falling back.")
                    stock_db_entry = db.query(Stock.name).filter(Stock.symbol == symbol).first()
                    stock_name = stock_db_entry.name if stock_db_entry else symbol
                    current_price = 0.0
                simulated_quantity = quantities_hardcoded.get(symbol, 0)
                current_value = simulated_quantity * current_price
                portfolio_list.append(
                    PortfolioItem(
                        symbol=symbol, 
                        name=stock_name, 
                        quantity=simulated_quantity, 
                        current_price=current_price, 
                        current_value=current_value, 
                        logo_url=logo_url
                    )
                )
                calculated_total_value += current_value
            self.portfolio_items = sorted(portfolio_list, key=lambda x: x.current_value, reverse=True)
            self.total_portfolio_value = calculated_total_value
            logger.info(f"Portfolio state updated (API prices): items={len(self.portfolio_items)}, total_value={self.total_portfolio_value:.2f}")
        except Exception as e: 
            logger.error(f"Error loading simulated portfolio: {e}", exc_info=True)
            self.portfolio_items = []
            self.total_portfolio_value = 0.0
        finally:
            if db and db.is_active: 
                db.close()
                logger.info("--- Loading Simulated Portfolio with Real-Time API Prices END ---")

    def _fetch_stock_history_data(self, symbol: str, period: str) -> pd.DataFrame:
        db = SessionLocal()
        df_result = pd.DataFrame(columns=['time', 'price'])
        try: 
            stock = db.query(Stock).filter(Stock.symbol == symbol).first()
            if not stock: 
                logger.warning(f"Stock symbol '{symbol}' not found in database for history fetch.")
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
                logger.warning(f"Unrecognized period '{period}', defaulting to 1D.")
                start_date = end_date - timedelta(days=1)
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
            logger.error(f"Error fetching stock history for {symbol} ({period}): {e}", exc_info=True)
        finally:
            if db and db.is_active: 
                db.close()
        return df_result

    # --- Lógica Gráfico Portfolio (SIN @rx.background) ---
    async def _update_portfolio_chart_data(self):
        self.is_loading_portfolio_chart = True
        logger.info(f"--- Updating Portfolio Chart Data START (Sync Mode - Period: {self.selected_period}) ---")
        if not self.portfolio_items: 
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
            logger.warning("No symbols with history found.")
            self.portfolio_chart_data = pd.DataFrame(columns=['time','total_value'])
            self.is_loading_portfolio_chart = False
            return

        all_history_dict = {}
        for symbol in symbols_to_chart:
            df = self._fetch_stock_history_data(symbol, period)
            if isinstance(df, pd.DataFrame) and not df.empty: 
                df['time'] = pd.to_datetime(df['time'], errors='coerce')
                df = df.set_index('time')
                all_history_dict[symbol] = df['price'].dropna()

        if not all_history_dict: 
            logger.warning("No history fetched.")
            self.portfolio_chart_data = pd.DataFrame(columns=['time','total_value'])
            self.is_loading_portfolio_chart = False
            return

        try: 
            combined_df = pd.DataFrame(all_history_dict)
            combined_df = combined_df.interpolate(method='time', limit_area='inside').bfill(limit=5).ffill(limit=5)
            combined_df = combined_df.dropna(how='all')
            
            if combined_df.empty: 
                logger.warning("Combined history empty.")
                self.portfolio_chart_data = pd.DataFrame(columns=['time','total_value'])
                self.is_loading_portfolio_chart = False
                return
            
            total_value_series = pd.Series(0.0, index=combined_df.index, dtype=float)
            for symbol, quantity in quantities.items():
                if symbol in combined_df.columns: 
                    total_value_series += combined_df[symbol].fillna(0.0) * quantity
            
            final_df = pd.DataFrame({'total_value': total_value_series}).reset_index()
            self.portfolio_chart_data = final_df
        except Exception as e: 
            logger.error(f"Error processing portfolio history: {e}", exc_info=True)
            self.portfolio_chart_data = pd.DataFrame(columns=['time', 'total_value'])
        finally: 
            self.is_loading_portfolio_chart = False
        logger.info("--- Updating Portfolio Chart Data END (Sync Mode) ---")

    # --- Lógica Carga Transacciones Recientes (SIN @rx.background) ---
    async def _load_recent_transactions(self):
        logger.info("--- Loading Recent Transactions START ---")
        if not self.user_id: 
            logger.warning("No user ID for transactions.")
            self.recent_transactions = []
            return
        
        db = SessionLocal()
        trans_list = []
        try:
            transactions_db = db.query(Transaction).filter(Transaction.user_id == self.user_id).order_by(Transaction.timestamp.desc()).limit(5).all()
            if transactions_db:
                formatted_list = []
                for t in transactions_db:
                    stock_obj = db.query(Stock).filter(Stock.id == t.stock_id).first()
                    stock_symbol = stock_obj.symbol if stock_obj else "??"
                    formatted_list.append(
                        TransactionDisplayItem(
                            timestamp=t.timestamp.strftime("%d/%m/%y %H:%M"),
                            symbol=stock_symbol,
                            quantity=t.quantity,
                            price=float(t.price),
                            type="Compra" if t.quantity > 0 else "Venta"
                        )
                    )
                trans_list = formatted_list
                logger.info(f"Loaded {len(trans_list)} recent transactions from DB for user {self.user_id}.")
            else: 
                logger.info(f"No transactions found in DB for user {self.user_id}. Using hardcoded examples.")
                trans_list = [
                    TransactionDisplayItem(timestamp="04/05/25 10:30", symbol="AAPL", quantity=10, price=210.50, type="Compra"),
                    TransactionDisplayItem(timestamp="03/05/25 15:01", symbol="MSFT", quantity=-5, price=405.10, type="Venta"),
                    TransactionDisplayItem(timestamp="02/05/25 09:15", symbol="GOOGL", quantity=20, price=155.80, type="Compra"),
                ]
            self.recent_transactions = trans_list
        except Exception as e: 
            logger.error(f"Error loading recent transactions: {e}", exc_info=True)
            self.recent_transactions = []
        finally:
            if db and db.is_active: 
                db.close()
        logger.info("--- Loading Recent Transactions END ---")

    # --- dashboard_on_mount (Llama a TODO síncrono/yield await) ---
    async def dashboard_on_mount(self):
        logger.info("--- Dashboard on_mount START ---")
        try:
            pnl_symbol = "AAPL"
            quantity = 10
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
                empty_df = pd.DataFrame(columns=['time','price'])
                self.daily_pnl_chart_data = empty_df
                self.monthly_pnl_chart_data = empty_df
                self.yearly_pnl_chart_data = empty_df
            
            self._load_simulated_portfolio_with_api_prices()
            yield self._update_portfolio_chart_data()
            yield self._load_recent_transactions()
        except Exception as e: 
            logger.error(f"Error on_mount: {e}", exc_info=True)
        logger.info("--- Dashboard on_mount END ---")

    # --- set_period (Actualiza gráfico portfolio - SIN background) ---
    @rx.event
    async def set_period(self, period: str):
        self.selected_period = period
        self.portfolio_chart_hover_info = None
        logger.info(f"Period changed to {period}. Triggering portfolio chart update.")
        await self._update_portfolio_chart_data()

    # --- Variables Computadas Gráfico Portfolio ---
    @rx.var
    def portfolio_change_info(self) -> Dict[str, Any]:
        df = self.portfolio_chart_data
        default = {"last_price": 0.0, "change": 0.0, "percent_change": 0.0, "is_positive": None}
        if not isinstance(df, pd.DataFrame) or df.empty or 'total_value' not in df.columns:
            return default
        prices = df['total_value'].dropna()
        if len(prices) < 2:
            return default if len(prices) == 0 else {"last_price": float(prices.iloc[-1]), "change": 0.0, "percent_change": 0.0, "is_positive": None}
        try:
            last_f = float(prices.iloc[-1])
            first_f = float(prices.iloc[0])
        except (ValueError, TypeError, IndexError):
            return default
        change_f = last_f - first_f
        percent_f = (change_f / first_f * 100) if first_f != 0 else 0.0
        is_positive = change_f > 0 if change_f != 0 else None
        return {"last_price": last_f, "change": change_f, "percent_change": percent_f, "is_positive": is_positive}

    @rx.var
    def is_portfolio_value_change_positive(self) -> bool | None:
        return self.portfolio_change_info["is_positive"]

    @rx.var
    def formatted_portfolio_value_percent_change(self) -> str:
        return f"{abs(self.portfolio_change_info['percent_change']):.2f}"

    @rx.var
    def formatted_portfolio_value_change_abs(self) -> str:
        return f"{self.portfolio_change_info['change']:+.2f}"

    @rx.var
    def portfolio_chart_color(self) -> str:
        is_positive = self.is_portfolio_value_change_positive
        return "#22c55e" if is_positive is True else "#ef4444" if is_positive is False else "#6b7280"

    @rx.var
    def portfolio_chart_area_color(self) -> str:
        is_positive = self.is_portfolio_value_change_positive
        return f"rgba({'34,197,94' if is_positive is True else '239,68,68' if is_positive is False else '107,114,128'},0.2)"

    @rx.var
    def portfolio_display_value(self) -> float:
        last_value = float(self.portfolio_change_info.get("last_price", 0.0))
        hover_info = self.portfolio_chart_hover_info
        if hover_info and "y" in hover_info:
            hover_y_data = hover_info["y"]
            y_to_convert = hover_y_data[0] if isinstance(hover_y_data, list) and hover_y_data else hover_y_data
            if y_to_convert is not None:
                try:
                    return float(y_to_convert)
                except (ValueError, TypeError):
                    pass
        return last_value

    @rx.var
    def portfolio_display_time(self) -> str:
        hover_info = self.portfolio_chart_hover_info
        if hover_info and "x" in hover_info:
            x_data = hover_info["x"]
            x_value = x_data[0] if isinstance(x_data, list) and x_data else x_data
            if x_value is not None:
                try:
                    if isinstance(x_value, (str, datetime, pd.Timestamp)):
                        return pd.to_datetime(x_value).strftime('%Y-%m-%d')
                    return str(x_value)
                except Exception as e:
                    logger.warning(f"Error formatting portfolio display time for x_value '{x_value}': {e}")
                    return str(x_value) if x_value else "--"
        return "--"

    @rx.var
    def main_portfolio_chart_figure(self) -> go.Figure:
        loading_fig = go.Figure().update_layout(height=300, annotations=[dict(text="Calculando gráfico portfolio...", showarrow=False)], paper_bgcolor='white', plot_bgcolor='white', xaxis=dict(visible=False), yaxis=dict(visible=False))
        error_fig = go.Figure().update_layout(height=300, annotations=[dict(text="Sin datos para gráfico.", showarrow=False)], paper_bgcolor='white', plot_bgcolor='white', xaxis=dict(visible=False), yaxis=dict(visible=False))

        if self.is_loading_portfolio_chart: return loading_fig
        df = self.portfolio_chart_data
        if not isinstance(df, pd.DataFrame) or df.empty or 'total_value' not in df.columns or 'time' not in df.columns: return error_fig

        try:
            df_chart = df.copy()
            df_chart['time'] = pd.to_datetime(df_chart['time'], errors='coerce')
            df_chart['total_value'] = pd.to_numeric(df_chart['total_value'], errors='coerce')
            df_chart = df_chart.dropna(subset=['time', 'total_value'])
            if df_chart.empty or len(df_chart) < 2: return error_fig

            fig=go.Figure()
            fig.add_trace(go.Scatter(x=df_chart['time'],y=df_chart['total_value'],mode='lines',line=dict(width=0),fill='tozeroy',fillcolor=self.portfolio_chart_area_color,hoverinfo='skip'))
            fig.add_trace(go.Scatter(x=df_chart['time'],y=df_chart['total_value'],mode='lines',line=dict(color=self.portfolio_chart_color,width=2.5,shape='spline'),name='Valor Total',hovertemplate='<b>Valor:</b> $%{y:,.2f}<br><b>Fecha:</b> %{x|%Y-%m-%d}<extra></extra>'))
            min_v,max_v=df_chart['total_value'].min(),df_chart['total_value'].max(); padding=(max_v-min_v)*0.1 if (max_v!=min_v) else abs(min_v)*0.1 or 1000; range_min,range_max=min_v-padding,max_v+padding
            fig.update_layout(height=300,margin=dict(l=50, r=10, t=10, b=30),paper_bgcolor='white',plot_bgcolor='white',xaxis=dict(showgrid=False,zeroline=False,tickmode='auto',nticks=6,showline=True,linewidth=1,linecolor='lightgrey',tickangle=-30),yaxis=dict(title=None,showgrid=True,gridcolor='rgba(230,230,230,0.5)',zeroline=False,showline=False,side='left',tickformat="$,.0f",range=[range_min,range_max]),hovermode='x unified',showlegend=False); return fig
        except Exception as e: logger.error(f"Err portfolio chart figure: {e}"); return error_fig

    # --- Event Handlers Gráfico Portfolio ---
    def portfolio_chart_handle_hover(self, event_data):
        new_hover_info = None; points = None
        if event_data and isinstance(event_data, list) and event_data[0] and isinstance(event_data[0], dict): points = event_data[0].get('points')
        if points and isinstance(points, list) and points[0] and isinstance(points[0], dict): new_hover_info = points[0]
        if self.portfolio_chart_hover_info != new_hover_info: self.portfolio_chart_hover_info = new_hover_info

    def portfolio_chart_handle_unhover(self, _):
        if self.portfolio_chart_hover_info is not None: self.portfolio_chart_hover_info = None

    def portfolio_toggle_change_display(self):
        self.portfolio_show_absolute_change = not self.portfolio_show_absolute_change

    # --- Métodos para Buscador ---
    def set_search_query(self, query: str):
        self.search_query = query
        self.search_error = ""


# --- Métodos para Página de Detalles de Acción ---

    @rx.event
    async def set_current_stock_period(self, period: str):
        """
        Establece el período para el gráfico de detalles de la acción y actualiza los datos del gráfico.
        """
        self.current_stock_selected_period = period
        self.stock_detail_chart_hover_info = None # Resetea la información de hover
        logger.info(f"Stock detail period changed to {period}. Triggering chart update for {self.viewing_stock_symbol}.")
        await self._update_current_stock_chart_data_internal()

    @rx.event
    async def load_stock_page_data(self, symbol: Optional[str] = None):
        if not symbol:
            route_symbol = self.router.page.params.get("symbol")
            if not route_symbol:
                logger.warning("load_stock_page_data: No symbol provided.")
                self.current_stock_info = {"error": "Símbolo no proporcionado."}
                return
            symbol = route_symbol
        self.viewing_stock_symbol = symbol.upper()
        self.is_loading_current_stock_details = True
        self.current_stock_info = {}
        self.current_stock_metrics = {}
        self.current_stock_history = pd.DataFrame(columns=['time', 'price'])
        logger.info(f"--- Loading stock page data for: {self.viewing_stock_symbol} ---")
        try:
            ticker = await asyncio.to_thread(yf.Ticker, self.viewing_stock_symbol)
            info = await asyncio.to_thread(getattr, ticker, 'info')
            if not info or (info.get("regularMarketPrice") is None and info.get("currentPrice") is None and info.get("previousClose") is None):
                logger.warning(f"No info for {self.viewing_stock_symbol}.")
                self.current_stock_info = {"error": f"No info for {self.viewing_stock_symbol}."}
                self.is_loading_current_stock_details = False
                return
            self.current_stock_info = {
                "symbol": info.get("symbol", self.viewing_stock_symbol),
                "longName": info.get("longName", info.get("shortName", self.viewing_stock_symbol)),
                "shortName": info.get("shortName", self.viewing_stock_symbol),
                "currentPrice": info.get("currentPrice", info.get("regularMarketPrice", info.get("previousClose"))),
                "previousClose": info.get("previousClose"),
                "open": info.get("open"),
                "dayHigh": info.get("dayHigh"),
                "dayLow": info.get("dayLow"),
                "volume": info.get("volume"),
                "marketCap": info.get("marketCap"),
                "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
                "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
                "averageVolume": info.get("averageVolume"),
                "averageVolume10days": info.get("averageVolume10days"),
                "beta": info.get("beta"),
                "trailingPE": info.get("trailingPE"),
                "forwardPE": info.get("forwardPE"),
                "dividendYield": info.get("dividendYield"),
                "logo_url": info.get("logo_url", "/default_logo.png"),
                "exchangeName": info.get("exchange", "N/A"),
                "currency": info.get("currency", "USD"),
                "currencySymbol": info.get("currencySymbol", "$"),
                "longBusinessSummary": info.get("longBusinessSummary", "No disponible."),
                "ceo": info.get("companyOfficers")[0].get("name", "N/A") if info.get("companyOfficers") and len(info.get("companyOfficers")) > 0 else "N/A",
            }
            market_cap = info.get('marketCap')
            avg_volume = info.get('averageVolume')
            currency_symbol = self.current_stock_info.get("currencySymbol", '$')
            self.current_stock_metrics = {
                "Tancament anterior": f"{currency_symbol}{info.get('previousClose', 'N/A'):,.2f}" if info.get('previousClose') else "N/A",
                "Interval de preus d'avui": f"{currency_symbol}{info.get('dayLow', 'N/A'):,.2f} - {currency_symbol}{info.get('dayHigh', 'N/A'):,.2f}" if info.get('dayLow') and info.get('dayHigh') else "N/A",
                "Interval anual": f"{currency_symbol}{info.get('fiftyTwoWeekLow', 'N/A'):,.2f} - {currency_symbol}{info.get('fiftyTwoWeekHigh', 'N/A'):,.2f}" if info.get('fiftyTwoWeekLow') and info.get('fiftyTwoWeekHigh') else "N/A",
                "Capitalització borsària": f"{currency_symbol}{market_cap / 1_000_000_000:.2f} B" if market_cap else "N/A",
                "Volum mitjà": f"{avg_volume / 1_000_000:.2f} M" if avg_volume else "N/A",
                "Ràtio PER": f"{info.get('trailingPE', 'N/A'):,.2f}" if info.get('trailingPE') else "N/A",
                "Rendibilitat per dividend": f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else "-",
                "Borsa principal": info.get("exchangeName", "N/A"),
            }
            await self._update_current_stock_chart_data_internal()
        except Exception as e:
            logger.error(f"Error loading stock details for {self.viewing_stock_symbol}: {e}")
            self.current_stock_info = {"error": f"Error loading data for {self.viewing_stock_symbol}."}
        finally:
            self.is_loading_current_stock_details = False

    async def _update_current_stock_chart_data_internal(self):
        if not self.viewing_stock_symbol:
            self.current_stock_history = pd.DataFrame(columns=['time', 'price'])
            return
        df = await asyncio.to_thread(
            self._fetch_stock_history_data_detail,
            self.viewing_stock_symbol,
            self.current_stock_selected_period
        )
        if not df.empty:
            self.current_stock_history = df
        else:
            logger.warning(
                f"Could not reload history for {self.viewing_stock_symbol} period {self.current_stock_selected_period}"
            )
            self.current_stock_history = pd.DataFrame(columns=['time', 'price'])

    def _fetch_stock_history_data_detail(self, symbol: str, period: str) -> pd.DataFrame:
        logger.info(f"Fetching yfinance history for {symbol}, period {period}")
        try:
            ticker = yf.Ticker(symbol)
            yf_period_map = {
                "1D": "1d", "5D": "5d", "1M": "1mo", "6M": "6mo",
                "ENG": "ytd", "1A": "1y", "5A": "5y", "MAX": "max"
            }
            yf_period = yf_period_map.get(period, "1mo")
            interval = "1d"
            end_date = datetime.now()
            start_date = None

            if period == "1D":
                interval = "1m"
                start_date = end_date - timedelta(days=1)
            elif period == "5D":
                interval = "5m"
                start_date = end_date - timedelta(days=5)
            elif period == "1M":
                interval = "60m"
                start_date = end_date - timedelta(days=30)

            if start_date:
                df_hist = ticker.history(start=start_date, end=end_date, interval=interval)
            else:
                df_hist = ticker.history(period=yf_period, interval=interval)

            if not df_hist.empty and 'Close' in df_hist.columns:
                df_result = df_hist[['Close']].copy()
                df_result.rename(columns={'Close': 'price'}, inplace=True)
                df_result.index.name = 'time'
                df_result = df_result.reset_index()
                if df_result['time'].dt.tz is None:
                    df_result['time'] = df_result['time'].dt.tz_localize('UTC')
                else:
                    df_result['time'] = df_result['time'].dt.tz_convert('UTC')
                return df_result
            else:
                logger.warning(
                    f"yfinance history fetch returned empty for {symbol} ({period}, {interval})."
                )
                return pd.DataFrame(columns=['time', 'price'])
        except Exception as e:
            logger.error(f"Error fetching yfinance history for {symbol} ({period}): {e}")
            return pd.DataFrame(columns=['time', 'price'])

    @rx.event
    async def search_stock(self):
        if not self.search_query:
            self.search_error = "Introduce un símbolo."
            self.search_result = SearchResultItem()
            return
        self.is_searching = True
        self.search_error = ""
        self.search_result = SearchResultItem()
        symbol = self.search_query.strip().upper()
        try:
            loop = asyncio.get_running_loop()
            ticker_info = await loop.run_in_executor(None, lambda s: yf.Ticker(s).info, symbol)
            if not ticker_info or (ticker_info.get("regularMarketPrice") is None and 
                                 ticker_info.get("currentPrice") is None):
                self.search_error = f"No info para '{symbol}'."
                self.is_searching = False
                return
            price = ticker_info.get("currentPrice", 
                                  ticker_info.get("regularMarketPrice", 
                                  ticker_info.get("previousClose", 0.0)))
            name = ticker_info.get("longName", ticker_info.get("shortName", symbol))
            logo = ticker_info.get("logo_url", "/default_logo.png")
            self.search_result = SearchResultItem(
                Symbol=symbol,
                Name=name,
                Current_Price=f"{float(price):,.2f}",
                Logo=logo
            )
        except Exception as e:
            logger.error(f"Error searching stock {symbol}: {e}")
            self.search_error = f"Error al buscar '{symbol}'."
            self.search_result = SearchResultItem(Symbol=symbol, Name="Error")
        finally:
            self.is_searching = False

    @rx.var
    def stock_detail_chart_change_info(self) -> Dict[str, Any]:
        df = self.current_stock_history
        default_info = {
            "last_price": 0.0, "change": 0.0, "percent_change": 0.0,
            "is_positive": None, "first_price_time": None, "last_price_time": None
        }
        current_price_from_info = self.current_stock_info.get("currentPrice")
        if current_price_from_info is not None:
            try:
                default_info["last_price"] = float(current_price_from_info)
            except (ValueError, TypeError):
                pass
        if not isinstance(df, pd.DataFrame) or df.empty or 'price' not in df.columns or 'time' not in df.columns:
            return default_info
        prices = df['price'].dropna()
        times = df['time'].dropna()
        if prices.empty or times.empty or len(prices) != len(times):
            return default_info
        if len(prices) < 1:
            return default_info
        last_f = float(prices.iloc[-1])
        last_t = pd.to_datetime(times.iloc[-1])
        default_info["last_price"] = last_f
        default_info["last_price_time"] = last_t
        if len(prices) < 2:
            return default_info
        first_f = float(prices.iloc[0])
        first_t = pd.to_datetime(times.iloc[0])
        change_f = last_f - first_f
        percent_f = (change_f / first_f * 100) if first_f != 0 else 0.0
        is_positive = change_f > 0 if change_f != 0 else None
        return {
            "last_price": last_f, "change": change_f, "percent_change": percent_f,
            "is_positive": is_positive, "first_price_time": first_t, "last_price_time": last_t
        }

    @rx.var
    def stock_detail_display_price(self) -> str:
        hover_info = self.stock_detail_chart_hover_info
        change_info = self.stock_detail_chart_change_info
        price_to_display = change_info.get("last_price", 0.0)
        currency_symbol = self.current_stock_info.get("currencySymbol", "$")
        if hover_info and "y" in hover_info:
            hover_y_data = hover_info["y"]
            y_to_convert = hover_y_data[0] if isinstance(hover_y_data, list) and hover_y_data else hover_y_data
            if y_to_convert is not None:
                try:
                    price_to_display = float(y_to_convert)
                except (ValueError, TypeError):
                    pass
        return f"{currency_symbol}{price_to_display:,.2f}"

    @rx.var
    def stock_detail_display_time_or_change(self) -> str:
        hover_info = self.stock_detail_chart_hover_info
        change_info = self.stock_detail_chart_change_info
        if hover_info and "x" in hover_info:
            x_data = hover_info["x"]
            x_value = x_data[0] if isinstance(x_data, list) and x_data else x_data
            if x_value is not None:
                try:
                    dt_obj = pd.to_datetime(x_value)
                    if self.current_stock_selected_period in ["1D", "5D"] or (
                        change_info.get("last_price_time") and change_info.get("first_price_time") and
                        isinstance(change_info["last_price_time"], pd.Timestamp) and
                        isinstance(change_info["first_price_time"], pd.Timestamp) and
                        (change_info["last_price_time"] - change_info["first_price_time"]).days < 2
                    ):
                        return dt_obj.strftime('%d %b, %H:%M')
                    return dt_obj.strftime('%d %b %Y')
                except Exception:
                    return str(x_value) if x_value else "--"
        change_val = change_info.get("change", 0.0)
        percent_change_val = change_info.get("percent_change", 0.0)
        currency_symbol = self.current_stock_info.get("currencySymbol", "$")
        period_map_display = {
            "1D": "avui", "5D": "5 dies", "1M": "1 mes", "6M": "6 mesos",
            "ENG": "aquest any", "1A": "1 any", "5A": "5 anys", "MAX": "màxim"
        }
        period_display_name = period_map_display.get(self.current_stock_selected_period, self.current_stock_selected_period)
        return f"{currency_symbol}{change_val:+.2f} ({percent_change_val:+.2f}%) {period_display_name}"

    @rx.var
    def stock_detail_change_color(self) -> str:
        is_positive = self.stock_detail_chart_change_info.get("is_positive")
        if self.stock_detail_chart_hover_info and "x" in self.stock_detail_chart_hover_info:
            return "var(--gray-11)"
        if is_positive is True:
            return "var(--green-10)"
        if is_positive is False:
            return "var(--red-10)"
        return "var(--gray-11)"

    @rx.var
    def stock_detail_chart_figure(self) -> go.Figure:
        loading_fig = go.Figure().update_layout(
            height=350,
            annotations=[dict(text="Carregant gràfic...", showarrow=False)],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        error_fig = go.Figure().update_layout(
            height=350,
            annotations=[dict(text="Sense dades per al gràfic.", showarrow=False)],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        if self.is_loading_current_stock_details and self.current_stock_history.empty:
            return loading_fig
        df = self.current_stock_history
        if not isinstance(df, pd.DataFrame) or df.empty or 'price' not in df.columns or 'time' not in df.columns:
            logger.warning("Stock detail chart: DataFrame invalid.")
            return error_fig
        try:
            df_chart = df.copy()
            df_chart['time'] = pd.to_datetime(df_chart['time'], errors='coerce')
            df_chart['price'] = pd.to_numeric(df_chart['price'], errors='coerce')
            df_chart = df_chart.dropna(subset=['time', 'price'])
            if df_chart.empty:
                logger.warning("Stock detail chart: No data points after cleaning.")
                return error_fig
            fig = go.Figure()
            change_info = self.stock_detail_chart_change_info
            is_positive = change_info.get("is_positive")
            line_color = "var(--gray-11)"
            area_color = "rgba(128, 128, 128, 0.1)"
            if is_positive is True:
                line_color = "var(--green-9)"
                area_color = "rgba(76, 175, 80, 0.1)"
            elif is_positive is False:
                line_color = "var(--red-9)"
                area_color = "rgba(244, 67, 54, 0.1)"
            fig.add_trace(go.Scatter(
                x=df_chart['time'], y=df_chart['price'], mode='lines',
                line=dict(width=0), fill='tozeroy', fillcolor=area_color, hoverinfo='skip'
            ))
            fig.add_trace(go.Scatter(
                x=df_chart['time'], y=df_chart['price'], mode='lines',
                line=dict(color=line_color, width=2.5, shape='spline'), name='Preu'
            ))
            min_v, max_v = df_chart['price'].min(), df_chart['price'].max()
            padding_percentage = 0.1
            padding = (max_v - min_v) * padding_percentage if (max_v != min_v) else (abs(min_v) * padding_percentage or 1.0)
            range_min, range_max = min_v - padding, max_v + padding
            tickformat = '%d %b %Y'
            dt_hover_format = '%d %b %Y, %H:%M'
            time_range_days = (df_chart['time'].max() - df_chart['time'].min()).days if len(df_chart['time']) > 1 else 0
            if time_range_days <= 2:
                tickformat = '%H:%M'
                dt_hover_format = '%H:%M (%d %b)'
            elif time_range_days <= 60:
                tickformat = '%d %b'
                dt_hover_format = '%d %b, %H:%M'
            fig.update_layout(
                height=350,
                margin=dict(l=60, r=20, t=20, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=False, zeroline=False, tickmode='auto',
                    nticks=5 if time_range_days > 2 else 8, showline=True,
                    linewidth=1, linecolor='var(--gray-a5)', tickangle=-30 if time_range_days > 7 else 0,
                    tickfont=dict(color='var(--gray-11)', size=10), tickformat=tickformat
                ),
                yaxis=dict(
                    title=None, showgrid=True, gridcolor='var(--gray-a3)',
                    zeroline=False, showline=False, side='left',
                    tickfont=dict(color='var(--gray-11)', size=10), tickformat=",.2f",
                    range=[range_min, range_max] if range_min < range_max else None
                ),
                hovermode='x unified', showlegend=False, font=dict(color="var(--gray-12)")
            )
            fig.update_traces(
                hovertemplate=f"<b>Preu:</b> %{{y:,.2f}}<br><b>Temps:</b> %{{x|{dt_hover_format}}}<extra></extra>",
                selector=dict(name="Preu")
            )
            return fig
        except Exception as e:
            logger.error(f"Err creating stock detail chart figure for {self.viewing_stock_symbol}: {e}", exc_info=True)
            return error_fig

    def stock_detail_chart_handle_hover(self, event_data):
        new_hover_info = None
        if event_data and isinstance(event_data, list) and event_data[0] and isinstance(event_data[0], dict):
            points = event_data[0].get('points')
            if points and isinstance(points, list) and points[0] and isinstance(points[0], dict):
                new_hover_info = points[0]
        if self.stock_detail_chart_hover_info != new_hover_info:
            self.stock_detail_chart_hover_info = new_hover_info

    def stock_detail_chart_handle_unhover(self, _):
        if self.stock_detail_chart_hover_info is not None:
            self.stock_detail_chart_hover_info = None

class TransactionDisplayItem(rx.Base):
    timestamp: str
    symbol: str
    quantity: int
    price: float
    type: str

    @property
    def formatted_quantity(self) -> str:
        """Devuelve la cantidad formateada con signo."""
        return f"{'+' if self.quantity > 0 else ''}{self.quantity}"