from sqlalchemy import Column, String, Boolean
from ..models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)