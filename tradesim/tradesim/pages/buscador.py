# import reflex as rx
# import yfinance as yf
# import plotly.graph_objects as go
# from datetime import datetime, timedelta
# from ..utils.auth_middleware import require_auth
# from ..state.auth_state import AuthState
# from ..components.layout import layout

# # Estado para la página del buscador
# class BuscadorState(rx.State):
#     # Estado para el término de búsqueda
#     search_term: str = ""
#     # Resultados de la búsqueda
#     search_results: list = []
#     # Stock seleccionado
#     selected_stock: str = ""
#     # Datos del stock
#     stock_data: dict = {}
#     # Datos para el gráfico - atributo privado
#     _chart_data: dict = {"x": [], "y": []}
#     # Mensaje de error
#     error_message: str = ""
    
#     @rx.var
#     def chart_data(self) -> dict:
#         """Obtener los datos del gráfico como un diccionario de Python normal."""
#         return self._chart_data
    
#     def search_stocks(self):
#         if len(self.search_term) < 2:
#             self.search_results = []
#             return
        
#         try:
#             # Simulando búsqueda - en producción usaríamos yfinance
#             stocks = [
#                 {"symbol": "AAPL", "name": "Apple Inc."},
#                 {"symbol": "MSFT", "name": "Microsoft Corporation"},
#                 {"symbol": "GOOGL", "name": "Alphabet Inc."},
#                 {"symbol": "AMZN", "name": "Amazon.com, Inc."},
#                 {"symbol": "TSLA", "name": "Tesla, Inc."}
#             ]
            
#             # Filtrar resultados basados en el término de búsqueda
#             self.search_results = [
#                 stock for stock in stocks 
#                 if self.search_term.upper() in stock["symbol"] or 
#                    self.search_term.lower() in stock["name"].lower()
#             ]
#         except Exception as e:
#             self.error_message = f"Error al buscar acciones: {str(e)}"
#             self.search_results = []
    
#     def get_stock_info(self, symbol: str):
#         self.selected_stock = symbol
        
#         try:
#             # Obtener información del stock usando yfinance
#             stock = yf.Ticker(symbol)
#             info = stock.info
            
#             # Obtener datos históricos para el gráfico
#             end_date = datetime.now()
#             start_date = end_date - timedelta(days=30)
#             history = stock.history(start=start_date, end=end_date)
            
#             # Convertir el índice de fechas a formato string para evitar problemas de serialización
#             dates = [date.strftime('%Y-%m-%d') for date in history.index]
#             prices = history['Close'].tolist()
            
#             # Guardar los datos para el gráfico como listas simples
#             self._chart_data = {
#                 "x": dates,
#                 "y": prices
#             }
            
#             # Guardar la información del stock
#             self.stock_data = {
#                 "symbol": symbol,
#                 "name": info.get("shortName", "N/A"),
#                 "price": info.get("currentPrice", 0),
#                 "change": info.get("regularMarketChangePercent", 0),
#                 "market_cap": info.get("marketCap", 0),
#                 "volume": info.get("volume", 0),
#                 "pe_ratio": info.get("trailingPE", 0),
#                 "dividend_yield": info.get("dividendYield", 0),
#                 "description": info.get("longBusinessSummary", "No hay descripción disponible.")
#             }
            
#             self.error_message = ""
#         except Exception as e:
#             self.error_message = f"Error al obtener información de {symbol}: {str(e)}"
#             self.stock_data = {}
#             self._chart_data = {"x": [], "y": []}

# # Función para generar el gráfico de línea
# def generate_line_chart(data):
#     # Utilizamos los datos que ya están en formato de lista
#     x = data["x"]
#     y = data["y"]
    
#     if not x or not y:
#         return rx.text("No hay datos disponibles para generar el gráfico.")
    
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name="Precio"))
    
#     # Configuración del diseño
#     fig.update_layout(
#         title="Historial de Precios (30 días)",
#         xaxis_title="Fecha",
#         yaxis_title="Precio ($)",
#         template="plotly_white",
#         height=400,
#     )
    
#     return rx.plotly(data=fig, width="100%")

# # Componente para la tarjeta de resultado de búsqueda
# def stock_result_card(symbol, name):
#     return rx.card(
#         rx.hstack(
#             rx.heading(symbol, size="4"),  # Valores numéricos para size
#             rx.spacer(),
#             rx.text(name, font_size="sm", color="gray.600"),
#             width="100%"
#         ),
#         on_click=lambda: BuscadorState.get_stock_info(symbol),
#         cursor="pointer",
#         _hover={"bg": "gray.100"},
#         margin_bottom="2",
#         padding="3"
#     )

# # Componente para mostrar información del stock
# def stock_info_card(stock_data):
#     return rx.vstack(
#         rx.hstack(
#             rx.heading(stock_data.get("name", ""), size="4"),  # Valores numéricos para size
#             rx.spacer(),
#             rx.heading(f"${stock_data.get('price', 0):.2f}", size="4"),  # Valores numéricos para size
#             width="100%"
#         ),
#         rx.hstack(
#             rx.text(stock_data.get("symbol", ""), color="gray.600"),
#             rx.spacer(),
#             rx.badge(
#                 f"{stock_data.get('change', 0):.2f}%",
#                 color_scheme="green" if stock_data.get('change', 0) >= 0 else "red",
#             ),
#             width="100%"
#         ),
#         rx.divider(),
#         rx.grid(
#             rx.grid_item(
#                 rx.vstack(
#                     rx.text("Cap. de Mercado", font_weight="bold"),
#                     rx.text(f"${stock_data.get('market_cap', 0)/1000000000:.2f}B"),
#                     align_items="center"
#                 ),
#                 col_span=1
#             ),
#             rx.grid_item(
#                 rx.vstack(
#                     rx.text("Volumen", font_weight="bold"),
#                     rx.text(f"{stock_data.get('volume', 0)/1000000:.1f}M"),
#                     align_items="center"
#                 ),
#                 col_span=1
#             ),
#             rx.grid_item(
#                 rx.vstack(
#                     rx.text("P/E Ratio", font_weight="bold"),
#                     rx.text(f"{stock_data.get('pe_ratio', 0):.2f}"),
#                     align_items="center"
#                 ),
#                 col_span=1
#             ),
#             rx.grid_item(
#                 rx.vstack(
#                     rx.text("Div. Yield", font_weight="bold"),
#                     rx.text(f"{stock_data.get('dividend_yield', 0)*100:.2f}%"),
#                     align_items="center"
#                 ),
#                 col_span=1
#             ),
#             template_columns="repeat(4, 1fr)",
#             gap=4,
#             width="100%",
#             margin_y="4"
#         ),
#         rx.divider(),
#         rx.text(stock_data.get("description", ""), text_align="justify"),
#         align_items="start",
#         width="100%",
#         spacing="4",
#         padding="4",
#         bg="white",
#         border_radius="lg",
#         shadow="md"
#     )

# # Componente para la página de búsqueda
# @require_auth
# def buscador_page() -> rx.Component:
#     return layout(
#         rx.vstack(
#             # Barra de búsqueda
#             rx.hstack(
#                 rx.input(
#                     placeholder="Buscar por símbolo o nombre de la empresa...",
#                     value=BuscadorState.search_term,
#                     on_change=BuscadorState.set_search_term,
#                     width="80%",
#                     padding="3",
#                     border_radius="md",
#                 ),
#                 rx.button(
#                     "Buscar",
#                     on_click=BuscadorState.search_stocks,
#                     color_scheme="blue",
#                 ),
#                 width="100%",
#                 padding="4",
#             ),
            
#             # Mensaje de error
#             rx.cond(
#                 BuscadorState.error_message != "",
#                 rx.box(
#                     rx.hstack(
#                         rx.icon(tag="alert_triangle", color="red.500"),  # Icono válido
#                         rx.text(BuscadorState.error_message, color="red.500"),
#                         spacing="2",
#                         padding="3",
#                         border="1px solid",
#                         border_color="red.300",
#                         border_radius="md",
#                         background="red.50",
#                         width="100%",
#                         margin_bottom="4"
#                     )
#                 )
#             ),
            
#             # Resultados de búsqueda o detalles del stock
#             rx.cond(
#                 BuscadorState.selected_stock == "",
#                 # Mostrar resultados de búsqueda
#                 rx.cond(
#                     BuscadorState.search_results.length() > 0,  # Usar .length() en lugar de len()
#                     rx.vstack(
#                         rx.heading("Resultados", size="4", margin_bottom="4"),
#                         rx.vstack(
#                             *[
#                                 stock_result_card(stock["symbol"], stock["name"])
#                                 for stock in BuscadorState.search_results
#                             ],
#                             width="100%",
#                         ),
#                         width="100%",
#                         align_items="start",
#                         padding="4",
#                     ),
#                     rx.cond(
#                         BuscadorState.search_term != "",
#                         rx.text("No se encontraron resultados.", padding="4"),
#                         rx.text("Ingrese un término de búsqueda para comenzar.", padding="4")
#                     )
#                 ),
#                 # Mostrar detalles del stock
#                 rx.vstack(
#                     rx.hstack(
#                         rx.button(
#                             "← Volver a la búsqueda",
#                             on_click=lambda: setattr(BuscadorState, "selected_stock", ""),
#                             variant="ghost",
#                             size="sm",
#                         ),
#                         rx.spacer(),
#                         width="100%",
#                         margin_bottom="4"
#                     ),
#                     rx.cond(
#                         BuscadorState.stock_data.length() > 0,  # Usar .length() en lugar de len()
#                         rx.vstack(
#                             stock_info_card(BuscadorState.stock_data),
#                             # Usando una función para generar el gráfico que recibe los datos directamente
#                             rx.cond(
#                                 BuscadorState.chart_data["x"].length() > 0,  # Usar .length() en lugar de len()
#                                 generate_line_chart(BuscadorState.chart_data),
#                                 rx.text("No hay datos históricos disponibles.")
#                             ),
#                             width="100%",
#                             align_items="start",
#                             spacing="6"
#                         ),
#                         rx.spinner(size="xl")
#                     ),
#                     width="100%",
#                     align_items="start",
#                     padding="4",
#                 )
#             ),
#             width="100%",
#             max_width="1200px",
#             margin="0 auto",
#             padding="4",
#             min_height="80vh",
#             align_items="start",
#         )
#     )

# # Función para la página de detalles de stock (redireccionamiento)
# def stock_detail_page(symbol: str) -> rx.Component:
#     return rx.fragment(
#         rx.script(f"BuscadorState.get_stock_info('{symbol}')")
#     )

# # Página de búsqueda
# buscador = rx.page(
#     route="/buscador",
#     title="TradeSim - Buscador de Acciones",
#     on_load=AuthState.on_load
# )(buscador_page)

# # Ruta para detalles de acción específica
# stock = rx.page(
#     route="/stock/[symbol]",
#     title="TradeSim - Detalles de Acción",
#     on_load=AuthState.on_load
# )(stock_detail_page)

import reflex as rx
import yfinance as yf
from typing import List, Dict, Any, Union
from ..components.layout import layout

# Helpers para crear elementos HTML arbitrarios usando rx.box con el parámetro as_
def thead(*children, **props) -> rx.Component:
    return rx.box(*children, as_="thead", **props)

def tbody(*children, **props) -> rx.Component:
    return rx.box(*children, as_="tbody", **props)

class StockInfo(rx.Base):
    """Tipo para info básica de una acción."""
    symbol: str
    name: str
    sector: str

class StockDetail(rx.Base):
    """Tipo para detalles completos de una acción."""
    symbol: str
    name: str = "Unknown"
    sector: str = "N/A"
    industry: str = "N/A"
    country: str = "N/A"
    website: str = "N/A"
    current_price: float = 0.0
    open_price: float = 0.0
    high: float = 0.0
    low: float = 0.0
    volume: int = 0
    market_cap: Union[float, str] = "N/A"
    pe_ratio: Union[float, str] = "N/A"
    eps: Union[float, str] = "N/A"
    dividend_yield: Union[float, str] = "N/A"
    daily_change: float = 0.0
    description: str = "No hay descripción disponible"
    error: str = ""

class BuscadorState(rx.State):
    """Estado del buscador de acciones."""
    search_query: str = ""
    search_results: List[StockInfo] = []
    selected_stock: Union[StockDetail, Dict[str, Any]] = {}
    
    def search_stocks(self):
        """Busca acciones basadas en la consulta."""
        if len(self.search_query) < 2:
            self.search_results = []
            return
            
        try:
            # Usamos yfinance para buscar símbolos que coincidan con la consulta
            tickers = yf.Tickers(self.search_query)
            data: List[StockInfo] = []
            
            # Limitamos a 10 resultados para simplificar
            count = 0
            for symbol in tickers.tickers:
                if count >= 10:
                    break
                    
                info = tickers.tickers[symbol].info
                if 'shortName' in info:
                    data.append(StockInfo(
                        symbol=symbol,
                        name=info.get('shortName', 'Unknown'),
                        sector=info.get('sector', 'N/A'),
                    ))
                    count += 1
                    
            self.search_results = data
        except Exception as e:
            self.search_results = []
            print(f"Error al buscar acciones: {e}")
    
    def get_stock_details(self, symbol: str):
        """Obtiene detalles de una acción específica."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            history = ticker.history(period="1mo")
            
            # Creamos un objeto de detalles básicos
            stock_detail = StockDetail(
                symbol=symbol,
                name=info.get('shortName', 'Unknown'),
                sector=info.get('sector', 'N/A'),
                industry=info.get('industry', 'N/A'),
                country=info.get('country', 'N/A'),
                website=info.get('website', 'N/A'),
                market_cap=info.get('marketCap', 'N/A'),
                pe_ratio=info.get('trailingPE', 'N/A'),
                eps=info.get('trailingEps', 'N/A'),
                dividend_yield=info.get('dividendYield', 'N/A'),
                description=info.get('longBusinessSummary', 'No hay descripción disponible'),
            )
            
            # Calculamos indicadores basados en los datos históricos
            if not history.empty:
                stock_detail.current_price = float(history['Close'].iloc[-1])
                stock_detail.open_price = float(history['Open'].iloc[-1])
                stock_detail.high = float(history['High'].iloc[-1])
                stock_detail.low = float(history['Low'].iloc[-1])
                stock_detail.volume = int(history['Volume'].iloc[-1])
                
                # Calculamos el cambio porcentual diario
                if len(history) > 1:
                    prev_close = history['Close'].iloc[-2]
                    stock_detail.daily_change = ((stock_detail.current_price - prev_close) / prev_close) * 100
            else:
                stock_detail.error = "No se pudieron obtener datos históricos"
            
            # Convertimos a diccionario para evitar problemas de serialización
            self.selected_stock = stock_detail.dict()
        except Exception as e:
            self.selected_stock = StockDetail(
                symbol=symbol,
                error=f"Error al obtener detalles: {str(e)}"
            ).dict()
            print(f"Error al obtener detalles de {symbol}: {e}")
    
    def clear_selected_stock(self):
        """Limpia el stock seleccionado para volver a la búsqueda."""
        self.selected_stock = {}

def search_bar() -> rx.Component:
    """Componente de barra de búsqueda."""
    return rx.vstack(
        rx.heading("Buscador de Acciones", size="5"),
        rx.hstack(
            rx.input(
                placeholder="Buscar acciones (ej: AAPL, MSFT, AMZN...)",
                value=BuscadorState.search_query,
                on_change=BuscadorState.set_search_query,
                width="100%",
                size="3",  # Valor permitido: "1", "2" o "3"
            ),
            rx.button("Buscar", on_click=BuscadorState.search_stocks),
        ),
        width="100%",
        padding="1em",
    )

def search_results() -> rx.Component:
    """Componente de resultados de búsqueda."""
    return rx.cond(
        len(BuscadorState.search_results) > 0,
        rx.vstack(
            rx.heading("Resultados de búsqueda", size="5"),
            rx.table(
                thead(
                    rx.box(
                        rx.box("Símbolo", as_="th"),
                        rx.box("Nombre", as_="th"),
                        rx.box("Sector", as_="th"),
                        as_="tr",
                    )
                ),
                tbody(
                    rx.foreach(
                        BuscadorState.search_results,
                        lambda item, idx: rx.box(
                            rx.box(item.symbol, as_="td"),
                            rx.box(item.name, as_="td"),
                            rx.box(item.sector, as_="td"),
                            on_click=lambda: BuscadorState.get_stock_details(item.symbol),
                            cursor="pointer",
                            _hover={"background_color": "lightblue"},
                            as_="tr",
                        )
                    )
                ),
                width="100%",
            ),
            width="100%",
            padding="1em",
        ),
        rx.text(
            "No hay resultados. Intenta buscar con un símbolo válido (ej: AAPL para Apple)."
        ) if BuscadorState.search_query else rx.text(""),
    )

def stock_details() -> rx.Component:
    """Componente de detalles de la acción."""
    return rx.cond(
        BuscadorState.selected_stock != {},
        rx.vstack(
            rx.hstack(
                rx.heading(
                    f"{BuscadorState.selected_stock.get('name', '')} ({BuscadorState.selected_stock.get('symbol', '')})",
                    size="5",
                ),
                rx.spacer(),
                rx.button("Volver", on_click=BuscadorState.clear_selected_stock),
                width="100%",
            ),
            rx.cond(
                BuscadorState.selected_stock.get("error", "") != "",
                rx.text(f"Error: {BuscadorState.selected_stock.get('error')}"),
                rx.vstack(
                    rx.hstack(
                        rx.vstack(
                            rx.heading("Precio actual", size="6"),
                            rx.hstack(
                                rx.heading(
                                    f"${BuscadorState.selected_stock.get('current_price', 0):.2f}",
                                    size="5",
                                ),
                                rx.text(
                                    f"{BuscadorState.selected_stock.get('daily_change', 0):.2f}%",
                                    color="green" if BuscadorState.selected_stock.get('daily_change', 0) >= 0 else "red",
                                    font_weight="bold",
                                ),
                            ),
                            align_items="flex-start",
                            width="50%",
                        ),
                        rx.vstack(
                            rx.grid(
                                rx.grid_item(
                                    rx.text("Apertura:", font_weight="bold"),
                                    rx.text(f"${BuscadorState.selected_stock.get('open_price', 0):.2f}"),
                                ),
                                rx.grid_item(
                                    rx.text("Máximo:", font_weight="bold"),
                                    rx.text(f"${BuscadorState.selected_stock.get('high', 0):.2f}"),
                                ),
                                rx.grid_item(
                                    rx.text("Mínimo:", font_weight="bold"),
                                    rx.text(f"${BuscadorState.selected_stock.get('low', 0):.2f}"),
                                ),
                                rx.grid_item(
                                    rx.text("Volumen:", font_weight="bold"),
                                    rx.text(f"{BuscadorState.selected_stock.get('volume', 0):,}"),
                                ),
                                template_columns="repeat(2, 1fr)",
                                gap="4",
                            ),
                            align_items="flex-start",
                            width="50%",
                        ),
                        width="100%",
                    ),
                    rx.divider(),
                    rx.heading("Información de la compañía", size="6"),
                    rx.grid(
                        rx.grid_item(
                            rx.text("Sector:", font_weight="bold"),
                            rx.text(BuscadorState.selected_stock.get('sector', 'N/A')),
                        ),
                        rx.grid_item(
                            rx.text("Industria:", font_weight="bold"),
                            rx.text(BuscadorState.selected_stock.get('industry', 'N/A')),
                        ),
                        rx.grid_item(
                            rx.text("País:", font_weight="bold"),
                            rx.text(BuscadorState.selected_stock.get('country', 'N/A')),
                        ),
                        rx.grid_item(
                            rx.text("Capitalización:", font_weight="bold"),
                            rx.text(f"${BuscadorState.selected_stock.get('market_cap', 0):,}" 
                                   if BuscadorState.selected_stock.get('market_cap') not in ['N/A', None] else "N/A"),
                        ),
                        rx.grid_item(
                            rx.text("P/E Ratio:", font_weight="bold"),
                            rx.text(f"{BuscadorState.selected_stock.get('pe_ratio', 'N/A')}"),
                        ),
                        rx.grid_item(
                            rx.text("EPS:", font_weight="bold"),
                            rx.text(f"${BuscadorState.selected_stock.get('eps', 'N/A')}" 
                                  if BuscadorState.selected_stock.get('eps') not in ['N/A', None] else "N/A"),
                        ),
                        rx.grid_item(
                            rx.text("Rendimiento de dividendo:", font_weight="bold"),
                            rx.text(f"{float(BuscadorState.selected_stock.get('dividend_yield', 0)) * 100:.2f}%" 
                                   if BuscadorState.selected_stock.get('dividend_yield') not in ['N/A', None] else "N/A"),
                            col_span=2,
                        ),
                        rx.grid_item(
                            rx.text("Sitio web:", font_weight="bold"),
                            rx.link(BuscadorState.selected_stock.get('website', 'N/A'), 
                                   href=BuscadorState.selected_stock.get('website', '#'),
                                   is_external=True),
                            col_span=2,
                        ),
                        template_columns="repeat(2, 1fr)",
                        gap="4",
                        width="100%",
                    ),
                    rx.divider(),
                    rx.heading("Descripción", size="6"),
                    rx.text(BuscadorState.selected_stock.get('description', 'No hay descripción disponible')),
                    width="100%",
                    gap="4",
                ),
            ),
            width="100%",
            padding="1em",
            border_radius="md",
            border="1px solid #eaeaea",
        ),
        rx.text(""),
    )

def buscador_content() -> rx.Component:
    """Contenido principal de la página de buscador."""
    return rx.container(
        search_bar(),
        rx.cond(
            BuscadorState.selected_stock == {},
            search_results(),
            stock_details(),
        ),
        padding="2em",
        max_width="1200px",
    )

def buscador_page() -> rx.Component:
    """Página de buscador integrada con el layout existente."""
    return layout(
        rx.center(
            buscador_content(),
            width="100%"
        )
    )

# Definición de la ruta de la página
buscador = rx.page(
    route="/buscador",
    title="TradeSim - Buscador"
)(buscador_page)