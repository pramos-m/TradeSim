# crud/sector.py
from sqlalchemy.orm import Session
from ..models.sector import Sector
from typing import List

def get_sector(db: Session, sector_id: int):
    return db.query(Sector).filter(Sector.id == sector_id).first()

def get_sector_by_name(db: Session, sector_name: str):
    return db.query(Sector).filter(Sector.sector_name == sector_name).first()

def get_sectors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Sector).offset(skip).limit(limit).all()

def create_sector(db: Session, sector_name: str):
    db_sector = Sector(sector_name=sector_name)
    db.add(db_sector)
    db.commit()
    db.refresh(db_sector)
    return db_sector

def update_sector(db: Session, sector_id: int, sector_name: str):
    db_sector = get_sector(db, sector_id)
    if db_sector:
        db_sector.sector_name = sector_name
        db.commit()
        db.refresh(db_sector)
    return db_sector

def delete_sector(db: Session, sector_id: int):
    db_sector = get_sector(db, sector_id)
    if db_sector:
        db.delete(db_sector)
        db.commit()
        return True
    return False