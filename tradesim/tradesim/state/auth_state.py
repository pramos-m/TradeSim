# tradesim/state/auth_state.py (FINAL CORREGIDO)
import reflex as rx
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from jose import jwt, JWTError
import os
import requests
import traceback
import pandas as pd
import plotly.graph_objects as go
from ..database import SessionLocal
from ..models.user import User
from ..models.stock import Stock
from ..models.stock_price_history import StockPriceHistory
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# --- Modelo de Dades para Noticias ---
class NewsArticle(rx.Base):
    title: str; url: str; publisher: str; date: str; summary: str; image: str = ""

class AuthState(rx.State):
    """Estado GLOBAL combinado para autenticación, noticias y dashboard."""

    # --- Variables de Autenticación ---
    is_authenticated: bool = False
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

    # --- Variables de Noticias ---
    processed_news: List[NewsArticle] = []
    is_loading_news: bool = False
    has_news: bool = False
    news_page: int = 1
    max_articles: int = 10
    selected_style: str = "panel"
    GNEWS_API_KEY = "f767bfe6df4f747e6b77c0178e8cc0d8" # Considera mover a .env
    GNEWS_API_URL = "https://gnews.io/api/v4/search"
    SEARCH_QUERY = "bolsa acciones"

    # --- Variables del Dashboard ---
    balance_date: str = datetime.now().strftime("%d/%m/%Y")
    daily_pnl: float = 0.0
    monthly_pnl: float = 0.0
    yearly_pnl: float = 0.0
    daily_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
    monthly_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
    yearly_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
    selected_period: str = "1D"
    current_period_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
    main_chart_hover_info: Dict | None = None
    show_absolute_change: bool = False
    SIMULATED_PORTFOLIO: Dict[str, int] = {"AAPL": 10}

    # --- Métodos de Autenticación ---
    def create_access_token(self, user_id: int) -> str:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES); data = {"sub": str(user_id), "exp": expire}
        try: return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        except Exception as e: logger.error(f"Err token: {e}"); return ""

    def verify_token(self, token: str | None) -> int:
        if not token: return -1
        try: payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]); return int(payload.get("sub"))
        except jwt.ExpiredSignatureError: return -1
        except (JWTError, ValueError, TypeError): return -1

    @rx.var
    def is_on_auth_page(self) -> bool: return self.router.page.path == "/login"

    @rx.event
    async def on_load(self):
        current_path = self.router.page.path
        if self.processed_token and self.last_path == current_path: return
        self.processed_token = True; self.last_path = current_path
        if current_path == "/": return

        user_id_from_token = self.verify_token(self.auth_token)
        if user_id_from_token <= 0:
            if self.is_authenticated: logger.info("on_load: Desautenticando."); self.is_authenticated = False; self.username = ""; self.email = ""; self.account_balance = 0.0; self.user_id = None
            if self.auth_token: self.auth_token = ""
            # *** Indentación CORREGIDA ***
            if current_path in ["/dashboard", "/profile", "/noticias", "/clasificacion", "/buscador"]:
                return rx.redirect("/login")
            return # No redirigir desde otras páginas (ej. /login)
            # *** Fin Corrección ***

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id_from_token).first()
            if user:
                if not self.is_authenticated or self.user_id != user.id:
                    self.username = user.username; self.email = user.email; self.account_balance = float(user.account_balance or 0.0); self.user_id = user.id; self.is_authenticated = True; logger.info(f"on_load: Auth state updated for user ID {self.user_id}")
                if current_path == "/login": return rx.redirect("/dashboard")
            else:
                logger.warning(f"on_load: User ID {user_id_from_token} not found."); self.is_authenticated = False; self.username = ""; self.email = ""; self.account_balance = 0.0; self.user_id = None; self.auth_token = ""
                if current_path in ["/dashboard", "/profile", "/noticias", "/clasificacion", "/buscador"]: return rx.redirect("/login")
        except Exception as e: logger.error(f"on_load: DB Error user ID {user_id_from_token}: {e}", exc_info=True); self.is_authenticated = False; self.account_balance = 0.0; self.user_id = None; self.auth_token = ""; return rx.redirect("/login") if current_path != "/login" else None
        finally:
             if db and db.is_active: db.close()

    @rx.event
    async def login(self):
        self.error_message = ""; self.loading = True
        if not self.email or not self.password: self.error_message = "Complete campos"; self.loading = False; return
        db = None
        try:
            db = SessionLocal(); user = db.query(User).filter(User.email.ilike(self.email)).first()
            if not user or not user.verify_password(self.password): self.error_message = "Credenciales inválidas"; self.loading = False; return
            self.is_authenticated = True; self.username = user.username; self.email = user.email; self.account_balance = float(user.account_balance or 0.0); self.user_id = user.id; token = self.create_access_token(user.id)
            if not token: logger.error("Login fail: No token."); self.error_message = "Error token."; self.loading = False; return
            self.auth_token = token; self.last_path = "/dashboard"; self.processed_token = True; self.loading = False
            return rx.call_script("window.location.href = '/dashboard';")
        except Exception as e: logger.error(f"Login fail: Exception: {e}", exc_info=True); self.error_message = "Error inesperado."; self.loading = False
        finally:
            if db and db.is_active: db.close()

    @rx.event
    async def register(self):
        self.error_message = ""; self.loading = True
        if not self.username or not self.email or not self.password: self.error_message = "Complete campos"; self.loading = False; return
        if self.password != self.confirm_password: self.error_message = "Contraseñas no coinciden"; self.loading = False; return
        db = None
        try:
            db = SessionLocal(); existing_user = db.query(User).filter( (User.email.ilike(self.email)) | (User.username.ilike(self.username)) ).first()
            if existing_user: self.error_message = "Usuario/email ya existen"; self.loading = False; return
            new_user = User(username=self.username.strip(), email=self.email.strip().lower()); new_user.set_password(self.password); db.add(new_user); db.commit(); db.refresh(new_user); logger.info(f"User created: {new_user.username}, Balance: {new_user.account_balance}")
            self.is_authenticated = True; self.username = new_user.username; self.email = new_user.email; self.account_balance = float(new_user.account_balance or 0.0); self.user_id = new_user.id
            token = self.create_access_token(new_user.id)
            if not token: logger.error("Register fail post-create: No token."); self.error_message = "Error token."; self.loading = False; return
            self.auth_token = token; self.last_path = "/dashboard"; self.processed_token = True; self.loading = False
            return rx.call_script("window.location.href = '/dashboard';")
        except Exception as e: logger.error(f"Register fail: Exception: {e}", exc_info=True); self.error_message = "Error inesperado."; self.loading = False
        finally:
            if db and db.is_active: db.close()

    @rx.event
    def logout(self):
        self.is_authenticated = False; self.username = ""; self.email = ""; self.password = ""; self.confirm_password = ""; self.account_balance = 0.0; self.auth_token = ""; self.user_id = None; self.processed_token = True; self.last_path = "/"
        return rx.call_script("window.location.href = '/';")

    def set_active_tab(self, tab: str): self.active_tab = tab; self.error_message = ""
    def set_username(self, username: str): self.username = username
    def set_email(self, email: str): self.email = email
    def set_password(self, password: str): self.password = password
    def set_confirm_password(self, confirm_password: str): self.confirm_password = confirm_password

    # --- Métodos / Variables Computadas de Noticias ---
    @rx.var
    def featured_news(self) -> Optional[NewsArticle]: return self.processed_news[0] if self.processed_news else None
    @rx.var
    def recent_news_list(self) -> List[NewsArticle]: return self.processed_news[1:min(4, len(self.processed_news))] if len(self.processed_news) > 1 else []
    @rx.var
    def can_load_more(self) -> bool: return len(self.processed_news) > 0 and not self.is_loading_news
    @rx.event
    def change_style(self, style: str): self.selected_style = style
    @rx.event
    def open_url_script(self, url: str): # <-- CORREGIDO f-string/paréntesis
        if isinstance(url, str) and url.startswith(("http://", "https://")):
             safe_url = url.replace("\\", "\\\\").replace("'", "\\'")
             js_command = f"window.open('{safe_url}', '_blank')"
             return rx.call_script(js_command)
        else: logger.warning(f"URL inv\u00E1lida para script: '{url}'."); return rx.console_log(f"URL inv\u00E1lida para script: {url}")
    @rx.event
    def get_news(self): # <-- CORREGIDO SyntaxError interno
        if self.is_loading_news: return
        self.is_loading_news = True; self.has_news = False; self.processed_news = []; self.news_page = 1
        try:
            params = {"q": self.SEARCH_QUERY, "token": self.GNEWS_API_KEY, "lang": "es", "country": "any", "max": self.max_articles, "sortby": "publishedAt", "from": "30d"}
            response = requests.get(self.GNEWS_API_URL, params=params); response.raise_for_status(); data = response.json(); articles = data.get("articles", [])
            if articles:
                processed_articles = []
                for article in articles:
                    try: # Asignaciones separadas
                        title = article.get("title", "Sin título"); url = article.get("url", "#"); src = article.get("source", {}); pub = src.get("name", "Fuente desconocida"); dt_str = article.get("publishedAt", ""); sumry = article.get("description", "Sin descripción."); img = article.get("image", "")
                        try: dt_str = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%d %b %Y, %H:%M") if dt_str else "?"
                        except (ValueError, TypeError): dt_str = "?"
                        processed_articles.append(NewsArticle(title=title, url=url, publisher=pub, date=dt_str, summary=sumry, image=img))
                    except Exception as e_inner: logger.error(f"Error procesando art\u00EDculo: {e_inner}")
                if processed_articles: self.processed_news=processed_articles; self.has_news=True; logger.info(f"Se procesaron {len(processed_articles)} noticias.")
                else: self._create_fallback_news()
            else: self._create_fallback_news()
        except requests.exceptions.RequestException as e_req: logger.error(f"Error de red: {e_req}"); self._create_fallback_news()
        except Exception as e_outer: logger.error(f"Error general get_news: {e_outer}", exc_info=True); self._create_fallback_news()
        finally: self.is_loading_news = False
    @rx.event
    def load_more_news(self): # <-- CORREGIDO SyntaxError interno
        if not self.can_load_more or self.is_loading_news: return
        self.is_loading_news = True; self.news_page += 1
        try:
            params = {"q": self.SEARCH_QUERY, "token": self.GNEWS_API_KEY, "lang": "es", "country": "any", "max": self.max_articles, "page": self.news_page, "sortby": "publishedAt", "from": "30d"}
            logger.info(f"Cargando m\u00E1s noticias (p\u00E1gina {self.news_page})...")
            response = requests.get(self.GNEWS_API_URL, params=params); response.raise_for_status(); data = response.json(); articles = data.get("articles", [])
            if articles:
                new_articles = []; current_titles = {news.title for news in self.processed_news}
                for article in articles:
                    try: # Asignaciones separadas
                        title = article.get("title", "Sin título");
                        if title in current_titles: continue
                        url = article.get("url", "#"); src = article.get("source", {}); pub = src.get("name", "?"); dt_str = article.get("publishedAt", ""); sumry = article.get("description", ""); img = article.get("image", "")
                        try: dt_str = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%d %b %Y, %H:%M") if dt_str else "?"
                        except (ValueError, TypeError): dt_str = "?"
                        news_article = NewsArticle(title=title, url=url, publisher=pub, date=dt_str, summary=sumry, image=img); new_articles.append(news_article); current_titles.add(title)
                    except Exception as e_inner: logger.error(f"Error procesando art\u00EDculo adicional: {e_inner}")
                if new_articles: self.processed_news.extend(new_articles); logger.info(f"Se a\u00F1adieron {len(new_articles)} noticias.")
                else: logger.info("No se encontraron m\u00E1s noticias nuevas.")
            else: logger.info("No hay m\u00E1s p\u00E1ginas de noticias.")
        except requests.exceptions.RequestException as e_req: logger.error(f"Error de red al cargar m\u00E1s: {e_req}")
        except Exception as e_outer: logger.error(f"Error general al cargar m\u00E1s: {e_outer}", exc_info=True)
        finally: self.is_loading_news = False
    def _create_fallback_news(self): logger.warning("Generando noticias de respaldo..."); # ... (lógica igual)
    def _add_more_fallback_news(self): logger.warning("A\u00F1adiendo noticias de respaldo adicionales..."); # ... (lógica igual)

    # --- Métodos / Variables Computadas del Dashboard ---
    @rx.var
    def price_change_info(self) -> Dict[str, Any]: # ... (igual) ...
        df=self.current_period_data; default={"last_price":0.0,"change":0.0,"percent_change":0.0,"is_positive":True}
        if not isinstance(df,pd.DataFrame) or df.empty or len(df)<2 or 'price' not in df.columns: return default
        try: prices=df['price'].dropna(); last_f=float(prices.iloc[-1]); first_f=float(prices.iloc[0])
        except Exception: return default
        change_f=last_f-first_f; percent_f=(change_f/first_f*100) if first_f!=0 else 0.0
        return {"last_price":last_f,"change":change_f,"percent_change":percent_f,"is_positive":change_f>=0}
    @rx.var
    def is_change_positive(self) -> bool: return self.price_change_info["is_positive"]
    @rx.var
    def formatted_percent_change(self) -> str: return f"{abs(self.price_change_info['percent_change']):.2f}"
    @rx.var
    def formatted_change_value(self) -> str: return f"{self.price_change_info['change']:+.2f}"
    @rx.var
    def chart_color(self) -> str: return "#22c55e" if self.is_change_positive else "#ef4444"
    @rx.var
    def chart_area_color(self) -> str: return f"rgba({'34,197,94' if self.is_change_positive else '239,68,68'},0.2)"
    @rx.var
    def display_price(self) -> float: # ... (igual) ...
        last_price = float(self.price_change_info.get("last_price", 0.0)); hover_y = self.main_chart_hover_info.get("y") if self.main_chart_hover_info else None; y = hover_y[0] if isinstance(hover_y, list) and hover_y else hover_y
        try: return float(y) if isinstance(y,(int,float,str,Decimal)) else last_price
        except: return last_price
    @rx.var
    def display_time(self) -> str: # ... (igual) ...
        if self.main_chart_hover_info and "x" in self.main_chart_hover_info:
            x = self.main_chart_hover_info.get("x"); x = x[0] if isinstance(x, list) and x else x
            try: return pd.to_datetime(x).strftime('%Y-%m-%d %H:%M') if isinstance(x, str) else x.strftime('%Y-%m-%d %H:%M') if isinstance(x, datetime) else str(x) if x else "--:--"
            except: return str(x) if x else "--:--"
        return "--:--"
    @rx.var
    def main_chart_figure(self) -> go.Figure: # ... (igual) ...
        df=self.current_period_data; error_fig=go.Figure().update_layout(height=300,annotations=[dict(text="Cargando/Sin datos...", showarrow=False)])
        if not isinstance(df,pd.DataFrame) or df.empty or 'price' not in df.columns or 'time' not in df.columns: return error_fig
        try:
            df_chart=df;
            if df_chart.empty or len(df_chart)<2: return error_fig
            fig=go.Figure(); fig.add_trace(go.Scatter(x=df_chart['time'],y=df_chart['price'],mode='lines',line=dict(width=0),fill='tozeroy',fillcolor=self.chart_area_color,hoverinfo='skip')); fig.add_trace(go.Scatter(x=df_chart['time'],y=df_chart['price'],mode='lines',line=dict(color=self.chart_color,width=2.5,shape='spline'),name='Price',hovertemplate='<b>Price:</b> %{y:.2f}<br><b>Time:</b> %{x|%Y-%m-%d %H:%M}<extra></extra>'))
            min_p,max_p=df_chart['price'].min(),df_chart['price'].max(); padding=(max_p-min_p)*0.1 if (max_p!=min_p) else abs(min_p)*0.1 or 1; range_min,range_max=min_p-padding,max_p+padding
            fig.update_layout(height=300,margin=dict(l=40,r=10,t=10,b=30),paper_bgcolor='white',plot_bgcolor='white',xaxis=dict(showgrid=False,zeroline=False,tickmode='auto',nticks=6,showline=True,linewidth=1,linecolor='lightgrey',tickangle=-30),yaxis=dict(title=None,showgrid=True,gridcolor='rgba(230,230,230,0.5)',zeroline=False,showline=False,side='left',tickformat=".2f",range=[range_min,range_max]),hovermode='x unified',showlegend=False); return fig
        except Exception as e: logger.error(f"Err main chart: {e}",exc_info=True); return error_fig

    # --- Métodos del Dashboard ---
    def _fetch_stock_history_data(self, symbol: str, period: str) -> pd.DataFrame: # ... (igual) ...
        db=SessionLocal(); df_result=pd.DataFrame(columns=['time','price'])
        try:
            stock=db.query(Stock).filter(Stock.symbol==symbol).first()
            if not stock: return df_result
            end_date=datetime.utcnow(); start_date=None; days_map={"1D":1,"5D":5,"1M":30,"6M":180,"1A":365,"5A":365*5}
            if period in days_map: start_date=end_date-timedelta(days=days_map[period])
            elif period=="ENG": start_date=datetime(end_date.year,1,1)
            elif period=="MAX": start_date=None
            else: start_date=end_date-timedelta(days=1)
            query=db.query(StockPriceHistory.timestamp,StockPriceHistory.price).filter(StockPriceHistory.stock_id==stock.id)
            if start_date: query=query.filter(StockPriceHistory.timestamp>=start_date)
            query=query.order_by(StockPriceHistory.timestamp.asc())
            df=pd.read_sql(query.statement,db.bind); # logger.info(f"Fetched {len(df)} for {symbol} {period}.")
            if not df.empty: df=df.rename(columns={"timestamp":"time"}); df['price']=pd.to_numeric(df['price'],errors='coerce'); df['time']=pd.to_datetime(df['time'],errors='coerce'); df=df.dropna(subset=['price','time']); df_result=df
        except Exception as e: logger.error(f"Err _fetch {symbol} {period}: {e}",exc_info=True)
        finally:
            if db and db.is_active: db.close()
        return df_result
    def _calculate_stock_pnl(self, symbol: str, period: str, quantity: int) -> Tuple[Optional[float], pd.DataFrame]: # <-- CORREGIDO try/except
        # logger.info(f"Calculating PNL for {quantity} {symbol} over period {period}...") # Log reducido
        df_history = self._fetch_stock_history_data(symbol, period)
        pnl: Optional[float] = None # Inicializar como None
        if not df_history.empty and len(df_history) >= 2:
            try: # <-- Bloque try/except CORREGIDO
                prices = df_history['price'].dropna()
                if len(prices) >= 2:
                    start_price = float(prices.iloc[0])
                    end_price = float(prices.iloc[-1])
                    pnl = (end_price - start_price) * quantity
                    # logger.info(f"PNL OK: {symbol}({period}): PNL={pnl:.2f}") # Log reducido
            except Exception as e:
                logger.error(f"Error calculating PNL {symbol} ({period}): {e}")
                pnl = None # Asegurar None en caso de error de cálculo
        # else: logger.warning(f"Not enough data ({len(df_history)}) for PNL {symbol} ({period}).") # Log reducido
        return pnl, df_history

    async def dashboard_on_mount(self): # ... (igual) ...
        logger.info("--- Dashboard on_mount START ---")
        try:
            symbol="AAPL"; quantity=self.SIMULATED_PORTFOLIO.get(symbol,0)
            if quantity > 0:
                daily_pnl_val, daily_df = self._calculate_stock_pnl(symbol, "1D", quantity); self.daily_pnl = daily_pnl_val if daily_pnl_val is not None else 0.0; self.daily_pnl_chart_data = daily_df
                monthly_pnl_val, monthly_df = self._calculate_stock_pnl(symbol, "1M", quantity); self.monthly_pnl = monthly_pnl_val if monthly_pnl_val is not None else 0.0; self.monthly_pnl_chart_data = monthly_df
                yearly_pnl_val, yearly_df = self._calculate_stock_pnl(symbol, "1A", quantity); self.yearly_pnl = yearly_pnl_val if yearly_pnl_val is not None else 0.0; self.yearly_pnl_chart_data = yearly_df
                # logger.info(f"PNL values set: D={self.daily_pnl:.2f},M={self.monthly_pnl:.2f},Y={self.yearly_pnl:.2f}") # Log reducido
            else: self.daily_pnl,self.monthly_pnl,self.yearly_pnl=0.0,0.0,0.0; self.daily_pnl_chart_data,self.monthly_pnl_chart_data,self.yearly_pnl_chart_data=[pd.DataFrame(columns=['time','price'])]*3
            self.current_period_data=self._fetch_stock_history_data(symbol,self.selected_period); logger.info(f"Initial main chart ({self.selected_period}) OK: {len(self.current_period_data)} rows")
        except Exception as e: logger.error(f"Error on_mount: {e}",exc_info=True)
        logger.info("--- Dashboard on_mount END ---")
    def set_period(self, period: str): # ... (igual) ...
        self.selected_period=period; self.main_chart_hover_info=None; default_symbol="AAPL"; self.current_period_data=self._fetch_stock_history_data(default_symbol,period)
    def handle_hover(self, event_data): # ... (igual) ...
        new_hover_info=None; points=None;
        if event_data and isinstance(event_data,list) and event_data[0] and isinstance(event_data[0],dict): points=event_data[0].get('points')
        if points and isinstance(points,list) and points[0] and isinstance(points[0],dict): new_hover_info=points[0]
        if self.main_chart_hover_info!=new_hover_info: self.main_chart_hover_info=new_hover_info
    def handle_unhover(self, _): # ... (igual) ...
        if self.main_chart_hover_info is not None: self.main_chart_hover_info=None
    def toggle_change_display(self): self.show_absolute_change = not self.show_absolute_change