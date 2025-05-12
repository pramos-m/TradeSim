from sqlalchemy import create_engine, inspect
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
        yield db
    finally:
        db.close()

def init_db_tables():
    """Explicitly import all models and create tables."""
    # Import all models so they are registered with Base
    from .models.user import User
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully!")

from sqlalchemy import text

def add_columns_to_users_table(engine):
    """
    Manually add new columns to existing SQLite database
    """
    try:
        # First, check if columns already exist to prevent errors
        inspector = inspect(engine)
        columns = inspector.get_columns('users')
        column_names = [col['name'] for col in columns]
        
        # Use SQLite connection to add columns with text()
        with engine.connect() as conn:
            if 'profile_picture' not in column_names:
                conn.execute(text("ALTER TABLE users ADD COLUMN profile_picture BLOB"))
                conn.commit()
            
            if 'profile_picture_type' not in column_names:
                conn.execute(text("ALTER TABLE users ADD COLUMN profile_picture_type TEXT"))
                conn.commit()
        
        print("Columns added successfully!")
    
    except Exception as e:
        print(f"Error adding columns: {e}")
        
# Optional: For convenience when needed
def drop_all_tables():
    """
    Drop all tables in the database.
    Use with caution - this will delete all data!
    """
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped successfully!")