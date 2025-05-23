# tradesim/tradesim/pages/detalles_accion.py
import reflex as rx
from reflex.vars import Var 
from ..state.auth_state import AuthState, NewsArticle # Import NewsArticle from AuthState
from ..state.news_state import NewsState # Import NewsState
from ..components.layout import layout 
from typing import Dict, List, Tuple, Any 

# Helper para el selector de período
def period_selector_detail(selected_var: Var[str], handler_event: rx.EventHandler) -> rx.Component:
    periods = ["1D", "5D", "1M", "6M", "YTD", "1Y", "5Y", "MAX"]
    buttons = []
    for i, p in enumerate(periods):
        is_selected = (selected_var == p)
        buttons.append(
            rx.button(
                p,
                on_click=lambda period=p: handler_event(period), 
                variant="ghost",
                size="1",
                color_scheme="gray",
                font_weight=rx.cond(is_selected, "bold", "normal"),
                color=rx.cond(is_selected, "var(--accent-9)", "var(--gray-11)"),
                bg=rx.cond(is_selected, "var(--accent-a3)", "transparent"),
                _hover={"background_color": "var(--gray-a4)"},
                margin_left="0.25em" if i > 0 else "0", 
                padding_x="0.5em", padding_y="0.2em", height="auto"
            )
        )
    return rx.hstack(*buttons, spacing="1", align="center", margin_y="0.75em")

# Helper para mostrar métricas individuales
def metric_row(label: str, value: rx.Var[str]) -> rx.Component:
    return rx.hstack(
        rx.text(label, size="2", color_scheme="gray", width="50%"),
        rx.text(value, size="2", weight="medium", width="50%", text_align="right", overflow="hidden", text_overflow="ellipsis", white_space="nowrap"),
        justify="between", width="100%", padding_y="0.6em",
        border_bottom="1px solid var(--gray-a4)",
        _last={"border_bottom": "none"} 
    )

# Componente para la cuadrícula de métricas
def stock_metrics_grid(metrics_list_var: rx.Var[List[Tuple[str, str]]]) -> rx.Component:
    return rx.vstack(
        rx.foreach(
            metrics_list_var,
            lambda item_tuple: metric_row(item_tuple[0], item_tuple[1])
        ),
        spacing="0", 
        border="1px solid var(--gray-a5)",
        border_radius="var(--radius-3)",
        padding_x="1em", padding_top="0.25em", padding_bottom="0.25em",
        bg="var(--gray-a1)",
        width="100%",
        min_height="200px" 
    )

# Helper para mostrar tarjetas de noticias
def news_item_card(news_item: NewsArticle) -> rx.Component: 
    return rx.link( 
        rx.card(
            rx.vstack(
                # Removed image display
                rx.text(news_item.title, weight="bold", size="3", mb="0.25rem", max_lines=2, text_overflow="ellipsis", line_height="1.2"),
                rx.hstack(
                    rx.text(news_item.publisher, size="1", color_scheme="gray"),
                    rx.spacer(),
                    rx.text(news_item.date, size="1", color_scheme="gray"),
                    width="100%",
                ),
                align_items="start",
                width="100%",
            ),
            width="100%",
            _hover={"transform": "translateY(-2px)", "box_shadow": "lg"},
            transition="all 0.2s ease-in-out",
        ),
        href=news_item.url,
        is_external=True,
        _hover={"text_decoration": "none"},
    )

def detalles_accion_page_content() -> rx.Component:
    """Contenido principal de la página de detalles de la acción."""
    return rx.vstack(
        rx.grid(
            # Columna Izquierda
            rx.vstack(
                # ... (content of left column: heading, price, chart, buy/sell) ...
                rx.hstack(
                    rx.vstack(
                        rx.heading(
                            AuthState.current_stock_info.get("name", AuthState.viewing_stock_symbol),
                            size="7", weight="bold", line_height="1.2"
                        ),
                        rx.text(
                            AuthState.current_stock_info.get("symbol", "N/A"),
                            size="3", color_scheme="gray"
                        ),
                        align_items="start", spacing="0"
                    ),
                    rx.spacer(),
                    rx.avatar(
                        fallback=AuthState.stock_symbol_first_letter_for_avatar,
                        size="5",
                        radius="medium",
                    ),
                    align_items="center", spacing="3", width="100%"
                ),

                rx.vstack(
                    rx.text(
                        AuthState.stock_detail_display_price,
                        font_size="2.75em", weight="bold", line_height="1.1"
                    ),
                    rx.text(
                        AuthState.stock_detail_display_time_or_change,
                        font_size="1em", color=AuthState.stock_detail_change_color,
                    ),
                    align_items="start", spacing="0", margin_top="0.75em", margin_bottom="0.5em",
                ),

                period_selector_detail(AuthState.current_stock_selected_period, AuthState.set_current_stock_period),

                rx.box(
                    rx.plotly(
                        data=AuthState.stock_detail_chart_figure,
                        on_hover=AuthState.stock_detail_chart_handle_hover,
                        on_unhover=AuthState.stock_detail_chart_handle_unhover,
                        width="100%", height="350px",
                    ),
                    width="100%", margin_bottom="1.5em",
                    border="1px solid var(--gray-a3)", border_radius="var(--radius-3)"
                ),

                rx.text(f"Acciones en tu portfolio: {AuthState.current_stock_shares_owned}", size="3", margin_bottom="0.5em"),
                rx.hstack(
                    rx.input(
                        placeholder="Cantidad", type="number", size="2",
                        value=AuthState.buy_sell_quantity.to(str),
                        on_change=AuthState.set_buy_sell_quantity,
                        min_="1",
                        width="100px"
                    ),
                    rx.button("Comprar", size="2", color_scheme="green",
                              on_click=AuthState.buy_stock,
                              is_disabled=~AuthState.is_authenticated | AuthState.loading,
                              flex_grow="1"),
                    rx.button("Vender", size="2", color_scheme="red",
                              on_click=AuthState.sell_stock,
                              is_disabled=~AuthState.is_authenticated | AuthState.loading | (AuthState.current_stock_shares_owned < AuthState.buy_sell_quantity),
                              flex_grow="1"),
                    spacing="3", width="100%"
                ),
                rx.cond(
                    AuthState.transaction_message != "",
                    rx.callout.root(
                        rx.callout.icon(rx.icon(tag=rx.cond(AuthState.transaction_message.contains("exitosa") | AuthState.transaction_message.contains("OK"), "check_circle", "x_circle"))),
                        rx.callout.text(AuthState.transaction_message),
                        color_scheme=rx.cond(AuthState.transaction_message.contains("exitosa") | AuthState.transaction_message.contains("OK"), "green", "red"),
                        variant="soft", margin_top="1em", width="100%"
                    )
                ),
                spacing="4", width="100%", padding_right="1.5em",
            ),

            # Columna Derecha
            rx.vstack(
                rx.heading("Estadísticas Clave", size="5", margin_bottom="0.75em"),
                stock_metrics_grid(AuthState.current_stock_metrics_list),

                rx.heading("Sobre la Empresa", size="5", margin_top="2em", margin_bottom="0.75em"),
                rx.scroll_area(
                    rx.text(
                        AuthState.current_stock_info.get("longBusinessSummary", "Información de la empresa no disponible."),
                        size="2", color_scheme="gray", line_height="1.6",
                    ),
                    type="auto", scrollbars="vertical", max_height="250px",
                    padding_right="1em"
                ),
                spacing="3", width="100%", padding_left="1.5em",
                border_left="1px solid var(--gray-a5)",
                height="100%"
            ),
            columns="2fr 1fr",
            spacing="6",
            width="100%",
            align_items="start",
            # padding_top="1em", # This was the original padding for the grid
            padding_x="1em"
        ),

        # Noticias relacionadas (debajo de las dos columnas principales)
        rx.cond(
            AuthState.is_authenticated & AuthState.featured_stock_page_news.length() > 0,
            rx.vstack(
                rx.heading(f"Noticias sobre {AuthState.viewing_stock_symbol}", size="5", margin_top="2em", margin_bottom="1em"),
                rx.grid(
                    rx.foreach(
                        AuthState.featured_stock_page_news,
                        lambda news_item: news_item_card(news_item)
                    ),
                    columns="repeat(auto-fill, minmax(300px, 1fr))",
                    gap="1em",
                    width="100%"
                ),
                width="100%",
            ),
            None
        ),
        spacing="5",
        width="100%",
        max_width="1400px",
        margin_x="auto",
        padding_bottom="2em",
        # 👇 Add or adjust padding_top for the entire page content here if needed
        padding_top="2em", # Example: adds more space at the top of the page content
    )

def detalles_accion_page() -> rx.Component:
    """Página de detalles de la acción, maneja estados de carga y error."""
    return layout(
        rx.cond(
            AuthState.is_loading_current_stock_details & 
            (AuthState.is_current_stock_info_empty | ~AuthState.current_stock_info.contains("symbol")),
            rx.center(
                rx.vstack(
                    rx.spinner(size="3"),
                    rx.text(f"Cargando detalles para {AuthState.viewing_stock_symbol}...", margin_top="1em", color_scheme="gray"),
                    spacing="3"
                ), 
                min_height="80vh" 
            ),
            rx.cond(
                AuthState.current_stock_info.contains("error"),
                rx.center(
                    rx.vstack(
                        rx.icon(tag="circle_help", size=48, color_scheme="red"), 
                        rx.heading("Error al Cargar Datos", color_scheme="red", margin_top="0.5em"),
                        rx.text(AuthState.current_stock_info.get("error", "Error desconocido.")),
                        rx.button("Volver al Dashboard", on_click=rx.redirect("/dashboard"), margin_top="1em", color_scheme="gray"),
                        spacing="3"
                    ), 
                    min_height="80vh"
                ),
                detalles_accion_page_content() 
            )
        )
    )

detalles_accion_page_instance = rx.page( 
    route="/detalles_accion/[symbol]",
    title="TradeSim - Detalles de Acción",
    on_load=AuthState.stock_detail_page_on_mount 
)(detalles_accion_page)
