# main.py
import reflex as rx
from .database import Base, engine

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# No es necesario crear una nueva instancia de App aquí
# ya que la aplicación se configura en __init__.py