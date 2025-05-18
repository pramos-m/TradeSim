from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, Enum as SQLAlchemyEnum, CheckConstraint
# from sqlalchemy.orm import relationship # Uncomment if you add relationships
from ..models.base import BaseModel # Assuming this is the SQLAlchemy declarative base
from datetime import datetime
from decimal import Decimal
import enum
from .stock import Stock

class TransactionType(str, enum.Enum):
    COMPRA = "compra"
    VENTA = "venta"
    # ... el resto del modelo ...
    # DIVIDEND = "dividend" # Example: if you want to add other types
    # ADJUSTMENT = "adjustment" # Example

# SQLAlchemy Table Model for Transaction
class StockTransaction(SQLModel, table=True):
    __tablename__ = "transactions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    stock_id: int = Field(foreign_key="stocks.id")
    transaction_type: TransactionType
    quantity: int = Field(gt=0)
    price_per_share: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "tradesim.tradesim.models.user.User" = Relationship(back_populates="transactions", sa_relationship_kwargs={"lazy": "selectin"})
    stock: "Stock" = Relationship(back_populates="transactions", sa_relationship_kwargs={"lazy": "selectin"})

    __table_args__ = (
        CheckConstraint('price_per_share > 0', name='check_transaction_price_positive'),
        CheckConstraint('quantity > 0', name='check_transaction_quantity_positive'), # Quantity is absolute
    )

# Pydantic-style Schemas for Transaction
class TransactionBase(SQLModel):
    user_id: int
    stock_id: int
    transaction_type: TransactionType
    quantity: int = Field(gt=0)
    price_per_share: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

class TransactionCreate(SQLModel):
    user_id: int
    stock_id: int
    transaction_type: TransactionType
    quantity: int = Field(gt=0)
    price_per_share: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

class TransactionRead(SQLModel):
    id: int
    user_id: int
    stock_id: int
    transaction_type: TransactionType
    quantity: int
    price_per_share: Decimal
    timestamp: datetime
    # You might want to include related data here if needed for API responses, e.g., stock_symbol
    # stock_symbol: Optional[str] = None # Example, would require joining in queries