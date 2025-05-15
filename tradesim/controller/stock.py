# crud/stock.py
from sqlalchemy.orm import Session
from ..models.stock import Stock
from decimal import Decimal
from typing import List, Optional

def get_stock(db: Session, stock_id: int):
    return db.query(Stock).filter(Stock.id == stock_id).first()

def get_stock_by_symbol(db: Session, symbol: str):
    return db.query(Stock).filter(Stock.symbol == symbol).first()

def get_stocks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Stock).offset(skip).limit(limit).all()

def get_stocks_by_sector(db: Session, sector_id: int, skip: int = 0, limit: int = 100):
    return db.query(Stock).filter(Stock.sector_id == sector_id).offset(skip).limit(limit).all()

def create_stock(db: Session, symbol: str, name: str, current_price: Decimal, sector_id: int):
    db_stock = Stock(
        symbol=symbol,
        name=name,
        current_price=current_price,
        sector_id=sector_id
    )
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

def update_stock(db: Session, stock_id: int, **kwargs):
    db_stock = get_stock(db, stock_id)
    if db_stock:
        for key, value in kwargs.items():
            setattr(db_stock, key, value)
        db.commit()
        db.refresh(db_stock)
    return db_stock

def update_stock_price(db: Session, stock_id: int, new_price: Decimal):
    db_stock = get_stock(db, stock_id)
    if db_stock:
        db_stock.current_price = new_price
        db.commit()
        db.refresh(db_stock)
    return db_stock

def delete_stock(db: Session, stock_id: int):
    db_stock = get_stock(db, stock_id)
    if db_stock:
        db.delete(db_stock)
        db.commit()
        return True
    return False