from sqlalchemy import Column, String, Boolean, Float, Integer, DateTime
from sqlalchemy.sql import func
from passlib.context import CryptContext
from ..models.base import BaseModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    __tablename__ = "users"

    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    profile_picture = Column(String, nullable=True, default="/default-profile.png")
    balance = Column(Float, nullable=False, default=0.0)
    initial_balance = Column(Float, nullable=False, default=0.0)
    is_active = Column(Boolean, default=True)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    def to_dict(self):
        """Convert user object to dictionary excluding sensitive data."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "profile_picture": self.profile_picture,
            "balance": self.balance,
            "initial_balance": self.initial_balance,
            "is_active": self.is_active,
            "created_at": self.created_at
        }