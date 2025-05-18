# models/stock.py
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal

class Stock(SQLModel, table=True):
    __tablename__ = "stocks"

    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(unique=True, index=True)
    name: str
    current_price: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    last_updated: Optional[str] = None
    sector_id: Optional[int] = Field(default=None, foreign_key="sectors.id")

    # Relationships
    sector: Optional["Sector"] = Relationship(back_populates="stocks")
    portfolio_items: List["PortfolioItemDB"] = Relationship(back_populates="stock")
    transactions: List["StockTransaction"] = Relationship(back_populates="stock")
    price_history: List["StockPriceHistory"] = Relationship(back_populates="stock")

class StockCreate(SQLModel):
    symbol: str
    name: str
    current_price: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    last_updated: Optional[str] = None
    sector_id: Optional[int] = None

class StockRead(SQLModel):
    id: int
    symbol: str
    name: str
    current_price: Decimal
    last_updated: Optional[str] = None
    sector_id: Optional[int] = None

class StockUpdate(SQLModel):
    name: Optional[str] = None
    current_price: Optional[Decimal] = None
    sector_id: Optional[int] = None
    last_updated: Optional[str] = None
    logo_url: Optional[str] = None