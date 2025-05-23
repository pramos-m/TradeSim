import reflex as rx
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any, Tuple, Optional
from sqlmodel import Field, Relationship, SQLModel
# Importar AuthState y modelos necesarios
from ..state.auth_state import AuthState, PortfolioItem, TransactionDisplayItem
# Importar middleware y layout
from ..utils.auth_middleware import require_auth
from ..components.layout import layout
import logging
from decimal import Decimal
from ..models.user import User
from ..models.portfolio_item import PortfolioItemDB
from ..state.search_state import SearchState # Asegúrate que la ruta a tu SearchState es correcta


print(f"DEBUG dashboard_page.py: AuthState imported. Has portfolio_chart_hover_info? {hasattr(AuthState, 'portfolio_chart_hover_info')}")
print(f"DEBUG dashboard_page.py: AuthState imported. Has total_portfolio_value? {hasattr(AuthState, 'total_portfolio_value')}")
print(f"DEBUG dashboard_page.py: AuthState imported. Has stock_detail_chart_change_info? {hasattr(AuthState, 'stock_detail_chart_change_info')}")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- Constantes y Componentes UI ---
TEXT_GRAY="#5F6368";BORDER_COLOR="rgba(0,0,0,0.1)"

# PNL Card (SIN mini-gráfico)
def pnl_card(title: str, value: rx.Var[float], chart_data_df: pd.DataFrame) -> rx.Component:
    fmt_val = rx.cond(value == 0.0, "N/A", rx.cond(value > 0.0, f"+${value:,.2f}", f"-${abs(value):,.2f}"))
    return rx.card(rx.vstack(rx.text(title, size="2", weight="medium", color="rgba(255,255,255,0.9)"), rx.text(fmt_val, size="6", weight="bold"), spacing="1", align="start", justify="between", min_height="80px"), bg="var(--accent-9)", color="white", size="2")

# Balance Card (igual)
def balance_card(balance: rx.Var[float], date: str) -> rx.Component:
    is_loading = AuthState.is_authenticated & (balance <= 0.0) & (AuthState.username != ""); display_value = rx.cond(is_loading, rx.spinner(size="2"), rx.cond(balance.to(float) >= 0, f"$ {balance.to(float):,.2f}", f"- $ {abs(balance.to(float)):,.2f}")); return rx.card(rx.vstack(rx.text("Balance", size="3", color="gray"), rx.text(display_value, size="6", weight="bold", color="var(--accent-9)"), rx.text("En", size="2", color="gray", mt="10px"), rx.text(date, size="4", color="var(--accent-9)"), align="start", p="16px", h="100%"))

# Selector Periodo (igual)

def period_selector(selected: rx.Var[str], handler: rx.EventHandler) -> rx.Component:
    periods = ["5D", "1M", "6M", "ENG", "1A", "5A", "MAX"]
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


# Tarjeta Stock Portfolio (modificado para incluir logo)
def portfolio_stock_card(item: PortfolioItem) -> rx.Component:
    # Implement the same image source logic as in search_state/buscador
    # Prioritize item.logo_url if it looks like a valid URL or starts with /.
    # Otherwise, construct a local path, and finally fallback to a default.
    logo_src = rx.cond(
        # Check if item.logo_url is not empty and starts with http or /
        (item.logo_url != "") & (item.logo_url.startswith("http") | item.logo_url.startswith("/")),
        item.logo_url, # Use the provided logo_url if it seems valid
        # If not valid, construct a local path like in search_state.py
        # Use item.symbol to create the potential local asset path
        rx.cond(
            (item.symbol != ""), # Check if symbol is available
            f"/{item.symbol.lower()}.png", # Construct local path (using lowercase for consistency)
            # Ultimate fallback if symbol is also not available
            "/assets/default_logo.png"
        )
    )

    details_link = rx.link("Ver Detalles", href="#", size="1", color_scheme="blue")
    return rx.cond(
        item.symbol & (item.symbol != ""), # Condition: symbol is not None and not empty string
        rx.card(
            rx.hstack(
                rx.image(
                    src=logo_src, # Use the determined logo_src
                    width="40px",
                    height="40px",
                    object_fit="contain",
                    fallback_src="/assets/default_logo.png", # Keep the fallback_src as a safety net
                    mr="3",
                ),  # Mostrar el logo
                rx.vstack(
                    # Using rx.text for name and quantity as in the provided code
                    rx.text(item.name, font_weight="medium", size="2", no_of_lines=1), 
                    rx.text(f"{item.quantity} Acciones", font_size="1", color=TEXT_GRAY),
                    align_items="start",
                    spacing="0",
                ),
                rx.spacer(), # Use spacer to push the next vstack to the right
                rx.vstack(
                    rx.text(f"$ {item.current_value:,.2f}", font_weight="medium", size="2", text_align="right"),
                    details_link, # Keep the 'Ver Detalles' link here
                    align_items="end",
                    spacing="1",
                ),
                spacing="4",
                align="center",
                width="100%",
                # The justify="space-between" is replaced by rx.spacer()
            ),
            size="1", # Keep size="1"
            bg="white",
            border_radius="xl",
            box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)",
            p="4", # Keep p="4"
            cursor="pointer", # Add cursor pointer to indicate clickability
            # Make the entire card clickable to navigate to the stock detail page
            on_click=AuthState.go_to_stock_detail_global(item.symbol), 
        ),
        # Fallback view if symbol is invalid - use a simple, non-erroring version
        rx.card(
            rx.vstack(
                rx.icon(tag="alert_triangle", size=24, color="var(--gray-11)"),
                rx.text("Datos de acción no disponibles", size="2", color=TEXT_GRAY),
                align="center",
                spacing="2",
            ),
            size="1",
            bg="gray.50",
            border_radius="xl",
            box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05)",
            p="4",
            width="100%",
        )
    )

# Componente para Fila de Transacción
def transaction_row(transaction: TransactionDisplayItem) -> rx.Component:
    row_color = rx.cond(transaction.type == "Compra", "var(--green-9)", "var(--red-9)") # Using Radix colors for consistency
    return rx.hstack(
        rx.text(transaction.timestamp, size="2", width="100px", white_space="nowrap", color=TEXT_GRAY),
        rx.badge(
            transaction.type, 
            color_scheme=rx.cond(transaction.type == "Compra", "green", "red"), 
            variant="soft", 
            width="60px", 
            text_align="center"
        ),
        rx.text(transaction.symbol, weight="medium", size="2", width="80px"),
        rx.text(
            transaction.quantity, 
            size="2", 
            text_align="right", 
            width="60px", 
            color=row_color
        ),
        rx.text(
            f"@ ${transaction.price:,.2f}", 
            size="2", 
            text_align="right", 
            flex_grow="1", 
            color=TEXT_GRAY
        ),
        width="100%", 
        justify="between", 
        align="center", 
        padding_y="2",
        border_bottom=f"1px solid {BORDER_COLOR}", 
        _last={"border_bottom": "none"}
    )

# --- Main Page Function ---
@rx.page(route="/dashboard")
@require_auth
def dashboard_page() -> rx.Component:
    """Dashboard funcional completo."""
    # Contenido principal del dashboard (el vstack interno)
    inner_dashboard_content = rx.vstack(
        rx.heading("Dashboard", size="8", weight="bold", mb="20px", align_self="flex_start"),
        # PNL / Balance Grid
        rx.grid(
            pnl_card("PNL Dia (AAPL)", AuthState.daily_pnl, AuthState.daily_pnl_chart_data),
            pnl_card("PNL Mes (AAPL)", AuthState.monthly_pnl, AuthState.monthly_pnl_chart_data),
            pnl_card("PNL Año (AAPL)", AuthState.yearly_pnl, AuthState.yearly_pnl_chart_data),
            balance_card(AuthState.account_balance, AuthState.balance_date),
            columns={"initial": "1", "sm": "2", "lg": "4"}, spacing="4", w="100%", mb="24px"
        ),
        # --- Gráfico Principal (PORTFOLIO) ---
        rx.card(
            rx.vstack(
                rx.vstack( # Info Valor/Cambio Portfolio
                        rx.heading(rx.cond(AuthState.portfolio_chart_hover_info, f"${AuthState.portfolio_display_value:,.2f} USD", AuthState.formatted_total_portfolio_value), size="6", weight="bold"),                        
                        rx.hstack(
                        rx.match(AuthState.is_portfolio_value_change_positive, (True, rx.icon(tag="arrow_up", size=16, color=AuthState.portfolio_chart_color)), (False, rx.icon(tag="arrow_down", size=16, color=AuthState.portfolio_chart_color)), rx.text("?", font_size="sm")),
                        rx.text(rx.cond(AuthState.portfolio_show_absolute_change, AuthState.formatted_portfolio_value_change_abs, f"{AuthState.formatted_portfolio_value_percent_change}%"), color=AuthState.portfolio_chart_color, size="4", weight="medium", on_click=AuthState.portfolio_toggle_change_display, cursor="pointer"),
                        rx.text(rx.cond(AuthState.portfolio_chart_hover_info, AuthState.portfolio_display_time, "Valor Total Portfolio"), color=TEXT_GRAY, size="2"),
                    spacing="3"),
                    align_items="start", spacing="1", mb="10px"
                ),
                period_selector(AuthState.selected_period, AuthState.set_period),
                rx.plotly(data=AuthState.main_portfolio_chart_figure, config={"displayModeBar": False, "scrollZoom": False}, on_hover=AuthState.portfolio_chart_handle_hover, on_unhover=AuthState.portfolio_chart_handle_unhover, width="100%", height="300px"),
                spacing="3", align="stretch", w="100%",
            ), w="100%", size="2", mb="24px"
        ),
        # Sección Mi Portfolio
        rx.vstack(
            rx.heading("Mi Portafolio", size="6", mb="1rem", align_self="flex_start"),
            rx.grid(rx.foreach(AuthState.portfolio_items, portfolio_stock_card), columns={"initial": "1", "md": "2", "lg":"3"}, spacing="4", width="100%"),
            rx.cond(
                AuthState.portfolio_items.length() == 0,
                rx.card(
                    rx.vstack(
                        rx.icon(tag="search", size=32, color="var(--gray-11)", mb="2"),
                        rx.heading("Tu portfolio está vacío", size="4", mb="2"),
                        rx.text("No tienes ninguna acción en tu portfolio. ¡Comienza a invertir!", color=TEXT_GRAY, mb="4"),
                        rx.link(
                            rx.button(
                                "Buscar Acciones",
                                color_scheme="blue",
                                size="2",
                                left_icon="search",
                            ),
                            href="/buscador",
                        ),
                        align="center",
                        spacing="2",
                        p="6",
                    ),
                    bg="white",
                    border_radius="xl",
                    box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)",
                    width="100%",
                ),
            ),
            align_items="stretch", width="100%", mb="24px"
        ),
        # Transacciones Recientes
        rx.vstack(
            rx.heading("Transacciones Recientes", size="5", mb="1rem", align_self="flex_start"),
            rx.card(
                rx.vstack(
                    rx.hstack( rx.text("Fecha", size="1", color=TEXT_GRAY, width="100px"), rx.text("Tipo", size="1", color=TEXT_GRAY, width="60px", text_align="center"), rx.text("Símbolo", size="1", color=TEXT_GRAY, width="80px"), rx.text("Cantidad", size="1", color=TEXT_GRAY, width="60px", text_align="right"), rx.text("Precio", size="1", color=TEXT_GRAY, flex_grow="1", text_align="right"), width="100%", justify="between", align="center", padding_bottom="1", border_bottom=f"1px solid {BORDER_COLOR}", mb="1" ),
                    rx.cond(
                        AuthState.recent_transactions.length() > 0,
                        rx.vstack( rx.foreach(AuthState.recent_transactions, transaction_row), spacing="0", width="100%" ),
                        rx.center(rx.text("No hay transacciones recientes.", color=TEXT_GRAY, padding_y="4"), width="100%")
                    ),
                    align_items="stretch", width="100%",
                ),
                width="100%", size="1",
                max_height="300px",
                overflow_y="auto"
            ),
            align_items="stretch", width="100%",
        ),
        # Propiedades del vstack interno
        spacing="5", 
        align="stretch", 
        w="100%", 
    )

    # Contenedor principal 'page_content'
    page_content = rx.vstack(
        inner_dashboard_content, # El vstack interno definido arriba
        
        # --- Modificaciones para centrar 'page_content' ---
        width="100%",             # page_content ocupa el 100% del ancho disponible en su contenedor padre (probablemente el layout).
        max_width="1000px",       # Establece un ancho máximo para el contenido. Puedes ajustar "1400px" (e.g., "1200px", "container.xl", etc.).
        margin_x="auto",          # Centra horizontalmente este Vstack.
        padding_y="1.5rem",       # Añade espacio vertical arriba y abajo del contenido (opcional, ajústalo).
        padding_x="1rem",         # Añade espacio horizontal a los lados del contenido, DENTRO del max_width (opcional, ajústalo).
                                  # El `p="0"` original ha sido reemplazado por estos paddings más específicos.
                                  # Si no deseas padding aquí, puedes eliminarlos.
        on_mount=AuthState.dashboard_on_mount, # El on_mount permanece en este vstack externo.
    )
    
    # Envolver en layout
    return layout(page_content)

# --- Database Models (e.g., starting around line 1379) ---

class StockData(SQLModel, table=True): # Using SQLModel directly
    __tablename__ = "stockdata"
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(index=True, unique=True)
    name: str
    logo_url: Optional[str]
    # ... other fields ...

# ...
# Your AuthState class and other Pydantic models (rx.Base) would follow
# ...

def handle_stock_click(self, symbol: str):
    return rx.redirect(f"/detalles_accion/{symbol}")

def portfolio_table():
    return rx.vstack(
        rx.heading("Mi Portafolio", size="lg", mb=4),
        rx.table(
            rx.thead(
                rx.tr(
                    rx.th("Símbolo"),
                    rx.th("Nombre"),
                    rx.th("Cantidad"),
                    rx.th("Precio Actual"),
                    rx.th("Valor Total"),
                    rx.th("Acciones")
                )
            ),
            rx.tbody(
                rx.foreach(
                    AuthState.portfolio_items,
                    lambda item: rx.tr(
                        rx.td(item.symbol),
                        rx.td(item.name),
                        rx.td(item.quantity),
                        rx.td(f"${item.current_price:.2f}"),
                        rx.td(f"${item.current_value:.2f}"),
                        rx.td(
                            rx.hstack(
                                rx.button(
                                "Ver Detalles", 
                                on_click=lambda: SearchState.go_to_stock_detail(SearchState.search_result.get("Symbol")),
                                color_scheme="blue", variant="solid", size="2", margin_top="16px",
                                is_disabled=(SearchState.search_result.get("Symbol", "N/A") == "N/A")
                            ),
                                rx.button(
                                    "Vender",
                                    on_click=rx.redirect(f"/detalles_accion/{item.symbol}")
                                )
                            )
                        )
                    )
                )
            ),
            variant="striped",
            width="100%"
        ),
        rx.text(f"Valor Total del Portafolio: ${AuthState.total_portfolio_value:.2f}", mt=4)
    )
