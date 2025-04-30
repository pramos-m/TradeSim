# main.py (en la raíz del proyecto)
from tradesim import app # Importa la app ya configurada e inicializada desde el paquete

# No necesitas importar ni llamar a init_db_tables aquí

if __name__ == "__main__":
    # Usa app.run() para versiones recientes de Reflex
    app.run()
    # Nota: Si usaras una versión muy antigua, sería app.start()