# tradesim/models/base.py
from sqlmodel import SQLModel

# This is the base class that all models will inherit from
class BaseModel(SQLModel):
    """
    Base model class that all models will inherit from.
    This provides common functionality and configuration for all models.
    """
    pass