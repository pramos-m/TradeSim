import requests
import reflex as rx
from datetime import datetime, timedelta
from typing import List, Optional

class NewsArticle(rx.Base):
    """Modelo de datos para una noticia."""
    title: str
    url: str
    publisher: str
    date: str
    summary: str
    image: str = ""  # URL de la imagen (si está disponible)

class NewsState(rx.State):
    """Estado para la página de noticias."""

    # Variables de estado
    processed_news: List[NewsArticle] = []
    is_loading: bool = False
    has_news: bool = False
    show_all_news: bool = False
    page: int = 1
    max_articles: int = 10
    selected_style: str = "panel"

    # Configuración de GNews API
    GNEWS_API_KEY = "f767bfe6df4f747e6b77c0178e8cc0d8" # Reemplaza con tu clave API si es necesario
    GNEWS_API_URL = "https://gnews.io/api/v4/search"
    SEARCH_QUERY = "bolsa acciones OR mercados financieros OR economía global" # Query más amplio

    @rx.event
    def change_style(self, style: str):
        """
        Cambia el estilo de visualización de las noticias.
        Es un event handler directo.
        """
        self.selected_style = style
        # No devuelve nada explícitamente

    @rx.var
    def featured_news(self) -> Optional[NewsArticle]:
        """Devuelve la primera noticia para destacar."""
        if self.processed_news:
            return self.processed_news[0]
        return None

    @rx.var
    def recent_news_list(self) -> List[NewsArticle]:
        """Devuelve las noticias recientes (2-5)."""
        if len(self.processed_news) > 1:
            # Asegura que no exceda el número de noticias disponibles
            end_index = min(5, len(self.processed_news))
            return self.processed_news[1:end_index]
        return []

    @rx.var
    def additional_news_list(self) -> List[NewsArticle]:
        """Devuelve noticias adicionales (a partir de la 6ª)."""
        if len(self.processed_news) > 5:
            return self.processed_news[5:]
        return []

    @rx.var
    def has_more_than_one_news(self) -> bool:
        """Indica si hay más de una noticia."""
        return len(self.processed_news) > 1

    @rx.var
    def has_more_than_five_news(self) -> bool:
        """Indica si hay más de 5 noticias disponibles."""
        return len(self.processed_news) > 5

    @rx.var
    def news_display_text(self) -> str:
        """Texto para mostrar sobre las noticias."""
        news_count = len(self.processed_news)
        if news_count > 0:
            return f"Mostrando {news_count} noticias recientes sobre mercados financieros"
        elif self.is_loading:
             return "Cargando noticias..."
        else:
            return "No hay noticias disponibles."

    @rx.var
    def can_load_more(self) -> bool:
        """Indica si se pueden cargar más noticias."""
        # Solo permitir cargar más si tenemos alguna noticia y no estamos ya cargando
        return len(self.processed_news) > 0 and not self.is_loading

    @rx.event
    def get_news(self):
        """Obtiene noticias desde GNews API."""
        if self.is_loading: # Evitar cargas múltiples simultáneas
            return
        self.is_loading = True
        self.has_news = False
        self.processed_news = []
        self.page = 1

        try:
            params = {
                "q": self.SEARCH_QUERY,
                "token": self.GNEWS_API_KEY,
                "lang": "es",
                "country": "any",
                "max": self.max_articles,
                "sortby": "publishedAt",
                # "from": "30d", # Quitar 'from' puede dar más resultados recientes
            }
            print(f"Buscando noticias: '{self.SEARCH_QUERY}'")
            response = requests.get(self.GNEWS_API_URL, params=params)
            response.raise_for_status() # Lanza excepción si hay error HTTP
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
                            # Intenta parsear la fecha
                            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
                            date_str = date_obj.strftime("%d %b %Y, %H:%M")
                        except (ValueError, TypeError):
                            date_str = "Fecha desconocida" # Fallback si el formato es incorrecto

                        summary = article.get("description", "Sin descripción disponible.")
                        image = article.get("image", "") # URL de la imagen

                        news_article = NewsArticle(
                            title=title, url=url, publisher=publisher, date=date_str, summary=summary, image=image
                        )
                        processed_articles.append(news_article)
                    except Exception as e_inner:
                        print(f"Error procesando artículo individual: {e_inner}")

                if processed_articles:
                    self.processed_news = processed_articles
                    self.has_news = True
                    print(f"Se procesaron {len(processed_articles)} noticias.")
                else:
                    print("No se pudieron procesar artículos válidos. Usando fallback.")
                    self._create_fallback_news()
            else:
                print("La API no devolvió artículos. Usando fallback.")
                self._create_fallback_news()

        except requests.exceptions.RequestException as e_req:
            print(f"Error de red al obtener noticias: {e_req}")
            self._create_fallback_news()
        except Exception as e_outer:
            print(f"Error general al obtener noticias: {e_outer}")
            import traceback
            traceback.print_exc() # Imprime el traceback completo para depuración
            self._create_fallback_news()
        finally:
            self.is_loading = False

    @rx.event
    def load_more_news(self):
        """Carga más noticias (siguiente página)."""
        if not self.can_load_more or self.is_loading:
            return

        self.is_loading = True
        self.page += 1

        try:
            params = {
                "q": self.SEARCH_QUERY,
                "token": self.GNEWS_API_KEY,
                "lang": "es",
                "country": "any",
                "max": self.max_articles,
                "page": self.page,
                "sortby": "publishedAt",
                # "from": "30d",
            }
            print(f"Cargando más noticias (página {self.page})")
            response = requests.get(self.GNEWS_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])

            if articles:
                new_articles = []
                current_titles = {news.title for news in self.processed_news} # Para evitar duplicados

                for article in articles:
                    try:
                        title = article.get("title", "Sin título")
                        # Evita añadir noticias duplicadas por título
                        if title in current_titles:
                            continue

                        url = article.get("url", "#")
                        source = article.get("source", {})
                        publisher = source.get("name", "Fuente desconocida")
                        date_str = article.get("publishedAt", "")
                        try:
                            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
                            date_str = date_obj.strftime("%d %b %Y, %H:%M")
                        except (ValueError, TypeError):
                            date_str = "Fecha desconocida"

                        summary = article.get("description", "Sin descripción disponible.")
                        image = article.get("image", "")

                        news_article = NewsArticle(
                            title=title, url=url, publisher=publisher, date=date_str, summary=summary, image=image
                        )
                        new_articles.append(news_article)
                        current_titles.add(title) # Añade el título al set de control
                    except Exception as e_inner:
                        print(f"Error procesando artículo adicional: {e_inner}")

                if new_articles:
                    self.processed_news.extend(new_articles)
                    print(f"Se añadieron {len(new_articles)} noticias adicionales.")
                else:
                    print("No se encontraron más noticias nuevas en esta página.")
                    # Considera no añadir fallback aquí para evitar repeticiones si la API simplemente no tiene más páginas
            else:
                print("No hay más páginas de noticias disponibles desde la API.")
                # Considera no añadir fallback aquí

        except requests.exceptions.RequestException as e_req:
            print(f"Error de red al cargar más noticias: {e_req}")
            # Considera no añadir fallback aquí
        except Exception as e_outer:
            print(f"Error general al cargar más noticias: {e_outer}")
            import traceback
            traceback.print_exc()
            # Considera no añadir fallback aquí
        finally:
            self.is_loading = False

    def _create_fallback_news(self):
        """Crea noticias de respaldo si la API falla en la carga inicial."""
        print("Generando noticias de respaldo...")
        today = datetime.now()
        fallback_news = []
        for i in range(1, 8): # Genera 7 noticias de ejemplo
            past_date = today - timedelta(days=i)
            date_str = past_date.strftime("%d %b %Y, %H:%M")
            fallback_news.append(
                NewsArticle(
                    title=f"Noticia de Respaldo {i}: Evento Importante en Mercados",
                    url="#",
                    publisher="Fuente Simulada",
                    date=date_str,
                    summary=f"Este es un resumen de la noticia de respaldo número {i}. Describe un evento significativo que afecta a los mercados financieros globales y locales.",
                    image=f"/api/placeholder/400/{200 + i*10}" # Imagen placeholder diferente
                )
            )
        self.processed_news = fallback_news
        self.has_news = True
        self.is_loading = False # Asegura que is_loading se desactive

    def _add_more_fallback_news(self):
        """Añade más noticias de respaldo si 'load_more' falla (opcional)."""
        # Esta función podría ser innecesaria si prefieres no añadir más fallbacks
        print("Añadiendo noticias de respaldo adicionales...")
        start_index = len(self.processed_news) + 1
        today = datetime.now()
        new_fallback = []
        for i in range(start_index, start_index + 5): # Añade 5 más
            past_date = today - timedelta(days=i)
            date_str = past_date.strftime("%d %b %Y, %H:%M")
            news_item = NewsArticle(
                title=f"Noticia de Respaldo Adicional {i}",
                url="#",
                publisher="Fuente Simulada Extra",
                date=date_str,
                summary=f"Detalles adicionales sobre eventos del mercado en la noticia {i}.",
                image=f"/api/placeholder/400/{250 + i*5}"
            )
            # Evitar duplicados (aunque improbable con este método)
            if not any(existing.title == news_item.title for existing in self.processed_news):
                new_fallback.append(news_item)

        if new_fallback:
            self.processed_news.extend(new_fallback)
            print(f"Se añadieron {len(new_fallback)} noticias de respaldo adicionales.")
        self.is_loading = False # Asegura que is_loading se desactive

    @rx.event
    def toggle_show_all(self):
        """Alterna entre mostrar todas las noticias o solo las primeras (no usado actualmente)."""
        self.show_all_news = not self.show_all_news
    @rx.event
    def open_url(self, url: str):
        """Abre un enlace en una nueva ventana/pestaña."""
        print(f"Intentando abrir URL: {url}")
        # Validación básica de URL (simplificada)
        if isinstance(url, str) and url.startswith(("http://", "https://")):
             # *** CORRECCIÓ: Eliminar external=True ***
             return rx.redirect(url)
        else:
             print(f"URL inválida o no externa: '{url}'. No se redirige.")
             # Opcional: redirigir a una página de error o similar
             # return rx.redirect("/error") # Exemple
             return # No fer res si la URL no és vàlida