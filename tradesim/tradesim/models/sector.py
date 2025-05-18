# tradesim/models/sector.py
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Sector(SQLModel, table=True):
    __tablename__ = "sectors"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    sector_name: str = Field(unique=True, index=True)
    
    # Relationship
    stocks: List["Stock"] = Relationship(back_populates="sector")

class SectorCreate(SQLModel):
    sector_name: str

class SectorRead(SQLModel):
    id: int
    sector_name: str

class SectorUpdate(SQLModel):
    sector_name: Optional[str] = None