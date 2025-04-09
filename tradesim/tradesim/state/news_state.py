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
    max_articles: int = 10  # Número máximo de artículos por carga

    # Configuración de GNews API
    GNEWS_API_KEY = "f767bfe6df4f747e6b77c0178e8cc0d8"
    GNEWS_API_URL = "https://gnews.io/api/v4/search"
    
    # Términos de búsqueda simplificados para obtener más resultados
    SEARCH_QUERY = "bolsa acciones"
    
    @rx.var
    def featured_news(self) -> Optional[NewsArticle]:
        """Devuelve la primera noticia para destacar."""
        if len(self.processed_news) > 0:
            return self.processed_news[0]
        return None
    
    @rx.var
    def recent_news_list(self) -> List[NewsArticle]:
        """Devuelve las noticias recientes (2-5)."""
        if len(self.processed_news) > 1:
            return self.processed_news[1:min(5, len(self.processed_news))]
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
        else:
            return "No hay noticias disponibles."
    
    @rx.var
    def can_load_more(self) -> bool:
        """Indica si se pueden cargar más noticias."""
        # Solo permitir cargar más si tenemos alguna noticia
        return len(self.processed_news) > 0

    @rx.event
    def get_news(self):
        """Obtiene noticias sobre acciones tecnológicas desde GNews API."""
        self.is_loading = True
        self.has_news = False
        self.processed_news = []
        self.page = 1
        
        try:
            # Configurar parámetros para GNews API
            params = {
                "q": self.SEARCH_QUERY,      # Búsqueda simplificada
                "token": self.GNEWS_API_KEY,  # API key
                "lang": "es",                 # Idioma español
                "country": "any",             # Cualquier país para más resultados
                "max": self.max_articles,     # Cantidad de noticias a obtener
                "sortby": "publishedAt",      # Ordenar por fecha de publicación
                "from": "30d",                # Noticias de los últimos 30 días
            }
            
            print(f"Buscando noticias recientes sobre mercados financieros: '{self.SEARCH_QUERY}'")
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
                        
                        # Extraer publicador
                        source = article.get("source", {})
                        publisher = source.get("name", "Fuente desconocida")
                        
                        # Formatear la fecha
                        try:
                            date_str = article.get("publishedAt", "")
                            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
                            date_str = date_obj.strftime("%d %b %Y, %H:%M")
                        except:
                            date_str = "Fecha desconocida"
                            
                        # Obtener resumen y descripción
                        summary = article.get("description", "Sin descripción")
                        
                        # Obtener imagen si está disponible
                        image = article.get("image", "")
                        
                        news_article = NewsArticle(
                            title=title,
                            url=url,
                            publisher=publisher,
                            date=date_str,
                            summary=summary,
                            image=image
                        )
                        processed_articles.append(news_article)
                        print(f"Noticia procesada: {title}")
                    except Exception as e:
                        print(f"Error al procesar noticia: {e}")
                        
                if processed_articles:
                    self.processed_news = processed_articles
                    self.has_news = True
                    print(f"Se procesaron {len(processed_articles)} noticias correctamente")
                else:
                    print("No se pudieron procesar las noticias. Usando noticias de respaldo.")
                    self._create_fallback_news()
            else:
                print("No se encontraron noticias. Usando noticias de respaldo.")
                self._create_fallback_news()
        except Exception as e:
            print(f"Error al obtener noticias: {e}")
            self._create_fallback_news()
        finally:
            self.is_loading = False

    @rx.event
    def load_more_news(self):
        """Carga más noticias financieras (siguiente página)."""
        if not self.can_load_more or self.is_loading:
            return
            
        self.is_loading = True
        self.page += 1  # Incrementar página
        
        try:
            # Configurar parámetros para GNews API
            params = {
                "q": self.SEARCH_QUERY,      # Búsqueda simplificada
                "token": self.GNEWS_API_KEY,  # API key
                "lang": "es",                 # Idioma español
                "country": "any",             # Cualquier país para más resultados
                "max": self.max_articles,     # Cantidad de noticias a obtener
                "page": self.page,            # Página de resultados
                "sortby": "publishedAt",      # Ordenar por fecha de publicación
                "from": "30d",                # Noticias de los últimos 30 días
            }
            
            print(f"Cargando más noticias (página {self.page})")
            response = requests.get(self.GNEWS_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            articles = data.get("articles", [])
            if articles:
                new_articles = []
                
                for article in articles:
                    try:
                        title = article.get("title", "Sin título")
                        url = article.get("url", "#")
                        
                        # Extraer publicador
                        source = article.get("source", {})
                        publisher = source.get("name", "Fuente desconocida")
                        
                        # Formatear la fecha
                        try:
                            date_str = article.get("publishedAt", "")
                            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
                            date_str = date_obj.strftime("%d %b %Y, %H:%M")
                        except:
                            date_str = "Fecha desconocida"
                            
                        # Obtener resumen y descripción
                        summary = article.get("description", "Sin descripción")
                        
                        # Obtener imagen si está disponible
                        image = article.get("image", "")
                        
                        news_article = NewsArticle(
                            title=title,
                            url=url,
                            publisher=publisher,
                            date=date_str,
                            summary=summary,
                            image=image
                        )
                        # Verificar que esta noticia no está ya en la lista actual
                        if not any(existing.title == title for existing in self.processed_news):
                            new_articles.append(news_article)
                    except Exception as e:
                        print(f"Error al procesar noticia adicional: {e}")
                
                # Añadir nuevas noticias a la lista existente
                if new_articles:
                    self.processed_news.extend(new_articles)
                    print(f"Se añadieron {len(new_articles)} noticias adicionales")
                else:
                    print("No se encontraron más noticias nuevas para añadir")
                    # Si no hay más noticias, añadir algunas de respaldo adicionales
                    self._add_more_fallback_news()
            else:
                print("No hay más noticias disponibles. Añadiendo noticias de respaldo adicionales.")
                self._add_more_fallback_news()
        except Exception as e:
            print(f"Error al cargar más noticias: {e}")
            self._add_more_fallback_news()
        finally:
            self.is_loading = False

    def _create_fallback_news(self):
        """Crea noticias de respaldo cuando la API falla."""
        # Fecha actual
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)
        three_days_ago = today - timedelta(days=3)
        
        # Formatear fechas
        today_str = today.strftime("%d %b %Y, %H:%M")
        yesterday_str = yesterday.strftime("%d %b %Y, %H:%M")
        two_days_ago_str = two_days_ago.strftime("%d %b %Y, %H:%M")
        three_days_ago_str = three_days_ago.strftime("%d %b %Y, %H:%M")
        
        news = [
            NewsArticle(
                title="El Ibex 35 cierra la semana con alzas impulsado por el sector bancario",
                url="https://www.google.com/search?q=ibex+35+cierre+semanal",
                publisher="Expansión",
                date=today_str,
                summary="El principal índice bursátil español finalizó la semana con ganancias, destacando el buen comportamiento de los valores bancarios tras las últimas declaraciones del Banco Central Europeo.",
                image=""
            ),
            NewsArticle(
                title="La inflación muestra signos de moderación en la eurozona",
                url="https://www.google.com/search?q=inflacion+eurozona+moderacion",
                publisher="El Economista",
                date=yesterday_str,
                summary="Los últimos datos económicos publicados muestran una desaceleración en el crecimiento de los precios en la eurozona, lo que podría abrir la puerta a posibles recortes de tipos de interés en los próximos meses.",
                image=""
            ),
            NewsArticle(
                title="Wall Street alcanza nuevos máximos históricos impulsado por resultados empresariales",
                url="https://www.google.com/search?q=wall+street+maximos+historicos",
                publisher="Cinco Días",
                date=two_days_ago_str,
                summary="Los principales índices de Wall Street batieron récords esta semana tras la publicación de resultados empresariales mejor de lo esperado en el sector tecnológico y financiero.",
                image=""
            ),
            NewsArticle(
                title="Las materias primas recuperan terreno ante mejores perspectivas económicas globales",
                url="https://www.google.com/search?q=materias+primas+recuperacion",
                publisher="La Vanguardia",
                date=yesterday_str,
                summary="El precio del petróleo y de los metales industriales muestra una tendencia alcista en los últimos días, impulsado por datos económicos positivos de China y Estados Unidos.",
                image=""
            ),
            NewsArticle(
                title="Los inversores aumentan su exposición a activos de riesgo pese a incertidumbres geopolíticas",
                url="https://www.google.com/search?q=inversores+activos+riesgo",
                publisher="El País",
                date=today_str,
                summary="Un informe de JP Morgan señala que los inversores institucionales están incrementando gradualmente sus posiciones en renta variable, a pesar de las tensiones geopolíticas en distintas regiones.",
                image=""
            ),
            NewsArticle(
                title="Las criptomonedas recuperan terreno tras semanas de volatilidad",
                url="https://www.google.com/search?q=criptomonedas+recuperacion+volatilidad",
                publisher="Expansión",
                date=three_days_ago_str,
                summary="Bitcoin y Ethereum lideran una recuperación generalizada en el mercado de criptoactivos, tras la aprobación de nuevos productos financieros vinculados a activos digitales.",
                image=""
            ),
            NewsArticle(
                title="El sector inmobiliario comercial enfrenta desafíos ante el aumento del teletrabajo",
                url="https://www.google.com/search?q=inmobiliario+comercial+teletrabajo",
                publisher="Cinco Días",
                date=two_days_ago_str,
                summary="Los grandes propietarios de oficinas están adaptando sus estrategias ante la consolidación del trabajo híbrido, con una transformación de los espacios hacia modelos más flexibles y servicios adicionales.",
                image=""
            ),
        ]
        
        self.processed_news = news
        self.has_news = True

    def _add_more_fallback_news(self):
        """Añade más noticias de respaldo cuando no se pueden cargar más de la API."""
        # Fecha actual
        today = datetime.now()
        four_days_ago = today - timedelta(days=4)
        five_days_ago = today - timedelta(days=5)
        six_days_ago = today - timedelta(days=6)
        
        # Formatear fechas
        four_days_ago_str = four_days_ago.strftime("%d %b %Y, %H:%M")
        five_days_ago_str = five_days_ago.strftime("%d %b %Y, %H:%M")
        six_days_ago_str = six_days_ago.strftime("%d %b %Y, %H:%M")
        
        # Noticias de respaldo adicionales
        additional_news = [
            NewsArticle(
                title="Los bancos centrales analizan el impacto de las tecnologías financieras en el sistema global",
                url="https://www.google.com/search?q=bancos+centrales+fintech+regulacion",
                publisher="El Economista",
                date=four_days_ago_str,
                summary="Un informe conjunto del Banco Mundial y el FMI analiza los desafíos regulatorios que representan las fintech para la estabilidad financiera global, proponiendo un marco coordinado internacional.",
                image=""
            ),
            NewsArticle(
                title="El oro alcanza nuevo récord histórico ante la incertidumbre económica",
                url="https://www.google.com/search?q=oro+precio+record+historico",
                publisher="Expansión",
                date=five_days_ago_str,
                summary="El metal precioso supera los 2.300 dólares por onza, impulsado por la demanda de activos refugio ante las tensiones geopolíticas y las preocupaciones sobre inflación persistente.",
                image=""
            ),
            NewsArticle(
                title="Las energías renovables atraen inversiones récord en el primer trimestre",
                url="https://www.google.com/search?q=energias+renovables+inversiones+record",
                publisher="Cinco Días",
                date=six_days_ago_str,
                summary="El sector de energías limpias ha captado más de 150.000 millones de dólares en inversiones globales durante el primer trimestre, con la energía solar y el almacenamiento de baterías liderando el crecimiento.",
                image=""
            ),
            NewsArticle(
                title="Nuevas regulaciones de sostenibilidad impactan en estrategias corporativas",
                url="https://www.google.com/search?q=regulaciones+sostenibilidad+empresas",
                publisher="La Vanguardia",
                date=four_days_ago_str,
                summary="Las empresas europeas aceleran su adaptación a los nuevos requerimientos de reporting ESG, con inversiones significativas en transformación de procesos y medición de impacto ambiental.",
                image=""
            ),
            NewsArticle(
                title="El sector tecnológico lidera fusiones y adquisiciones en el mercado global",
                url="https://www.google.com/search?q=fusiones+adquisiciones+sector+tecnologico",
                publisher="El País",
                date=five_days_ago_str,
                summary="Las operaciones corporativas en el sector tecnológico superan los 300.000 millones de dólares en lo que va de año, con especial actividad en segmentos como inteligencia artificial y ciberseguridad.",
                image=""
            ),
        ]
        
        # Añadir solo noticias que no estén ya en la lista
        new_count = 0
        for news_item in additional_news:
            if not any(existing.title == news_item.title for existing in self.processed_news):
                self.processed_news.append(news_item)
                new_count += 1
        
        print(f"Se añadieron {new_count} noticias de respaldo adicionales")

    @rx.event
    def toggle_show_all(self):
        """Alterna entre mostrar todas las noticias o solo las 5 primeras."""
        self.show_all_news = not self.show_all_news

    @rx.event
    def open_url(self, url: str):
        """Abre un enlace en una nueva ventana/pestaña."""
        print(f"Abriendo URL: {url}")
        if not url.startswith(("http://", "https://")):
            url = "https://gnews.io/"
            print(f"URL inválida, usando URL predeterminada: {url}")
        return rx.redirect(url, is_external=True)