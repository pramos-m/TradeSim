from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal

class PortfolioItemDB(SQLModel, table=True):
    __tablename__ = "portfolio_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    stock_id: int = Field(foreign_key="stocks.id")
    quantity: int = Field(gt=0)
    purchase_price: Decimal = Field(max_digits=10, decimal_places=2, gt=0)

    # Relationships
    user: "User" = Relationship(back_populates="portfolio_items")
    stock: "Stock" = Relationship(back_populates="portfolio_items")

class PortfolioItemCreate(SQLModel):
    user_id: int
    stock_id: int
    quantity: int = Field(gt=0)
    purchase_price: Decimal = Field(max_digits=10, decimal_places=2, gt=0)

class PortfolioItemRead(SQLModel):
    id: int
    user_id: int
    stock_id: int
    quantity: int
    purchase_price: Decimal

class PortfolioItemUpdate(SQLModel):
    quantity: Optional[int] = Field(default=None, gt=0)
    purchase_price: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2, gt=0) 