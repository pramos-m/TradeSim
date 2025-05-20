# # tradesim/tradesim/models/stock.py
# from typing import Optional, List
# from sqlmodel import SQLModel, Field, Relationship
# from decimal import Decimal
# from datetime import datetime

# class Sector(SQLModel, table=True): # Definición placeholder si no la tienes aquí
#     id: Optional[int] = Field(default=None, primary_key=True)
#     sector_name: str = Field(unique=True)
#     stocks: List["Stock"] = Relationship(back_populates="sector")

# class StockTransaction(SQLModel, table=True): # Definición placeholder
#     id: Optional[int] = Field(default=None, primary_key=True)
#     # ... otros campos ...
#     stock_id: Optional[int] = Field(default=None, foreign_key="stocks.id")
#     stock: Optional["Stock"] = Relationship(back_populates="transactions")


# class StockPriceHistory(SQLModel, table=True): # Definición placeholder
#     id: Optional[int] = Field(default=None, primary_key=True)
#     # ... otros campos ...
#     stock_id: Optional[int] = Field(default=None, foreign_key="stocks.id")
#     stock: Optional["Stock"] = Relationship(back_populates="price_history")

# class PortfolioItemDB(SQLModel, table=True): # Definición placeholder
#     id: Optional[int] = Field(default=None, primary_key=True)
#     # ... otros campos ...
#     stock_id: Optional[int] = Field(default=None, foreign_key="stocks.id")
#     stock: Optional["Stock"] = Relationship(back_populates="portfolio_items")


# class Stock(SQLModel, table=True):
#     __tablename__ = "stocks"

#     id: Optional[int] = Field(default=None, primary_key=True)
#     symbol: str = Field(unique=True, index=True)
#     name: str
#     current_price: Decimal = Field(max_digits=10, decimal_places=2, default=0.0) # Default para evitar nulls si no se provee
#     last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow) # Usar datetime
    
#     logo_url: Optional[str] = Field(default=None)  # <--- CAMP AFEGIT/ASSEGURAT

#     sector_id: Optional[int] = Field(default=None, foreign_key="sectors.id")

#     # Relationships
#     sector: Optional["Sector"] = Relationship(back_populates="stocks")
#     # Asegúrate que los nombres en back_populates coinciden con los definidos en las otras clases
#     portfolio_items: List["PortfolioItemDB"] = Relationship(back_populates="stock") 
#     transactions: List["StockTransaction"] = Relationship(back_populates="stock")
#     price_history: List["StockPriceHistory"] = Relationship(back_populates="stock")

# class StockCreate(SQLModel):
#     symbol: str
#     name: str
#     current_price: Decimal = Field(max_digits=10, decimal_places=2)
#     logo_url: Optional[str] = None
#     sector_id: Optional[int] = None

# class StockRead(SQLModel):
#     id: int
#     symbol: str
#     name: str
#     current_price: Decimal
#     logo_url: Optional[str] = None
#     sector_id: Optional[int] = None
#     last_updated: Optional[datetime] = None

# class StockUpdate(SQLModel):
#     name: Optional[str] = None
#     current_price: Optional[Decimal] = None
#     logo_url: Optional[str] = None
#     sector_id: Optional[int] = None
#     last_updated: Optional[datetime] = None

# tradesim/tradesim/models/stock.py
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal
from datetime import datetime

# Forward references
# Sector = "tradesim.tradesim.models.sector.Sector" # Ya definido en portfolio_item o sector.py
# PortfolioItemDB = "tradesim.tradesim.models.portfolio_item.PortfolioItemDB" # Ya definido
# StockTransaction = "tradesim.tradesim.models.transaction.StockTransaction" # Ya definido
# StockPriceHistory = "tradesim.tradesim.models.stock_price_history.StockPriceHistory" # Ya definido

class Stock(SQLModel, table=True):
    __tablename__ = "stocks"

    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(unique=True, index=True, max_length=10) # Longitud máxima para símbolos
    name: str = Field(index=True, max_length=100) # Longitud máxima para nombres
    current_price: Decimal = Field(default=Decimal("0.00"), max_digits=12, decimal_places=2)
    last_updated: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    
    logo_url: Optional[str] = Field(default=None, max_length=255) 
    sector_id: Optional[int] = Field(default=None, foreign_key="sectors.id")

    # Relationships
    sector: Optional["Sector"] = Relationship(back_populates="stocks")
    portfolio_items: List["PortfolioItemDB"] = Relationship(back_populates="stock") 
    transactions: List["StockTransaction"] = Relationship(back_populates="stock")
    price_history: List["StockPriceHistory"] = Relationship(back_populates="stock")

class StockCreate(SQLModel):
    symbol: str
    name: str
    current_price: Optional[Decimal] = Decimal("0.00")
    logo_url: Optional[str] = None
    sector_id: Optional[int] = None

class StockRead(SQLModel):
    id: int
    symbol: str
    name: str
    current_price: Decimal
    logo_url: Optional[str]
    sector_id: Optional[int]
    last_updated: datetime
    # Podrías añadir el nombre del sector aquí si haces un join
    # sector_name: Optional[str] = None

class StockUpdate(SQLModel):
    name: Optional[str] = None
    current_price: Optional[Decimal] = None
    logo_url: Optional[str] = None
    sector_id: Optional[int] = None
