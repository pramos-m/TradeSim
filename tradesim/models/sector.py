# models/sector.py
from sqlalchemy import Column, String
from ..models.base import BaseModel

class Sector(BaseModel):
    __tablename__ = "sectors"
    
    sector_name = Column(String, nullable=False)