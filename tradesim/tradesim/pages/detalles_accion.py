import reflex as rx
from ..state.auth_state import AuthState
# from ..state.news_state import NewsState # Remove this line if NewsState functionality is merged into AuthState
from ..pages.noticias import featured_article
from ..components.layout import layout
from typing import Dict, List, Tuple # AÑADIDO List y Tuple AQUÍ

# Helper for period selector (can be moved to a common components file)
def period_selector_detail(selected: rx.Var[str], handler: rx.EventHandler) -> rx.Component:
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
                color_scheme="gray", # Keep it subtle
                font_weight=rx.cond(is_sel, "bold", "normal"),
                padding_x="0.5em", padding_y="0.2em",
                height="auto",
                _hover={"background_color": "var(--gray-a3)"}
            )
        )
    return rx.hstack(*buttons, spacing="1", align="center", margin_top="0.5em")

# Helper for data grid rows
def metric_row(label: str, value: rx.Var[str]) -> rx.Component:
    return rx.hstack(
        rx.text(label, font_size="0.9em", color_scheme="gray", width="55%"), # Adjusted width
        rx.text(value, font_size="0.9em", font_weight="medium", width="45%", text_align="right"), # Adjusted width
        justify="between",
        width="100%",
        padding_y="0.75em", # Increased padding
        border_bottom="1px solid var(--gray-a4)", # Slightly darker border
    )

# Data grid component
def stock_metrics_grid(metrics_list: rx.Var[List[Tuple[str, str]]]) -> rx.Component:
    return rx.vstack(
        rx.foreach(
            metrics_list, # Usar la lista directamente
            lambda item: metric_row(item[0], item[1])
        ),
        spacing="0",
        border="1px solid var(--gray-a5)", # Slightly darker border for the container
        border_radius="var(--radius-3)",
        padding_x="1.2em", # Increased padding
        padding_top="0.5em", # Padding for the first item
        padding_bottom="0.5em", # Padding for the last item
        background_color="var(--gray-a1)", # Subtle background
        width="100%",
    )

def detalles_accion_page_content() -> rx.Component:
    return rx.vstack(
        # Main content: Stock Info (Left) and Metrics (Right)
        rx.hstack(
            # Left Column: Stock Info, Chart, Buttons
            rx.vstack(
                rx.hstack(
                    rx.cond(
                        AuthState.current_stock_info.get("logo_url"), # Use .get() for safer condition
                        rx.image(
                            src=AuthState.current_stock_info.get("logo_url"), # Use .get() for safer src
                            height="48px",
                            width="48px",
                            object_fit="contain",
                            margin_right="1em",
                            fallback=rx.icon(tag="dollar_sign", size=32) # Fallback icon
                        ),
                        rx.box() # Empty box if no logo_url
                    ),
                    rx.heading(
                        AuthState.current_stock_info.get("longName", AuthState.viewing_stock_symbol), 
                        size="7", 
                        weight="bold"
                    ),
                    align_items="center",
                    spacing="3",
                ),
                # Price and Change
                rx.vstack(
                    rx.text(
                        AuthState.stock_detail_display_price,
                        font_size="2.5em", # Larger price
                        font_weight="bold",
                        line_height="1.1"
                    ),
                    rx.text(
                        AuthState.stock_detail_display_time_or_change,
                        font_size="1em",
                        color=AuthState.stock_detail_change_color,
                    ),
                    align_items="start",
                    spacing="0",
                    margin_top="0.5em",
                    margin_bottom="1em",
                ),
                
                period_selector_detail(AuthState.current_stock_selected_period, AuthState.set_current_stock_period),
                
                rx.box(
                    rx.plotly(
                        data=AuthState.stock_detail_chart_figure,
                        on_hover=AuthState.stock_detail_chart_handle_hover,
                        on_unhover=AuthState.stock_detail_chart_handle_unhover,
                        width="100%",
                        height="350px", # Adjusted height
                    ),
                    width="100%",
                    margin_top="0.5em",
                    margin_bottom="1.5em",
                ),
                
                rx.hstack(
                    rx.button("Comprar", size="3", width="100%", color_scheme="blue"), # Updated color scheme
                    rx.button("Vender", size="3", width="100%", color_scheme="red"), # Updated color scheme
                    spacing="4",
                    width="100%",
                ),
                spacing="4",
                width="100%",
                padding_right="2em", # Space between left and right columns
            ),

            # Right Column: Metrics Grid and Info
            rx.vstack(
                rx.text(
                    f"Acció | Cotitzada en {AuthState.current_stock_info.get('exchangeName', 'N/A')}", # Safe access
                    font_size="0.9em",
                    color_scheme="gray",
                    margin_bottom="0.5em",
                ),
                stock_metrics_grid(AuthState.current_stock_metrics_list), 
                
                rx.heading("Informació", size="4", margin_top="2em", margin_bottom="0.5em"),
                rx.text(
                    AuthState.current_stock_info.get("longBusinessSummary", "Informació no disponible."), # Safe access
                    font_size="0.9em",
                    color_scheme="gray",
                    line_height="1.6",
                    max_height="200px", 
                    overflow_y="auto",
                    padding_right="0.5em", 
                ),

                rx.cond(AuthState.current_stock_info.get("ceo") != "N/A", # Safe access
                    rx.vstack(
                        rx.heading("Conseller delegat, CEO", size="3", margin_top="1.5em", margin_bottom="0.3em"),
                        rx.text(AuthState.current_stock_info.get("ceo"), font_size="0.9em"), # Safe access
                        align_items="start",
                        width="100%"
                    )
                ),
                spacing="3",
                width="100%",
                padding_left="1em", # Space from the chart
            ),
            align_items="start", # Align columns to the top
            spacing="6", # Spacing between columns
            width="100%",
            padding_x="2em", # Page padding
            padding_top="1em",
        ),

        # News Section (Below the main content)
        rx.vstack(
            rx.heading("En les notícies", size="6", margin_top="3em", margin_bottom="1em", padding_x="2em"),
            rx.box(
                rx.cond(
                    AuthState.featured_news, # Assuming AuthState now holds featured_news
                    featured_article(AuthState.featured_news),
                    rx.center(
                        rx.cond(
                            AuthState.is_loading_news, # Assuming AuthState has is_loading_news
                            rx.text("Carregant notícies...", font_size="md"),
                            rx.text("No hi ha notícies disponibles.", font_size="md")
                        ),
                        min_height="150px" # Reduced height
                    )
                ),
                background_color="var(--gray-a1)",
                border_radius="var(--radius-3)",
                padding="1.5em",
                margin_x="2em", # Match page padding
                width="calc(100% - 4em)", # Adjust width considering padding
            ),
            rx.button(
                "Visita el nostre panell de notícies!",
                on_click=rx.redirect("/noticias"),
                size="3", # Larger button
                color_scheme="indigo", # Different color
                width="calc(100% - 4em)",
                margin_x="2em",
                margin_top="1.5em",
                margin_bottom="2em",
            ),
            align_items="stretch", # Stretch children to full width
            width="100%",
        ),
        spacing="5",
        width="100%",
        max_width="1400px", # Max width for the content
        margin_x="auto", # Center the content
        align_items="center", # Center vstack content if max_width is applied
    )

def detalles_accion_page() -> rx.Component:
    # The on_load will pass the symbol from the route to AuthState.load_stock_page_data
    # Ensure the symbol from the route is named 'symbol' for this to work directly.
    # If the route param is named differently, adjust AuthState.load_stock_page_data or the on_load call.
    return layout(
        rx.cond(
            AuthState.is_loading_current_stock_details & AuthState.is_current_stock_info_empty,
            rx.center(
                rx.vstack(
                    rx.spinner(size="3"),
                    rx.text(f"Carregant detalls per a {AuthState.viewing_stock_symbol}...", margin_top="1em"),
                    min_height="70vh", # Full viewport height for loading
                ),
            ),
            rx.cond(
                AuthState.current_stock_info.contains("error"),
                 rx.center(
                    rx.vstack(
                        rx.icon(tag="triangle_alert", size=48, color_scheme="red"), # CAMBIADO AQUÍ
                        rx.heading("Error en carregar les dades", color_scheme="red", margin_top="0.5em"),
                        rx.text(AuthState.current_stock_info["error"]),
                        rx.button("Torna al Dashboard", on_click=rx.redirect("/dashboard"), margin_top="1em"),
                        min_height="70vh",
                    ),

                ),
                detalles_accion_page_content() # Actual page content
            )
        )
    )

detalles_accion = rx.page(
    route="/detalles_accion/[symbol]",  # Ruta dinámica
    title="TradeSim - Detalles de Acción",
    on_load=[AuthState.load_stock_page_data, AuthState.get_news]  # Changed to AuthState.get_news
)(detalles_accion_page)