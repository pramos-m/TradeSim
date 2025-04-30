# tradesim/pages/dashboard_page.py
import reflex as rx
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any, Tuple
# Importar AuthState que ahora lo contiene todo
from ..state.auth_state import AuthState, NewsArticle # NewsArticle no se usa aquí pero no molesta
from ..database import SessionLocal
from ..models.stock import Stock
from ..models.stock_price_history import StockPriceHistory
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- Ya no hay clase DashboardState aquí ---

# --- UI Components ---
def create_pnl_chart(df_data: pd.DataFrame, color: str = "rgba(255,255,255,0.7)") -> go.Figure:
    fig = go.Figure().update_layout(height=64, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))
    if isinstance(df_data, pd.DataFrame) and not df_data.empty and 'price' in df_data.columns:
        prices = pd.to_numeric(df_data['price'], errors='coerce').dropna().tolist()
        if len(prices) >= 2: fig.add_trace(go.Scatter(y=prices, mode='lines', line=dict(color=color, width=2), fill="tozeroy", fillcolor="rgba(255,255,255,0.1)", hoverinfo='none'))
    return fig

def pnl_card(title: str, value: rx.Var[float], chart_data_df: rx.Var[pd.DataFrame]) -> rx.Component:
    figure = create_pnl_chart(chart_data_df)
    fmt_val = rx.cond(value >= 0, f"+${value:,.2f}", f"-${abs(value):,.2f}")
    return rx.card(rx.vstack(rx.text(title, size="2", weight="medium", color="rgba(255,255,255,0.9)"), rx.text(fmt_val, size="6", weight="bold"), rx.box(rx.plotly(data=figure, layout={}, config={"displayModeBar": False}), height="64px", width="100%"), spacing="1", align="start"), bg="var(--accent-9)", color="white", size="2")

def balance_card(balance: rx.Var[float], date: str) -> rx.Component:
    is_loading = AuthState.is_authenticated & (balance <= 0.0) & (AuthState.username != "")
    display_value = rx.cond(is_loading, rx.spinner(size="2"),
                            rx.cond(balance.to(float) >= 0, f"$ {balance.to(float):,.2f}", f"- $ {abs(balance.to(float)):,.2f}"))
    return rx.vstack(rx.text("Balance", size="3", weight="medium", color="gray"), rx.text(display_value, size="6", weight="bold", color="var(--accent-9)"), rx.text("En", size="2", color="gray", mt="10px"), rx.text(date, size="4", color="var(--accent-9)"), align="start", p="16px", h="100%")

def period_selector(selected: rx.Var[str], handler: rx.EventHandler) -> rx.Component:
    periods=["1D", "5D", "1M", "6M", "ENG", "1A", "5A", "MAX"]; buttons=[]
    for i, p in enumerate(periods):
        is_sel=(selected == p);
        if i > 0: buttons.append(rx.text("|", color="lightgray", mx="2px", align_self="center"))
        buttons.append(rx.button(p, on_click=lambda period=p: handler(period), variant="ghost", size="1", color_scheme=rx.cond(is_sel,"accent","gray"), font_weight=rx.cond(is_sel,"bold","normal"), px="8px", py="4px", _hover={"bg": rx.cond(is_sel, "var(--accent-4)", "var(--accent-3)")}))
    return rx.hstack(*buttons, spacing="1", align="center")

# --- Main Page Function ---
@rx.page(route="/dashboard") # on_mount ya no se pone aquí
def dashboard_page() -> rx.Component:
    """Builds the dashboard UI using data from the combined AuthState."""
    return rx.container(
        rx.vstack(
            # Header
            rx.hstack(rx.hstack(rx.avatar(fallback=rx.cond(AuthState.is_authenticated&(AuthState.username!=""), AuthState.username[0:2].upper(), "??"), size="3"), rx.text(AuthState.username, weight="bold", size="4"), align="center"), rx.spacer(), rx.hstack(rx.image(src="/logo.png", h="30px", w="auto"), rx.text("tradesim", weight="bold", color="var(--accent-9)"), align="center", spacing="2"), justify="between", w="100%", pb="16px", border_bottom="1px solid var(--gray-a6)", mb="24px"),
            # Content
            rx.vstack(
                 rx.heading("Dashboard", size="7", weight="bold", mb="20px"),
                 # Top Cards Row - Referencia a variables en AuthState
                 rx.grid(
                     pnl_card("Ultimo dia PNL", AuthState.daily_pnl, AuthState.daily_pnl_chart_data),
                     pnl_card("Ultimo mes PNL", AuthState.monthly_pnl, AuthState.monthly_pnl_chart_data),
                     pnl_card("Ultimo año PNL", AuthState.yearly_pnl, AuthState.yearly_pnl_chart_data),
                     balance_card(AuthState.account_balance, AuthState.balance_date),
                     columns="4", spacing="4", w="100%", mb="24px"),
                 # Main Chart Card - Referencia a variables/handlers en AuthState
                 rx.card(
                     rx.vstack(
                         rx.vstack( # Price/Change display
                             rx.heading(rx.cond(AuthState.main_chart_hover_info, f"{AuthState.display_price:.2f} USD @ {AuthState.display_time}", rx.cond(AuthState.price_change_info['last_price']!=0.0, f"{AuthState.price_change_info['last_price']:.2f} USD", "-- USD")), size="6", weight="bold"),
                             rx.hstack( # Change indicator
                                 rx.match(AuthState.is_change_positive, (True, rx.icon(tag="arrow_up", size=16, color=AuthState.chart_color)), (False, rx.icon(tag="arrow_down", size=16, color=AuthState.chart_color)), rx.text("?", font_size="sm")),
                                 rx.text(rx.cond(AuthState.show_absolute_change, AuthState.formatted_change_value, f"({AuthState.formatted_percent_change} %)"), color=AuthState.chart_color, size="4", weight="medium"),
                                 # Referencia directa a método de AuthState
                                 on_click=AuthState.toggle_change_display, cursor="pointer", align="center", spacing="1"),
                             align="start", spacing="1", mb="10px"),
                         # Referencia directa a método de AuthState
                         period_selector(AuthState.selected_period, AuthState.set_period),
                         # Referencia directa a método de AuthState
                         rx.plotly(data=AuthState.main_chart_figure, config={"displayModeBar": False, "scrollZoom": False}, on_hover=AuthState.handle_hover, on_unhover=AuthState.handle_unhover, width="100%", height="300px"),
                         spacing="3", align="stretch", w="100%",
                     ), w="100%", size="2"
                 ),
                 # --- PLACEHOLDERS PARA PORTFOLIO Y TRANSACCIONES ---
                 rx.grid(
                     rx.card(rx.vstack(rx.heading("Mi Portfolio", size="5"), rx.divider(), rx.text("(Próximamente: Resumen de acciones poseídas)", size="2", color_scheme="gray"), align_items="stretch", spacing="3", min_height="150px"), size="2"),
                     rx.card(rx.vstack(rx.heading("Transacciones Recientes", size="5"), rx.divider(), rx.text("(Próximamente: Lista de últimas operaciones)", size="2", color_scheme="gray"), align_items="stretch", spacing="3", min_height="150px"), size="2"),
                     columns="2", spacing="4", width="100%", margin_top="24px",
                 ),
                 # --- FIN PLACEHOLDERS ---
                 spacing="5", align="stretch", w="100%",
            ), w="100%", p="16px",
        ),
        # on_mount se llama desde AuthState ahora
        on_mount=AuthState.dashboard_on_mount,
        max_width="1200px", p="16px",
    )