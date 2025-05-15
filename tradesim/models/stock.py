# models/stock.py
from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from ..models.base import BaseModel

class Stock(BaseModel):
    __tablename__ = "stocks"
    
    symbol = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    current_price = Column(Numeric(10, 2), nullable=False)
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=False)
    
    # Relaciones
    sector = relationship("Sector", backref="stocks")
    
    __table_args__ = (
        CheckConstraint('current_price > 0', name='check_current_price_positive'),
    )