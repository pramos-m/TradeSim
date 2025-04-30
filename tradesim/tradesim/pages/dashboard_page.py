# tradesim/pages/dashboard_page.py
import reflex as rx
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any, Tuple # Importar Tuple
# Importa Estados y elementos de BBDD/Modelos necesarios
from ..state.auth_state import AuthState
from ..database import SessionLocal
from ..models.stock import Stock
from ..models.stock_price_history import StockPriceHistory
# Importa logging
import logging
from decimal import Decimal # Necesario para precios

# Configura el logger para este módulo
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO) # Asegura que los logs INFO se muestren

# --- Función de Utilidad para PNL Plots (NO USADA para cálculo principal) ---
# def generate_pnl_plot_data(start_value, end_value, points=12) -> List[float]: ... # La dejamos comentada por si acaso

# --- Reflex State for Dashboard ---
class DashboardState(rx.State):
    """Manages the dashboard's specific UI state and data interactions."""
    balance_date: str = datetime.now().strftime("%d/%m/%Y")

    # --- PNL Data (Calculados en on_mount desde BBDD) ---
    daily_pnl: float = 0.0
    monthly_pnl: float = 0.0
    yearly_pnl: float = 0.0
    # DataFrames para los gráficos PNL pequeños (obtenidos desde BBDD)
    daily_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
    monthly_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])
    yearly_pnl_chart_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price'])

    # --- Main Chart Data/UI State ---
    selected_period: str = "1D"
    current_period_data: pd.DataFrame = pd.DataFrame(columns=['time', 'price']) # Inicializar vacío
    main_chart_hover_info: Dict | None = None
    show_absolute_change: bool = False

    # --- Constante Simulación Portfolio ---
    SIMULATED_PORTFOLIO: Dict[str, int] = {"AAPL": 10} # Asumir 10 acciones de AAPL

    # --- DB Data Fetching (Función reutilizable, sincrónica) --- #
    def _fetch_stock_history_data(self, symbol: str, period: str) -> pd.DataFrame:
        """Fetches historical stock price data from the database for a given period."""
        # logger.info(f"SYNC Fetching history for {symbol} period {period} from DB...") # Log reducido
        db = SessionLocal()
        df_result = pd.DataFrame(columns=['time', 'price']) # Default empty DF
        try:
            stock = db.query(Stock).filter(Stock.symbol == symbol).first()
            if not stock:
                logger.warning(f"_fetch_stock_history_data: Stock symbol {symbol} not found in DB."); return df_result

            end_date = datetime.utcnow()
            start_date = None
            days_map = {"1D": 1, "5D": 5, "1M": 30, "6M": 180, "1A": 365, "5A": 365*5}
            if period in days_map: start_date = end_date - timedelta(days=days_map[period])
            elif period == "ENG": start_date = datetime(end_date.year, 1, 1)
            elif period == "MAX": start_date = None
            else: start_date = end_date - timedelta(days=1) # Default 1D

            query = db.query(StockPriceHistory.timestamp, StockPriceHistory.price)\
                      .filter(StockPriceHistory.stock_id == stock.id)
            if start_date: query = query.filter(StockPriceHistory.timestamp >= start_date)
            query = query.order_by(StockPriceHistory.timestamp.asc())

            df = pd.read_sql(query.statement, db.bind)
            logger.info(f"_fetch_stock_history_data: Fetched {len(df)} rows for {symbol} {period}.") # Log útil

            if not df.empty:
                df = df.rename(columns={"timestamp": "time"})
                if 'price' in df.columns and 'time' in df.columns:
                    df['price'] = pd.to_numeric(df['price'], errors='coerce')
                    df['time'] = pd.to_datetime(df['time'], errors='coerce')
                    df = df.dropna(subset=['price', 'time'])
                    if not df.empty: df_result = df
                else: logger.error(f"_fetch_stock_history_data: DataFrame missing required columns after rename for {symbol}.")
            # else: logger.warning(f"_fetch_stock_history_data: No history data found in DB for {symbol} period {period}.") # Log reducido

        except Exception as e:
            logger.error(f"Error in _fetch_stock_history_data for {symbol} period {period}: {e}", exc_info=True)
        finally:
            if db and db.is_active: db.close() # Asegurar cierre solo si está activa
        return df_result # Always return a DataFrame (possibly empty)

    # --- Cálculo de PNL (Basado en Historial) ---
    def _calculate_stock_pnl(self, symbol: str, period: str, quantity: int) -> Tuple[float, pd.DataFrame]:
        """Calcula el PNL para un símbolo/periodo y devuelve el PNL y los datos del gráfico."""
        logger.info(f"Calculating PNL for {quantity} {symbol} over period {period}...")
        df_history = self._fetch_stock_history_data(symbol, period)
        pnl = 0.0

        if not df_history.empty and len(df_history) >= 2:
            try:
                # Usar la columna 'price' ya procesada (numérica) por _fetch_stock_history_data
                prices = df_history['price'].dropna() # Asegurarse de quitar NaNs si alguno quedó
                if len(prices) >= 2:
                    start_price = float(prices.iloc[0])
                    end_price = float(prices.iloc[-1])
                    pnl = (end_price - start_price) * quantity
                    logger.info(f"PNL calculated for {symbol} ({period}): Start={start_price:.2f}, End={end_price:.2f}, Qty={quantity}, PNL={pnl:.2f}")
                else:
                    logger.warning(f"Not enough valid prices for PNL calculation for {symbol} ({period}) after potential cleaning.")
            except Exception as e:
                logger.error(f"Error calculating PNL from history for {symbol} ({period}): {e}")
        else:
            logger.warning(f"Not enough historical data ({len(df_history)} rows) for PNL calculation for {symbol} ({period}). PNL set to 0.")

        return pnl, df_history # Devuelve PNL y el DataFrame (puede estar vacío)

    # --- Variables Computadas ---
    @rx.var
    def price_change_info(self) -> Dict[str, Any]:
        df = self.current_period_data; default = {"last_price": 0.0, "change": 0.0, "percent_change": 0.0, "is_positive": True}
        if not isinstance(df, pd.DataFrame) or df.empty or len(df) < 2 or 'price' not in df.columns: return default
        try:
            prices = df['price'].dropna() # Ya debería ser numérico
            if len(prices) < 2: return default
            last_f = float(prices.iloc[-1]); first_f = float(prices.iloc[0])
        except Exception: return default
        change_f = last_f - first_f; percent_f = (change_f / first_f * 100) if first_f != 0 else 0.0
        return {"last_price": last_f, "change": change_f, "percent_change": percent_f, "is_positive": change_f >= 0}

    @rx.var
    def is_change_positive(self) -> bool: return self.price_change_info["is_positive"]
    @rx.var
    def formatted_percent_change(self) -> str: return f"{abs(self.price_change_info['percent_change']):.2f}"
    @rx.var
    def formatted_change_value(self) -> str: return f"{self.price_change_info['change']:+.2f}"
    @rx.var
    def chart_color(self) -> str: return "#22c55e" if self.is_change_positive else "#ef4444"
    @rx.var
    def chart_area_color(self) -> str: return f"rgba({ '34, 197, 94' if self.is_change_positive else '239, 68, 68'}, 0.2)"

    @rx.var
    def display_price(self) -> float:
        last_price = float(self.price_change_info.get("last_price", 0.0))
        if self.main_chart_hover_info and "y" in self.main_chart_hover_info:
            y = self.main_chart_hover_info.get("y"); y = y[0] if isinstance(y, list) and y else y
            try:
                 if isinstance(y, (int, float, str, Decimal)): return float(y)
            except (ValueError, TypeError): pass
        return last_price

    @rx.var
    def display_time(self) -> str:
        if self.main_chart_hover_info and "x" in self.main_chart_hover_info:
            x = self.main_chart_hover_info.get("x"); x = x[0] if isinstance(x, list) and x else x
            try:
                if isinstance(x, str): return pd.to_datetime(x).strftime('%Y-%m-%d %H:%M')
                elif isinstance(x, datetime): return x.strftime('%Y-%m-%d %H:%M')
            except (ValueError, TypeError): return str(x) if x else "--:--"
        return "--:--"

    @rx.var
    def main_chart_figure(self) -> go.Figure:
        df = self.current_period_data; error_fig = go.Figure().update_layout(height=300, paper_bgcolor='white', plot_bgcolor='white', xaxis=dict(visible=False), yaxis=dict(visible=False), annotations=[dict(text="Cargando/Sin datos...", showarrow=False)])
        if not isinstance(df, pd.DataFrame) or df.empty or 'price' not in df.columns or 'time' not in df.columns: return error_fig
        try:
            # No necesita copiar/limpiar de nuevo, ya se hizo en _fetch_stock_history_data
            df_chart = df
            if df_chart.empty or len(df_chart) < 2: return error_fig # Doble check
            fig = go.Figure(); fig.add_trace(go.Scatter(x=df_chart['time'], y=df_chart['price'], mode='lines', line=dict(width=0), fill='tozeroy', fillcolor=self.chart_area_color, hoverinfo='skip')); fig.add_trace(go.Scatter(x=df_chart['time'], y=df_chart['price'], mode='lines', line=dict(color=self.chart_color, width=2.5, shape='spline'), name='Price', hovertemplate='<b>Price:</b> %{y:.2f}<br><b>Time:</b> %{x|%Y-%m-%d %H:%M}<extra></extra>'))
            min_p, max_p = df_chart['price'].min(), df_chart['price'].max()
            if pd.isna(min_p) or pd.isna(max_p): return error_fig
            padding = (max_p - min_p) * 0.1 if (max_p != min_p) else abs(min_p) * 0.1 or 1; range_min, range_max = min_p - padding, max_p + padding
            fig.update_layout(height=300, margin=dict(l=40, r=10, t=10, b=30), paper_bgcolor='white', plot_bgcolor='white', xaxis=dict(showgrid=False, zeroline=False, tickmode='auto', nticks=6, showline=True, linewidth=1, linecolor='lightgrey', tickangle=-30), yaxis=dict(title=None, showgrid=True, gridcolor='rgba(230, 230, 230, 0.5)', zeroline=False, showline=False, side='left', tickformat=".2f", range=[range_min, range_max]), hovermode='x unified', showlegend=False)
            return fig
        except Exception as e: logger.error(f"Error generating main_chart_figure: {e}", exc_info=True); return error_fig

    # --- Event Handlers --- #
    async def dashboard_on_mount(self):
        """Called when the dashboard page loads. Fetches PNL and main chart data."""
        logger.info("--- Dashboard on_mount START ---")
        try:
            symbol = "AAPL" # Símbolo principal
            quantity = self.SIMULATED_PORTFOLIO.get(symbol, 0)

            if quantity > 0:
                # Calcular PNL diario y obtener datos para su gráfico
                self.daily_pnl, self.daily_pnl_chart_data = self._calculate_stock_pnl(symbol, "1D", quantity)
                # Calcular PNL mensual y obtener datos para su gráfico
                self.monthly_pnl, self.monthly_pnl_chart_data = self._calculate_stock_pnl(symbol, "1M", quantity)
                # Calcular PNL anual y obtener datos para su gráfico
                self.yearly_pnl, self.yearly_pnl_chart_data = self._calculate_stock_pnl(symbol, "1A", quantity)
                logger.info(f"PNL values calculated: D={self.daily_pnl:.2f}, M={self.monthly_pnl:.2f}, Y={self.yearly_pnl:.2f}")
            else: # Resetear si no hay cantidad simulada
                logger.warning(f"Symbol {symbol} quantity is 0 in SIMULATED_PORTFOLIO. PNLs set to 0.")
                self.daily_pnl, self.monthly_pnl, self.yearly_pnl = 0.0, 0.0, 0.0
                self.daily_pnl_chart_data, self.monthly_pnl_chart_data, self.yearly_pnl_chart_data = [pd.DataFrame(columns=['time', 'price'])] * 3

            # Fetch initial main chart data (para el período seleccionado por defecto, 1D)
            self.current_period_data = self._fetch_stock_history_data(symbol, self.selected_period)
            logger.info(f"Initial main chart data fetch COMPLETE ({self.selected_period}). Rows: {len(self.current_period_data)}")

        except Exception as e: logger.error(f"Error during dashboard_on_mount: {e}", exc_info=True)
        logger.info("--- Dashboard on_mount END ---")

    def set_period(self, period: str):
        """Updates the selected period and fetches new chart data for the main chart."""
        logger.info(f"--- set_period START --- Period: {period}")
        self.selected_period = period
        self.main_chart_hover_info = None
        default_symbol = "AAPL"
        self.current_period_data = self._fetch_stock_history_data(default_symbol, period)
        logger.info(f"Main chart data fetch COMPLETE for period {period}. Rows: {len(self.current_period_data)}")
        logger.info("--- set_period END ---")

    # handle_hover, handle_unhover, toggle_change_display sin cambios
    def handle_hover(self, event_data):
        new_hover_info = None; points = None
        if event_data and isinstance(event_data, list) and event_data[0] and isinstance(event_data[0], dict): points = event_data[0].get('points')
        if points and isinstance(points, list) and points[0] and isinstance(points[0], dict): new_hover_info = points[0]
        if self.main_chart_hover_info != new_hover_info: self.main_chart_hover_info = new_hover_info
    def handle_unhover(self, _):
        if self.main_chart_hover_info is not None: self.main_chart_hover_info = None
    def toggle_change_display(self): self.show_absolute_change = not self.show_absolute_change


# --- UI Components ---
def create_pnl_chart(df_data: pd.DataFrame, color: str = "rgba(255,255,255,0.7)") -> go.Figure:
    """Creates a minimal Plotly figure for PNL cards from DataFrame."""
    fig = go.Figure().update_layout(height=64, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))
    if isinstance(df_data, pd.DataFrame) and not df_data.empty and 'price' in df_data.columns:
        prices = pd.to_numeric(df_data['price'], errors='coerce').dropna().tolist()
        if len(prices) >= 2:
             fig.add_trace(go.Scatter(y=prices, mode='lines', line=dict(color=color, width=2), fill="tozeroy", fillcolor="rgba(255,255,255,0.1)", hoverinfo='none'))
    return fig

def pnl_card(title: str, value: rx.Var[float], chart_data_df: rx.Var[pd.DataFrame]) -> rx.Component:
    """Creates a UI card for displaying PNL metrics, using DataFrame for the chart."""
    figure = create_pnl_chart(chart_data_df) # Llama a la función con el Var
    fmt_val = rx.cond(value >= 0, f"+${value:,.2f}", f"-${abs(value):,.2f}")
    return rx.card(rx.vstack(rx.text(title, size="2", weight="medium", color="rgba(255,255,255,0.9)"), rx.text(fmt_val, size="6", weight="bold"), rx.box(rx.plotly(data=figure, layout={}, config={"displayModeBar": False}), height="64px", width="100%"), spacing="1", align="start"), bg="var(--accent-9)", color="white", size="2")

def balance_card(balance: rx.Var[float], date: str) -> rx.Component:
    """Creates a UI card for displaying the balance from AuthState."""
    is_loading = AuthState.is_authenticated & (balance <= 0.0) & (AuthState.username != "")

    display_value = rx.cond(
        is_loading,
        # Corrección: Usar tamaño válido para Radix Spinner
        rx.spinner(size="2"), # <--- CAMBIADO DE 'sm' A '2'
        rx.cond(
             balance.to(float) >= 0,
             f"$ {balance.to(float):,.2f}",
             f"- $ {abs(balance.to(float)):,.2f}"
        )
    )
    return rx.vstack(
        rx.text("Balance", size="3", weight="medium", color="gray"),
        rx.text(display_value, size="6", weight="bold", color="var(--accent-9)"),
        rx.text("En", size="2", color="gray", margin_top="10px"),
        rx.text(date, size="4", color="var(--accent-9)"),
        align="start", padding="16px", height="100%",
    )

def period_selector(selected: rx.Var[str], handler: rx.EventHandler) -> rx.Component:
    periods = ["1D", "5D", "1M", "6M", "ENG", "1A", "5A", "MAX"]; buttons = []
    for i, p in enumerate(periods):
        is_sel = (selected == p);
        if i > 0: buttons.append(rx.text("|", color="lightgray", mx="2px", align_self="center"))
        buttons.append(rx.button(p, on_click=lambda period=p: handler(period), variant="ghost", size="1", color_scheme=rx.cond(is_sel, "accent", "gray"), font_weight=rx.cond(is_sel, "bold", "normal"), px="8px", py="4px", _hover={"bg": rx.cond(is_sel, "var(--accent-4)", "var(--accent-3)")}))
    return rx.hstack(*buttons, spacing="1", align="center")

# --- Main Page Function ---
@rx.page(route="/dashboard")
def dashboard_page() -> rx.Component:
    """Builds the dashboard UI using data primarily from AuthState and DashboardState."""
    # No se pre-generan datos PNL aquí
    return rx.container(
        rx.vstack(
            # Header
            rx.hstack(rx.hstack(rx.avatar(fallback=rx.cond(AuthState.is_authenticated&(AuthState.username!=""), AuthState.username[0:2].upper(), "??"), size="3"), rx.text(AuthState.username, weight="bold", size="4"), align="center"), rx.spacer(), rx.hstack(rx.image(src="/logo.png", h="30px", w="auto"), rx.text("tradesim", weight="bold", color="var(--accent-9)"), align="center", spacing="2"), justify="between", w="100%", pb="16px", border_bottom="1px solid var(--gray-a6)", mb="24px"),
            # Content
            rx.vstack(
                 rx.heading("Dashboard", size="7", weight="bold", mb="20px"),
                 # Cards - Pasan las variables de estado correctas para PNL y gráficos PNL
                 rx.grid(
                     pnl_card("Ultimo dia PNL", DashboardState.daily_pnl, DashboardState.daily_pnl_chart_data),
                     pnl_card("Ultimo mes PNL", DashboardState.monthly_pnl, DashboardState.monthly_pnl_chart_data),
                     pnl_card("Ultimo año PNL", DashboardState.yearly_pnl, DashboardState.yearly_pnl_chart_data),
                     balance_card(AuthState.account_balance, DashboardState.balance_date),
                     columns="4", spacing="4", w="100%", mb="24px"),
                 # Chart Card
                 rx.card(
                     rx.vstack(
                         rx.vstack( # Price/Change display
                             rx.heading(rx.cond(DashboardState.main_chart_hover_info, f"{DashboardState.display_price:.2f} USD @ {DashboardState.display_time}", rx.cond(DashboardState.price_change_info['last_price']!=0.0, f"{DashboardState.price_change_info['last_price']:.2f} USD", "-- USD")), size="6", weight="bold"),
                             rx.hstack( # Change indicator
                                 rx.match(DashboardState.is_change_positive, (True, rx.icon(tag="arrow_up", size=16, color=DashboardState.chart_color)), (False, rx.icon(tag="arrow_down", size=16, color=DashboardState.chart_color)), rx.text("?", font_size="sm")),
                                 rx.text(rx.cond(DashboardState.show_absolute_change, DashboardState.formatted_change_value, f"({DashboardState.formatted_percent_change} %)"), color=DashboardState.chart_color, size="4", weight="medium"),
                                 on_click=DashboardState.toggle_change_display, cursor="pointer", align="center", spacing="1"),
                             align="start", spacing="1", mb="10px"),
                         period_selector(DashboardState.selected_period, DashboardState.set_period), # Period Selector
                         rx.plotly(data=DashboardState.main_chart_figure, config={"displayModeBar": False, "scrollZoom": False}, on_hover=DashboardState.handle_hover, on_unhover=DashboardState.handle_unhover, width="100%", height="300px"), # Plotly Chart
                         spacing="3", align="stretch", w="100%",
                     ), w="100%", size="2"
                 ), spacing="5", align="stretch", w="100%",
            ), w="100%", p="16px",
        ),
        on_mount=DashboardState.dashboard_on_mount, # on_mount en el container
        max_width="1200px", p="16px",
    )