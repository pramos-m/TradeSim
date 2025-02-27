import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tradesim.tradesim.database import engine, Base
from tradesim.tradesim.models.user import User

def init_db():
    """Initialize the database with required tables."""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()