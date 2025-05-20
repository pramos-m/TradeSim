# tradesim/tradesim/models/portfolio_item.py
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal
from datetime import datetime

# Forward references para evitar importaciones circulares
# Se usan strings para los tipos de los modelos relacionados
# User = "tradesim.tradesim.models.user.User" 
# Stock = "tradesim.tradesim.models.stock.Stock"
# StockTransaction = "tradesim.tradesim.models.transaction.StockTransaction"

class PortfolioItemDB(SQLModel, table=True):
    __tablename__ = "portfolio_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    stock_id: int = Field(foreign_key="stocks.id")
    
    quantity: int = Field(gt=0, description="Number of shares owned")
    average_price: Decimal = Field(default=0.0, max_digits=10, decimal_places=2, description="Average purchase price per share")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    # Relationships
    # El nombre 'user' debe coincidir con el back_populates en el modelo User
    user: Optional["User"] = Relationship(back_populates="portfolio_items") 
    # El nombre 'stock' debe coincidir con el back_populates en el modelo Stock
    stock: Optional["Stock"] = Relationship(back_populates="portfolio_items")
    
    # Si quieres que PortfolioItemDB tenga una lista de sus transacciones (menos común, usualmente Transaction tiene el portfolio_item_id)
    # transactions: List["StockTransaction"] = Relationship(back_populates="portfolio_item")


# Pydantic-style Schemas para API/Estado si los necesitas
class PortfolioItemBase(SQLModel):
    user_id: int
    stock_id: int
    quantity: int
    average_price: Decimal

class PortfolioItemCreate(PortfolioItemBase):
    pass

class PortfolioItemRead(PortfolioItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # Podrías añadir aquí datos del stock si haces un join en la consulta
    # stock_symbol: Optional[str] = None
    # stock_name: Optional[str] = None

class PortfolioItemUpdate(SQLModel):
    quantity: Optional[int] = None
    average_price: Optional[Decimal] = None
