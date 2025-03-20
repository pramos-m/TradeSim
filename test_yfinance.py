import yfinance as yf
import json
from pprint import pprint

def test_yfinance():
    try:
        # Prueba con diferentes tickers
        tickers = ["AAPL", "MSFT", "GOOGL"]
        
        for ticker in tickers:
            print(f"\n{'='*40}\nObteniendo información para {ticker}...\n{'='*40}")
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if not news:
                print(f"No se encontraron noticias para {ticker}")
                continue
                
            print(f"Noticias para {ticker}: {len(news)}")
            
            if len(news) > 0:
                print("\nEstructura de la primera noticia:")
                print(f"Claves disponibles: {list(news[0].keys())}")
                
                # Examinar el contenido detalladamente
                for key in news[0].keys():
                    print(f"\nDetalle de '{key}':")
                    value = news[0][key]
                    value_type = type(value)
                    print(f"  - Tipo: {value_type}")
                    
                    # Mostrar el valor de manera apropiada según su tipo
                    if isinstance(value, str):
                        print(f"  - Valor: {value[:100]}{'...' if len(value) > 100 else ''}")
                    elif isinstance(value, dict):
                        print(f"  - Claves del diccionario: {list(value.keys())}")
                        for subkey, subvalue in list(value.items())[:3]:
                            subval_display = str(subvalue)[:50] + '...' if len(str(subvalue)) > 50 else subvalue
                            print(f"    - {subkey}: {subval_display}")
                        if len(value) > 3:
                            print(f"    - ...y {len(value) - 3} claves más")
                    elif isinstance(value, list):
                        print(f"  - Lista con {len(value)} elementos")
                        if len(value) > 0:
                            print(f"  - Primer elemento (tipo {type(value[0])}): {str(value[0])[:50]}")
                    else:
                        print(f"  - Valor: {value}")
                
                # Si hay un campo content, analízalo más a fondo
                if "content" in news[0]:
                    print("\nAnálisis específico del campo 'content':")
                    content = news[0]["content"]
                    
                    if isinstance(content, str):
                        print("  - Content es una cadena, intentando parsear como JSON:")
                        try:
                            content_dict = json.loads(content)
                            print("  - JSON parseado correctamente")
                            print("  - Claves en el JSON:", list(content_dict.keys()))
                            
                            # Mostrar algunos valores importantes del content
                            important_keys = ["title", "text", "provider", "published"]
                            for key in important_keys:
                                if key in content_dict:
                                    print(f"  - {key}: {str(content_dict[key])[:100]}")
                        except json.JSONDecodeError:
                            print("  - No es un JSON válido")
                            print("  - Primeros 100 caracteres:", content[:100])
                    elif isinstance(content, dict):
                        print("  - Content es un diccionario directamente")
                        print("  - Claves:", list(content.keys()))
                        
                        # Mostrar algunos valores importantes del content
                        important_keys = ["title", "text", "provider", "published"]
                        for key in important_keys:
                            if key in content:
                                print(f"  - {key}: {str(content[key])[:100]}")
                
                # Probar algunos métodos para extraer datos útiles
                print("\nPrueba de extracción de datos:")
                
                # Extracción de título
                title = None
                if "title" in news[0]:
                    title = news[0]["title"]
                elif "content" in news[0] and isinstance(news[0]["content"], dict) and "title" in news[0]["content"]:
                    title = news[0]["content"]["title"]
                print(f"Título extraído: {title}")
                
                # Extracción de enlace
                link = None
                for key in ["link", "url"]:
                    if key in news[0]:
                        link = news[0][key]
                        break
                if not link and "id" in news[0]:
                    link = f"https://finance.yahoo.com/news/{news[0]['id']}"
                print(f"Enlace extraído: {link}")
                
    except Exception as e:
        print(f"Error general: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_yfinance()