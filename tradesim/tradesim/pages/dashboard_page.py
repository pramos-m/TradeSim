# tradesim/pages/dashboard_page.py (FINAL - Usa Lógica Gráfico Portfolio)
import reflex as rx
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any, Tuple
# Importar AuthState y PortfolioItem
from ..state.auth_state import AuthState, PortfolioItem
# Importar middleware y layout
from ..utils.auth_middleware import require_auth
from ..components.layout import layout # Usamos tu layout existente
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- Constantes de Estilo ---
TEXT_GRAY = "#5F6368"
BORDER_COLOR = "rgba(0, 0, 0, 0.1)"

# --- UI Components (Versión Estable Anterior) ---
def create_pnl_chart(df_data: pd.DataFrame, color: str = "rgba(255,255,255,0.7)") -> go.Figure:
    fig = go.Figure().update_layout(
        height=64,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    if isinstance(df_data, pd.DataFrame) and not df_data.empty and 'price' in df_data.columns:
        prices = pd.to_numeric(df_data['price'], errors='coerce').dropna().tolist()
        if len(prices) >= 2:
            fig.add_trace(go.Scatter(
                y=prices,
                mode='lines',
                line=dict(color=color, width=2),
                fill="tozeroy",
                fillcolor="rgba(255,255,255,0.1)",
                hoverinfo='none'
            ))
    return fig

def pnl_card(title: str, value: rx.Var[float], chart_data_df: pd.DataFrame) -> rx.Component: # Cambiado tipo chart_data_df
    figure = create_pnl_chart(chart_data_df)
    # Corrected f-string formatting
    fmt_val = rx.cond(
        value == 0.0,
        "N/A",
        rx.cond(
            value > 0.0,
            f"+${value:,.2f}",
            f"-${abs(value):,.2f}"
        )
    )
    return rx.card(
        rx.vstack(
            rx.text(title, size="2", weight="medium", color="rgba(255,255,255,0.9)"),
            rx.text(fmt_val, size="6", weight="bold"),
            rx.box(
                rx.plotly(data=figure, layout={}, config={"displayModeBar": False}),
                height="64px",
                width="100%"
            ),
            spacing="1",
            align="start"
        ),
        bg="var(--accent-9)",
        color="white",
        size="2"
    )

def balance_card(balance: rx.Var[float], date: str) -> rx.Component:
    is_loading = AuthState.is_authenticated & (balance <= 0.0) & (AuthState.username != "")
    display_value = rx.cond(
        is_loading,
        rx.spinner(size="2"),
        rx.cond(
            balance.to(float) >= 0,
            f"$ {balance.to(float):,.2f}",
            f"- $ {abs(balance.to(float)):,.2f}"
        )
    )
    return rx.card(
        rx.vstack(
            rx.text("Balance", size="3", color="gray"),
            rx.text(display_value, size="6", weight="bold", color="var(--accent-9)"),
            rx.text("En", size="2", color="gray", mt="10px"),
            rx.text(date, size="4", color="var(--accent-9)"),
            align="start",
            p="16px",
            h="100%"
        )
    )

def period_selector(selected: rx.Var[str], handler: rx.EventHandler) -> rx.Component:
    periods = ["1D", "5D", "1M", "6M", "ENG", "1A", "5A", "MAX"]
    buttons = []
    for i, p in enumerate(periods):
        is_sel = (selected == p)
        if i > 0:
            buttons.append(rx.text("|", color="lightgray", mx="1", align_self="center"))
        buttons.append(
            rx.button(
                p,
                on_click=lambda period=p: handler(period),
                variant="ghost",
                size="1",
                color_scheme=rx.cond(is_sel, "gray", "gray"),
                font_weight=rx.cond(is_sel, "bold", "normal"),
                px="1",
                py="1",
                height="auto",
                _hover={"bg": "rgba(0,0,0,0.05)"}
            )
        )
    return rx.hstack(*buttons, spacing="1", align="center")

def portfolio_stock_card(item: PortfolioItem) -> rx.Component:
    logo_src = item.logo_url
    details_link = rx.link("Ver Detalles", href="#", size="1", color_scheme="blue")
    return rx.card(
        rx.hstack(
            rx.image(
                src=logo_src,
                width="40px",
                height="40px",
                object_fit="contain",
                fallback="/default_logo.png",
                mr="3"
            ),
            rx.vstack(
                rx.text(item.name, font_weight="medium", size="2", no_of_lines=1),
                rx.text(f"{item.quantity} Acciones", font_size="1", color=TEXT_GRAY),
                align_items="start",
                spacing="0"
            ),
            rx.spacer(),
            rx.vstack(
                rx.text(f"$ {item.current_value:,.2f}", font_weight="medium", size="2", text_align="right"),
                details_link,
                align_items="end",
                spacing="1"
            ),
            spacing="4",
            align="center",
            width="100%"
        ),
        size="1",
        bg="white",
        border_radius="xl",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)",
        p="4"
    )

# --- Main Page Function ---
@rx.page(route="/dashboard")
@require_auth
def dashboard_page() -> rx.Component:
    """Dashboard con gráfico de portfolio funcional."""

    # Contenido principal
    page_content = rx.vstack(
        # Header
        rx.hstack(
            rx.hstack(
                rx.avatar(fallback=rx.cond(AuthState.is_authenticated & (AuthState.username != ""), AuthState.username[0:2].upper(), "??"), size="3"),
                rx.text(AuthState.username, weight="bold", size="4"),
                align="center"
            ),
            rx.spacer(),
            rx.hstack(
                rx.image(src="/logo.png", h="30px", w="auto"),
                rx.text("tradesim", weight="bold", color="var(--accent-9)"),
                align="center",
                spacing="2"
            ),
            justify="between",
            w="100%",
            pb="16px",
            border_bottom="1px solid var(--gray-a6)",
            mb="24px"
        ),
        # Content Vstack
        rx.vstack(
            rx.heading("Dashboard", size="8", weight="bold", mb="20px", align_self="flex-start"),
            # PNL / Balance Grid (PNLs basados en AAPL)
            rx.grid(
                pnl_card("PNL Dia (AAPL)", AuthState.daily_pnl, AuthState.daily_pnl_chart_data),
                pnl_card("PNL Mes (AAPL)", AuthState.monthly_pnl, AuthState.monthly_pnl_chart_data),
                pnl_card("PNL Año (AAPL)", AuthState.yearly_pnl, AuthState.yearly_pnl_chart_data),
                balance_card(AuthState.account_balance, AuthState.balance_date),
                columns={"initial": "1", "sm": "2", "lg": "4"},
                spacing="4",
                w="100%",
                mb="24px"
            ),
            # --- Gráfico Principal (AHORA USA LÓGICA PORTFOLIO) ---
            rx.card(
                rx.vstack(
                    rx.vstack( # Info Valor/Cambio Portfolio
                        # Usa las nuevas variables computadas del portfolio
                        rx.heading(
                            rx.cond(
                                AuthState.portfolio_chart_hover_info,
                                f"${AuthState.portfolio_display_value:,.2f} USD", # Corrected f-string
                                f"${AuthState.portfolio_change_info['last_price']:,.2f} USD" # Corrected f-string
                            ),
                            size="6",
                            weight="bold"
                        ),
                        rx.hstack(
                            rx.match(
                                AuthState.is_portfolio_value_change_positive,
                                (True, rx.icon(tag="arrow_up", size=16, color=AuthState.portfolio_chart_color)),
                                (False, rx.icon(tag="arrow_down", size=16, color=AuthState.portfolio_chart_color)),
                                rx.text("?", font_size="sm") # Default case for match
                            ), # Usa nueva var
                            rx.text(
                                rx.cond(
                                    AuthState.portfolio_show_absolute_change,
                                    AuthState.formatted_portfolio_value_change_abs,
                                    f"({AuthState.formatted_portfolio_value_percent_change}%)"
                                ),
                                color=AuthState.portfolio_chart_color,
                                size="4",
                                weight="medium",
                                on_click=AuthState.portfolio_toggle_change_display,
                                cursor="pointer"
                            ), # Usa nueva var/handler
                            rx.text(
                                rx.cond(
                                    AuthState.portfolio_chart_hover_info,
                                    AuthState.portfolio_display_time,
                                    "Valor Total Portfolio"
                                ),
                                color=TEXT_GRAY,
                                size="2"
                            ), # Usa nueva var
                            spacing="3"
                        ),
                        align_items="start",
                        spacing="1",
                        mb="10px"
                    ),
                    # Selector de periodo ahora llama a la función que recalcula el gráfico del portfolio
                    period_selector(AuthState.selected_period, AuthState.set_period),
                    # Gráfico Plotly ahora usa la figura del portfolio
                    rx.plotly(
                        data=AuthState.main_portfolio_chart_figure,
                        config={"displayModeBar": False, "scrollZoom": False},
                        on_hover=AuthState.portfolio_chart_handle_hover,
                        on_unhover=AuthState.portfolio_chart_handle_unhover,
                        width="100%",
                        height="300px"
                    ), # Usa nuevas vars/handlers
                    spacing="3",
                    align="stretch",
                    w="100%",
                ),
                w="100%",
                size="2",
                mb="24px"
            ),
            # --- FIN Gráfico Principal ---

            # Sección Mi Portfolio (GRID DE TARJETAS - usa portfolio_items)
            rx.vstack(
                rx.heading("Mi Portafolio", size="6", mb="1rem", align_self="flex-start"),
                rx.grid(
                    rx.foreach(AuthState.portfolio_items, portfolio_stock_card),
                    columns={"initial": "1", "md": "2", "lg": "3"},
                    spacing="4",
                    width="100%"
                ),
                rx.cond(
                    AuthState.portfolio_items.length() == 0,
                    rx.text("Tu portfolio está vacío.", color=TEXT_GRAY, mt="4")
                ),
                align_items="stretch",
                width="100%",
                mb="24px"
            ),
            # Transacciones Recientes Placeholder
            rx.vstack(
                rx.heading("Transacciones Recientes", size="5", mb="1rem", align_self="flex-start"),
                rx.card(
                    rx.text("(Próximamente...)", size="2", color_scheme="gray"),
                    width="100%",
                    min_height="100px"
                ),
                align_items="stretch",
                width="100%"
            ),
            spacing="5",
            align="stretch",
            w="100%",
        ),
        w="100%",
        p="0",
        # *** on_mount AÑADIDO AQUÍ ***
        on_mount=AuthState.dashboard_on_mount,
    )

    # Envolver en layout
    return layout(page_content)