# scripts/init_db.py
from ..database import engine, Base
from ..models.user import User
from ..models.base import BaseModel

def init_database():
    """Initialize the database by creating all tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()