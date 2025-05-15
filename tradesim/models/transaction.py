# models/transaction.py
from sqlalchemy import Column, Integer, Numeric, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..models.base import BaseModel

class Transaction(BaseModel):
    __tablename__ = "transactions"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    timestamp = Column(DateTime, default=func.now())
    
    # Relaciones
    user = relationship("User", backref="transactions")
    stock = relationship("Stock", backref="transactions")
    
    __table_args__ = (
        CheckConstraint('price > 0', name='check_price_positive'),
    )