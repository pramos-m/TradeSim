# crud/transaction.py
from sqlalchemy.orm import Session
from ..models.transaction import Transaction
from ..models.user import User
from ..models.stock import Stock
from decimal import Decimal
from typing import List, Optional
from datetime import datetime

def get_transaction(db: Session, transaction_id: int):
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()

def get_user_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Transaction).filter(Transaction.user_id == user_id).order_by(Transaction.timestamp.desc()).offset(skip).limit(limit).all()

def get_stock_transactions(db: Session, stock_id: int, skip: int = 0, limit: int = 100):
    return db.query(Transaction).filter(Transaction.stock_id == stock_id).order_by(Transaction.timestamp.desc()).offset(skip).limit(limit).all()

def create_transaction(db: Session, user_id: int, stock_id: int, quantity: int, price: Decimal):
    # Verificar que el usuario existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"Usuario con id {user_id} no encontrado")
        
    # Verificar que la acción existe
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise ValueError(f"Acción con id {stock_id} no encontrada")
    
    # Calcular el monto total de la transacción
    total_amount = price * abs(quantity)
    
    # Si es una compra, verificar que el usuario tiene saldo suficiente
    if quantity > 0 and user.account_balance < total_amount:
        raise ValueError("Saldo insuficiente para realizar la compra")
    
    # Ejecutar la transacción
    db_transaction = Transaction(
        user_id=user_id,
        stock_id=stock_id,
        quantity=quantity,
        price=price,
        timestamp=datetime.utcnow()
    )
    
    # Actualizar el saldo del usuario
    if quantity > 0:  # Compra
        user.account_balance -= total_amount
    else:  # Venta
        user.account_balance += total_amount
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_user_portfolio(db: Session, user_id: int):
    # Obtener todas las transacciones del usuario
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    
    # Calcular la posición por cada acción
    portfolio = {}
    for transaction in transactions:
        stock_id = transaction.stock_id
        if stock_id not in portfolio:
            stock = db.query(Stock).filter(Stock.id == stock_id).first()
            portfolio[stock_id] = {
                "stock": stock,
                "shares": 0,
                "average_price": Decimal("0.0"),
                "total_investment": Decimal("0.0")
            }
        
        # Actualizar la posición
        if transaction.quantity > 0:  # Compra
            current_shares = portfolio[stock_id]["shares"]
            current_investment = portfolio[stock_id]["total_investment"]
            new_shares = current_shares + transaction.quantity
            new_investment = current_investment + (transaction.price * transaction.quantity)
            
            # Recalcular precio promedio
            if new_shares > 0:
                portfolio[stock_id]["average_price"] = new_investment / new_shares
            
            portfolio[stock_id]["shares"] = new_shares
            portfolio[stock_id]["total_investment"] = new_investment
        else:  # Venta
            portfolio[stock_id]["shares"] += transaction.quantity
    
    # Filtrar solo posiciones activas (shares > 0)
    active_positions = {k: v for k, v in portfolio.items() if v["shares"] > 0}
    return active_positions