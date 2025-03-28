import reflex as rx
import yfinance as yf
import requests
from typing import List, Dict, Any, Union
from ..components.layout import layout

# Increased timeout and error handling
yf.utils.CONNECTIONS_TIMEOUT = 120
yf.utils.ERRORS_TIMEOUT = 120

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

def get_ticker_info(symbol):
    """Método mejorado para obtener información de un ticker"""
    try:
        # Usar un host de Yahoo Finance más estable
        ticker = yf.Ticker(symbol, session=requests.Session())
        
        # Verificar si la información básica está disponible
        info = ticker.info
        if not info or 'shortName' not in info:
            print(f"No se encontró información para: {symbol}")
            return None
        
        return ticker
    except Exception as e:
        print(f"Error al obtener información para {symbol}: {e}")
        return None

class BuscadorState(rx.State):
    """Estado del buscador de acciones."""
    search_query: str = ""
    search_results: List[StockInfo] = []
    selected_stock: Dict[str, Any] = {}
    daily_change_value: float = 0.0
    error_message: str = ""

    def search_stocks(self):
        """Busca acciones basadas en la consulta."""
        if len(self.search_query) < 2:
            self.search_results = []
            self.error_message = ""
            return

        try:
            # Manejar múltiples símbolos separados por coma
            search_symbols = [sym.strip().upper() for sym in self.search_query.split(',')]
            data: List[StockInfo] = []

            for symbol in search_symbols:
                try:
                    # Intentar obtener información del ticker
                    ticker = get_ticker_info(symbol)
                    
                    if ticker is None:
                        continue

                    info = ticker.info

                    # Agregar la información de la acción a los resultados
                    data.append(StockInfo(
                        symbol=symbol,
                        name=info.get('shortName', 'Unknown'),
                        sector=info.get('sector', 'N/A'),
                    ))
                except Exception as e:
                    print(f"Error procesando {symbol}: {e}")

            # Actualizar los resultados de búsqueda
            self.search_results = data
            self.error_message = "No se encontraron resultados" if not data else ""

        except Exception as e:
            self.search_results = []
            self.error_message = f"Error al buscar acciones: {e}"
            print(f"Error al buscar acciones: {e}")

    def get_stock_details(self, symbol: str):
        """Obtiene detalles de una acción específica."""
        try:
            # Usar la función mejorada de obtención de ticker
            ticker = get_ticker_info(symbol)
            
            if ticker is None:
                self.selected_stock = {}
                self.error_message = f"No se pudo obtener información para: {symbol}"
                return

            info = ticker.info
            
            # Intentar obtener datos históricos con múltiples intentos
            try:
                history = ticker.history(period="3mo")
                if history.empty:
                    history = ticker.history(period="1mo")
            except Exception:
                try:
                    history = ticker.history(period="1mo")
                except Exception:
                    history = None

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
            
            if history is not None and not history.empty:
                stock_detail.current_price = round(float(history['Close'].iloc[-1]), 2)
                stock_detail.open_price = round(float(history['Open'].iloc[-1]), 2)
                stock_detail.high = round(float(history['High'].iloc[-1]), 2)
                stock_detail.low = round(float(history['Low'].iloc[-1]), 2)
                stock_detail.volume = int(history['Volume'].iloc[-1])
                
                if len(history) > 1:
                    prev_close = history['Close'].iloc[-2]
                    daily_change = round(((stock_detail.current_price - prev_close) / prev_close) * 100, 2)
                    stock_detail.daily_change = daily_change
                    self.daily_change_value = daily_change
            else:
                stock_detail.error = "No se pudieron obtener datos históricos"
                self.daily_change_value = 0.0
            
            # Convertir a diccionario y manejar casos especiales
            self.selected_stock = {
                key: 'N/A' if value is None else value 
                for key, value in stock_detail.dict().items()
            }
            self.error_message = ""
        except Exception as e:
            self.selected_stock = StockDetail(
                symbol=symbol,
                error=f"Error al obtener detalles: {str(e)}"
            ).dict()
            self.daily_change_value = 0.0
            self.error_message = f"Error al obtener detalles de {symbol}: {e}"
            print(f"Error al obtener detalles de {symbol}: {e}")

    def clear_selected_stock(self):
        """Limpia el stock seleccionado para volver a la búsqueda."""
        self.selected_stock = {}
        self.daily_change_value = 0.0
        self.error_message = ""

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
                size="3",
            ),
            rx.button("Buscar", on_click=BuscadorState.search_stocks),
        ),
        rx.text(
            "Consejo: Puedes buscar múltiples acciones separadas por coma",
            color="gray.500",
            font_size="sm"
        ),
        width="100%",
        padding="1em",
    )

def search_results() -> rx.Component:
    """Componente de resultados de búsqueda."""
    return rx.cond(
        BuscadorState.search_results.length() > 0,
        rx.vstack(
            rx.heading("Resultados de búsqueda", size="5"),
            rx.box(
                rx.hstack(
                    rx.box("Símbolo", font_weight="bold", width="33%", padding="0.5em"),
                    rx.box("Nombre", font_weight="bold", width="33%", padding="0.5em"),
                    rx.box("Sector", font_weight="bold", width="33%", padding="0.5em"),
                    border_bottom="1px solid #eaeaea",
                    background_color="rgba(0,0,0,0.03)",
                    width="100%",
                ),
                rx.foreach(
                    BuscadorState.search_results,
                    lambda item: rx.hstack(
                        rx.box(item.symbol, width="33%", padding="0.5em"),
                        rx.box(item.name, width="33%", padding="0.5em"),
                        rx.box(item.sector, width="33%", padding="0.5em"),
                        border_bottom="1px solid #eaeaea",
                        on_click=lambda item=item: BuscadorState.get_stock_details(item.symbol),
                        cursor="pointer",
                        _hover={"background_color": "lightblue"},
                        width="100%",
                    )
                ),
                width="100%",
                border="1px solid #eaeaea",
                border_radius="md",
                overflow="hidden",
            ),
            width="100%",
            padding="1em",
        ),
        rx.cond(
            BuscadorState.search_query != "",
            rx.text("No hay resultados. Intenta buscar con un símbolo válido (ej: AAPL para Apple)."),
            rx.text("")
        ),
    )

def stock_details() -> rx.Component:
    """Componente de detalles de la acción."""
    return rx.cond(
        BuscadorState.selected_stock != {},
        rx.vstack(
            rx.hstack(
                rx.heading(
                    f"{BuscadorState.selected_stock.get('name', 'Desconocido')} ({BuscadorState.selected_stock.get('symbol', '')})",
                    size="5",
                ),
                rx.spacer(),
                rx.button("Volver", on_click=BuscadorState.clear_selected_stock),
                width="100%",
            ),
            rx.grid(
                rx.box(
                    rx.text("Precio actual:", font_weight="bold"),
                    rx.text(f"${BuscadorState.selected_stock.get('current_price', 0):,.2f}"),
                ),
                rx.box(
                    rx.text("Cambio diario:", font_weight="bold"),
                    rx.cond(
                        BuscadorState.daily_change_value >= 0,
                        rx.text(
                            f"{BuscadorState.daily_change_value:.2f}%",
                            color="green",
                        ),
                        rx.text(
                            f"{BuscadorState.daily_change_value:.2f}%",
                            color="red",
                        )
                    )
                ),
                rx.box(
                    rx.text("Apertura:", font_weight="bold"),
                    rx.text(f"${BuscadorState.selected_stock.get('open_price', 0):,.2f}"),
                ),
                rx.box(
                    rx.text("Máximo:", font_weight="bold"),
                    rx.text(f"${BuscadorState.selected_stock.get('high', 0):,.2f}"),
                ),
                rx.box(
                    rx.text("Mínimo:", font_weight="bold"),
                    rx.text(f"${BuscadorState.selected_stock.get('low', 0):,.2f}"),
                ),
                rx.box(
                    rx.text("Volumen:", font_weight="bold"),
                    rx.text(f"{BuscadorState.selected_stock.get('volume', 0):,}"),
                ),
                rx.box(
                    rx.text("Sector:", font_weight="bold"),
                    rx.text(BuscadorState.selected_stock.get('sector', 'N/A')),
                ),
                rx.box(
                    rx.text("Industria:", font_weight="bold"),
                    rx.text(BuscadorState.selected_stock.get('industry', 'N/A')),
                ),
                rx.box(
                    rx.text("País:", font_weight="bold"),
                    rx.text(BuscadorState.selected_stock.get('country', 'N/A')),
                ),
                rx.box(
                    rx.text("Capitalización:", font_weight="bold"),
                    rx.text(f"${BuscadorState.selected_stock.get('market_cap', 'N/A')}"),
                ),
                rx.box(
                    rx.text("P/E Ratio:", font_weight="bold"),
                    rx.text(f"{BuscadorState.selected_stock.get('pe_ratio', 'N/A')}"),
                ),
                rx.box(
                    rx.text("EPS:", font_weight="bold"),
                    rx.text(f"${BuscadorState.selected_stock.get('eps', 'N/A')}"),
                ),
                rx.box(
                    rx.text("Rendimiento de dividendos:", font_weight="bold"),
                    rx.text(f"{BuscadorState.selected_stock.get('dividend_yield', 'N/A')}%"),
                ),
                template_columns="repeat(2, 1fr)",
                gap="4",
                width="100%",
            ),
            rx.divider(),
            rx.heading("Descripción", size="6"),
            rx.text(BuscadorState.selected_stock.get('description', 'No hay descripción disponible')),
            width="100%",
            padding="1em",
        ),
        rx.text("Selecciona una acción para ver los detalles."),
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