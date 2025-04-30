from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
from decimal import Decimal

class StockPriceHistory(Base):
    __tablename__ = "stock_price_history"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True, default=func.now())
    price = Column(Numeric(10, 2), nullable=False)

    # Relationship (optional but good practice)
    stock = relationship("Stock") # Assuming Stock model is defined elsewhere

    def __repr__(self):
        return f"<StockPriceHistory(stock_id={self.stock_id}, timestamp={self.timestamp}, price={self.price})>" 