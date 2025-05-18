from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal
from datetime import datetime, timezone
from passlib.context import CryptContext

# Configuración de Passlib para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    account_balance: Decimal = Field(default=Decimal("100000.00"), max_digits=15, decimal_places=2)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    profile_picture: Optional[str] = None
    profile_picture_type: Optional[str] = None

    # Relationships
    portfolio_items: List["PortfolioItemDB"] = Relationship(back_populates="user")
    transactions: List["tradesim.tradesim.models.transaction.StockTransaction"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})

    def set_password(self, plain_password: str):
        self.hashed_password = pwd_context.hash(plain_password)

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.hashed_password)

# Pydantic-style Schemas para API/Estado
class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    account_balance: Decimal = Field(default=Decimal("100000.00"), max_digits=15, decimal_places=2)

class UserCreate(SQLModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    account_balance: Decimal = Field(default=Decimal("100000.00"), max_digits=15, decimal_places=2)

class UserRead(SQLModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    account_balance: Decimal
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

class UserUpdate(SQLModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    account_balance: Optional[Decimal] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None