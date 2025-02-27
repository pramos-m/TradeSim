from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Ensure database is created in the correct location
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "../tradesim.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create engine with absolute path to ensure correct location
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise

def init_db_tables():
    """Explicitly import all models and create tables."""
    # Import all models so they are registered with Base
    from .models.user import User
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully!")