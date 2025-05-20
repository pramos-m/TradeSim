# <<<--- CODI COMPLET FINAL PER A news_state.py --- >>>
import requests
import reflex as rx
from datetime import datetime, timedelta, timezone
from typing import List, Optional
import traceback # Per a millor debugging
import os
import asyncio
import logging

# Configuración del logger
logger = logging.getLogger(__name__)

# --- Model de Dades ---
class NewsArticle(rx.Base):
    """Modelo de datos para una noticia."""
    title: str
    url: str
    publisher: str
    date: str
    summary: str
    image: str = ""

# --- Estat Principal ---
class NewsState(rx.State):
    """Estado para la página de noticias."""

    # --- Variables d'Estat ---
    processed_news: List[NewsArticle] = []
    is_loading: bool = False
    has_news: bool = False
    page: int = 1
    max_articles: int = 10  # Número màxim d'articles per càrrega
    selected_style: str = "panel" # Controla la vista: "panel" o "publicaciones"

    # --- Configuració de GNews API ---
    GNEWS_API_KEY = "f767bfe6df4f747e6b77c0178e8cc0d8" # La teva clau API
    GNEWS_API_URL = "https://gnews.io/api/v4/search"
    # Query que va funcionar per obtenir 10 notícies
    SEARCH_QUERY = "bolsa acciones"

    # --- Variables Computades (Vars) ---
    @rx.var
    def featured_news(self) -> Optional[NewsArticle]:
        """Devuelve la primera noticia para destacar."""
        if self.processed_news:
            return self.processed_news[0]
        return None

    @rx.var
    def recent_news_list(self) -> List[NewsArticle]:
        """Devuelve las noticias recents (índexs 1, 2, 3) per al panell."""
        if len(self.processed_news) > 1:
            end_index = min(4, len(self.processed_news))
            return self.processed_news[1:end_index]
        return []

    @rx.var
    def additional_news_list(self) -> List[NewsArticle]:
        """Devuelve noticias adicionales (a partir de la 5ª, índex 4)."""
        if len(self.processed_news) > 4:
            return self.processed_news[4:]
        return []

    @rx.var
    def has_more_than_one_news(self) -> bool:
        """Indica si hay más de una noticia."""
        return len(self.processed_news) > 1

    @rx.var
    def has_more_than_five_news(self) -> bool: # Comprova si hi ha més de 4
        """Indica si hay más de 4 noticias disponibles (per additional_news_list)."""
        return len(self.processed_news) > 4

    @rx.var
    def news_display_text(self) -> str:
        news_count = len(self.processed_news)
        if news_count > 0:
            return f"Mostrando {news_count} noticias recientes sobre mercados financieros"
        elif self.is_loading:
             return "Cargando noticias..."
        else:
            return "No hay noticias disponibles."

    @rx.var
    def can_load_more(self) -> bool:
        """Indica si es pot intentar carregar més (hi ha notícies i no està carregant)."""
        # Aquesta lògica és simple, no garanteix que l'API tingui més pàgines.
        return len(self.processed_news) > 0 and not self.is_loading

    # --- Gestors d'Events (Event Handlers) ---
    @rx.event
    def change_style(self, style: str):
        """Canvia l'estil de visualització (panel / publicaciones)."""
        self.selected_style = style

    @rx.event
    def open_url(self, url: str):
        """Abre un enlace externo (sense argument 'external')."""
        print(f"Intentando abrir URL: {url}")
        if isinstance(url, str) and url.startswith(("http://", "https://")):
             return rx.redirect(url)
        else:
             print(f"URL inválida o no externa: '{url}'. No se redirige.")
             return # No fer res si la URL no és vàlida

    # --- Lògica API ---
    @rx.event
    def get_news(self):
        """Obtiene la primera página de noticias desde GNews API."""
        if self.is_loading: return
        self.is_loading = True
        self.has_news = False
        self.processed_news = []
        self.page = 1
        try:
            params = {
                "q": self.SEARCH_QUERY, "token": self.GNEWS_API_KEY, "lang": "es",
                "country": "any", "max": self.max_articles, "sortby": "publishedAt",
                "from": "30d" # Buscar en els últims 30 dies
            }
            print(f"Buscando noticias (página 1): '{self.SEARCH_QUERY}', from=30d")
            response = requests.get(self.GNEWS_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])
            if articles:
                processed_articles = []
                for article in articles:
                    try:
                        title = article.get("title", "Sin título")
                        url = article.get("url", "#")
                        source = article.get("source", {})
                        publisher = source.get("name", "Fuente desconocida")
                        date_str = article.get("publishedAt", "")
                        try:
                            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
                            date_str = date_obj.strftime("%d %b %Y, %H:%M")
                        except (ValueError, TypeError): date_str = "Fecha desconocida"
                        summary = article.get("description", "Sin descripción disponible.")
                        image = article.get("image", "")
                        news_article = NewsArticle(title=title, url=url, publisher=publisher, date=date_str, summary=summary, image=image)
                        processed_articles.append(news_article)
                    except Exception as e_inner: print(f"Error procesando artículo individual: {e_inner}")
                if processed_articles:
                    self.processed_news = processed_articles
                    self.has_news = True
                    print(f"Se procesaron {len(processed_articles)} noticias.")
                else: self._create_fallback_news()
            else: self._create_fallback_news()
        except requests.exceptions.RequestException as e_req: print(f"Error de red: {e_req}"); self._create_fallback_news()
        except Exception as e_outer: print(f"Error general: {e_outer}"); traceback.print_exc(); self._create_fallback_news()
        finally: self.is_loading = False

    @rx.event
    def load_more_news(self):
        """Carga más noticias (siguiente página)."""
        if not self.can_load_more or self.is_loading:
            print("No se puede cargar más o ya está cargando.")
            return
        self.is_loading = True
        self.page += 1
        try:
            params = {
                "q": self.SEARCH_QUERY, "token": self.GNEWS_API_KEY, "lang": "es",
                "country": "any", "max": self.max_articles, "page": self.page,
                "sortby": "publishedAt", "from": "30d"
            }
            print(f"Cargando más noticias (página {self.page})")
            response = requests.get(self.GNEWS_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])
            if articles:
                new_articles = []
                current_titles = {news.title for news in self.processed_news}
                for article in articles:
                    try:
                        title = article.get("title", "Sin título")
                        if title in current_titles: continue
                        url = article.get("url", "#")
                        source = article.get("source", {})
                        publisher = source.get("name", "Fuente desconocida")
                        date_str = article.get("publishedAt", "")
                        try:
                            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
                            date_str = date_obj.strftime("%d %b %Y, %H:%M")
                        except (ValueError, TypeError): date_str = "Fecha desconocida"
                        summary = article.get("description", "Sin descripción disponible.")
                        image = article.get("image", "")
                        news_article = NewsArticle(title=title, url=url, publisher=publisher, date=date_str, summary=summary, image=image)
                        new_articles.append(news_article)
                        current_titles.add(title)
                    except Exception as e_inner: print(f"Error procesando artículo adicional: {e_inner}")
                if new_articles:
                    self.processed_news.extend(new_articles); print(f"Se añadieron {len(new_articles)} noticias.")
                else:
                    print("No se encontraron más noticias nuevas en esta página.")
                    # Opcionalment pots cridar a _add_more_fallback_news() aquí
            else:
                print("No hay más páginas de noticias disponibles desde la API.")
                # Opcionalment pots cridar a _add_more_fallback_news() aquí
        except requests.exceptions.RequestException as e_req: print(f"Error de red al cargar más: {e_req}")
        except Exception as e_outer: print(f"Error general al cargar más: {e_outer}"); traceback.print_exc()
        finally: self.is_loading = False

    # --- Mètodes Privats de Fallback ---
    def _create_fallback_news(self):
        """Crea noticias de respaldo si la API falla en la carga inicial."""
        print("Generando noticias de respaldo...")
        today = datetime.now()
        fallback_news = []
        titles = [
            "El Ibex 35 cierra la semana con alzas", "La inflación muestra signos de moderación",
            "Wall Street alcanza nuevos máximos", "Materias primas recuperan terreno",
            "Inversores aumentan exposición a riesgo", "Criptomonedas recuperan terreno",
            "Sector inmobiliario enfrenta desafíos"
        ]
        publishers = ["Expansión", "El Economista", "Cinco Días", "La Vanguardia", "El País", "Expansión", "Cinco Días"]
        for i in range(min(len(titles), 7)): # Genera fins a 7 notícies
            past_date = today - timedelta(days=i+1)
            date_str = past_date.strftime("%d %b %Y, %H:%M")
            fallback_news.append(
                NewsArticle(
                    title=titles[i], url="#fallback", publisher=publishers[i], date=date_str,
                    summary=f"Este es un resumen de la noticia de respaldo número {i+1} sobre {titles[i].lower()}.",
                    image=f"/api/placeholder/400/{200 + i*10}?text=Fallback+{i+1}"
                )
            )
        self.processed_news = fallback_news
        self.has_news = True
        self.is_loading = False


    def _add_more_fallback_news(self):
        """Añade más noticias de respaldo si 'load_more' falla."""
        print("Añadiendo noticias de respaldo adicionales...")
        start_index = len(self.processed_news) + 1
        today = datetime.now()
        new_fallback = []
        titles = [
            "Bancos centrales analizan impacto fintech", "Oro alcanza nuevo récord histórico",
            "Energías renovables atraen inversiones récord", "Nuevas regulaciones de sostenibilidad impactan",
            "Sector tecnológico lidera fusiones y adquisiciones"
        ]
        publishers = ["El Economista", "Expansión", "Cinco Días", "La Vanguardia", "El País"]
        for i in range(min(len(titles), 5)): # Afegeix fins a 5 més
            current_index = start_index + i
            past_date = today - timedelta(days=current_index)
            date_str = past_date.strftime("%d %b %Y, %H:%M")
            news_item = NewsArticle(
                title=titles[i], url="#fallback_more", publisher=publishers[i], date=date_str,
                summary=f"Detalles adicionales sobre {titles[i].lower()} en la noticia de respaldo {current_index}.",
                image=f"/api/placeholder/400/{250 + i*5}?text=Fallback+{current_index}"
            )
            if not any(existing.title == news_item.title for existing in self.processed_news):
                new_fallback.append(news_item)
        if new_fallback:
            self.processed_news.extend(new_fallback)
            print(f"Se añadieron {len(new_fallback)} noticias de respaldo adicionales.")
        self.is_loading = False