# from typing import Optional, List
# from sqlmodel import SQLModel, Field, Relationship
# from decimal import Decimal
# from datetime import datetime, timezone
# from passlib.context import CryptContext

# # Configuración de Passlib para hashing de contraseñas
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# class User(SQLModel, table=True):
#     __tablename__ = "users"

#     id: Optional[int] = Field(default=None, primary_key=True)
#     username: str = Field(unique=True, index=True)
#     email: str = Field(unique=True, index=True)
#     hashed_password: str
#     full_name: Optional[str] = None
#     account_balance: Decimal = Field(default=Decimal("100000.00"), max_digits=15, decimal_places=2)
#     is_active: bool = Field(default=True)
#     is_superuser: bool = Field(default=False)
#     created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
#     updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
#     profile_picture: Optional[str] = None
#     profile_picture_type: Optional[str] = None

#     # Relationships
#     portfolio_items: List["PortfolioItemDB"] = Relationship(back_populates="user")
#     transactions: List["tradesim.tradesim.models.transaction.StockTransaction"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})

#     def set_password(self, plain_password: str):
#         self.hashed_password = pwd_context.hash(plain_password)

#     def verify_password(self, plain_password: str) -> bool:
#         return pwd_context.verify(plain_password, self.hashed_password)

# # Pydantic-style Schemas para API/Estado
# class UserBase(SQLModel):
#     username: str = Field(unique=True, index=True)
#     email: str = Field(unique=True, index=True)
#     full_name: Optional[str] = None
#     account_balance: Decimal = Field(default=Decimal("100000.00"), max_digits=15, decimal_places=2)

# class UserCreate(SQLModel):
#     username: str
#     email: str
#     password: str
#     full_name: Optional[str] = None
#     account_balance: Decimal = Field(default=Decimal("100000.00"), max_digits=15, decimal_places=2)

# class UserRead(SQLModel):
#     id: int
#     username: str
#     email: str
#     full_name: Optional[str] = None
#     account_balance: Decimal
#     is_active: bool
#     is_superuser: bool
#     created_at: datetime
#     updated_at: datetime

# class UserUpdate(SQLModel):
#     email: Optional[str] = None
#     full_name: Optional[str] = None
#     account_balance: Optional[Decimal] = None
#     is_active: Optional[bool] = None
#     is_superuser: Optional[bool] = None

# models/user.py
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal
from datetime import datetime, timezone
# from passlib.context import CryptContext # Comentado temporalmente

# Configuración de Passlib para hashing de contraseñas
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # Comentado temporalmente

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
    # Asegúrate que los tipos string para las relaciones son correctos según tu estructura
    portfolio_items: List["PortfolioItemDB"] = Relationship(back_populates="user")
    transactions: List["tradesim.tradesim.models.transaction.StockTransaction"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})

    def set_password(self, plain_password: str):
    # self.hashed_password = pwd_context.hash(plain_password) # Comentado
        self.hashed_password = f"PLAIN:{plain_password}" # ¡¡INSEGURO!!
        print(f"MODELS/USER.PY (PATCH): Storing password for {self.email} as {self.hashed_password}")

    def verify_password(self, plain_password: str) -> bool:
        # return pwd_context.verify(plain_password, self.hashed_password) # Comentado
        expected_plain_format = f"PLAIN:{plain_password}"
        is_correct = self.hashed_password == expected_plain_format
        print(f"MODELS/USER.PY (PATCH): Verifying for {self.email}. Expected: '{expected_plain_format}', Got: '{self.hashed_password}', Correct: {is_correct}")
        if not is_correct:
            # Intento de fallback si la contraseña ya estaba hasheada (poco probable si el registro usa el parche)
            try:
                from passlib.context import CryptContext
                temp_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                is_correct_bcrypt = temp_pwd_context.verify(plain_password, self.hashed_password)
                if is_correct_bcrypt:
                    print(f"MODELS/USER.PY (PATCH): Fallback bcrypt verification for {self.email} was successful.")
                    return True
            except Exception as e_bcrypt_fallback:
                print(f"MODELS/USER.PY (PATCH): Fallback bcrypt verification failed for {self.email}: {e_bcrypt_fallback}")
        return is_correct

# Pydantic-style Schemas para API/Estado (sin cambios)
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
