import reflex as rx
from ..state.auth_state import AuthState
from ..components.layout import layout # Assuming layout component exists
from typing import Dict, Any, List # Ensure List is imported
import reflex.components.radix.themes as rt # THIS IS THE CORRECT IMPORT FOR RADIX THEMES
from ..components.callout import callout  # Import the custom callout component
# En detalles_accion.py, después de los imports
from ..state.auth_state import AuthState
print(f"DEBUG detalles_accion.py: AuthState imported. Has load_stock_page_data? {hasattr(AuthState, 'load_stock_page_data')}")
print(f"DEBUG detalles_accion.py: AuthState imported. Has dashboard_on_mount? {hasattr(AuthState, 'dashboard_on_mount')}")
from ..database import SessionLocal
from ..models.stock import Stock
from ..models.portfolio_item import PortfolioItemDB

# Helper for period selector
def period_selector_detail(selected: rx.Var[str], handler: rx.EventHandler) -> rx.Component:
    periods = ["1D", "5D", "1M", "6M", "YTD", "1Y", "5Y", "MAX"] # Common periods
    buttons = []
    for i, p in enumerate(periods):
        is_sel = (selected == p)
        if i > 0:
            buttons.append(rx.text("|", color="var(--gray-a8)", mx="1", align_self="center")) # Adjusted color
        buttons.append(
            rx.button(
                p,
                on_click=lambda period=p: handler(period),
                variant="ghost",
                size="1",
                color_scheme="gray", 
                font_weight=rx.cond(is_sel, "bold", "normal"),
                color=rx.cond(is_sel, "var(--accent-9)", "var(--gray-11)"), # Highlight selected
                padding_x="0.5em", padding_y="0.2em",
                height="auto",
                _hover={"background_color": "var(--gray-a3)"}
            )
        )
    return rx.hstack(*buttons, spacing="1", align="center", margin_top="0.5em", mb="1em")

# Helper for individual metric display
def metric_card(key: str, value: str) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.text(key, size="2", color_scheme="gray", flex_shrink=0),
            rx.spacer(),
            rx.text(value, size="2", weight="medium", text_align="right", white_space="nowrap", overflow="hidden", text_overflow="ellipsis"),
            justify="between",
            width="100%"
        ),
        padding_y="0.65rem", # Adjusted padding
        border_bottom="1px solid var(--gray-a5)", # Adjusted border
        width="100%",
    )

# Helper for news item display
def news_item_card(news_item: Dict[str, str]) -> rx.Component:
    return rx.link(
        rx.card(
            rx.vstack(
                rx.text(news_item.get("title", "Noticia sin título"), weight="bold", size="2", mb="0.25rem", max_lines=2, text_overflow="ellipsis"),
                rx.hstack(
                    rx.text(news_item.get("publisher", ""), size="1", color_scheme="gray"),
                    rx.spacer(),
                    rx.text(news_item.get("providerPublishTime", ""), size="1", color_scheme="gray"),
                    justify="between",
                    width="100%"
                ),
                align_items="start", spacing="1", width="100%"
            ),
            as_child=True # Makes the card itself the link target
        ),
        href=news_item.get("link", "#"),
        is_external=True,
        width="100%",
        _hover={"text_decoration": "none"}
    )

def stock_details() -> rx.Component:
    """Stock details page content."""
    return rx.vstack(
        rx.heading(AuthState.current_stock_info.get("name", ""), size="1"),
        rx.text(f"Sector: {AuthState.current_stock_info.get('sector', 'N/A')}"),
        rx.hstack(
            rx.text(f"Precio actual: ${AuthState.current_stock_info.get('current_price', 0):.2f}"),
            rx.text(
                f"Cambio: {AuthState.current_stock_info.get('change', 0):.2f}%",
                color=AuthState.current_stock_change_color
            ),
        ),
        rx.text(f"Acciones en tu portfolio: {AuthState.current_stock_shares_owned}"),
        rx.divider(),
        rx.heading("Comprar/Vender", size="2"),
        rx.hstack(
            rx.input(
                type_="number",
                value=str(AuthState.buy_sell_quantity),
                on_change=AuthState.set_buy_sell_quantity,
                min_=1,
            ),
            rx.button(
                "Comprar",
                on_click=AuthState.buy_stock,
                is_disabled=rx.cond(AuthState.is_authenticated, False, True),
            ),
            rx.button(
                "Vender",
                on_click=AuthState.sell_stock,
                is_disabled=rx.cond(
                    AuthState.is_authenticated & (AuthState.current_stock_shares_owned > 0),
                    False,
                    True
                ),
            ),
        ),
        rx.text(
            AuthState.transaction_message,
            color=rx.cond(AuthState.transaction_message.contains("éxito"), "green", "red")
        ),
        rx.divider(),
        rx.heading("Gráfico de Precios", size="2"),
        rx.plotly(
            data=AuthState.stock_detail_chart_figure,
        ),
        width="100%",
        spacing="4",
    )

def stock_detail_page_content() -> rx.Component:
    """Stock detail page content with authentication check."""
    return rx.cond(
        AuthState.is_authenticated,
        stock_details(),
        rx.vstack(
            rx.heading("Inicia sesión para ver los detalles de la acción", size="1"),
            rx.button("Iniciar Sesión", on_click=rx.redirect("/login")),
            spacing="4",
        ),
    )

def stock_detail_page() -> rx.Component:
    """Stock detail page."""
    return rx.vstack(
        stock_detail_page_content(),
        width="100%",
        max_width="1200px",
        margin="0 auto",
        padding="4",
    )

# Set up the page route
detalles_accion_page = rx.page(
    route="/detalles_accion/[symbol]",
    title="Detalles de Acción",
)(stock_detail_page)