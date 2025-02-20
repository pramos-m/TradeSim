# crud/user.py
from sqlalchemy.orm import Session
from ..models.user import User
from decimal import Decimal
from typing import Optional, List

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, email: str, username: str, profile_image: Optional[str] = None):
    db_user = User(
        email=email,
        username=username,
        profile_image=profile_image,
        account_balance=Decimal("0.00")
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, **kwargs):
    db_user = get_user(db, user_id)
    if db_user:
        for key, value in kwargs.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def update_balance(db: Session, user_id: int, amount: Decimal):
    db_user = get_user(db, user_id)
    if db_user:
        db_user.account_balance += amount
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False