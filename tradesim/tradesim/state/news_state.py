import reflex as rx
import yfinance as yf
import asyncio
from datetime import datetime
from typing import List, Dict, Any

class NewsState(rx.State):
    """Estado para la página de noticias."""
    
    # Variables de estado
    selected_ticker: str = "AAPL"
    custom_ticker: str = ""
    news: List[Dict[str, Any]] = []
    processed_news: List[Dict[str, Any]] = []  # Noticias preprocesadas para la UI
    is_loading: bool = False
    has_news: bool = False
    show_all_news: bool = False
    
    # Lista de empresas populares para el selector
    default_tickers: List[str] = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", 
        "TSLA", "NVDA", "PYPL", "NFLX", "DIS"
    ]
    
    # Métodos para variables calculadas
    @rx.var
    def displayed_news(self) -> List[Dict[str, Any]]:
        """Devuelve las noticias que se deben mostrar según el estado actual."""
        if self.show_all_news:
            return self.processed_news
        else:
            return self.processed_news[:5] if len(self.processed_news) > 5 else self.processed_news
    
    @rx.var
    def news_count(self) -> int:
        """Devuelve el número de noticias disponibles."""
        return len(self.processed_news)
    
    @rx.var
    def has_more_than_five_news(self) -> bool:
        """Indica si hay más de 5 noticias disponibles."""
        return len(self.processed_news) > 5
    
    @rx.var
    def news_display_text(self) -> str:
        """Texto para mostrar sobre las noticias."""
        if not self.has_news:
            return ""
        
        news_count = len(self.processed_news)
        
        if news_count > 5:
            if self.show_all_news:
                return f"Mostrando todas las {news_count} noticias para {self.selected_ticker}"
            else:
                return f"Mostrando 5 de {news_count} noticias para {self.selected_ticker}"
        else:
            return f"Mostrando {news_count} noticias para {self.selected_ticker}"
    
    # Métodos para procesar datos
    def _process_news(self, raw_news: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Procesa los datos de noticias para que sean seguros para la UI."""
        processed = []
        
        for article in raw_news:
            # Crear un diccionario con valores por defecto
            processed_article = {
                "title": "Sin título",
                "publisher": "Fuente desconocida",
                "link": "#",
                "formatted_date": "Fecha desconocida",
                "summary": "",
                "summary_display": "",
                "thumbnail_url": None
            }
            
            # Actualizar con valores reales si existen
            if "title" in article:
                processed_article["title"] = article["title"]
            
            if "publisher" in article:
                processed_article["publisher"] = article["publisher"]
            
            if "link" in article:
                processed_article["link"] = article["link"]
            
            # Procesar la fecha
            if "providerPublishTime" in article:
                try:
                    dt = datetime.fromtimestamp(article["providerPublishTime"])
                    processed_article["formatted_date"] = dt.strftime("%d %b %Y, %H:%M")
                except:
                    pass
            
            # Procesar el resumen
            if "summary" in article:
                summary = article["summary"]
                processed_article["summary"] = summary
                if len(summary) > 150:
                    processed_article["summary_display"] = summary[:150] + "..."
                else:
                    processed_article["summary_display"] = summary
            
            # Procesar la miniatura
            if "thumbnail" in article and article["thumbnail"] and "resolutions" in article["thumbnail"]:
                try:
                    processed_article["thumbnail_url"] = article["thumbnail"]["resolutions"][0]["url"]
                except:
                    pass
            
            processed.append(processed_article)
        
        return processed
    
    # Eventos para la UI
    @rx.event
    async def set_ticker(self, ticker: str):
        """Establece el ticker seleccionado y obtiene las noticias."""
        self.selected_ticker = ticker
        await self.get_news()
    
    def set_custom_ticker(self, ticker: str):
        """Establece el ticker personalizado."""
        self.custom_ticker = ticker
    
    @rx.event
    async def search_custom_ticker(self):
        """Busca noticias para el ticker personalizado."""
        if self.custom_ticker:
            self.selected_ticker = self.custom_ticker.upper()
            await self.get_news()
    
    @rx.event
    async def get_news(self):
        """Obtiene noticias para el ticker seleccionado."""
        self.is_loading = True
        self.has_news = False
        self.news = []
        self.processed_news = []
        yield
        
        try:
            # Usar asyncio para no bloquear la interfaz
            def fetch_news():
                try:
                    stock = yf.Ticker(self.selected_ticker)
                    return stock.news
                except Exception as e:
                    print(f"Error fetching news: {e}")
                    return []
            
            # Ejecutar la obtención de noticias en un hilo separado
            loop = asyncio.get_event_loop()
            news = await loop.run_in_executor(None, fetch_news)
            
            if news and len(news) > 0:
                self.news = news
                self.processed_news = self._process_news(news)
                self.has_news = True
            else:
                self.has_news = False
        except Exception as e:
            print(f"Error al obtener noticias: {e}")
            self.has_news = False
        finally:
            self.is_loading = False
    
    @rx.event
    async def toggle_show_all(self):
        """Alterna entre mostrar todas las noticias o solo las 5 primeras."""
        self.show_all_news = not self.show_all_news
    
    @rx.event
    async def on_load(self):
        """Carga las noticias cuando se abre la página."""
        await self.get_news()