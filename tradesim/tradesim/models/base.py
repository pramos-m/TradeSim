# /models/base.py
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from ..database import Base

class BaseModel(Base):
    """Base model with common fields for all models."""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    # Using func.now() instead of datetime.utcnow for better database compatibility
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def to_dict(self):
        """Base method to convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
