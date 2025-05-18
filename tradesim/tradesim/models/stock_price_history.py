# tradesim/models/stock_price_history.py
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal
from datetime import datetime

class StockPriceHistory(SQLModel, table=True):
    __tablename__ = "stock_price_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    stock_id: int = Field(foreign_key="stocks.id")
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    price: Decimal = Field(max_digits=10, decimal_places=2)
    
    # Relationship
    stock: "Stock" = Relationship(back_populates="price_history")

class StockPriceHistoryCreate(SQLModel):
    stock_id: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    price: Decimal = Field(max_digits=10, decimal_places=2)

class StockPriceHistoryRead(SQLModel):
    id: int
    stock_id: int
    timestamp: datetime
    price: Decimal

# No es común tener un StockPriceHistoryUpdate, ya que los datos históricos suelen ser inmutables.
# Si lo necesitas, puedes definirlo:
# class StockPriceHistoryUpdate(PydanticBaseModel):
#     timestamp: Optional[datetime] = None
#     price: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)